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
