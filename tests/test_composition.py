"""Tests for ComposedWorkflow builder."""

import pytest

from wetwire_github.workflow import (
    Job,
    Permissions,
    PullRequestTrigger,
    PushTrigger,
    Step,
    Workflow,
)
from wetwire_github.workflow.composition import ComposedWorkflow


class TestComposedWorkflowBasics:
    """Tests for basic ComposedWorkflow functionality."""

    def test_build_simple_workflow(self):
        """ComposedWorkflow can build a simple workflow."""
        workflow = ComposedWorkflow().name("CI").build()
        assert isinstance(workflow, Workflow)
        assert workflow.name == "CI"

    def test_build_workflow_with_name(self):
        """ComposedWorkflow can set workflow name."""
        workflow = ComposedWorkflow().name("My Workflow").build()
        assert workflow.name == "My Workflow"

    def test_fluent_interface_returns_self(self):
        """All builder methods return self for chaining."""
        composer = ComposedWorkflow()
        assert composer.name("CI") is composer
        assert composer.add_env({"KEY": "value"}) is composer
        assert composer.add_permissions({"contents": "read"}) is composer

    def test_build_workflow_with_single_job(self):
        """ComposedWorkflow can add a single job."""
        job = Job(name="build", runs_on="ubuntu-latest", steps=[Step(run="make build")])
        workflow = ComposedWorkflow().name("CI").add_job("build", job).build()
        assert "build" in workflow.jobs
        assert workflow.jobs["build"].name == "build"


class TestComposedWorkflowTriggers:
    """Tests for adding triggers to ComposedWorkflow."""

    def test_add_push_trigger(self):
        """ComposedWorkflow can add push trigger."""
        workflow = (
            ComposedWorkflow()
            .name("CI")
            .add_trigger("push", PushTrigger(branches=["main"]))
            .build()
        )
        assert workflow.on.push is not None
        assert workflow.on.push.branches == ["main"]

    def test_add_pull_request_trigger(self):
        """ComposedWorkflow can add pull_request trigger."""
        workflow = (
            ComposedWorkflow()
            .name("CI")
            .add_trigger("pull_request", PullRequestTrigger(branches=["main"]))
            .build()
        )
        assert workflow.on.pull_request is not None
        assert workflow.on.pull_request.branches == ["main"]

    def test_add_multiple_triggers(self):
        """ComposedWorkflow can add multiple triggers."""
        workflow = (
            ComposedWorkflow()
            .name("CI")
            .add_trigger("push", PushTrigger(branches=["main"]))
            .add_trigger("pull_request", PullRequestTrigger(branches=["main"]))
            .build()
        )
        assert workflow.on.push is not None
        assert workflow.on.pull_request is not None

    def test_invalid_trigger_type_raises_error(self):
        """ComposedWorkflow raises error for invalid trigger type."""
        composer = ComposedWorkflow()
        with pytest.raises(ValueError, match="Unknown trigger type"):
            composer.add_trigger("invalid_trigger", {})


class TestComposedWorkflowJobs:
    """Tests for adding jobs with dependencies."""

    def test_add_multiple_jobs(self):
        """ComposedWorkflow can add multiple jobs."""
        build_job = Job(name="build", steps=[Step(run="make build")])
        test_job = Job(name="test", steps=[Step(run="make test")])

        workflow = (
            ComposedWorkflow()
            .name("CI")
            .add_job("build", build_job)
            .add_job("test", test_job)
            .build()
        )
        assert "build" in workflow.jobs
        assert "test" in workflow.jobs

    def test_add_job_with_single_dependency(self):
        """ComposedWorkflow can add job with single dependency."""
        build_job = Job(name="build", steps=[Step(run="make build")])
        test_job = Job(name="test", steps=[Step(run="make test")])

        workflow = (
            ComposedWorkflow()
            .name("CI")
            .add_job("build", build_job)
            .add_job("test", test_job, needs=["build"])
            .build()
        )
        assert workflow.jobs["test"].needs == ["build"]

    def test_add_job_with_multiple_dependencies(self):
        """ComposedWorkflow can add job with multiple dependencies."""
        build_job = Job(name="build", steps=[Step(run="make build")])
        test_job = Job(name="test", steps=[Step(run="make test")])
        lint_job = Job(name="lint", steps=[Step(run="make lint")])
        deploy_job = Job(name="deploy", steps=[Step(run="make deploy")])

        workflow = (
            ComposedWorkflow()
            .name("CI/CD")
            .add_job("build", build_job)
            .add_job("test", test_job)
            .add_job("lint", lint_job)
            .add_job("deploy", deploy_job, needs=["build", "test", "lint"])
            .build()
        )
        assert workflow.jobs["deploy"].needs == ["build", "test", "lint"]

    def test_add_job_validates_missing_dependency(self):
        """ComposedWorkflow validates that job dependencies exist."""
        test_job = Job(name="test", steps=[Step(run="make test")])

        composer = (
            ComposedWorkflow().name("CI").add_job("test", test_job, needs=["build"])
        )

        with pytest.raises(ValueError, match="depends on non-existent job"):
            composer.build()

    def test_circular_dependency_detection(self):
        """ComposedWorkflow detects circular dependencies."""
        job_a = Job(name="a", steps=[Step(run="echo a")])
        job_b = Job(name="b", steps=[Step(run="echo b")])

        composer = (
            ComposedWorkflow()
            .name("CI")
            .add_job("a", job_a, needs=["b"])
            .add_job("b", job_b, needs=["a"])
        )

        with pytest.raises(ValueError, match="Circular dependency detected"):
            composer.build()

    def test_self_dependency_detection(self):
        """ComposedWorkflow detects self-referencing dependencies."""
        job = Job(name="build", steps=[Step(run="make build")])

        composer = ComposedWorkflow().name("CI").add_job("build", job, needs=["build"])

        with pytest.raises(ValueError, match="cannot depend on itself"):
            composer.build()


class TestComposedWorkflowEnvironment:
    """Tests for environment variables in ComposedWorkflow."""

    def test_add_single_env_variable(self):
        """ComposedWorkflow can add a single environment variable."""
        workflow = ComposedWorkflow().name("CI").add_env({"NODE_ENV": "test"}).build()
        assert workflow.env == {"NODE_ENV": "test"}

    def test_merge_multiple_env_calls(self):
        """ComposedWorkflow merges multiple add_env calls."""
        workflow = (
            ComposedWorkflow()
            .name("CI")
            .add_env({"NODE_ENV": "test"})
            .add_env({"DEBUG": "true"})
            .build()
        )
        assert workflow.env == {"NODE_ENV": "test", "DEBUG": "true"}

    def test_env_override_with_later_values(self):
        """Later add_env calls override earlier values."""
        workflow = (
            ComposedWorkflow()
            .name("CI")
            .add_env({"NODE_ENV": "development"})
            .add_env({"NODE_ENV": "production"})
            .build()
        )
        assert workflow.env == {"NODE_ENV": "production"}


class TestComposedWorkflowPermissions:
    """Tests for permissions in ComposedWorkflow."""

    def test_add_permissions_dict(self):
        """ComposedWorkflow can add permissions as dict."""
        workflow = (
            ComposedWorkflow()
            .name("CI")
            .add_permissions({"contents": "read", "issues": "write"})
            .build()
        )
        assert workflow.permissions.contents == "read"
        assert workflow.permissions.issues == "write"

    def test_add_permissions_object(self):
        """ComposedWorkflow can add permissions as Permissions object."""
        perms = Permissions(contents="read", pull_requests="write")
        workflow = ComposedWorkflow().name("CI").add_permissions(perms).build()
        assert workflow.permissions.contents == "read"
        assert workflow.permissions.pull_requests == "write"

    def test_add_permissions_read_all_string(self):
        """ComposedWorkflow can set read-all permissions with string."""
        workflow = ComposedWorkflow().name("CI").add_permissions("read-all").build()
        assert workflow.permissions.read_all is True

    def test_add_permissions_write_all_string(self):
        """ComposedWorkflow can set write-all permissions with string."""
        workflow = ComposedWorkflow().name("CI").add_permissions("write-all").build()
        assert workflow.permissions.write_all is True


class TestComposedWorkflowIntegration:
    """Integration tests for complete workflows."""

    def test_complex_workflow_composition(self):
        """ComposedWorkflow can build a complex workflow with all features."""
        build_job = Job(
            name="Build",
            runs_on="ubuntu-latest",
            steps=[
                Step(uses="actions/checkout@v4"),
                Step(run="npm install"),
                Step(run="npm run build"),
            ],
        )

        test_job = Job(
            name="Test",
            runs_on="ubuntu-latest",
            steps=[
                Step(uses="actions/checkout@v4"),
                Step(run="npm install"),
                Step(run="npm test"),
            ],
        )

        deploy_job = Job(
            name="Deploy",
            runs_on="ubuntu-latest",
            steps=[
                Step(run="./deploy.sh"),
            ],
        )

        workflow = (
            ComposedWorkflow()
            .name("CI/CD Pipeline")
            .add_trigger("push", PushTrigger(branches=["main"]))
            .add_trigger("pull_request", PullRequestTrigger(branches=["main"]))
            .add_env({"NODE_ENV": "production"})
            .add_env({"CI": "true"})
            .add_permissions({"contents": "read", "deployments": "write"})
            .add_job("build", build_job)
            .add_job("test", test_job, needs=["build"])
            .add_job("deploy", deploy_job, needs=["build", "test"])
            .build()
        )

        assert workflow.name == "CI/CD Pipeline"
        assert workflow.on.push.branches == ["main"]
        assert workflow.on.pull_request.branches == ["main"]
        assert workflow.env == {"NODE_ENV": "production", "CI": "true"}
        assert workflow.permissions.contents == "read"
        assert workflow.permissions.deployments == "write"
        assert "build" in workflow.jobs
        assert "test" in workflow.jobs
        assert "deploy" in workflow.jobs
        assert workflow.jobs["test"].needs == ["build"]
        assert workflow.jobs["deploy"].needs == ["build", "test"]

    def test_build_workflow_with_no_jobs(self):
        """ComposedWorkflow can build a workflow with no jobs."""
        workflow = (
            ComposedWorkflow()
            .name("Empty Workflow")
            .add_trigger("push", PushTrigger(branches=["main"]))
            .build()
        )
        assert workflow.name == "Empty Workflow"
        assert len(workflow.jobs) == 0

    def test_build_workflow_multiple_times(self):
        """ComposedWorkflow can build multiple workflows from same state."""
        composer = (
            ComposedWorkflow()
            .name("CI")
            .add_trigger("push", PushTrigger(branches=["main"]))
            .add_job("build", Job(name="build", steps=[Step(run="make build")]))
        )

        workflow1 = composer.build()
        workflow2 = composer.build()

        assert workflow1.name == workflow2.name
        assert workflow1.on.push.branches == workflow2.on.push.branches
        assert "build" in workflow1.jobs
        assert "build" in workflow2.jobs
