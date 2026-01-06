"""Tests for expression types and contexts."""

from wetwire_github.workflow.expressions import (
    Env,
    Expression,
    GitHub,
    Inputs,
    Matrix,
    Needs,
    Runner,
    Secrets,
    Steps,
    always,
    branch,
    cancelled,
    failure,
    success,
    tag,
)


class TestExpression:
    """Tests for Expression class."""

    def test_expression_str(self):
        """Expression wraps value in ${{ }}."""
        e = Expression("github.ref")
        assert str(e) == "${{ github.ref }}"

    def test_expression_and(self):
        """Expression supports && operator."""
        e1 = Expression("github.ref == 'refs/heads/main'")
        e2 = Expression("github.event_name == 'push'")
        result = e1.and_(e2)
        assert "&&" in str(result)

    def test_expression_or(self):
        """Expression supports || operator."""
        e1 = Expression("github.ref == 'refs/heads/main'")
        e2 = Expression("github.ref == 'refs/heads/develop'")
        result = e1.or_(e2)
        assert "||" in str(result)

    def test_expression_not(self):
        """Expression supports negation."""
        e = Expression("github.event.pull_request.draft")
        result = e.not_()
        assert "!" in str(result)


class TestSecretsContext:
    """Tests for Secrets context."""

    def test_secrets_get(self):
        """Secrets.get returns expression for secret."""
        expr = Secrets.get("GITHUB_TOKEN")
        assert "secrets.GITHUB_TOKEN" in str(expr)


class TestMatrixContext:
    """Tests for Matrix context."""

    def test_matrix_get(self):
        """Matrix.get returns expression for matrix value."""
        expr = Matrix.get("os")
        assert "matrix.os" in str(expr)


class TestGitHubContext:
    """Tests for GitHub context."""

    def test_github_ref(self):
        """GitHub.ref returns ref expression."""
        assert "github.ref" in str(GitHub.ref)

    def test_github_sha(self):
        """GitHub.sha returns sha expression."""
        assert "github.sha" in str(GitHub.sha)

    def test_github_actor(self):
        """GitHub.actor returns actor expression."""
        assert "github.actor" in str(GitHub.actor)

    def test_github_event_name(self):
        """GitHub.event_name returns event_name expression."""
        assert "github.event_name" in str(GitHub.event_name)

    def test_github_repository(self):
        """GitHub.repository returns repository expression."""
        assert "github.repository" in str(GitHub.repository)

    def test_github_run_id(self):
        """GitHub.run_id returns run_id expression."""
        assert "github.run_id" in str(GitHub.run_id)

    def test_github_run_number(self):
        """GitHub.run_number returns run_number expression."""
        assert "github.run_number" in str(GitHub.run_number)

    def test_github_workflow(self):
        """GitHub.workflow returns workflow expression."""
        assert "github.workflow" in str(GitHub.workflow)


class TestEnvContext:
    """Tests for Env context."""

    def test_env_get(self):
        """Env.get returns expression for environment variable."""
        expr = Env.get("MY_VAR")
        assert "env.MY_VAR" in str(expr)


class TestRunnerContext:
    """Tests for Runner context."""

    def test_runner_os(self):
        """Runner.os returns os expression."""
        assert "runner.os" in str(Runner.os)

    def test_runner_arch(self):
        """Runner.arch returns arch expression."""
        assert "runner.arch" in str(Runner.arch)

    def test_runner_name(self):
        """Runner.name returns name expression."""
        assert "runner.name" in str(Runner.name)

    def test_runner_temp(self):
        """Runner.temp returns temp expression."""
        assert "runner.temp" in str(Runner.temp)

    def test_runner_tool_cache(self):
        """Runner.tool_cache returns tool_cache expression."""
        assert "runner.tool_cache" in str(Runner.tool_cache)


class TestNeedsContext:
    """Tests for Needs context."""

    def test_needs_output(self):
        """Needs.output returns expression for job output."""
        expr = Needs.output("build", "version")
        assert "needs.build.outputs.version" in str(expr)

    def test_needs_result(self):
        """Needs.result returns expression for job result."""
        expr = Needs.result("build")
        assert "needs.build.result" in str(expr)


class TestInputsContext:
    """Tests for Inputs context."""

    def test_inputs_get(self):
        """Inputs.get returns expression for workflow input."""
        expr = Inputs.get("environment")
        assert "inputs.environment" in str(expr)


class TestStepsContext:
    """Tests for Steps context."""

    def test_steps_output(self):
        """Steps.output returns expression for step output."""
        expr = Steps.output("build", "artifact")
        assert "steps.build.outputs.artifact" in str(expr)

    def test_steps_outcome(self):
        """Steps.outcome returns expression for step outcome."""
        expr = Steps.outcome("build")
        assert "steps.build.outcome" in str(expr)

    def test_steps_conclusion(self):
        """Steps.conclusion returns expression for step conclusion."""
        expr = Steps.conclusion("build")
        assert "steps.build.conclusion" in str(expr)


class TestConditionBuilders:
    """Tests for condition builder functions."""

    def test_always(self):
        """always() returns always() expression."""
        expr = always()
        assert "always()" in str(expr)

    def test_failure(self):
        """failure() returns failure() expression."""
        expr = failure()
        assert "failure()" in str(expr)

    def test_success(self):
        """success() returns success() expression."""
        expr = success()
        assert "success()" in str(expr)

    def test_cancelled(self):
        """cancelled() returns cancelled() expression."""
        expr = cancelled()
        assert "cancelled()" in str(expr)

    def test_branch(self):
        """branch() returns branch comparison expression."""
        expr = branch("main")
        assert "refs/heads/main" in str(expr)

    def test_tag(self):
        """tag() returns tag comparison expression."""
        expr = tag("v1.0.0")
        assert "refs/tags/v1.0.0" in str(expr)
