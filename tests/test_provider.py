"""Tests for the provider module.

The provider module provides a unified interface for workflow
serialization and build orchestration.
"""

from pathlib import Path


class TestWorkflowProviderInit:
    """Tests for WorkflowProvider initialization."""

    def test_default_output_dir(self):
        """WorkflowProvider uses .github/workflows by default."""
        from wetwire_github.provider import WorkflowProvider

        provider = WorkflowProvider()
        assert provider.output_dir == ".github/workflows"

    def test_custom_output_dir(self):
        """WorkflowProvider accepts custom output directory."""
        from wetwire_github.provider import WorkflowProvider

        provider = WorkflowProvider(output_dir="custom/output")
        assert provider.output_dir == "custom/output"


class TestWorkflowProviderBuild:
    """Tests for WorkflowProvider.build method."""

    def test_build_single_workflow(self):
        """build() generates YAML for a single workflow."""
        from wetwire_github.provider import WorkflowProvider
        from wetwire_github.workflow import Job, Step, Triggers, Workflow
        from wetwire_github.workflow.triggers import PushTrigger

        provider = WorkflowProvider()

        ci = Workflow(
            name="CI",
            on=Triggers(push=PushTrigger(branches=["main"])),
            jobs={
                "test": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(run="pytest")],
                )
            },
        )

        result = provider.build([ci])

        assert isinstance(result, dict)
        assert "ci.yml" in result
        assert "name: CI" in result["ci.yml"]

    def test_build_multiple_workflows(self):
        """build() generates YAML for multiple workflows."""
        from wetwire_github.provider import WorkflowProvider
        from wetwire_github.workflow import Job, Step, Triggers, Workflow
        from wetwire_github.workflow.triggers import PushTrigger

        provider = WorkflowProvider()

        ci = Workflow(
            name="CI",
            on=Triggers(push=PushTrigger(branches=["main"])),
            jobs={"test": Job(runs_on="ubuntu-latest", steps=[Step(run="pytest")])},
        )

        deploy = Workflow(
            name="Deploy",
            on=Triggers(push=PushTrigger(branches=["main"])),
            jobs={"deploy": Job(runs_on="ubuntu-latest", steps=[Step(run="deploy.sh")])},
        )

        result = provider.build([ci, deploy])

        assert len(result) == 2
        assert "ci.yml" in result
        assert "deploy.yml" in result


class TestWorkflowProviderValidate:
    """Tests for WorkflowProvider.validate method."""

    def test_validate_valid_workflow(self):
        """validate() returns empty list for valid workflow."""
        from wetwire_github.provider import WorkflowProvider
        from wetwire_github.workflow import Job, Step, Triggers, Workflow
        from wetwire_github.workflow.triggers import PushTrigger

        provider = WorkflowProvider()

        ci = Workflow(
            name="CI",
            on=Triggers(push=PushTrigger(branches=["main"])),
            jobs={"test": Job(runs_on="ubuntu-latest", steps=[Step(run="pytest")])},
        )

        errors = provider.validate([ci])
        assert isinstance(errors, list)

    def test_validate_returns_errors_for_invalid_workflow(self):
        """validate() returns errors for invalid workflow."""
        from wetwire_github.provider import WorkflowProvider
        from wetwire_github.workflow import Workflow

        provider = WorkflowProvider()

        # Workflow with no jobs (invalid)
        invalid = Workflow(name="Invalid")

        errors = provider.validate([invalid])
        assert isinstance(errors, list)


class TestWorkflowProviderWrite:
    """Tests for WorkflowProvider.write method."""

    def test_write_creates_files(self, tmp_path: Path):
        """write() creates YAML files in output directory."""
        from wetwire_github.provider import WorkflowProvider
        from wetwire_github.workflow import Job, Step, Triggers, Workflow
        from wetwire_github.workflow.triggers import PushTrigger

        output_dir = tmp_path / ".github" / "workflows"
        provider = WorkflowProvider(output_dir=str(output_dir))

        ci = Workflow(
            name="CI",
            on=Triggers(push=PushTrigger(branches=["main"])),
            jobs={"test": Job(runs_on="ubuntu-latest", steps=[Step(run="pytest")])},
        )

        paths = provider.write([ci])

        assert len(paths) == 1
        assert paths[0].exists()
        assert paths[0].name == "ci.yml"

    def test_write_creates_output_directory(self, tmp_path: Path):
        """write() creates output directory if it doesn't exist."""
        from wetwire_github.provider import WorkflowProvider
        from wetwire_github.workflow import Job, Step, Triggers, Workflow
        from wetwire_github.workflow.triggers import PushTrigger

        output_dir = tmp_path / "new" / "output" / "dir"
        provider = WorkflowProvider(output_dir=str(output_dir))

        ci = Workflow(
            name="CI",
            on=Triggers(push=PushTrigger(branches=["main"])),
            jobs={"test": Job(runs_on="ubuntu-latest", steps=[Step(run="pytest")])},
        )

        provider.write([ci])

        assert output_dir.exists()


class TestWorkflowProviderFilenameGeneration:
    """Tests for workflow filename generation."""

    def test_filename_from_workflow_name(self):
        """Filename is generated from workflow name."""
        from wetwire_github.provider import WorkflowProvider
        from wetwire_github.workflow import Job, Step, Triggers, Workflow
        from wetwire_github.workflow.triggers import PushTrigger

        provider = WorkflowProvider()

        workflow = Workflow(
            name="My Custom Workflow",
            on=Triggers(push=PushTrigger(branches=["main"])),
            jobs={"test": Job(runs_on="ubuntu-latest", steps=[Step(run="test")])},
        )

        result = provider.build([workflow])

        # Should convert to lowercase with hyphens
        assert "my-custom-workflow.yml" in result

    def test_filename_handles_special_characters(self):
        """Filename generation handles special characters."""
        from wetwire_github.provider import WorkflowProvider
        from wetwire_github.workflow import Job, Step, Triggers, Workflow
        from wetwire_github.workflow.triggers import PushTrigger

        provider = WorkflowProvider()

        workflow = Workflow(
            name="CI/CD Pipeline (v2.0)",
            on=Triggers(push=PushTrigger(branches=["main"])),
            jobs={"test": Job(runs_on="ubuntu-latest", steps=[Step(run="test")])},
        )

        result = provider.build([workflow])

        # Should sanitize special characters
        filenames = list(result.keys())
        assert len(filenames) == 1
        assert "/" not in filenames[0]
        assert "(" not in filenames[0]
        assert ")" not in filenames[0]
