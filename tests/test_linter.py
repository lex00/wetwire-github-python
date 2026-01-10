"""Tests for Python code linter rules."""

from wetwire_github.linter import (
    Linter,
    LintError,
    LintResult,
    lint_directory,
    lint_file,
)
from wetwire_github.linter.rules import (
    WAG001TypedActionWrappers,
    WAG002UseConditionBuilders,
    WAG003UseSecretsContext,
    WAG004UseMatrixBuilder,
    WAG005ExtractInlineEnvVariables,
    WAG006DuplicateWorkflowNames,
    WAG007FileTooLarge,
    WAG008HardcodedExpressions,
)


class TestLintError:
    """Tests for LintError dataclass."""

    def test_lint_error(self):
        """LintError stores error details."""
        error = LintError(
            rule_id="WAG001",
            message="Use typed action wrappers instead of raw strings",
            file_path="/path/to/file.py",
            line=10,
            column=5,
        )
        assert error.rule_id == "WAG001"
        assert error.line == 10
        assert error.file_path == "/path/to/file.py"

    def test_lint_error_with_suggestion(self):
        """LintError can include fix suggestion."""
        error = LintError(
            rule_id="WAG001",
            message="Use typed action wrappers",
            file_path="/test.py",
            line=1,
            column=1,
            suggestion="Replace with: checkout()",
        )
        assert error.suggestion == "Replace with: checkout()"


class TestLintResult:
    """Tests for LintResult dataclass."""

    def test_lint_result_clean(self):
        """LintResult for clean code."""
        result = LintResult(errors=[])
        assert result.is_clean is True
        assert len(result.errors) == 0

    def test_lint_result_with_errors(self):
        """LintResult with errors."""
        errors = [
            LintError("WAG001", "test", "/test.py", 1, 1),
        ]
        result = LintResult(errors=errors)
        assert result.is_clean is False
        assert len(result.errors) == 1


class TestRuleProtocol:
    """Tests for Rule protocol."""

    def test_rule_has_id(self):
        """Rules have an id."""
        rule = WAG001TypedActionWrappers()
        assert rule.id == "WAG001"

    def test_rule_has_description(self):
        """Rules have a description."""
        rule = WAG001TypedActionWrappers()
        assert len(rule.description) > 0

    def test_rule_has_check_method(self):
        """Rules have a check method."""
        rule = WAG001TypedActionWrappers()
        assert callable(rule.check)


class TestLinter:
    """Tests for Linter class."""

    def test_linter_default_rules(self):
        """Linter has default rules enabled."""
        linter = Linter()
        assert len(linter.rules) > 0

    def test_linter_custom_rules(self):
        """Linter can use custom rules."""
        rule = WAG001TypedActionWrappers()
        linter = Linter(rules=[rule])
        assert len(linter.rules) == 1

    def test_linter_check_code(self):
        """Linter checks code against rules."""
        linter = Linter()
        result = linter.check(
            """
from wetwire_github.workflow import Workflow
w = Workflow(name="CI")
""",
            file_path="test.py",
        )
        assert isinstance(result, LintResult)


class TestWAG001TypedActionWrappers:
    """Tests for WAG001: Use typed action wrappers."""

    def test_detect_raw_uses_string(self):
        """Detect raw 'uses' string literals."""
        rule = WAG001TypedActionWrappers()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step = Step(uses="actions/checkout@v4")
""",
            "test.py",
        )
        assert len(errors) == 1
        assert "typed action wrapper" in errors[0].message.lower()

    def test_allow_typed_action_calls(self):
        """Allow typed action function calls."""
        rule = WAG001TypedActionWrappers()
        errors = rule.check(
            """
from wetwire_github.actions import checkout
step = checkout(ref="main")
""",
            "test.py",
        )
        assert len(errors) == 0

    def test_allow_unknown_actions(self):
        """Allow actions not in our wrappers."""
        rule = WAG001TypedActionWrappers()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step = Step(uses="owner/custom-action@v1")
""",
            "test.py",
        )
        # Custom actions are allowed
        assert len(errors) == 0


class TestWAG006DuplicateWorkflowNames:
    """Tests for WAG006: Duplicate workflow names."""

    def test_detect_duplicate_names(self):
        """Detect duplicate workflow names in same file."""
        rule = WAG006DuplicateWorkflowNames()
        errors = rule.check(
            """
from wetwire_github.workflow import Workflow
ci1 = Workflow(name="CI")
ci2 = Workflow(name="CI")
""",
            "test.py",
        )
        assert len(errors) >= 1
        assert "duplicate" in errors[0].message.lower()

    def test_allow_unique_names(self):
        """Allow unique workflow names."""
        rule = WAG006DuplicateWorkflowNames()
        errors = rule.check(
            """
from wetwire_github.workflow import Workflow
ci = Workflow(name="CI")
deploy = Workflow(name="Deploy")
""",
            "test.py",
        )
        assert len(errors) == 0


class TestWAG007FileTooLarge:
    """Tests for WAG007: File too large."""

    def test_detect_too_many_jobs(self):
        """Detect files with too many jobs."""
        rule = WAG007FileTooLarge(max_jobs=2)
        errors = rule.check(
            """
from wetwire_github.workflow import Job
job1 = Job(runs_on="ubuntu-latest")
job2 = Job(runs_on="ubuntu-latest")
job3 = Job(runs_on="ubuntu-latest")
""",
            "test.py",
        )
        assert len(errors) == 1
        assert "too many" in errors[0].message.lower()

    def test_allow_few_jobs(self):
        """Allow files with few jobs."""
        rule = WAG007FileTooLarge(max_jobs=10)
        errors = rule.check(
            """
from wetwire_github.workflow import Job
job1 = Job(runs_on="ubuntu-latest")
job2 = Job(runs_on="ubuntu-latest")
""",
            "test.py",
        )
        assert len(errors) == 0


class TestWAG008HardcodedExpressions:
    """Tests for WAG008: Hardcoded expression strings."""

    def test_detect_hardcoded_expression(self):
        """Detect hardcoded ${{ }} expressions."""
        rule = WAG008HardcodedExpressions()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step = Step(env={"TOKEN": "${{ secrets.GITHUB_TOKEN }}"})
""",
            "test.py",
        )
        assert len(errors) == 1
        assert (
            "hardcoded" in errors[0].message.lower()
            or "expression" in errors[0].message.lower()
        )

    def test_allow_expression_objects(self):
        """Allow Expression objects."""
        rule = WAG008HardcodedExpressions()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
from wetwire_github.workflow.expressions import secrets
step = Step(env={"TOKEN": secrets.GITHUB_TOKEN})
""",
            "test.py",
        )
        assert len(errors) == 0


class TestLintFile:
    """Tests for lint_file function."""

    def test_lint_file(self, tmp_path):
        """Lint a Python file."""
        file_path = tmp_path / "workflows.py"
        file_path.write_text("""
from wetwire_github.workflow import Workflow
ci = Workflow(name="CI")
""")
        result = lint_file(str(file_path))
        assert isinstance(result, LintResult)

    def test_lint_file_handles_syntax_error(self, tmp_path):
        """Handle syntax errors gracefully."""
        file_path = tmp_path / "broken.py"
        file_path.write_text("""def incomplete(""")
        result = lint_file(str(file_path))
        # Should return errors or empty result, not crash
        assert isinstance(result, LintResult)


class TestLintDirectory:
    """Tests for lint_directory function."""

    def test_lint_directory(self, tmp_path):
        """Lint all Python files in directory."""
        (tmp_path / "file1.py").write_text("""
from wetwire_github.workflow import Workflow
ci = Workflow(name="CI")
""")
        (tmp_path / "file2.py").write_text("""
from wetwire_github.workflow import Job
job = Job(runs_on="ubuntu-latest")
""")
        results = lint_directory(str(tmp_path))
        assert len(results) == 2

    def test_lint_directory_recursive(self, tmp_path):
        """Recursively lint subdirectories."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "nested.py").write_text("""
from wetwire_github.workflow import Workflow
w = Workflow(name="Nested")
""")
        results = lint_directory(str(tmp_path))
        # Should find the nested file
        assert any("nested.py" in r.file_path for r in results)

    def test_lint_directory_excludes_pycache(self, tmp_path):
        """Exclude __pycache__ directories."""
        pycache = tmp_path / "__pycache__"
        pycache.mkdir()
        (pycache / "cached.py").write_text("""test""")
        (tmp_path / "regular.py").write_text("""x = 1""")
        results = lint_directory(str(tmp_path))
        assert len(results) == 1
        assert "pycache" not in results[0].file_path


class TestWAG002UseConditionBuilders:
    """Tests for WAG002: Use condition builders."""

    def test_detect_hardcoded_always(self):
        """Detect hardcoded always() condition."""
        rule = WAG002UseConditionBuilders()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step = Step(if_="${{ always() }}")
""",
            "test.py",
        )
        assert len(errors) == 1
        assert "always()" in errors[0].message

    def test_detect_hardcoded_failure(self):
        """Detect hardcoded failure() condition."""
        rule = WAG002UseConditionBuilders()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step = Step(if_="${{ failure() }}")
""",
            "test.py",
        )
        assert len(errors) == 1
        assert "failure()" in errors[0].message

    def test_detect_hardcoded_success(self):
        """Detect hardcoded success() condition."""
        rule = WAG002UseConditionBuilders()
        errors = rule.check(
            """
from wetwire_github.workflow import Job
job = Job(runs_on="ubuntu-latest", if_="${{ success() }}")
""",
            "test.py",
        )
        assert len(errors) == 1
        assert "success()" in errors[0].message

    def test_detect_hardcoded_cancelled(self):
        """Detect hardcoded cancelled() condition."""
        rule = WAG002UseConditionBuilders()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step = Step(if_="${{ cancelled() }}")
""",
            "test.py",
        )
        assert len(errors) == 1
        assert "cancelled()" in errors[0].message

    def test_allow_condition_builder_calls(self):
        """Allow typed condition builder calls."""
        rule = WAG002UseConditionBuilders()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
from wetwire_github.workflow.expressions import always
step = Step(if_=always())
""",
            "test.py",
        )
        assert len(errors) == 0

    def test_allow_other_conditions(self):
        """Allow other condition expressions."""
        rule = WAG002UseConditionBuilders()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step = Step(if_="${{ github.event_name == 'push' }}")
""",
            "test.py",
        )
        # This is a general expression, not a condition builder pattern
        assert len(errors) == 0


class TestWAG003UseSecretsContext:
    """Tests for WAG003: Use secrets context."""

    def test_detect_hardcoded_secret(self):
        """Detect hardcoded secrets access."""
        rule = WAG003UseSecretsContext()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step = Step(env={"TOKEN": "${{ secrets.GITHUB_TOKEN }}"})
""",
            "test.py",
        )
        assert len(errors) == 1
        assert "Secrets.get" in errors[0].message
        assert "GITHUB_TOKEN" in errors[0].message

    def test_detect_multiple_secrets(self):
        """Detect multiple hardcoded secrets."""
        rule = WAG003UseSecretsContext()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step = Step(
    env={
        "TOKEN": "${{ secrets.GITHUB_TOKEN }}",
        "API_KEY": "${{ secrets.API_KEY }}",
    }
)
""",
            "test.py",
        )
        assert len(errors) == 2

    def test_allow_secrets_context(self):
        """Allow Secrets.get() helper."""
        rule = WAG003UseSecretsContext()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
from wetwire_github.workflow.expressions import Secrets
step = Step(env={"TOKEN": Secrets.get("GITHUB_TOKEN")})
""",
            "test.py",
        )
        assert len(errors) == 0


class TestWAG004UseMatrixBuilder:
    """Tests for WAG004: Use Matrix builder."""

    def test_detect_raw_strategy_dict(self):
        """Detect raw dict for strategy."""
        rule = WAG004UseMatrixBuilder()
        errors = rule.check(
            """
from wetwire_github.workflow import Job
job = Job(
    runs_on="ubuntu-latest",
    strategy={"matrix": {"os": ["ubuntu", "windows"]}}
)
""",
            "test.py",
        )
        assert len(errors) == 1
        assert "Strategy class" in errors[0].message

    def test_detect_raw_matrix_dict(self):
        """Detect raw dict for matrix inside Strategy."""
        rule = WAG004UseMatrixBuilder()
        errors = rule.check(
            """
from wetwire_github.workflow import Job, Strategy
job = Job(
    runs_on="ubuntu-latest",
    strategy=Strategy(matrix={"os": ["ubuntu", "windows"]})
)
""",
            "test.py",
        )
        assert len(errors) == 1
        assert "Matrix class" in errors[0].message

    def test_allow_strategy_with_matrix_class(self):
        """Allow Strategy with Matrix class."""
        rule = WAG004UseMatrixBuilder()
        errors = rule.check(
            """
from wetwire_github.workflow import Job, Strategy, Matrix
job = Job(
    runs_on="ubuntu-latest",
    strategy=Strategy(matrix=Matrix(values={"os": ["ubuntu", "windows"]}))
)
""",
            "test.py",
        )
        assert len(errors) == 0


class TestWAG005ExtractInlineEnvVariables:
    """Tests for WAG005: Extract inline env variables."""

    def test_detect_repeated_env_vars(self):
        """Detect same env var in multiple steps."""
        rule = WAG005ExtractInlineEnvVariables()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step1 = Step(run="echo $DEBUG", env={"DEBUG": "true"})
step2 = Step(run="echo $DEBUG", env={"DEBUG": "true"})
""",
            "test.py",
        )
        assert len(errors) == 1
        assert "DEBUG" in errors[0].message
        assert "2 steps" in errors[0].message

    def test_allow_unique_env_vars(self):
        """Allow unique env vars per step."""
        rule = WAG005ExtractInlineEnvVariables()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step1 = Step(run="echo $FOO", env={"FOO": "1"})
step2 = Step(run="echo $BAR", env={"BAR": "2"})
""",
            "test.py",
        )
        assert len(errors) == 0

    def test_allow_single_occurrence(self):
        """Allow env var used in single step."""
        rule = WAG005ExtractInlineEnvVariables()
        errors = rule.check(
            """
from wetwire_github.workflow import Step
step1 = Step(run="echo $DEBUG", env={"DEBUG": "true"})
step2 = Step(run="echo hello")
""",
            "test.py",
        )
        assert len(errors) == 0


class TestWAG001AutoFix:
    """Tests for WAG001 auto-fix functionality."""

    def test_fix_checkout_action(self):
        """Fix Step(uses='actions/checkout@v4') to checkout()."""
        rule = WAG001TypedActionWrappers()
        source = """
from wetwire_github.workflow import Step
step = Step(uses="actions/checkout@v4")
"""
        fixed, count, remaining = rule.fix(source, "test.py")

        assert count == 1
        assert "checkout()" in fixed
        assert 'Step(uses="actions/checkout@v4")' not in fixed

    def test_fix_setup_python_action(self):
        """Fix Step(uses='actions/setup-python@v5') to setup_python()."""
        rule = WAG001TypedActionWrappers()
        source = """
from wetwire_github.workflow import Step
step = Step(uses="actions/setup-python@v5")
"""
        fixed, count, remaining = rule.fix(source, "test.py")

        assert count == 1
        assert "setup_python()" in fixed

    def test_fix_multiple_actions(self):
        """Fix multiple action uses in same file."""
        rule = WAG001TypedActionWrappers()
        source = """
from wetwire_github.workflow import Step
step1 = Step(uses="actions/checkout@v4")
step2 = Step(uses="actions/setup-python@v5")
step3 = Step(uses="actions/cache@v3")
"""
        fixed, count, remaining = rule.fix(source, "test.py")

        assert count == 3
        assert "checkout()" in fixed
        assert "setup_python()" in fixed
        assert "cache()" in fixed

    def test_no_fix_needed(self):
        """No fix needed when using wrapper functions."""
        rule = WAG001TypedActionWrappers()
        source = """
from wetwire_github.workflow import Step
from wetwire_github.actions import checkout
step = checkout()
"""
        fixed, count, remaining = rule.fix(source, "test.py")

        assert count == 0
        assert fixed == source


class TestWAG002AutoFix:
    """Tests for WAG002 auto-fix functionality."""

    def test_fix_always_condition(self):
        """Fix if_='${{ always() }}' to if_=always()."""
        rule = WAG002UseConditionBuilders()
        source = """
from wetwire_github.workflow import Step
step = Step(if_="${{ always() }}")
"""
        fixed, count, remaining = rule.fix(source, "test.py")

        assert count == 1
        assert "if_=always()" in fixed
        assert "${{ always() }}" not in fixed

    def test_fix_failure_condition(self):
        """Fix if_='${{ failure() }}' to if_=failure()."""
        rule = WAG002UseConditionBuilders()
        source = """
from wetwire_github.workflow import Job
job = Job(runs_on="ubuntu-latest", if_="${{ failure() }}")
"""
        fixed, count, remaining = rule.fix(source, "test.py")

        assert count == 1
        assert "if_=failure()" in fixed

    def test_fix_success_condition(self):
        """Fix if_='${{ success() }}' to if_=success()."""
        rule = WAG002UseConditionBuilders()
        source = """
from wetwire_github.workflow import Step
step = Step(if_="${{ success() }}")
"""
        fixed, count, remaining = rule.fix(source, "test.py")

        assert count == 1
        assert "if_=success()" in fixed

    def test_fix_cancelled_condition(self):
        """Fix if_='${{ cancelled() }}' to if_=cancelled()."""
        rule = WAG002UseConditionBuilders()
        source = """
from wetwire_github.workflow import Step
step = Step(if_="${{ cancelled() }}")
"""
        fixed, count, remaining = rule.fix(source, "test.py")

        assert count == 1
        assert "if_=cancelled()" in fixed

    def test_no_fix_for_typed_conditions(self):
        """No fix needed when using typed condition builders."""
        rule = WAG002UseConditionBuilders()
        source = """
from wetwire_github.workflow import Step
from wetwire_github.workflow.expressions import always
step = Step(if_=always())
"""
        fixed, count, remaining = rule.fix(source, "test.py")

        assert count == 0
        assert fixed == source


class TestWAG003AutoFix:
    """Tests for WAG003 auto-fix functionality."""

    def test_fix_secrets_access(self):
        """Fix ${{ secrets.TOKEN }} to Secrets.get('TOKEN')."""
        rule = WAG003UseSecretsContext()
        source = """
from wetwire_github.workflow import Step
step = Step(env={"TOKEN": "${{ secrets.GITHUB_TOKEN }}"})
"""
        fixed, count, remaining = rule.fix(source, "test.py")

        assert count == 1
        assert 'Secrets.get("GITHUB_TOKEN")' in fixed
        assert "${{ secrets.GITHUB_TOKEN }}" not in fixed

    def test_fix_multiple_secrets(self):
        """Fix multiple secrets in same file."""
        rule = WAG003UseSecretsContext()
        source = """
from wetwire_github.workflow import Step
step = Step(
    env={
        "TOKEN": "${{ secrets.GITHUB_TOKEN }}",
        "API_KEY": "${{ secrets.API_KEY }}",
    }
)
"""
        fixed, count, remaining = rule.fix(source, "test.py")

        assert count == 2
        assert 'Secrets.get("GITHUB_TOKEN")' in fixed
        assert 'Secrets.get("API_KEY")' in fixed


class TestLinterAutoFix:
    """Tests for Linter.fix() method."""

    def test_linter_fix_applies_all_fixable_rules(self):
        """Linter.fix() applies fixes from all fixable rules."""
        linter = Linter()
        source = """
from wetwire_github.workflow import Step
step1 = Step(uses="actions/checkout@v4")
step2 = Step(env={"TOKEN": "${{ secrets.GITHUB_TOKEN }}"})
step3 = Step(if_="${{ always() }}")
"""
        result = linter.fix(source, "test.py")

        assert result.fixed_count >= 3
        assert "checkout()" in result.source
        assert 'Secrets.get("GITHUB_TOKEN")' in result.source
        assert "if_=always()" in result.source
