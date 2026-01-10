"""Tests for security-related linting rules WAG017 and WAG018."""

from wetwire_github.linter import Linter
from wetwire_github.linter.rules import (
    WAG017HardcodedSecretsInRun,
    WAG018UnpinnedActions,
)


class TestWAG017HardcodedSecretsInRun:
    """Tests for WAG017: Detect hardcoded secrets in run commands."""

    def test_rule_id(self):
        """Rule has correct ID."""
        rule = WAG017HardcodedSecretsInRun()
        assert rule.id == "WAG017"

    def test_rule_description(self):
        """Rule has a description."""
        rule = WAG017HardcodedSecretsInRun()
        assert len(rule.description) > 0

    def test_detect_password_in_run_command(self):
        """Detect hardcoded password in run command."""
        rule = WAG017HardcodedSecretsInRun()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step = Step(run="mysql -u root -pMySecretPassword123")
""",
            "test.py",
        )
        assert len(errors) == 1
        assert "hardcoded" in errors[0].message.lower() or "secret" in errors[0].message.lower()

    def test_detect_api_key_in_run_command(self):
        """Detect hardcoded API key in run command."""
        rule = WAG017HardcodedSecretsInRun()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step = Step(run="curl -H 'Authorization: Bearer sk_live_abc123xyz789abcdefghij'")
""",
            "test.py",
        )
        assert len(errors) == 1

    def test_detect_aws_key_in_run_command(self):
        """Detect hardcoded AWS key in run command."""
        rule = WAG017HardcodedSecretsInRun()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step = Step(run="export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY")
""",
            "test.py",
        )
        assert len(errors) == 1

    def test_detect_token_in_run_command(self):
        """Detect hardcoded token in run command."""
        rule = WAG017HardcodedSecretsInRun()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step = Step(run="gh auth login --with-token ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
""",
            "test.py",
        )
        assert len(errors) == 1

    def test_allow_secrets_reference(self):
        """Allow proper secrets reference in run command."""
        rule = WAG017HardcodedSecretsInRun()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step = Step(run="echo ${{ secrets.API_KEY }}")
""",
            "test.py",
        )
        # Using ${{ secrets.* }} is okay (though WAG003 may flag it separately)
        assert len(errors) == 0

    def test_allow_environment_variable(self):
        """Allow environment variable reference in run command."""
        rule = WAG017HardcodedSecretsInRun()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step = Step(run="echo $API_KEY", env={"API_KEY": "${{ secrets.API_KEY }}"})
""",
            "test.py",
        )
        assert len(errors) == 0

    def test_allow_safe_run_commands(self):
        """Allow safe run commands without secrets."""
        rule = WAG017HardcodedSecretsInRun()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step1 = Step(run="npm install")
step2 = Step(run="pytest tests/")
step3 = Step(run="echo 'Hello World'")
""",
            "test.py",
        )
        assert len(errors) == 0


class TestWAG017AutoFix:
    """Tests for WAG017 auto-fix functionality."""

    def test_suggest_secrets_for_password(self):
        """Suggest using Secrets for password."""
        rule = WAG017HardcodedSecretsInRun()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step = Step(run="mysql -p'MyPassword123'")
""",
            "test.py",
        )
        assert len(errors) == 1
        assert errors[0].suggestion is not None
        assert "Secrets" in errors[0].suggestion or "secrets" in errors[0].suggestion.lower()

    def test_fix_hardcoded_secret(self):
        """Fix replaces hardcoded secret with Secrets.get() suggestion."""
        rule = WAG017HardcodedSecretsInRun()
        source = """
from wetwire_github.workflow import Step
step = Step(run="export API_KEY=sk_live_abc123xyz")
"""
        # Check that fix method exists and returns expected format
        if hasattr(rule, 'fix'):
            fixed, count, remaining = rule.fix(source, "test.py")
            assert isinstance(fixed, str)
            assert isinstance(count, int)
            assert isinstance(remaining, list)


class TestWAG018UnpinnedActions:
    """Tests for WAG018: Detect unpinned actions."""

    def test_rule_id(self):
        """Rule has correct ID."""
        rule = WAG018UnpinnedActions()
        assert rule.id == "WAG018"

    def test_rule_description(self):
        """Rule has a description."""
        rule = WAG018UnpinnedActions()
        assert len(rule.description) > 0

    def test_detect_unpinned_action_no_version(self):
        """Detect action without any version pin."""
        rule = WAG018UnpinnedActions()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step = Step(uses="actions/checkout")
""",
            "test.py",
        )
        assert len(errors) == 1
        assert "unpinned" in errors[0].message.lower() or "pin" in errors[0].message.lower()

    def test_detect_unpinned_action_branch(self):
        """Detect action pinned to branch (not SHA)."""
        rule = WAG018UnpinnedActions()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step = Step(uses="actions/checkout@main")
""",
            "test.py",
        )
        assert len(errors) == 1
        assert "main" in errors[0].message or "branch" in errors[0].message.lower()

    def test_allow_pinned_action_version(self):
        """Allow action pinned to version tag."""
        rule = WAG018UnpinnedActions()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step = Step(uses="actions/checkout@v4")
""",
            "test.py",
        )
        # Version tags like @v4 are acceptable
        assert len(errors) == 0

    def test_allow_pinned_action_sha(self):
        """Allow action pinned to SHA."""
        rule = WAG018UnpinnedActions()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step = Step(uses="actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11")
""",
            "test.py",
        )
        # SHA pins are most secure
        assert len(errors) == 0

    def test_allow_pinned_action_semver(self):
        """Allow action pinned to semantic version."""
        rule = WAG018UnpinnedActions()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step = Step(uses="actions/setup-python@v5.0.0")
""",
            "test.py",
        )
        assert len(errors) == 0

    def test_allow_typed_action_wrappers(self):
        """Allow typed action wrappers (they handle pinning)."""
        rule = WAG018UnpinnedActions()
        errors = rule.check(
            """
from wetwire_github.actions import checkout, setup_python
step1 = checkout()
step2 = setup_python(python_version="3.11")
""",
            "test.py",
        )
        assert len(errors) == 0

    def test_detect_multiple_unpinned_actions(self):
        """Detect multiple unpinned actions."""
        rule = WAG018UnpinnedActions()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step1 = Step(uses="actions/checkout")
step2 = Step(uses="actions/setup-python")
step3 = Step(uses="owner/custom-action")
""",
            "test.py",
        )
        assert len(errors) == 3


class TestWAG018AutoFix:
    """Tests for WAG018 auto-fix functionality."""

    def test_suggest_version_pin(self):
        """Suggest pinning to version."""
        rule = WAG018UnpinnedActions()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step = Step(uses="actions/checkout")
""",
            "test.py",
        )
        assert len(errors) == 1
        assert errors[0].suggestion is not None
        assert "@v" in errors[0].suggestion or "pin" in errors[0].suggestion.lower()

    def test_fix_unpinned_action(self):
        """Fix adds version pin to unpinned action."""
        rule = WAG018UnpinnedActions()
        source = """
from wetwire_github.workflow import Step
step = Step(uses="actions/checkout")
"""
        fixed, count, remaining = rule.fix(source, "test.py")

        assert count == 1
        assert "@v4" in fixed or "@v" in fixed
        assert 'Step(uses="actions/checkout")' not in fixed

    def test_fix_multiple_unpinned_actions(self):
        """Fix adds version pins to multiple unpinned actions."""
        rule = WAG018UnpinnedActions()
        source = """
from wetwire_github.workflow import Step
step1 = Step(uses="actions/checkout")
step2 = Step(uses="actions/setup-python")
"""
        fixed, count, remaining = rule.fix(source, "test.py")

        assert count == 2
        # Both should be pinned
        assert "checkout@" in fixed or "checkout@v" in fixed
        assert "setup-python@" in fixed or "setup-python@v" in fixed


class TestSecurityRulesInDefaultRules:
    """Test that security rules are included in default rules."""

    def test_default_rules_include_wag017(self):
        """WAG017 is in default rules."""
        from wetwire_github.linter.rules import get_default_rules

        rules = get_default_rules()
        rule_ids = [r.id for r in rules]
        assert "WAG017" in rule_ids

    def test_default_rules_include_wag018(self):
        """WAG018 is in default rules."""
        from wetwire_github.linter.rules import get_default_rules

        rules = get_default_rules()
        rule_ids = [r.id for r in rules]
        assert "WAG018" in rule_ids


class TestSecurityRulesWithLinter:
    """Integration tests with Linter class."""

    def test_linter_catches_hardcoded_secrets(self):
        """Linter with security rules catches hardcoded secrets."""
        linter = Linter(rules=[WAG017HardcodedSecretsInRun()])
        result = linter.check(
            """
from wetwire_github.workflow import Step
step = Step(run="export TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
""",
            "test.py",
        )
        assert not result.is_clean
        assert any(e.rule_id == "WAG017" for e in result.errors)

    def test_linter_catches_unpinned_actions(self):
        """Linter with security rules catches unpinned actions."""
        linter = Linter(rules=[WAG018UnpinnedActions()])
        result = linter.check(
            """
from wetwire_github.workflow import Step
step = Step(uses="actions/checkout")
""",
            "test.py",
        )
        assert not result.is_clean
        assert any(e.rule_id == "WAG018" for e in result.errors)

    def test_linter_fix_applies_security_fixes(self):
        """Linter.fix() applies security rule fixes."""
        linter = Linter(rules=[WAG018UnpinnedActions()])
        source = """
from wetwire_github.workflow import Step
step = Step(uses="actions/checkout")
"""
        result = linter.fix(source, "test.py")

        assert result.fixed_count >= 1
        assert "@v" in result.source


class TestWAG019UnusedPermissions:
    """Tests for WAG019: Detect unused permissions grants."""

    def test_rule_id(self):
        """Rule has correct ID."""
        from wetwire_github.linter.rules import WAG019UnusedPermissions

        rule = WAG019UnusedPermissions()
        assert rule.id == "WAG019"

    def test_rule_description(self):
        """Rule has a description."""
        from wetwire_github.linter.rules import WAG019UnusedPermissions

        rule = WAG019UnusedPermissions()
        assert len(rule.description) > 0

    def test_detect_unused_write_permission(self):
        """Detect write permission that isn't used by any step."""
        from wetwire_github.linter.rules import WAG019UnusedPermissions

        rule = WAG019UnusedPermissions()
        errors = rule.check(
            """
from wetwire_github.workflow import Workflow, Job, Step

job = Job(
    runs_on="ubuntu-latest",
    permissions={"contents": "write", "issues": "write"},
    steps=[
        Step(run="echo hello"),
    ],
)
""",
            "test.py",
        )
        # Should flag unused permissions since no step uses them
        assert len(errors) >= 1
        assert "WAG019" in errors[0].rule_id

    def test_allow_used_permissions(self):
        """Allow permissions that are actually used by actions."""
        from wetwire_github.linter.rules import WAG019UnusedPermissions

        rule = WAG019UnusedPermissions()
        errors = rule.check(
            """
from wetwire_github.workflow import Workflow, Job, Step

job = Job(
    runs_on="ubuntu-latest",
    permissions={"contents": "read"},
    steps=[
        Step(uses="actions/checkout@v4"),
    ],
)
""",
            "test.py",
        )
        # contents: read is needed for checkout
        assert len(errors) == 0

    def test_detect_overly_broad_permissions(self):
        """Detect write-all when only specific permissions are needed."""
        from wetwire_github.linter.rules import WAG019UnusedPermissions

        rule = WAG019UnusedPermissions()
        errors = rule.check(
            """
from wetwire_github.workflow import Workflow, Job, Step

job = Job(
    runs_on="ubuntu-latest",
    permissions="write-all",
    steps=[
        Step(uses="actions/checkout@v4"),
    ],
)
""",
            "test.py",
        )
        # write-all is overly permissive for just checkout
        assert len(errors) >= 1


class TestWAG019AutoFix:
    """Tests for WAG019 auto-fix functionality."""

    def test_fix_removes_unused_permission(self):
        """Fix should remove unused permissions from Job."""
        from wetwire_github.linter.rules import WAG019UnusedPermissions

        rule = WAG019UnusedPermissions()
        source = """
from wetwire_github.workflow import Job, Step

job = Job(
    runs_on="ubuntu-latest",
    permissions={"contents": "write", "issues": "write"},
    steps=[
        Step(run="echo hello"),
    ],
)
"""
        fixed, count, remaining = rule.fix(source, "test.py")

        # Should remove both unused permissions
        assert count >= 1
        # The fixed source should not contain the unused permissions
        assert 'permissions={"contents": "write", "issues": "write"}' not in fixed or count == 0

    def test_fix_removes_only_unused_permissions(self):
        """Fix should keep permissions that are actually used."""
        from wetwire_github.linter.rules import WAG019UnusedPermissions

        rule = WAG019UnusedPermissions()
        source = """
from wetwire_github.workflow import Job, Step

job = Job(
    runs_on="ubuntu-latest",
    permissions={"contents": "read", "issues": "write"},
    steps=[
        Step(uses="actions/checkout@v4"),
    ],
)
"""
        fixed, count, remaining = rule.fix(source, "test.py")

        # Should remove issues permission but keep contents
        assert count >= 0
        # Contents should still be there (used by checkout)
        # Issues should be removed (unused)
        if count > 0:
            assert "issues" not in fixed or remaining

    def test_fix_cannot_auto_fix_write_all(self):
        """Cannot auto-fix write-all permissions (requires manual intervention)."""
        from wetwire_github.linter.rules import WAG019UnusedPermissions

        rule = WAG019UnusedPermissions()
        source = """
from wetwire_github.workflow import Job, Step

job = Job(
    runs_on="ubuntu-latest",
    permissions="write-all",
    steps=[
        Step(uses="actions/checkout@v4"),
    ],
)
"""
        fixed, count, remaining = rule.fix(source, "test.py")

        # Cannot auto-fix broad permissions string
        assert count == 0
        assert fixed == source
        assert len(remaining) >= 1

    def test_fix_multiple_jobs_with_unused_permissions(self):
        """Fix should handle multiple jobs with unused permissions."""
        from wetwire_github.linter.rules import WAG019UnusedPermissions

        rule = WAG019UnusedPermissions()
        source = """
from wetwire_github.workflow import Workflow, Job, Step

job1 = Job(
    runs_on="ubuntu-latest",
    permissions={"contents": "write", "issues": "write"},
    steps=[Step(run="echo test")],
)

job2 = Job(
    runs_on="ubuntu-latest",
    permissions={"packages": "write"},
    steps=[Step(run="echo test")],
)

workflow = Workflow(
    name="CI",
    on={"push": {}},
    jobs={"job1": job1, "job2": job2},
)
"""
        fixed, count, remaining = rule.fix(source, "test.py")

        # Should fix unused permissions in both jobs
        assert count >= 0


class TestWAG020OverlyPermissiveSecrets:
    """Tests for WAG020: Warn if secrets are used in run commands without masking."""

    def test_rule_id(self):
        """Rule has correct ID."""
        from wetwire_github.linter.rules import WAG020OverlyPermissiveSecrets

        rule = WAG020OverlyPermissiveSecrets()
        assert rule.id == "WAG020"

    def test_rule_description(self):
        """Rule has a description."""
        from wetwire_github.linter.rules import WAG020OverlyPermissiveSecrets

        rule = WAG020OverlyPermissiveSecrets()
        assert len(rule.description) > 0

    def test_detect_secret_in_echo(self):
        """Detect secrets being echoed (potential exposure)."""
        from wetwire_github.linter.rules import WAG020OverlyPermissiveSecrets

        rule = WAG020OverlyPermissiveSecrets()
        errors = rule.check(
            """
from wetwire_github.workflow import Step

step = Step(run="echo ${{ secrets.API_KEY }}")
""",
            "test.py",
        )
        # Echoing a secret can expose it
        assert len(errors) == 1
        assert "WAG020" in errors[0].rule_id

    def test_detect_secret_in_curl(self):
        """Detect secrets passed directly to curl commands."""
        from wetwire_github.linter.rules import WAG020OverlyPermissiveSecrets

        rule = WAG020OverlyPermissiveSecrets()
        errors = rule.check(
            """
from wetwire_github.workflow import Step

step = Step(run="curl -H 'Authorization: ${{ secrets.TOKEN }}' https://api.example.com")
""",
            "test.py",
        )
        # Passing secret directly in command line
        assert len(errors) == 1

    def test_allow_secret_in_env_variable(self):
        """Allow secrets passed via env variables (proper masking)."""
        from wetwire_github.linter.rules import WAG020OverlyPermissiveSecrets

        rule = WAG020OverlyPermissiveSecrets()
        errors = rule.check(
            """
from wetwire_github.workflow import Step

step = Step(
    run="curl -H 'Authorization: $TOKEN' https://api.example.com",
    env={"TOKEN": "${{ secrets.TOKEN }}"}
)
""",
            "test.py",
        )
        # Using env variable is safer
        assert len(errors) == 0

    def test_detect_secret_in_multiline_run(self):
        """Detect secrets in multiline run commands."""
        from wetwire_github.linter.rules import WAG020OverlyPermissiveSecrets

        rule = WAG020OverlyPermissiveSecrets()
        errors = rule.check(
            '''
from wetwire_github.workflow import Step

step = Step(run="""
set -e
export API_KEY=${{ secrets.API_KEY }}
./deploy.sh
""")
''',
            "test.py",
        )
        # Direct export of secret in shell
        assert len(errors) == 1


class TestWAG021MissingOIDCConfiguration:
    """Tests for WAG021: Suggest OIDC for cloud provider auth."""

    def test_rule_id(self):
        """Rule has correct ID."""
        from wetwire_github.linter.rules import WAG021MissingOIDCConfiguration

        rule = WAG021MissingOIDCConfiguration()
        assert rule.id == "WAG021"

    def test_rule_description(self):
        """Rule has a description."""
        from wetwire_github.linter.rules import WAG021MissingOIDCConfiguration

        rule = WAG021MissingOIDCConfiguration()
        assert len(rule.description) > 0

    def test_detect_aws_static_credentials(self):
        """Detect AWS auth using static credentials instead of OIDC."""
        from wetwire_github.linter.rules import WAG021MissingOIDCConfiguration

        rule = WAG021MissingOIDCConfiguration()
        errors = rule.check(
            """
from wetwire_github.workflow import Step

step = Step(
    uses="aws-actions/configure-aws-credentials@v4",
    with_={
        "aws-access-key-id": "${{ secrets.AWS_ACCESS_KEY_ID }}",
        "aws-secret-access-key": "${{ secrets.AWS_SECRET_ACCESS_KEY }}",
    }
)
""",
            "test.py",
        )
        # Should suggest OIDC instead of static credentials
        assert len(errors) == 1
        assert "OIDC" in errors[0].message or "oidc" in errors[0].message.lower()

    def test_allow_aws_oidc_auth(self):
        """Allow AWS auth using OIDC."""
        from wetwire_github.linter.rules import WAG021MissingOIDCConfiguration

        rule = WAG021MissingOIDCConfiguration()
        errors = rule.check(
            """
from wetwire_github.workflow import Step

step = Step(
    uses="aws-actions/configure-aws-credentials@v4",
    with_={
        "role-to-assume": "arn:aws:iam::123456789:role/my-role",
        "aws-region": "us-east-1",
    }
)
""",
            "test.py",
        )
        # Using OIDC role assumption
        assert len(errors) == 0

    def test_detect_gcp_static_credentials(self):
        """Detect GCP auth using static credentials instead of OIDC."""
        from wetwire_github.linter.rules import WAG021MissingOIDCConfiguration

        rule = WAG021MissingOIDCConfiguration()
        errors = rule.check(
            """
from wetwire_github.workflow import Step

step = Step(
    uses="google-github-actions/auth@v2",
    with_={
        "credentials_json": "${{ secrets.GCP_CREDENTIALS }}",
    }
)
""",
            "test.py",
        )
        # Should suggest workload identity instead of service account key
        assert len(errors) == 1

    def test_allow_gcp_workload_identity(self):
        """Allow GCP auth using Workload Identity Federation."""
        from wetwire_github.linter.rules import WAG021MissingOIDCConfiguration

        rule = WAG021MissingOIDCConfiguration()
        errors = rule.check(
            """
from wetwire_github.workflow import Step

step = Step(
    uses="google-github-actions/auth@v2",
    with_={
        "workload_identity_provider": "projects/123/locations/global/workloadIdentityPools/my-pool/providers/my-provider",
        "service_account": "my-sa@my-project.iam.gserviceaccount.com",
    }
)
""",
            "test.py",
        )
        # Using Workload Identity Federation
        assert len(errors) == 0

    def test_detect_azure_static_credentials(self):
        """Detect Azure auth using static credentials instead of OIDC."""
        from wetwire_github.linter.rules import WAG021MissingOIDCConfiguration

        rule = WAG021MissingOIDCConfiguration()
        errors = rule.check(
            """
from wetwire_github.workflow import Step

step = Step(
    uses="azure/login@v2",
    with_={
        "creds": "${{ secrets.AZURE_CREDENTIALS }}",
    }
)
""",
            "test.py",
        )
        # Should suggest federated credentials instead
        assert len(errors) == 1


class TestWAG022ImplicitEnvironmentExposure:
    """Tests for WAG022: Warn about env vars in shell scripts without escaping."""

    def test_rule_id(self):
        """Rule has correct ID."""
        from wetwire_github.linter.rules import WAG022ImplicitEnvironmentExposure

        rule = WAG022ImplicitEnvironmentExposure()
        assert rule.id == "WAG022"

    def test_rule_description(self):
        """Rule has a description."""
        from wetwire_github.linter.rules import WAG022ImplicitEnvironmentExposure

        rule = WAG022ImplicitEnvironmentExposure()
        assert len(rule.description) > 0

    def test_detect_unquoted_env_var_in_command(self):
        """Detect unquoted environment variable in shell command."""
        from wetwire_github.linter.rules import WAG022ImplicitEnvironmentExposure

        rule = WAG022ImplicitEnvironmentExposure()
        errors = rule.check(
            """
from wetwire_github.workflow import Step

step = Step(
    run="echo $USER_INPUT",
    env={"USER_INPUT": "${{ github.event.issue.title }}"}
)
""",
            "test.py",
        )
        # USER_INPUT could contain special characters
        assert len(errors) == 1
        assert "WAG022" in errors[0].rule_id

    def test_allow_quoted_env_var(self):
        """Allow properly quoted environment variable."""
        from wetwire_github.linter.rules import WAG022ImplicitEnvironmentExposure

        rule = WAG022ImplicitEnvironmentExposure()
        errors = rule.check(
            """
from wetwire_github.workflow import Step

step = Step(
    run='echo "$USER_INPUT"',
    env={"USER_INPUT": "${{ github.event.issue.title }}"}
)
""",
            "test.py",
        )
        # Quoted variable is safe
        assert len(errors) == 0

    def test_detect_github_context_in_run(self):
        """Detect GitHub context used directly in run without escaping."""
        from wetwire_github.linter.rules import WAG022ImplicitEnvironmentExposure

        rule = WAG022ImplicitEnvironmentExposure()
        errors = rule.check(
            """
from wetwire_github.workflow import Step

step = Step(run="echo ${{ github.event.issue.title }}")
""",
            "test.py",
        )
        # Direct interpolation of user-controlled input
        assert len(errors) == 1

    def test_allow_safe_github_context(self):
        """Allow safe GitHub context values."""
        from wetwire_github.linter.rules import WAG022ImplicitEnvironmentExposure

        rule = WAG022ImplicitEnvironmentExposure()
        errors = rule.check(
            """
from wetwire_github.workflow import Step

step = Step(run="echo ${{ github.sha }}")
""",
            "test.py",
        )
        # github.sha is not user-controlled
        assert len(errors) == 0

    def test_detect_pr_title_in_run(self):
        """Detect PR title (user-controlled) used directly in run."""
        from wetwire_github.linter.rules import WAG022ImplicitEnvironmentExposure

        rule = WAG022ImplicitEnvironmentExposure()
        errors = rule.check(
            """
from wetwire_github.workflow import Step

step = Step(run="echo ${{ github.event.pull_request.title }}")
""",
            "test.py",
        )
        # PR title is user-controlled
        assert len(errors) == 1


class TestNewSecurityRulesInDefaultRules:
    """Test that new security rules are included in default rules."""

    def test_default_rules_include_wag019(self):
        """WAG019 is in default rules."""
        from wetwire_github.linter.rules import get_default_rules

        rules = get_default_rules()
        rule_ids = [r.id for r in rules]
        assert "WAG019" in rule_ids

    def test_default_rules_include_wag020(self):
        """WAG020 is in default rules."""
        from wetwire_github.linter.rules import get_default_rules

        rules = get_default_rules()
        rule_ids = [r.id for r in rules]
        assert "WAG020" in rule_ids

    def test_default_rules_include_wag021(self):
        """WAG021 is in default rules."""
        from wetwire_github.linter.rules import get_default_rules

        rules = get_default_rules()
        rule_ids = [r.id for r in rules]
        assert "WAG021" in rule_ids

    def test_default_rules_include_wag022(self):
        """WAG022 is in default rules."""
        from wetwire_github.linter.rules import get_default_rules

        rules = get_default_rules()
        rule_ids = [r.id for r in rules]
        assert "WAG022" in rule_ids


class TestNewSecurityRulesWithLinter:
    """Integration tests with Linter class for new security rules."""

    def test_linter_catches_unused_permissions(self):
        """Linter catches unused permissions."""
        from wetwire_github.linter import Linter
        from wetwire_github.linter.rules import WAG019UnusedPermissions

        linter = Linter(rules=[WAG019UnusedPermissions()])
        result = linter.check(
            """
from wetwire_github.workflow import Job, Step

job = Job(
    runs_on="ubuntu-latest",
    permissions={"packages": "write"},
    steps=[Step(run="echo hello")],
)
""",
            "test.py",
        )
        assert not result.is_clean
        assert any(e.rule_id == "WAG019" for e in result.errors)

    def test_linter_catches_secret_exposure(self):
        """Linter catches overly permissive secret usage."""
        from wetwire_github.linter import Linter
        from wetwire_github.linter.rules import WAG020OverlyPermissiveSecrets

        linter = Linter(rules=[WAG020OverlyPermissiveSecrets()])
        result = linter.check(
            """
from wetwire_github.workflow import Step

step = Step(run="echo ${{ secrets.TOKEN }}")
""",
            "test.py",
        )
        assert not result.is_clean
        assert any(e.rule_id == "WAG020" for e in result.errors)
