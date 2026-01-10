"""Tests for self-hosted runner configuration support."""

import yaml

from wetwire_github.serialize import to_dict, to_yaml
from wetwire_github.workflow import Job, SelfHostedRunner, Step


class TestSelfHostedRunner:
    """Tests for SelfHostedRunner dataclass."""

    def test_self_hosted_runner_with_labels(self):
        """SelfHostedRunner can be created with labels."""
        runner = SelfHostedRunner(labels=["self-hosted", "linux", "x64"])
        assert runner.labels == ["self-hosted", "linux", "x64"]

    def test_self_hosted_runner_with_group(self):
        """SelfHostedRunner can be created with a group."""
        runner = SelfHostedRunner(
            labels=["self-hosted", "linux"],
            group="production-runners",
        )
        assert runner.group == "production-runners"

    def test_self_hosted_runner_defaults(self):
        """SelfHostedRunner has sensible defaults."""
        runner = SelfHostedRunner()
        assert runner.labels == []
        assert runner.group is None

    def test_self_hosted_runner_with_gpu_labels(self):
        """SelfHostedRunner can specify GPU labels."""
        runner = SelfHostedRunner(
            labels=["self-hosted", "linux", "x64", "gpu"],
            group="gpu-runners",
        )
        assert "gpu" in runner.labels
        assert runner.group == "gpu-runners"


class TestJobWithSelfHostedRunner:
    """Tests for Job using SelfHostedRunner."""

    def test_job_with_self_hosted_runner(self):
        """Job can use SelfHostedRunner for runs_on."""
        runner = SelfHostedRunner(
            labels=["self-hosted", "linux", "x64"],
            group="production-runners",
        )
        job = Job(
            name="build",
            runs_on=runner,
            steps=[Step(run="echo hello")],
        )
        assert isinstance(job.runs_on, SelfHostedRunner)
        assert job.runs_on.labels == ["self-hosted", "linux", "x64"]
        assert job.runs_on.group == "production-runners"

    def test_job_with_simple_self_hosted_string(self):
        """Job can still use simple 'self-hosted' string."""
        job = Job(
            name="build",
            runs_on="self-hosted",
            steps=[Step(run="echo hello")],
        )
        assert job.runs_on == "self-hosted"

    def test_job_with_self_hosted_labels_list(self):
        """Job can still use list of labels as strings."""
        job = Job(
            name="build",
            runs_on=["self-hosted", "linux", "x64"],
            steps=[Step(run="echo hello")],
        )
        assert job.runs_on == ["self-hosted", "linux", "x64"]


class TestSelfHostedRunnerSerialization:
    """Tests for serializing SelfHostedRunner to YAML."""

    def test_self_hosted_runner_serializes_to_dict_labels_only(self):
        """SelfHostedRunner with only labels serializes correctly."""
        runner = SelfHostedRunner(labels=["self-hosted", "linux", "x64"])
        result = to_dict(runner)
        assert result == {"labels": ["self-hosted", "linux", "x64"]}

    def test_self_hosted_runner_serializes_to_dict_with_group(self):
        """SelfHostedRunner with group serializes correctly."""
        runner = SelfHostedRunner(
            labels=["self-hosted", "linux", "x64", "gpu"],
            group="production-runners",
        )
        result = to_dict(runner)
        assert result == {
            "labels": ["self-hosted", "linux", "x64", "gpu"],
            "group": "production-runners",
        }

    def test_self_hosted_runner_empty_labels_omitted(self):
        """SelfHostedRunner with empty labels is omitted."""
        runner = SelfHostedRunner()
        result = to_dict(runner)
        # Empty labels should be omitted
        assert result == {}

    def test_job_runs_on_with_self_hosted_runner_serializes(self):
        """Job with SelfHostedRunner serializes runs-on correctly."""
        runner = SelfHostedRunner(
            labels=["self-hosted", "linux", "x64"],
            group="production-runners",
        )
        job = Job(
            name="build",
            runs_on=runner,
            steps=[Step(run="make build")],
        )
        result = to_dict(job)
        assert result["runs-on"] == {
            "labels": ["self-hosted", "linux", "x64"],
            "group": "production-runners",
        }

    def test_job_runs_on_with_string_still_works(self):
        """Job with string runs_on still serializes correctly."""
        job = Job(
            name="build",
            runs_on="self-hosted",
            steps=[Step(run="make build")],
        )
        result = to_dict(job)
        assert result["runs-on"] == "self-hosted"

    def test_job_runs_on_with_list_still_works(self):
        """Job with list runs_on still serializes correctly."""
        job = Job(
            name="build",
            runs_on=["self-hosted", "linux", "x64"],
            steps=[Step(run="make build")],
        )
        result = to_dict(job)
        assert result["runs-on"] == ["self-hosted", "linux", "x64"]

    def test_self_hosted_runner_to_yaml(self):
        """SelfHostedRunner produces valid YAML."""
        runner = SelfHostedRunner(
            labels=["self-hosted", "linux", "x64", "gpu"],
            group="production-runners",
        )
        job = Job(
            name="gpu-test",
            runs_on=runner,
            steps=[Step(run="nvidia-smi")],
        )
        result = to_yaml(job)
        parsed = yaml.safe_load(result)
        assert parsed["runs-on"]["labels"] == ["self-hosted", "linux", "x64", "gpu"]
        assert parsed["runs-on"]["group"] == "production-runners"

    def test_complete_workflow_with_self_hosted_runner(self):
        """Complete workflow with self-hosted runner serializes correctly."""
        from wetwire_github.workflow import PushTrigger, Triggers, Workflow

        runner = SelfHostedRunner(
            labels=["self-hosted", "linux", "x64", "gpu"],
            group="production-runners",
        )
        workflow = Workflow(
            name="GPU Test",
            on=Triggers(push=PushTrigger(branches=["main"])),
            jobs={
                "gpu-test": Job(
                    name="GPU Test",
                    runs_on=runner,
                    steps=[
                        Step(name="Check GPU", run="nvidia-smi"),
                        Step(name="Run tests", run="pytest tests/"),
                    ],
                )
            },
        )
        result = to_yaml(workflow)
        parsed = yaml.safe_load(result)
        assert parsed["jobs"]["gpu-test"]["runs-on"]["labels"] == [
            "self-hosted",
            "linux",
            "x64",
            "gpu",
        ]
        assert parsed["jobs"]["gpu-test"]["runs-on"]["group"] == "production-runners"
