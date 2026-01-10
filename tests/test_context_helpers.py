"""Tests for additional context helpers: JobContext, VarsContext, StrategyContext."""

from wetwire_github.workflow.expressions import (
    Expression,
    JobContext,
    StrategyContext,
    VarsContext,
)


class TestJobContext:
    """Tests for JobContext class."""

    def test_job_status(self):
        """JobContext.status returns the job status expression."""
        assert isinstance(JobContext.status, Expression)
        assert str(JobContext.status) == "${{ job.status }}"

    def test_job_container_id(self):
        """JobContext.container_id returns container ID expression."""
        assert isinstance(JobContext.container_id, Expression)
        assert str(JobContext.container_id) == "${{ job.container.id }}"

    def test_job_container_network(self):
        """JobContext.container_network returns container network expression."""
        assert isinstance(JobContext.container_network, Expression)
        assert str(JobContext.container_network) == "${{ job.container.network }}"

    def test_job_services(self):
        """JobContext.services() returns service info expression."""
        expr = JobContext.services("postgres", "id")
        assert isinstance(expr, Expression)
        assert str(expr) == "${{ job.services.postgres.id }}"

    def test_job_services_ports(self):
        """JobContext.services() can access port mappings."""
        expr = JobContext.services("redis", "ports.6379")
        assert isinstance(expr, Expression)
        assert str(expr) == "${{ job.services.redis.ports.6379 }}"


class TestVarsContext:
    """Tests for VarsContext class."""

    def test_vars_get_simple(self):
        """VarsContext.get() returns variable expression."""
        expr = VarsContext.get("API_URL")
        assert isinstance(expr, Expression)
        assert str(expr) == "${{ vars.API_URL }}"

    def test_vars_get_nested_name(self):
        """VarsContext.get() works with any variable name."""
        expr = VarsContext.get("MY_CUSTOM_VAR")
        assert isinstance(expr, Expression)
        assert str(expr) == "${{ vars.MY_CUSTOM_VAR }}"

    def test_vars_returns_expression_type(self):
        """VarsContext.get() always returns Expression instance."""
        result = VarsContext.get("TEST_VAR")
        assert type(result) is Expression


class TestStrategyContext:
    """Tests for StrategyContext class."""

    def test_strategy_fail_fast(self):
        """StrategyContext.fail_fast returns fail-fast setting."""
        assert isinstance(StrategyContext.fail_fast, Expression)
        assert str(StrategyContext.fail_fast) == "${{ strategy.fail-fast }}"

    def test_strategy_job_index(self):
        """StrategyContext.job_index returns current job index."""
        assert isinstance(StrategyContext.job_index, Expression)
        assert str(StrategyContext.job_index) == "${{ strategy.job-index }}"

    def test_strategy_job_total(self):
        """StrategyContext.job_total returns total jobs count."""
        assert isinstance(StrategyContext.job_total, Expression)
        assert str(StrategyContext.job_total) == "${{ strategy.job-total }}"

    def test_strategy_max_parallel(self):
        """StrategyContext.max_parallel returns max parallel jobs."""
        assert isinstance(StrategyContext.max_parallel, Expression)
        assert str(StrategyContext.max_parallel) == "${{ strategy.max-parallel }}"


class TestContextInstances:
    """Tests for module-level context instances."""

    def test_job_instance_exists(self):
        """Job module-level instance exists."""
        from wetwire_github.workflow.expressions import Job as JobInstance
        assert isinstance(JobInstance, JobContext)

    def test_vars_instance_exists(self):
        """Vars module-level instance exists."""
        from wetwire_github.workflow.expressions import Vars
        assert isinstance(Vars, VarsContext)

    def test_strategy_instance_exists(self):
        """StrategyInstance module-level instance exists."""
        from wetwire_github.workflow.expressions import StrategyInstance
        assert isinstance(StrategyInstance, StrategyContext)


class TestContextsInStepConditions:
    """Tests for using new contexts in Step conditions."""

    def test_job_status_in_step_if(self):
        """Job.status works in Step if conditions."""
        from wetwire_github.workflow import Step
        from wetwire_github.workflow.expressions import Job as JobInstance

        step = Step(
            name="Cleanup",
            run="cleanup.sh",
            if_=JobInstance.status,
        )
        assert step.if_ is not None
        assert "job.status" in str(step.if_)

    def test_vars_in_step_env(self):
        """Vars.get() works in Step env."""
        from wetwire_github.workflow import Step
        from wetwire_github.workflow.expressions import Vars

        step = Step(
            name="Use variable",
            run="echo $API_URL",
            env={"API_URL": Vars.get("API_URL")},
        )
        assert step.env is not None
        assert "vars.API_URL" in str(step.env["API_URL"])

    def test_strategy_in_step_name(self):
        """Strategy context works in Step naming."""
        from wetwire_github.workflow.expressions import StrategyInstance

        # Create a formatted step name using strategy context
        job_progress = f"Job {StrategyInstance.job_index} of {StrategyInstance.job_total}"
        assert "strategy.job-index" in job_progress
        assert "strategy.job-total" in job_progress
