"""Tests for string manipulation expression functions (lower, upper)."""

from wetwire_github.workflow.expressions import (
    Expression,
    GitHub,
    lower,
    upper,
)


class TestLower:
    """Tests for the lower() function."""

    def test_lower_with_string_input(self):
        """lower() with a plain string wraps it in quotes."""
        result = lower("HELLO")
        assert isinstance(result, Expression)
        assert str(result) == "${{ lower('HELLO') }}"

    def test_lower_with_expression_input(self):
        """lower() with an Expression extracts the inner expression."""
        result = lower(GitHub.ref)
        assert isinstance(result, Expression)
        assert str(result) == "${{ lower(github.ref) }}"

    def test_lower_with_custom_expression(self):
        """lower() works with custom Expression objects."""
        custom_expr = Expression("env.MY_VAR")
        result = lower(custom_expr)
        assert isinstance(result, Expression)
        assert str(result) == "${{ lower(env.MY_VAR) }}"

    def test_lower_returns_expression_type(self):
        """lower() always returns an Expression instance."""
        result1 = lower("test")
        result2 = lower(GitHub.actor)
        assert type(result1) is Expression
        assert type(result2) is Expression


class TestUpper:
    """Tests for the upper() function."""

    def test_upper_with_string_input(self):
        """upper() with a plain string wraps it in quotes."""
        result = upper("hello")
        assert isinstance(result, Expression)
        assert str(result) == "${{ upper('hello') }}"

    def test_upper_with_expression_input(self):
        """upper() with an Expression extracts the inner expression."""
        result = upper(GitHub.ref)
        assert isinstance(result, Expression)
        assert str(result) == "${{ upper(github.ref) }}"

    def test_upper_with_custom_expression(self):
        """upper() works with custom Expression objects."""
        custom_expr = Expression("env.MY_VAR")
        result = upper(custom_expr)
        assert isinstance(result, Expression)
        assert str(result) == "${{ upper(env.MY_VAR) }}"

    def test_upper_returns_expression_type(self):
        """upper() always returns an Expression instance."""
        result1 = upper("test")
        result2 = upper(GitHub.actor)
        assert type(result1) is Expression
        assert type(result2) is Expression


class TestStringFunctionsGitHubActionsSyntax:
    """Tests verifying proper GitHub Actions syntax in output."""

    def test_lower_produces_valid_github_actions_syntax(self):
        """lower() output follows GitHub Actions expression syntax."""
        result = lower("TEST")
        output = str(result)
        # GitHub Actions expressions are wrapped in ${{ }}
        assert output.startswith("${{")
        assert output.endswith("}}")
        # The function call should be lowercase 'lower'
        assert "lower(" in output

    def test_upper_produces_valid_github_actions_syntax(self):
        """upper() output follows GitHub Actions expression syntax."""
        result = upper("test")
        output = str(result)
        # GitHub Actions expressions are wrapped in ${{ }}
        assert output.startswith("${{")
        assert output.endswith("}}")
        # The function call should be lowercase 'upper'
        assert "upper(" in output

    def test_string_literals_are_quoted(self):
        """String literal arguments are wrapped in single quotes."""
        lower_result = str(lower("MyString"))
        upper_result = str(upper("MyString"))
        assert "'MyString'" in lower_result
        assert "'MyString'" in upper_result

    def test_expressions_are_not_quoted(self):
        """Expression arguments are NOT wrapped in quotes."""
        lower_result = str(lower(GitHub.ref))
        upper_result = str(upper(GitHub.ref))
        # github.ref should appear without quotes
        assert "lower(github.ref)" in lower_result
        assert "upper(github.ref)" in upper_result
        # Should NOT have quotes around the expression
        assert "'github.ref'" not in lower_result
        assert "'github.ref'" not in upper_result
