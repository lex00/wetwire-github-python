"""Provider module for workflow serialization and build orchestration.

This module provides a unified interface for building and writing
GitHub Actions workflow files from Python declarations.

Usage:
    from wetwire_github.provider import WorkflowProvider
    from wetwire_github.workflow import Workflow, Job, Step, Triggers
    from wetwire_github.workflow.triggers import PushTrigger

    provider = WorkflowProvider()

    ci = Workflow(
        name="CI",
        on=Triggers(push=PushTrigger(branches=["main"])),
        jobs={"test": Job(runs_on="ubuntu-latest", steps=[Step(run="pytest")])},
    )

    # Generate YAML content
    yaml_content = provider.build([ci])

    # Write to files
    paths = provider.write([ci])
"""

import re
from dataclasses import dataclass
from pathlib import Path

from wetwire_github.serialize import to_yaml
from wetwire_github.workflow import Workflow

__all__ = ["WorkflowProvider", "ValidationError"]


@dataclass
class ValidationError:
    """Represents a validation error for a workflow."""

    workflow_name: str
    message: str
    field: str | None = None


class WorkflowProvider:
    """Orchestrates workflow serialization and file output.

    This class provides a unified interface for:
    - Building YAML content from workflow definitions
    - Validating workflows before output
    - Writing workflow files to disk
    """

    def __init__(self, output_dir: str = ".github/workflows") -> None:
        """Initialize the provider.

        Args:
            output_dir: Directory where workflow YAML files will be written.
                       Defaults to ".github/workflows".
        """
        self.output_dir = output_dir

    def build(self, workflows: list[Workflow]) -> dict[str, str]:
        """Build YAML content for all workflows.

        Args:
            workflows: List of Workflow instances to build.

        Returns:
            Dictionary mapping filenames to YAML content.

        Example:
            provider = WorkflowProvider()
            result = provider.build([ci, deploy])
            # result = {"ci.yml": "name: CI\\n...", "deploy.yml": "..."}
        """
        result: dict[str, str] = {}

        for workflow in workflows:
            filename = self._generate_filename(workflow)
            yaml_content = to_yaml(workflow)
            result[filename] = yaml_content

        return result

    def validate(self, workflows: list[Workflow]) -> list[ValidationError]:
        """Validate workflows before building.

        Performs basic validation checks on workflows:
        - Workflow must have a name
        - Workflow should have at least one job

        Args:
            workflows: List of Workflow instances to validate.

        Returns:
            List of ValidationError objects. Empty list means all valid.
        """
        errors: list[ValidationError] = []

        for workflow in workflows:
            # Check for name
            if not workflow.name:
                errors.append(
                    ValidationError(
                        workflow_name="<unnamed>",
                        message="Workflow must have a name",
                        field="name",
                    )
                )
                continue

            # Check for jobs
            if not workflow.jobs:
                errors.append(
                    ValidationError(
                        workflow_name=workflow.name,
                        message="Workflow should have at least one job",
                        field="jobs",
                    )
                )

        return errors

    def write(self, workflows: list[Workflow]) -> list[Path]:
        """Write workflows to YAML files.

        Creates the output directory if it doesn't exist, then writes
        each workflow to a separate YAML file.

        Args:
            workflows: List of Workflow instances to write.

        Returns:
            List of Path objects for the written files.
        """
        output_path = Path(self.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        built = self.build(workflows)
        written_files: list[Path] = []

        for filename, content in built.items():
            file_path = output_path / filename
            file_path.write_text(content)
            written_files.append(file_path)

        return written_files

    def _generate_filename(self, workflow: Workflow) -> str:
        """Generate a filename from a workflow name.

        Converts the workflow name to a safe filename:
        - Converts to lowercase
        - Replaces spaces with hyphens
        - Removes special characters
        - Adds .yml extension

        Args:
            workflow: Workflow instance.

        Returns:
            Safe filename string ending in .yml.
        """
        name = workflow.name or "workflow"

        # Convert to lowercase and replace spaces with hyphens
        filename = name.lower().replace(" ", "-")

        # Remove special characters (keep only alphanumeric, hyphens, underscores)
        filename = re.sub(r"[^a-z0-9_-]", "", filename)

        # Remove consecutive hyphens
        filename = re.sub(r"-+", "-", filename)

        # Remove leading/trailing hyphens
        filename = filename.strip("-")

        # Ensure non-empty
        if not filename:
            filename = "workflow"

        return f"{filename}.yml"
