"""Step output type for workflow definitions."""

from dataclasses import dataclass


@dataclass
class StepOutput:
    """Output definition for a step in a GitHub Actions workflow.

    Steps can define outputs that can be referenced by other steps in the same job
    or by the job itself (when the job declares outputs that reference step outputs).
    """

    description: str | None = None
    value: str | None = None
