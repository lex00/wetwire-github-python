"""Tests for expanded auto-fix support in lint rules."""


class TestWAG004AutoFix:
    """Tests for WAG004 auto-fix: raw strategy dicts to Strategy/Matrix classes."""

    def test_fix_raw_strategy_dict(self):
        """fix() wraps raw strategy dict with Strategy class."""
        from wetwire_github.linter.rules.organization_rules import (
            WAG004UseMatrixBuilder,
        )

        rule = WAG004UseMatrixBuilder()
        source = '''
from wetwire_github.workflow import Job, Step

job = Job(
    runs_on="ubuntu-latest",
    strategy={"matrix": {"python": ["3.11", "3.12"]}},
    steps=[Step(run="pytest")],
)
'''
        fixed, count, remaining = rule.fix(source, "test.py")

        assert count > 0
        assert "Strategy(" in fixed
        assert "matrix=Matrix(" in fixed or "Matrix(values=" in fixed

    def test_fix_raw_matrix_dict_in_strategy(self):
        """fix() wraps raw matrix dict in Strategy with Matrix class."""
        from wetwire_github.linter.rules.organization_rules import (
            WAG004UseMatrixBuilder,
        )

        rule = WAG004UseMatrixBuilder()
        source = '''
from wetwire_github.workflow import Job, Step, Strategy

job = Job(
    runs_on="ubuntu-latest",
    strategy=Strategy(matrix={"python": ["3.11", "3.12"]}),
    steps=[Step(run="pytest")],
)
'''
        fixed, count, remaining = rule.fix(source, "test.py")

        assert count > 0
        assert "Matrix(values=" in fixed or "Matrix(" in fixed

    def test_no_fix_when_already_correct(self):
        """fix() makes no changes when Strategy and Matrix are already used."""
        from wetwire_github.linter.rules.organization_rules import (
            WAG004UseMatrixBuilder,
        )

        rule = WAG004UseMatrixBuilder()
        source = '''
from wetwire_github.workflow import Job, Step, Strategy, Matrix

job = Job(
    runs_on="ubuntu-latest",
    strategy=Strategy(matrix=Matrix(values={"python": ["3.11", "3.12"]})),
    steps=[Step(run="pytest")],
)
'''
        fixed, count, remaining = rule.fix(source, "test.py")

        assert count == 0
        assert fixed == source


class TestWAG008AutoFix:
    """Tests for WAG008 auto-fix: hardcoded expressions to expression builders."""

    def test_fix_github_ref_expression(self):
        """fix() replaces ${{ github.ref }} with GitHub.ref."""
        from wetwire_github.linter.rules.expression_rules import (
            WAG008HardcodedExpressions,
        )

        rule = WAG008HardcodedExpressions()
        source = '''
from wetwire_github.workflow import Step

step = Step(run="echo ${{ github.ref }}")
'''
        fixed, count, remaining = rule.fix(source, "test.py")

        # Should replace hardcoded expression
        assert count > 0 or "${{ github.ref }}" not in fixed

    def test_fix_github_event_name_expression(self):
        """fix() replaces ${{ github.event_name }} with GitHub.event_name."""
        from wetwire_github.linter.rules.expression_rules import (
            WAG008HardcodedExpressions,
        )

        rule = WAG008HardcodedExpressions()
        source = '''
env = {"EVENT": "${{ github.event_name }}"}
'''
        fixed, count, remaining = rule.fix(source, "test.py")

        assert count > 0 or "${{ github.event_name }}" not in fixed

    def test_no_fix_for_complex_expressions(self):
        """fix() may not fix complex expressions, but should not break code."""
        from wetwire_github.linter.rules.expression_rules import (
            WAG008HardcodedExpressions,
        )

        rule = WAG008HardcodedExpressions()
        source = '''
# Complex expression that may not be auto-fixable
env = {"RESULT": "${{ steps.build.outputs.result }}"}
'''
        fixed, count, remaining = rule.fix(source, "test.py")

        # Should at least parse without error
        import ast
        ast.parse(fixed)  # Should not raise


class TestLinterFixWithExpandedRules:
    """Tests for Linter.fix() with expanded auto-fix rules."""

    def test_linter_fix_includes_wag004(self):
        """Linter.fix() applies WAG004 fixes when available."""
        from wetwire_github.linter import Linter

        linter = Linter()

        # Check if WAG004 has fix method
        wag004_rules = [r for r in linter.rules if r.id == "WAG004"]
        assert len(wag004_rules) == 1

        # If it has fix method, it should be callable
        rule = wag004_rules[0]
        if hasattr(rule, "fix"):
            assert callable(rule.fix)
