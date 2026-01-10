"""Composite action types.

Dataclasses for composite GitHub Actions definitions.
Based on the GitHub composite action schema.
"""

from dataclasses import dataclass

from wetwire_github.workflow.step import Step


@dataclass
class ActionInput:
    """Input definition for a composite action.

    Attributes:
        description: Description of the input
        required: Whether the input is required (omit or set to None for false)
        default: Default value for the input
    """

    description: str
    required: bool | None = None
    default: str | None = None


@dataclass
class ActionOutput:
    """Output definition for a composite action.

    Attributes:
        description: Description of the output
        value: Expression that defines the output value
    """

    description: str
    value: str


@dataclass
class CompositeRuns:
    """Runs configuration for a composite action.

    Attributes:
        using: The runner to use (always 'composite' for composite actions)
        steps: List of steps to run
    """

    steps: list[Step]
    using: str = "composite"


@dataclass
class CompositeAction:
    """Composite GitHub Action definition.

    Attributes:
        name: Name of the action
        description: Description of what the action does
        inputs: Dictionary of input definitions (optional)
        outputs: Dictionary of output definitions (optional)
        runs: Runs configuration with steps
    """

    name: str
    description: str
    runs: CompositeRuns
    inputs: dict[str, ActionInput] | None = None
    outputs: dict[str, ActionOutput] | None = None
