"""Tests for expression function helpers."""

from wetwire_github.workflow.expressions import (
    Event,
    Expression,
    Runner,
    contains,
    endsWith,
    format,
    fromJson,
    hashFiles,
    join,
    startsWith,
    toJson,
)


class TestContains:
    """Tests for contains() function."""

    def test_contains_with_string(self):
        """contains() works with string input."""
        expr = contains("hello world", "world")
        assert str(expr) == "${{ contains('hello world', 'world') }}"

    def test_contains_with_expression(self):
        """contains() works with Expression input."""
        expr = contains(Event.pr_title, "bug")
        assert (
            str(expr)
            == "${{ contains(github.event.pull_request.title, 'bug') }}"
        )

    def test_contains_returns_expression(self):
        """contains() returns an Expression instance."""
        expr = contains("test", "es")
        assert isinstance(expr, Expression)


class TestStartsWith:
    """Tests for startsWith() function."""

    def test_startswith_with_string(self):
        """startsWith() works with string input."""
        expr = startsWith("hello world", "hello")
        assert str(expr) == "${{ startsWith('hello world', 'hello') }}"

    def test_startswith_with_expression(self):
        """startsWith() works with Expression input."""
        expr = startsWith(Event.pr_title, "feat:")
        assert (
            str(expr)
            == "${{ startsWith(github.event.pull_request.title, 'feat:') }}"
        )

    def test_startswith_returns_expression(self):
        """startsWith() returns an Expression instance."""
        expr = startsWith("test", "te")
        assert isinstance(expr, Expression)


class TestEndsWith:
    """Tests for endsWith() function."""

    def test_endswith_with_string(self):
        """endsWith() works with string input."""
        expr = endsWith("hello world", "world")
        assert str(expr) == "${{ endsWith('hello world', 'world') }}"

    def test_endswith_with_expression(self):
        """endsWith() works with Expression input."""
        expr = endsWith(Event.pr_title, ".md")
        assert (
            str(expr)
            == "${{ endsWith(github.event.pull_request.title, '.md') }}"
        )

    def test_endswith_returns_expression(self):
        """endsWith() returns an Expression instance."""
        expr = endsWith("test", "st")
        assert isinstance(expr, Expression)


class TestFormat:
    """Tests for format() function."""

    def test_format_with_single_arg(self):
        """format() works with single argument."""
        expr = format("Hello {0}", "world")
        assert str(expr) == "${{ format('Hello {0}', 'world') }}"

    def test_format_with_multiple_args(self):
        """format() works with multiple arguments."""
        expr = format("cache-{0}-{1}", "linux", "v1")
        assert str(expr) == "${{ format('cache-{0}-{1}', 'linux', 'v1') }}"

    def test_format_with_expression_args(self):
        """format() works with Expression arguments."""
        expr = format("cache-{0}-{1}", Runner.os, hashFiles("*.lock"))
        assert (
            str(expr)
            == "${{ format('cache-{0}-{1}', runner.os, hashFiles('*.lock')) }}"
        )

    def test_format_returns_expression(self):
        """format() returns an Expression instance."""
        expr = format("test {0}", "value")
        assert isinstance(expr, Expression)


class TestHashFiles:
    """Tests for hashFiles() function."""

    def test_hashfiles_single_pattern(self):
        """hashFiles() works with single pattern."""
        expr = hashFiles("requirements.txt")
        assert str(expr) == "${{ hashFiles('requirements.txt') }}"

    def test_hashfiles_multiple_patterns(self):
        """hashFiles() works with multiple patterns."""
        expr = hashFiles("**/requirements*.txt")
        assert str(expr) == "${{ hashFiles('**/requirements*.txt') }}"

    def test_hashfiles_returns_expression(self):
        """hashFiles() returns an Expression instance."""
        expr = hashFiles("*.lock")
        assert isinstance(expr, Expression)


class TestJoin:
    """Tests for join() function."""

    def test_join_with_string(self):
        """join() works with string input."""
        expr = join("items", ",")
        assert str(expr) == "${{ join(items, ',') }}"

    def test_join_with_default_separator(self):
        """join() uses comma as default separator."""
        expr = join("items")
        assert str(expr) == "${{ join(items, ',') }}"

    def test_join_with_expression(self):
        """join() works with Expression input."""
        array_expr = Expression("matrix.versions")
        expr = join(array_expr, ", ")
        assert str(expr) == "${{ join(matrix.versions, ', ') }}"

    def test_join_returns_expression(self):
        """join() returns an Expression instance."""
        expr = join("test")
        assert isinstance(expr, Expression)


class TestToJson:
    """Tests for toJson() function."""

    def test_tojson_with_string(self):
        """toJson() works with string input."""
        expr = toJson("matrix")
        assert str(expr) == "${{ toJSON(matrix) }}"

    def test_tojson_with_expression(self):
        """toJson() works with Expression input."""
        expr = toJson(Expression("github.event"))
        assert str(expr) == "${{ toJSON(github.event) }}"

    def test_tojson_returns_expression(self):
        """toJson() returns an Expression instance."""
        expr = toJson("test")
        assert isinstance(expr, Expression)


class TestFromJson:
    """Tests for fromJson() function."""

    def test_fromjson_with_string(self):
        """fromJson() works with string input."""
        expr = fromJson("env.JSON_DATA")
        assert str(expr) == "${{ fromJSON(env.JSON_DATA) }}"

    def test_fromjson_with_expression(self):
        """fromJson() works with Expression input."""
        expr = fromJson(Expression("steps.data.outputs.json"))
        assert str(expr) == "${{ fromJSON(steps.data.outputs.json) }}"

    def test_fromjson_returns_expression(self):
        """fromJson() returns an Expression instance."""
        expr = fromJson("test")
        assert isinstance(expr, Expression)


class TestComplexExpressions:
    """Tests for complex expression combinations."""

    def test_format_with_hashfiles(self):
        """Complex expression: format with hashFiles."""
        expr = format("cache-{0}-{1}", Runner.os, hashFiles("*.lock"))
        expected = (
            "${{ format('cache-{0}-{1}', runner.os, hashFiles('*.lock')) }}"
        )
        assert str(expr) == expected

    def test_contains_in_conditional(self):
        """Complex expression: contains can be combined with logical operators."""
        expr = contains(Event.pr_title, "bug")
        assert isinstance(expr, Expression)
        # Can be used in conditionals
        combined = expr.and_(Expression("github.event.pull_request.draft == false"))
        assert "&&" in str(combined)
