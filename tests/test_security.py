"""Tests for security scanner module."""

from wetwire_github.security import (
    SecurityIssue,
    SecurityReport,
    SecurityScanner,
    Severity,
)
from wetwire_github.workflow import Job, Permissions, Step, Workflow
from wetwire_github.workflow.expressions import GitHub


class TestSeverity:
    """Tests for Severity enum."""

    def test_severity_values(self):
        """Severity enum has correct values."""
        assert Severity.CRITICAL.value == "critical"
        assert Severity.HIGH.value == "high"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.LOW.value == "low"


class TestSecurityIssue:
    """Tests for SecurityIssue dataclass."""

    def test_security_issue_creation(self):
        """SecurityIssue can be created with required fields."""
        issue = SecurityIssue(
            title="Hardcoded Secret",
            description="API key found in run command",
            severity=Severity.CRITICAL,
            recommendation="Use GitHub Secrets instead",
        )
        assert issue.title == "Hardcoded Secret"
        assert issue.description == "API key found in run command"
        assert issue.severity == Severity.CRITICAL
        assert issue.recommendation == "Use GitHub Secrets instead"
        assert issue.location == ""

    def test_security_issue_with_location(self):
        """SecurityIssue can include location information."""
        issue = SecurityIssue(
            title="Script Injection",
            description="Unsafe use of github.event",
            severity=Severity.HIGH,
            recommendation="Sanitize inputs",
            location="job: build, step: 2",
        )
        assert issue.location == "job: build, step: 2"


class TestSecurityReport:
    """Tests for SecurityReport dataclass."""

    def test_security_report_empty(self):
        """SecurityReport can be created empty."""
        report = SecurityReport()
        assert report.issues == []
        assert report.critical_count == 0
        assert report.high_count == 0
        assert report.medium_count == 0
        assert report.low_count == 0
        assert report.total_count == 0

    def test_security_report_with_issues(self):
        """SecurityReport counts issues by severity."""
        report = SecurityReport(
            issues=[
                SecurityIssue(
                    title="Issue 1",
                    description="Critical issue",
                    severity=Severity.CRITICAL,
                    recommendation="Fix it",
                ),
                SecurityIssue(
                    title="Issue 2",
                    description="High issue",
                    severity=Severity.HIGH,
                    recommendation="Fix it",
                ),
                SecurityIssue(
                    title="Issue 3",
                    description="Another critical issue",
                    severity=Severity.CRITICAL,
                    recommendation="Fix it",
                ),
                SecurityIssue(
                    title="Issue 4",
                    description="Medium issue",
                    severity=Severity.MEDIUM,
                    recommendation="Fix it",
                ),
                SecurityIssue(
                    title="Issue 5",
                    description="Low issue",
                    severity=Severity.LOW,
                    recommendation="Fix it",
                ),
            ]
        )
        assert report.critical_count == 2
        assert report.high_count == 1
        assert report.medium_count == 1
        assert report.low_count == 1
        assert report.total_count == 5


class TestSecurityScannerHardcodedSecrets:
    """Tests for hardcoded secrets detection."""

    def test_detect_api_key_in_run(self):
        """Scanner detects hardcoded API keys in run commands."""
        workflow = Workflow(
            name="Test",
            jobs={
                "build": Job(
                    steps=[
                        Step(run="export API_KEY=sk_test_1234567890abcdef"),
                    ]
                )
            },
        )
        scanner = SecurityScanner()
        report = scanner.scan(workflow)
        secret_issues = [i for i in report.issues if "hardcoded" in i.title.lower()]
        assert len(secret_issues) == 1
        assert secret_issues[0].severity == Severity.CRITICAL

    def test_detect_password_in_run(self):
        """Scanner detects hardcoded passwords in run commands."""
        workflow = Workflow(
            name="Test",
            jobs={
                "build": Job(
                    steps=[
                        Step(run="mysql -u root -p'MyPassword123!'"),
                    ]
                )
            },
        )
        scanner = SecurityScanner()
        report = scanner.scan(workflow)
        secret_issues = [i for i in report.issues if "hardcoded" in i.title.lower()]
        assert len(secret_issues) == 1
        assert secret_issues[0].severity == Severity.CRITICAL

    def test_detect_token_in_env(self):
        """Scanner detects hardcoded tokens in environment variables."""
        workflow = Workflow(
            name="Test",
            jobs={
                "build": Job(
                    steps=[
                        Step(
                            run="echo 'Deploy'",
                            env={"GITHUB_TOKEN": "ghp_1234567890abcdefghijklmnop"},
                        ),
                    ]
                )
            },
        )
        scanner = SecurityScanner()
        report = scanner.scan(workflow)
        secret_issues = [i for i in report.issues if "hardcoded" in i.title.lower()]
        assert len(secret_issues) == 1
        assert secret_issues[0].severity == Severity.CRITICAL


class TestSecurityScannerScriptInjection:
    """Tests for script injection detection."""

    def test_detect_github_event_in_run(self):
        """Scanner detects unsafe use of github.event in run."""
        workflow = Workflow(
            name="Test",
            jobs={
                "build": Job(
                    steps=[
                        Step(run="echo 'Title: ${{ github.event.issue.title }}'"),
                    ]
                )
            },
        )
        scanner = SecurityScanner()
        report = scanner.scan(workflow)
        injection_issues = [i for i in report.issues if "injection" in i.title.lower()]
        assert len(injection_issues) == 1
        assert injection_issues[0].severity == Severity.HIGH

    def test_detect_github_event_pull_request(self):
        """Scanner detects github.event.pull_request injection."""
        workflow = Workflow(
            name="Test",
            jobs={
                "build": Job(
                    steps=[
                        Step(run="git checkout ${{ github.event.pull_request.head.ref }}"),
                    ]
                )
            },
        )
        scanner = SecurityScanner()
        report = scanner.scan(workflow)
        injection_issues = [i for i in report.issues if "injection" in i.title.lower()]
        assert len(injection_issues) == 1
        assert injection_issues[0].severity == Severity.HIGH

    def test_safe_github_context_usage(self):
        """Scanner allows safe github context usage."""
        workflow = Workflow(
            name="Test",
            jobs={
                "build": Job(
                    steps=[
                        Step(run="echo 'Ref: ${{ github.ref }}'"),
                        Step(run="echo 'SHA: ${{ github.sha }}'"),
                    ]
                )
            },
        )
        scanner = SecurityScanner()
        report = scanner.scan(workflow)
        # github.ref and github.sha are safe
        injection_issues = [i for i in report.issues if "injection" in i.title.lower()]
        assert len(injection_issues) == 0


class TestSecurityScannerUnpinnedActions:
    """Tests for unpinned actions detection."""

    def test_detect_action_without_version(self):
        """Scanner detects actions without version or SHA."""
        workflow = Workflow(
            name="Test",
            jobs={
                "build": Job(
                    steps=[
                        Step(uses="actions/checkout"),
                    ]
                )
            },
        )
        scanner = SecurityScanner()
        report = scanner.scan(workflow)
        unpinned_issues = [i for i in report.issues if "unpinned" in i.title.lower()]
        assert len(unpinned_issues) == 1
        assert unpinned_issues[0].severity == Severity.MEDIUM

    def test_detect_action_with_branch(self):
        """Scanner detects actions pinned to branch."""
        workflow = Workflow(
            name="Test",
            jobs={
                "build": Job(
                    steps=[
                        Step(uses="actions/checkout@main"),
                    ]
                )
            },
        )
        scanner = SecurityScanner()
        report = scanner.scan(workflow)
        unpinned_issues = [i for i in report.issues if "unpinned" in i.title.lower()]
        assert len(unpinned_issues) == 1
        assert unpinned_issues[0].severity == Severity.MEDIUM

    def test_allow_action_with_sha(self):
        """Scanner allows actions pinned to SHA."""
        workflow = Workflow(
            name="Test",
            jobs={
                "build": Job(
                    steps=[
                        Step(uses="actions/checkout@8e5e7e5ab8b370d6c329ec480221332ada57f0ab"),
                    ]
                )
            },
        )
        scanner = SecurityScanner()
        report = scanner.scan(workflow)
        unpinned_issues = [i for i in report.issues if "unpinned" in i.title.lower()]
        assert len(unpinned_issues) == 0

    def test_allow_action_with_version_tag(self):
        """Scanner allows actions with semantic version tags."""
        workflow = Workflow(
            name="Test",
            jobs={
                "build": Job(
                    steps=[
                        Step(uses="actions/checkout@v4"),
                        Step(uses="actions/setup-python@v5.0.0"),
                    ]
                )
            },
        )
        scanner = SecurityScanner()
        report = scanner.scan(workflow)
        unpinned_issues = [i for i in report.issues if "unpinned" in i.title.lower()]
        assert len(unpinned_issues) == 0


class TestSecurityScannerExcessivePermissions:
    """Tests for excessive permissions detection."""

    def test_detect_write_all_permissions(self):
        """Scanner detects write-all permissions."""
        workflow = Workflow(
            name="Test",
            permissions=Permissions(write_all=True),
            jobs={
                "build": Job(
                    steps=[Step(run="echo 'test'")],
                )
            },
        )
        scanner = SecurityScanner()
        report = scanner.scan(workflow)
        assert len(report.issues) == 1
        assert report.issues[0].severity == Severity.HIGH
        assert "excessive" in report.issues[0].title.lower()

    def test_detect_write_all_in_job(self):
        """Scanner detects write-all permissions in job."""
        workflow = Workflow(
            name="Test",
            jobs={
                "build": Job(
                    permissions=Permissions(write_all=True),
                    steps=[Step(run="echo 'test'")],
                )
            },
        )
        scanner = SecurityScanner()
        report = scanner.scan(workflow)
        excessive_issues = [i for i in report.issues if "excessive" in i.title.lower()]
        assert len(excessive_issues) == 1
        assert excessive_issues[0].severity == Severity.HIGH

    def test_allow_specific_permissions(self):
        """Scanner allows specific permissions."""
        workflow = Workflow(
            name="Test",
            permissions=Permissions(contents="read", issues="write"),
            jobs={
                "build": Job(
                    steps=[Step(run="echo 'test'")],
                )
            },
        )
        scanner = SecurityScanner()
        report = scanner.scan(workflow)
        excessive_issues = [i for i in report.issues if "excessive" in i.title.lower()]
        assert len(excessive_issues) == 0


class TestSecurityScannerMissingPermissions:
    """Tests for missing permissions detection."""

    def test_detect_missing_permissions_in_workflow(self):
        """Scanner detects workflows without permissions block."""
        workflow = Workflow(
            name="Test",
            jobs={
                "build": Job(
                    steps=[Step(run="echo 'test'")],
                )
            },
        )
        scanner = SecurityScanner()
        report = scanner.scan(workflow)
        missing_issues = [i for i in report.issues if "missing" in i.title.lower()]
        assert len(missing_issues) == 1
        assert missing_issues[0].severity == Severity.LOW

    def test_allow_workflow_with_permissions(self):
        """Scanner allows workflows with permissions block."""
        workflow = Workflow(
            name="Test",
            permissions=Permissions(contents="read"),
            jobs={
                "build": Job(
                    steps=[Step(run="echo 'test'")],
                )
            },
        )
        scanner = SecurityScanner()
        report = scanner.scan(workflow)
        missing_issues = [i for i in report.issues if "missing" in i.title.lower()]
        assert len(missing_issues) == 0

    def test_allow_read_all_permissions(self):
        """Scanner allows read-all permissions."""
        workflow = Workflow(
            name="Test",
            permissions=Permissions(read_all=True),
            jobs={
                "build": Job(
                    steps=[Step(run="echo 'test'")],
                )
            },
        )
        scanner = SecurityScanner()
        report = scanner.scan(workflow)
        missing_issues = [i for i in report.issues if "missing" in i.title.lower()]
        assert len(missing_issues) == 0


class TestSecurityScannerCleanWorkflow:
    """Tests for clean workflow (no issues)."""

    def test_clean_workflow_no_issues(self):
        """Scanner reports no issues for secure workflow."""
        workflow = Workflow(
            name="CI",
            permissions=Permissions(contents="read"),
            jobs={
                "build": Job(
                    steps=[
                        Step(uses="actions/checkout@v4"),
                        Step(run="make build"),
                        Step(
                            run="echo 'Token: $TOKEN'",
                            env={"TOKEN": str(GitHub.token)},
                        ),
                    ]
                )
            },
        )
        scanner = SecurityScanner()
        report = scanner.scan(workflow)
        assert report.total_count == 0
        assert len(report.issues) == 0


class TestSecurityScannerMultipleIssues:
    """Tests for workflows with multiple security issues."""

    def test_multiple_issues_in_same_workflow(self):
        """Scanner detects multiple issues in same workflow."""
        workflow = Workflow(
            name="Deploy",
            jobs={
                "deploy": Job(
                    permissions=Permissions(write_all=True),
                    steps=[
                        Step(uses="actions/checkout"),
                        Step(run="export API_KEY=sk_test_123"),
                        Step(run="echo '${{ github.event.issue.title }}'"),
                    ]
                )
            },
        )
        scanner = SecurityScanner()
        report = scanner.scan(workflow)

        # Should detect:
        # 1. Missing workflow-level permissions
        # 2. Write-all permissions in job
        # 3. Unpinned action
        # 4. Hardcoded secret
        # 5. Script injection
        assert report.total_count >= 5
        assert report.critical_count >= 1  # Hardcoded secret
        assert report.high_count >= 1  # Write-all or script injection
        assert report.medium_count >= 1  # Unpinned action
        assert report.low_count >= 1  # Missing permissions

    def test_issue_locations_are_set(self):
        """Scanner sets location information for issues."""
        workflow = Workflow(
            name="Test",
            jobs={
                "build": Job(
                    steps=[
                        Step(run="export TOKEN=secret123"),
                    ]
                ),
                "deploy": Job(
                    steps=[
                        Step(uses="actions/checkout"),
                    ]
                ),
            },
        )
        scanner = SecurityScanner()
        report = scanner.scan(workflow)

        # All issues should have location information
        for issue in report.issues:
            if "hardcoded" in issue.title.lower():
                assert "build" in issue.location
            elif "unpinned" in issue.title.lower():
                assert "deploy" in issue.location
