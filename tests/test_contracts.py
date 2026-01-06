"""Tests for contracts (protocols and result types)."""

from wetwire_github.contracts import (
    BuildResult,
    DiscoveredJob,
    DiscoveredWorkflow,
    LintIssue,
    LintResult,
    ListResult,
    ListWorkflow,
    OutputRef,
    ValidateResult,
)


class TestOutputRef:
    """Tests for OutputRef dataclass."""

    def test_output_ref_str(self):
        """OutputRef converts to expression string."""
        ref = OutputRef(step_id="build", output="version")
        assert str(ref) == "${{ steps.build.outputs.version }}"

    def test_output_ref_fields(self):
        """OutputRef stores step_id and output."""
        ref = OutputRef(step_id="test", output="result")
        assert ref.step_id == "test"
        assert ref.output == "result"


class TestDiscoveredWorkflow:
    """Tests for DiscoveredWorkflow dataclass."""

    def test_discovered_workflow(self):
        """DiscoveredWorkflow stores discovery info."""
        dw = DiscoveredWorkflow(
            name="ci",
            file="src/my_ci/workflows.py",
            line=10,
            jobs=["build", "test"],
        )
        assert dw.name == "ci"
        assert dw.file == "src/my_ci/workflows.py"
        assert dw.line == 10
        assert dw.jobs == ["build", "test"]


class TestDiscoveredJob:
    """Tests for DiscoveredJob dataclass."""

    def test_discovered_job(self):
        """DiscoveredJob stores discovery info."""
        dj = DiscoveredJob(
            name="build",
            file="src/my_ci/jobs.py",
            line=15,
            dependencies=["setup"],
        )
        assert dj.name == "build"
        assert dj.file == "src/my_ci/jobs.py"
        assert dj.line == 15
        assert dj.dependencies == ["setup"]


class TestBuildResult:
    """Tests for BuildResult dataclass."""

    def test_build_result_success(self):
        """BuildResult can indicate success."""
        result = BuildResult(
            success=True,
            workflows=["ci", "release"],
            files=[".github/workflows/ci.yml", ".github/workflows/release.yml"],
        )
        assert result.success is True
        assert len(result.workflows) == 2
        assert len(result.files) == 2

    def test_build_result_failure(self):
        """BuildResult can indicate failure."""
        result = BuildResult(
            success=False,
            errors=["Invalid workflow definition"],
        )
        assert result.success is False
        assert "Invalid workflow definition" in result.errors


class TestLintIssue:
    """Tests for LintIssue dataclass."""

    def test_lint_issue(self):
        """LintIssue stores issue details."""
        issue = LintIssue(
            file="src/my_ci/workflows.py",
            line=10,
            column=5,
            severity="warning",
            message="Use typed action wrapper instead of raw string",
            rule="WAG001",
            fixable=True,
        )
        assert issue.file == "src/my_ci/workflows.py"
        assert issue.line == 10
        assert issue.column == 5
        assert issue.severity == "warning"
        assert issue.rule == "WAG001"
        assert issue.fixable is True


class TestLintResult:
    """Tests for LintResult dataclass."""

    def test_lint_result_success(self):
        """LintResult can indicate no issues."""
        result = LintResult(success=True)
        assert result.success is True
        assert result.issues is None

    def test_lint_result_with_issues(self):
        """LintResult can contain issues."""
        issues = [
            LintIssue(
                file="src/my_ci/workflows.py",
                line=10,
                column=5,
                severity="warning",
                message="Test",
                rule="WAG001",
                fixable=True,
            )
        ]
        result = LintResult(success=False, issues=issues)
        assert result.success is False
        assert len(result.issues) == 1


class TestValidateResult:
    """Tests for ValidateResult dataclass."""

    def test_validate_result_valid(self):
        """ValidateResult can indicate valid workflow."""
        result = ValidateResult(success=True)
        assert result.success is True

    def test_validate_result_with_errors(self):
        """ValidateResult can contain errors."""
        result = ValidateResult(
            success=False,
            errors=["unknown action: invalid/action@v1"],
        )
        assert result.success is False
        assert len(result.errors) == 1

    def test_validate_result_with_warnings(self):
        """ValidateResult can contain warnings."""
        result = ValidateResult(
            success=True,
            warnings=["deprecated syntax"],
        )
        assert result.success is True
        assert len(result.warnings) == 1


class TestListWorkflow:
    """Tests for ListWorkflow dataclass."""

    def test_list_workflow(self):
        """ListWorkflow stores workflow summary."""
        lw = ListWorkflow(
            name="ci",
            file="src/my_ci/workflows.py",
            line=10,
            jobs=3,
        )
        assert lw.name == "ci"
        assert lw.file == "src/my_ci/workflows.py"
        assert lw.line == 10
        assert lw.jobs == 3


class TestListResult:
    """Tests for ListResult dataclass."""

    def test_list_result(self):
        """ListResult contains workflow list."""
        workflows = [
            ListWorkflow(name="ci", file="workflows.py", line=10, jobs=2),
            ListWorkflow(name="release", file="workflows.py", line=50, jobs=1),
        ]
        result = ListResult(workflows=workflows)
        assert len(result.workflows) == 2
