"""Tests for Runner context helpers."""

from wetwire_github.workflow import Job, Step
from wetwire_github.workflow.expressions import Expression, Runner


class TestRunnerContextProperties:
    """Tests for Runner context properties."""

    def test_runner_os(self):
        """Runner.os returns correct expression."""
        assert str(Runner.os) == "${{ runner.os }}"

    def test_runner_arch(self):
        """Runner.arch returns correct expression."""
        assert str(Runner.arch) == "${{ runner.arch }}"

    def test_runner_name(self):
        """Runner.name returns correct expression."""
        assert str(Runner.name) == "${{ runner.name }}"

    def test_runner_temp(self):
        """Runner.temp returns correct expression."""
        assert str(Runner.temp) == "${{ runner.temp }}"

    def test_runner_tool_cache(self):
        """Runner.tool_cache returns correct expression."""
        assert str(Runner.tool_cache) == "${{ runner.tool_cache }}"

    def test_runner_debug(self):
        """Runner.debug returns correct expression."""
        assert str(Runner.debug) == "${{ runner.debug }}"


class TestRunnerContextHelpers:
    """Tests for Runner context helper methods."""

    def test_is_linux(self):
        """Runner.is_linux() returns correct condition."""
        expr = Runner.is_linux()
        assert isinstance(expr, Expression)
        assert str(expr) == "${{ runner.os == 'Linux' }}"

    def test_is_windows(self):
        """Runner.is_windows() returns correct condition."""
        expr = Runner.is_windows()
        assert isinstance(expr, Expression)
        assert str(expr) == "${{ runner.os == 'Windows' }}"

    def test_is_macos(self):
        """Runner.is_macos() returns correct condition."""
        expr = Runner.is_macos()
        assert isinstance(expr, Expression)
        assert str(expr) == "${{ runner.os == 'macOS' }}"


class TestRunnerContextInSteps:
    """Tests for using Runner context in Step conditions."""

    def test_runner_in_step_if(self):
        """Runner context works in Step if_ conditions."""
        step = Step(
            name="Linux only step",
            run="echo 'Running on Linux'",
            if_=Runner.is_linux(),
        )
        assert step.if_ is not None
        assert "runner.os == 'Linux'" in str(step.if_)

    def test_runner_os_in_step_if(self):
        """Runner.os works in custom Step if_ conditions."""
        # Create a custom condition using Runner.os
        condition = Expression("runner.os == 'Linux'")
        step = Step(
            name="Custom condition",
            run="echo 'Custom'",
            if_=condition,
        )
        assert "runner.os == 'Linux'" in str(step.if_)

    def test_multiple_runner_conditions(self):
        """Multiple Runner conditions can be combined."""
        linux_or_macos = Runner.is_linux().or_(Runner.is_macos())
        step = Step(
            name="Unix-like systems",
            run="echo 'Running on Unix-like system'",
            if_=linux_or_macos,
        )
        assert "runner.os == 'Linux'" in str(step.if_)
        assert "runner.os == 'macOS'" in str(step.if_)
        assert "||" in str(step.if_)


class TestRunnerContextInEnv:
    """Tests for using Runner context in environment variables."""

    def test_runner_os_in_env(self):
        """Runner.os can be used in environment variables."""
        job = Job(
            runs_on="ubuntu-latest",
            env={"CURRENT_OS": Runner.os},
            steps=[Step(run="echo $CURRENT_OS")],
        )
        assert job.env is not None
        assert "CURRENT_OS" in job.env
        assert "runner.os" in str(job.env["CURRENT_OS"])

    def test_runner_temp_in_env(self):
        """Runner.temp can be used in environment variables."""
        job = Job(
            runs_on="ubuntu-latest",
            env={"TEMP_DIR": Runner.temp},
            steps=[Step(run="echo $TEMP_DIR")],
        )
        assert job.env is not None
        assert "TEMP_DIR" in job.env
        assert "runner.temp" in str(job.env["TEMP_DIR"])

    def test_runner_tool_cache_in_env(self):
        """Runner.tool_cache can be used in environment variables."""
        job = Job(
            runs_on="ubuntu-latest",
            env={"TOOL_CACHE": Runner.tool_cache},
            steps=[Step(run="echo $TOOL_CACHE")],
        )
        assert job.env is not None
        assert "TOOL_CACHE" in job.env
        assert "runner.tool_cache" in str(job.env["TOOL_CACHE"])


class TestRunnerContextInCacheKeys:
    """Tests for using Runner context in cache keys."""

    def test_runner_os_in_cache_key(self):
        """Runner.os can be used in cache key construction."""
        # Test that we can create an expression that includes runner.os
        # This would be used like: f"pip-{Runner.os}-hash"
        assert "runner.os" in str(Runner.os)

    def test_runner_arch_in_cache_key(self):
        """Runner.arch can be used in cache key construction."""
        assert "runner.arch" in str(Runner.arch)
