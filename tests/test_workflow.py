"""Tests for workflow core types."""

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


class TestWorkflow:
    """Tests for Workflow dataclass."""

    def test_workflow_minimal(self):
        """Workflow can be created with minimal fields."""
        w = Workflow(name="CI")
        assert w.name == "CI"

    def test_workflow_with_triggers(self):
        """Workflow accepts trigger configuration."""
        push = PushTrigger(branches=["main"])
        w = Workflow(name="CI", on=Triggers(push=push))
        assert w.on.push is not None
        assert w.on.push.branches == ["main"]

    def test_workflow_with_env(self):
        """Workflow can have environment variables."""
        w = Workflow(name="CI", env={"NODE_ENV": "test"})
        assert w.env == {"NODE_ENV": "test"}

    def test_workflow_with_defaults(self):
        """Workflow can have default settings."""
        defaults = Defaults(run=DefaultsRun(shell="bash", working_directory="/app"))
        w = Workflow(name="CI", defaults=defaults)
        assert w.defaults.run.shell == "bash"

    def test_workflow_with_concurrency(self):
        """Workflow can have concurrency settings."""
        w = Workflow(name="CI", concurrency=Concurrency(group="ci-${{ github.ref }}"))
        assert w.concurrency.group == "ci-${{ github.ref }}"

    def test_workflow_with_permissions(self):
        """Workflow can have permissions."""
        w = Workflow(name="CI", permissions=Permissions(contents="read"))
        assert w.permissions.contents == "read"


class TestJob:
    """Tests for Job dataclass."""

    def test_job_minimal(self):
        """Job can be created with minimal fields."""
        j = Job(name="build")
        assert j.name == "build"
        assert j.runs_on == "ubuntu-latest"  # default

    def test_job_with_runs_on_list(self):
        """Job can specify multiple runner labels."""
        j = Job(name="build", runs_on=["self-hosted", "linux"])
        assert j.runs_on == ["self-hosted", "linux"]

    def test_job_with_needs(self):
        """Job can depend on other jobs."""
        build = Job(name="build")
        test = Job(name="test", needs=[build])
        assert test.needs == [build]

    def test_job_with_if_condition(self):
        """Job can have conditional execution."""
        j = Job(name="deploy", if_="github.ref == 'refs/heads/main'")
        assert j.if_ == "github.ref == 'refs/heads/main'"

    def test_job_with_environment(self):
        """Job can target an environment."""
        env = Environment(name="production", url="https://example.com")
        j = Job(name="deploy", environment=env)
        assert j.environment.name == "production"

    def test_job_with_strategy(self):
        """Job can have a matrix strategy."""
        matrix = Matrix(values={"os": ["ubuntu-latest", "macos-latest"]})
        strategy = Strategy(matrix=matrix, fail_fast=False)
        j = Job(name="test", strategy=strategy)
        assert j.strategy.matrix.values["os"] == ["ubuntu-latest", "macos-latest"]
        assert j.strategy.fail_fast is False

    def test_job_with_container(self):
        """Job can run in a container."""
        container = Container(image="node:18")
        j = Job(name="build", container=container)
        assert j.container.image == "node:18"

    def test_job_with_services(self):
        """Job can have service containers."""
        postgres = Service(image="postgres:15", env={"POSTGRES_PASSWORD": "test"})
        j = Job(name="test", services={"db": postgres})
        assert j.services["db"].image == "postgres:15"

    def test_job_with_steps(self):
        """Job can have steps."""
        steps = [
            Step(uses="actions/checkout@v4"),
            Step(run="npm test"),
        ]
        j = Job(name="test", steps=steps)
        assert len(j.steps) == 2

    def test_job_with_timeout(self):
        """Job can have a timeout."""
        j = Job(name="build", timeout_minutes=30)
        assert j.timeout_minutes == 30

    def test_job_with_outputs(self):
        """Job can define outputs for other jobs."""
        j = Job(name="build", outputs={"version": "${{ steps.version.outputs.value }}"})
        assert j.outputs["version"] == "${{ steps.version.outputs.value }}"


class TestStep:
    """Tests for Step dataclass."""

    def test_step_with_uses(self):
        """Step can use an action."""
        s = Step(uses="actions/checkout@v4")
        assert s.uses == "actions/checkout@v4"

    def test_step_with_run(self):
        """Step can run a command."""
        s = Step(run="echo hello")
        assert s.run == "echo hello"

    def test_step_with_id(self):
        """Step can have an id for referencing outputs."""
        s = Step(id="build", run="npm run build")
        assert s.id == "build"

    def test_step_with_name(self):
        """Step can have a display name."""
        s = Step(name="Build project", run="npm run build")
        assert s.name == "Build project"

    def test_step_with_if_condition(self):
        """Step can have conditional execution."""
        s = Step(run="deploy.sh", if_="success()")
        assert s.if_ == "success()"

    def test_step_with_with(self):
        """Step can pass inputs to actions."""
        s = Step(uses="actions/checkout@v4", with_={"fetch-depth": 0})
        assert s.with_["fetch-depth"] == 0

    def test_step_with_env(self):
        """Step can have environment variables."""
        s = Step(run="npm test", env={"CI": "true"})
        assert s.env["CI"] == "true"

    def test_step_with_shell(self):
        """Step can specify a shell."""
        s = Step(run="Get-Process", shell="pwsh")
        assert s.shell == "pwsh"

    def test_step_with_working_directory(self):
        """Step can specify working directory."""
        s = Step(run="npm test", working_directory="./frontend")
        assert s.working_directory == "./frontend"

    def test_step_with_continue_on_error(self):
        """Step can continue on error."""
        s = Step(run="npm test", continue_on_error=True)
        assert s.continue_on_error is True

    def test_step_with_timeout(self):
        """Step can have a timeout."""
        s = Step(run="long-task.sh", timeout_minutes=60)
        assert s.timeout_minutes == 60


class TestMatrix:
    """Tests for Matrix and Strategy dataclasses."""

    def test_matrix_with_values(self):
        """Matrix can define value combinations."""
        m = Matrix(values={"os": ["ubuntu-latest"], "python": ["3.11", "3.12"]})
        assert m.values["os"] == ["ubuntu-latest"]
        assert m.values["python"] == ["3.11", "3.12"]

    def test_matrix_with_include(self):
        """Matrix can include specific combinations."""
        m = Matrix(
            values={"os": ["ubuntu-latest"]},
            include=[{"os": "windows-latest", "python": "3.12"}],
        )
        assert len(m.include) == 1

    def test_matrix_with_exclude(self):
        """Matrix can exclude specific combinations."""
        m = Matrix(
            values={
                "os": ["ubuntu-latest", "windows-latest"],
                "python": ["3.11", "3.12"],
            },
            exclude=[{"os": "windows-latest", "python": "3.11"}],
        )
        assert len(m.exclude) == 1

    def test_strategy_with_max_parallel(self):
        """Strategy can limit parallel jobs."""
        s = Strategy(matrix=Matrix(values={"os": ["ubuntu-latest"]}), max_parallel=2)
        assert s.max_parallel == 2

    def test_strategy_fail_fast(self):
        """Strategy can disable fail-fast behavior."""
        s = Strategy(fail_fast=False)
        assert s.fail_fast is False


class TestTriggers:
    """Tests for trigger types."""

    def test_push_trigger_branches(self):
        """PushTrigger can filter by branches."""
        t = PushTrigger(branches=["main", "develop"])
        assert t.branches == ["main", "develop"]

    def test_push_trigger_tags(self):
        """PushTrigger can filter by tags."""
        t = PushTrigger(tags=["v*"])
        assert t.tags == ["v*"]

    def test_push_trigger_paths(self):
        """PushTrigger can filter by paths."""
        t = PushTrigger(paths=["src/**"])
        assert t.paths == ["src/**"]

    def test_push_trigger_paths_ignore(self):
        """PushTrigger can ignore paths."""
        t = PushTrigger(paths_ignore=["docs/**"])
        assert t.paths_ignore == ["docs/**"]

    def test_pull_request_trigger(self):
        """PullRequestTrigger can filter by branches and types."""
        t = PullRequestTrigger(
            branches=["main"],
            types=["opened", "synchronize"],
        )
        assert t.branches == ["main"]
        assert t.types == ["opened", "synchronize"]

    def test_schedule_trigger(self):
        """ScheduleTrigger accepts cron expression."""
        t = ScheduleTrigger(cron="0 0 * * *")
        assert t.cron == "0 0 * * *"

    def test_workflow_dispatch_trigger(self):
        """WorkflowDispatchTrigger can define inputs."""
        t = WorkflowDispatchTrigger(
            inputs={
                "environment": WorkflowInput(
                    description="Deployment environment",
                    required=True,
                    default="staging",
                    type="choice",
                    options=["staging", "production"],
                )
            }
        )
        assert t.inputs["environment"].description == "Deployment environment"

    def test_workflow_call_trigger(self):
        """WorkflowCallTrigger for reusable workflows."""
        t = WorkflowCallTrigger(
            inputs={
                "version": WorkflowInput(description="Version to deploy", type="string")
            },
            outputs={
                "result": WorkflowOutput(
                    description="Deployment result",
                    value="${{ jobs.deploy.outputs.result }}",
                )
            },
            secrets={"token": WorkflowSecret(description="API token", required=True)},
        )
        assert t.inputs["version"].type == "string"
        assert t.outputs["result"].description == "Deployment result"
        assert t.secrets["token"].required is True

    def test_triggers_container(self):
        """Triggers container holds multiple trigger types."""
        t = Triggers(
            push=PushTrigger(branches=["main"]),
            pull_request=PullRequestTrigger(branches=["main"]),
            schedule=[ScheduleTrigger(cron="0 0 * * *")],
        )
        assert t.push is not None
        assert t.pull_request is not None
        assert len(t.schedule) == 1


class TestConcurrency:
    """Tests for Concurrency dataclass."""

    def test_concurrency_group(self):
        """Concurrency can specify a group."""
        c = Concurrency(group="ci-${{ github.ref }}")
        assert c.group == "ci-${{ github.ref }}"

    def test_concurrency_cancel_in_progress(self):
        """Concurrency can cancel in-progress runs."""
        c = Concurrency(group="ci", cancel_in_progress=True)
        assert c.cancel_in_progress is True


class TestEnvironment:
    """Tests for Environment dataclass."""

    def test_environment_name_only(self):
        """Environment can be just a name."""
        e = Environment(name="production")
        assert e.name == "production"

    def test_environment_with_url(self):
        """Environment can have a URL."""
        e = Environment(name="production", url="https://example.com")
        assert e.url == "https://example.com"


class TestContainer:
    """Tests for Container dataclass."""

    def test_container_image_only(self):
        """Container can be just an image."""
        c = Container(image="node:18")
        assert c.image == "node:18"

    def test_container_with_credentials(self):
        """Container can have registry credentials."""
        c = Container(
            image="ghcr.io/owner/image",
            credentials={
                "username": "${{ github.actor }}",
                "password": "${{ secrets.GITHUB_TOKEN }}",
            },
        )
        assert c.credentials["username"] == "${{ github.actor }}"

    def test_container_with_env(self):
        """Container can have environment variables."""
        c = Container(image="node:18", env={"NODE_ENV": "test"})
        assert c.env["NODE_ENV"] == "test"

    def test_container_with_ports(self):
        """Container can expose ports."""
        c = Container(image="node:18", ports=["8080:80"])
        assert c.ports == ["8080:80"]

    def test_container_with_volumes(self):
        """Container can mount volumes."""
        c = Container(image="node:18", volumes=["data:/data"])
        assert c.volumes == ["data:/data"]

    def test_container_with_options(self):
        """Container can have Docker options."""
        c = Container(image="node:18", options="--cpus 2")
        assert c.options == "--cpus 2"


class TestService:
    """Tests for Service dataclass."""

    def test_service_image(self):
        """Service requires an image."""
        s = Service(image="postgres:15")
        assert s.image == "postgres:15"

    def test_service_with_env(self):
        """Service can have environment variables."""
        s = Service(image="postgres:15", env={"POSTGRES_PASSWORD": "test"})
        assert s.env["POSTGRES_PASSWORD"] == "test"

    def test_service_with_ports(self):
        """Service can expose ports."""
        s = Service(image="postgres:15", ports=["5432:5432"])
        assert s.ports == ["5432:5432"]


class TestPermissions:
    """Tests for Permissions dataclass."""

    def test_permissions_read_all(self):
        """Permissions can be set to read-all."""
        p = Permissions(read_all=True)
        assert p.read_all is True

    def test_permissions_write_all(self):
        """Permissions can be set to write-all."""
        p = Permissions(write_all=True)
        assert p.write_all is True

    def test_permissions_individual(self):
        """Permissions can be set individually."""
        p = Permissions(contents="read", issues="write", pull_requests="write")
        assert p.contents == "read"
        assert p.issues == "write"
        assert p.pull_requests == "write"
