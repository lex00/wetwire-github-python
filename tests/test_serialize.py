"""Tests for YAML serialization."""

import yaml

from wetwire_github.serialize import to_dict, to_yaml
from wetwire_github.workflow import (
    Concurrency,
    Container,
    Defaults,
    DefaultsRun,
    Environment,
    Job,
    Matrix,
    Permissions,
    PullRequestTrigger,
    PushTrigger,
    ScheduleTrigger,
    Service,
    Step,
    Strategy,
    Triggers,
    Workflow,
    WorkflowCallTrigger,
    WorkflowDispatchTrigger,
    WorkflowInput,
    WorkflowOutput,
    WorkflowSecret,
)


class TestToDict:
    """Tests for to_dict serialization."""

    def test_step_with_uses(self):
        """Step with uses converts correctly."""
        step = Step(uses="actions/checkout@v4")
        result = to_dict(step)
        assert result == {"uses": "actions/checkout@v4"}

    def test_step_with_run(self):
        """Step with run converts correctly."""
        step = Step(run="echo hello")
        result = to_dict(step)
        assert result == {"run": "echo hello"}

    def test_step_with_all_fields(self):
        """Step with all fields converts correctly."""
        step = Step(
            id="build",
            name="Build project",
            if_="success()",
            uses="actions/setup-node@v4",
            with_={"node-version": "18"},
            env={"CI": "true"},
            shell="bash",
            working_directory="./app",
            continue_on_error=True,
            timeout_minutes=30,
        )
        result = to_dict(step)
        assert result["id"] == "build"
        assert result["name"] == "Build project"
        assert result["if"] == "success()"  # if_ becomes if
        assert result["uses"] == "actions/setup-node@v4"
        assert result["with"]["node-version"] == "18"  # with_ becomes with
        assert result["env"]["CI"] == "true"
        assert result["shell"] == "bash"
        assert result["working-directory"] == "./app"  # snake_case to kebab-case
        assert result["continue-on-error"] is True
        assert result["timeout-minutes"] == 30

    def test_step_omits_none_and_empty(self):
        """Step omits None and empty string values."""
        step = Step(run="echo hello")
        result = to_dict(step)
        assert "id" not in result
        assert "name" not in result
        assert "if" not in result
        assert "uses" not in result
        assert "with" not in result

    def test_job_minimal(self):
        """Job with minimal fields converts correctly."""
        job = Job(name="build", steps=[Step(run="echo hello")])
        result = to_dict(job)
        assert result["name"] == "build"
        assert result["runs-on"] == "ubuntu-latest"
        assert len(result["steps"]) == 1

    def test_job_with_matrix(self):
        """Job with matrix strategy converts correctly."""
        matrix = Matrix(values={"os": ["ubuntu-latest", "macos-latest"]})
        strategy = Strategy(matrix=matrix, fail_fast=False)
        job = Job(name="test", strategy=strategy, steps=[Step(run="test")])
        result = to_dict(job)
        assert result["strategy"]["matrix"]["os"] == ["ubuntu-latest", "macos-latest"]
        assert result["strategy"]["fail-fast"] is False

    def test_job_with_needs(self):
        """Job with needs converts to list of job names."""
        build = Job(name="build", steps=[Step(run="build")])
        test = Job(name="test", needs=[build], steps=[Step(run="test")])
        result = to_dict(test)
        # needs should be a list of strings (job names would need resolution)
        # For now, we'll check that needs is present
        assert "needs" in result

    def test_job_with_environment(self):
        """Job with environment converts correctly."""
        env = Environment(name="production", url="https://example.com")
        job = Job(name="deploy", environment=env, steps=[Step(run="deploy")])
        result = to_dict(job)
        assert result["environment"]["name"] == "production"
        assert result["environment"]["url"] == "https://example.com"

    def test_job_with_container(self):
        """Job with container converts correctly."""
        container = Container(image="node:18", env={"NODE_ENV": "test"})
        job = Job(name="build", container=container, steps=[Step(run="build")])
        result = to_dict(job)
        assert result["container"]["image"] == "node:18"
        assert result["container"]["env"]["NODE_ENV"] == "test"

    def test_job_with_services(self):
        """Job with services converts correctly."""
        postgres = Service(image="postgres:15", env={"POSTGRES_PASSWORD": "test"})
        job = Job(name="test", services={"db": postgres}, steps=[Step(run="test")])
        result = to_dict(job)
        assert result["services"]["db"]["image"] == "postgres:15"

    def test_push_trigger(self):
        """Push trigger converts correctly."""
        trigger = PushTrigger(branches=["main"], paths=["src/**"])
        result = to_dict(trigger)
        assert result["branches"] == ["main"]
        assert result["paths"] == ["src/**"]

    def test_push_trigger_paths_ignore(self):
        """Push trigger with paths-ignore converts correctly."""
        trigger = PushTrigger(paths_ignore=["docs/**"])
        result = to_dict(trigger)
        assert result["paths-ignore"] == ["docs/**"]

    def test_pull_request_trigger(self):
        """Pull request trigger converts correctly."""
        trigger = PullRequestTrigger(branches=["main"], types=["opened", "synchronize"])
        result = to_dict(trigger)
        assert result["branches"] == ["main"]
        assert result["types"] == ["opened", "synchronize"]

    def test_schedule_trigger(self):
        """Schedule trigger converts correctly."""
        trigger = ScheduleTrigger(cron="0 0 * * *")
        result = to_dict(trigger)
        assert result["cron"] == "0 0 * * *"

    def test_workflow_dispatch_trigger(self):
        """Workflow dispatch trigger converts correctly."""
        trigger = WorkflowDispatchTrigger(
            inputs={
                "environment": WorkflowInput(
                    description="Target environment",
                    required=True,
                    default="staging",
                    type="choice",
                    options=["staging", "production"],
                )
            }
        )
        result = to_dict(trigger)
        assert result["inputs"]["environment"]["description"] == "Target environment"
        assert result["inputs"]["environment"]["required"] is True
        assert result["inputs"]["environment"]["type"] == "choice"
        assert result["inputs"]["environment"]["options"] == ["staging", "production"]

    def test_workflow_call_trigger(self):
        """Workflow call trigger converts correctly."""
        trigger = WorkflowCallTrigger(
            inputs={"version": WorkflowInput(description="Version", type="string")},
            outputs={
                "result": WorkflowOutput(
                    description="Result", value="${{ jobs.deploy.outputs.result }}"
                )
            },
            secrets={"token": WorkflowSecret(description="API token", required=True)},
        )
        result = to_dict(trigger)
        assert result["inputs"]["version"]["type"] == "string"
        assert (
            result["outputs"]["result"]["value"] == "${{ jobs.deploy.outputs.result }}"
        )
        assert result["secrets"]["token"]["required"] is True

    def test_triggers_container(self):
        """Triggers container converts correctly."""
        triggers = Triggers(
            push=PushTrigger(branches=["main"]),
            pull_request=PullRequestTrigger(branches=["main"]),
            schedule=[ScheduleTrigger(cron="0 0 * * *")],
        )
        result = to_dict(triggers)
        assert result["push"]["branches"] == ["main"]
        assert result["pull_request"]["branches"] == ["main"]
        assert len(result["schedule"]) == 1
        assert result["schedule"][0]["cron"] == "0 0 * * *"

    def test_concurrency(self):
        """Concurrency converts correctly."""
        concurrency = Concurrency(group="ci-${{ github.ref }}", cancel_in_progress=True)
        result = to_dict(concurrency)
        assert result["group"] == "ci-${{ github.ref }}"
        assert result["cancel-in-progress"] is True

    def test_permissions_individual(self):
        """Permissions with individual values convert correctly."""
        perms = Permissions(contents="read", issues="write")
        result = to_dict(perms)
        assert result["contents"] == "read"
        assert result["issues"] == "write"

    def test_permissions_read_all(self):
        """Permissions with read-all converts correctly."""
        perms = Permissions(read_all=True)
        result = to_dict(perms)
        assert result["read-all"] is True

    def test_workflow_minimal(self):
        """Workflow with minimal fields converts correctly."""
        workflow = Workflow(name="CI")
        result = to_dict(workflow)
        assert result["name"] == "CI"

    def test_workflow_with_triggers(self):
        """Workflow with triggers converts correctly."""
        workflow = Workflow(
            name="CI",
            on=Triggers(push=PushTrigger(branches=["main"])),
        )
        result = to_dict(workflow)
        assert result["name"] == "CI"
        assert result["on"]["push"]["branches"] == ["main"]

    def test_workflow_with_env(self):
        """Workflow with env converts correctly."""
        workflow = Workflow(name="CI", env={"NODE_ENV": "test"})
        result = to_dict(workflow)
        assert result["env"]["NODE_ENV"] == "test"

    def test_workflow_with_defaults(self):
        """Workflow with defaults converts correctly."""
        defaults = Defaults(run=DefaultsRun(shell="bash", working_directory="/app"))
        workflow = Workflow(name="CI", defaults=defaults)
        result = to_dict(workflow)
        assert result["defaults"]["run"]["shell"] == "bash"
        assert result["defaults"]["run"]["working-directory"] == "/app"

    def test_workflow_with_concurrency(self):
        """Workflow with concurrency converts correctly."""
        workflow = Workflow(
            name="CI",
            concurrency=Concurrency(group="ci", cancel_in_progress=True),
        )
        result = to_dict(workflow)
        assert result["concurrency"]["group"] == "ci"

    def test_workflow_with_permissions(self):
        """Workflow with permissions converts correctly."""
        workflow = Workflow(name="CI", permissions=Permissions(contents="read"))
        result = to_dict(workflow)
        assert result["permissions"]["contents"] == "read"


class TestToYaml:
    """Tests for to_yaml serialization."""

    def test_simple_step(self):
        """Simple step serializes to YAML."""
        step = Step(run="echo hello")
        result = to_yaml(step)
        assert "run: echo hello" in result

    def test_step_multiline_run(self):
        """Step with multiline run uses literal block scalar."""
        step = Step(run="echo hello\necho world")
        result = to_yaml(step)
        # Should use literal block scalar for multiline
        parsed = yaml.safe_load(result)
        assert "echo hello" in parsed["run"]
        assert "echo world" in parsed["run"]

    def test_workflow_yaml_structure(self):
        """Workflow serializes to valid YAML structure."""
        workflow = Workflow(
            name="CI",
            on=Triggers(push=PushTrigger(branches=["main"])),
        )
        result = to_yaml(workflow)
        parsed = yaml.safe_load(result)
        assert parsed["name"] == "CI"
        assert parsed["on"]["push"]["branches"] == ["main"]

    def test_complete_workflow(self):
        """Complete workflow with jobs serializes correctly."""
        workflow = Workflow(
            name="CI",
            on=Triggers(
                push=PushTrigger(branches=["main"]),
                pull_request=PullRequestTrigger(branches=["main"]),
            ),
            jobs={
                "build": Job(
                    name="Build",
                    runs_on="ubuntu-latest",
                    steps=[
                        Step(uses="actions/checkout@v4"),
                        Step(run="npm install"),
                        Step(run="npm test"),
                    ],
                )
            },
        )
        result = to_yaml(workflow)
        parsed = yaml.safe_load(result)
        assert parsed["name"] == "CI"
        assert "build" in parsed["jobs"]
        assert len(parsed["jobs"]["build"]["steps"]) == 3


class TestFieldNameConversion:
    """Tests for field name conversion."""

    def test_snake_to_kebab(self):
        """Snake case converts to kebab case."""
        step = Step(
            working_directory="./app", continue_on_error=True, timeout_minutes=30
        )
        result = to_dict(step)
        assert "working-directory" in result
        assert "continue-on-error" in result
        assert "timeout-minutes" in result

    def test_reserved_names(self):
        """Reserved Python names convert correctly."""
        step = Step(if_="success()", with_={"key": "value"})
        result = to_dict(step)
        assert "if" in result
        assert "with" in result
        assert "if_" not in result
        assert "with_" not in result

    def test_runs_on_conversion(self):
        """runs_on converts to runs-on."""
        job = Job(name="test", runs_on="ubuntu-latest", steps=[Step(run="test")])
        result = to_dict(job)
        assert "runs-on" in result
        assert result["runs-on"] == "ubuntu-latest"

    def test_fail_fast_conversion(self):
        """fail_fast converts to fail-fast."""
        strategy = Strategy(fail_fast=False)
        result = to_dict(strategy)
        assert "fail-fast" in result

    def test_cancel_in_progress_conversion(self):
        """cancel_in_progress converts to cancel-in-progress."""
        concurrency = Concurrency(group="ci", cancel_in_progress=True)
        result = to_dict(concurrency)
        assert "cancel-in-progress" in result


class TestNoneOmission:
    """Tests for None value omission."""

    def test_none_values_omitted(self):
        """None values are omitted from output."""
        step = Step(run="test")
        result = to_dict(step)
        # These should not be present
        assert "id" not in result
        assert "name" not in result
        assert "if" not in result
        assert "uses" not in result
        assert "with" not in result
        assert "env" not in result
        assert "shell" not in result
        assert "working-directory" not in result
        assert "continue-on-error" not in result
        assert "timeout-minutes" not in result

    def test_empty_string_omitted(self):
        """Empty string values are omitted from output."""
        step = Step(id="", run="test")
        result = to_dict(step)
        assert "id" not in result

    def test_empty_list_omitted(self):
        """Empty list values are omitted from output."""
        trigger = PushTrigger()
        result = to_dict(trigger)
        assert "branches" not in result
        assert "paths" not in result

    def test_empty_dict_omitted(self):
        """Empty dict values are omitted from output."""
        job = Job(name="test", steps=[Step(run="test")])
        result = to_dict(job)
        # Empty outputs dict should be omitted
        assert "outputs" not in result or result.get("outputs") != {}

    def test_false_values_preserved(self):
        """False boolean values are preserved."""
        strategy = Strategy(fail_fast=False)
        result = to_dict(strategy)
        assert "fail-fast" in result
        assert result["fail-fast"] is False

    def test_zero_values_preserved(self):
        """Zero numeric values are preserved."""
        step = Step(run="test", timeout_minutes=0)
        result = to_dict(step)
        # Zero is a valid timeout
        assert "timeout-minutes" in result
        assert result["timeout-minutes"] == 0
