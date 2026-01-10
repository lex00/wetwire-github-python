"""Step dataclass for workflow definitions."""

from dataclasses import dataclass
from typing import Any

from .step_output import StepOutput


@dataclass
class Step:
    """A step in a GitHub Actions job."""

    id: str = ""
    name: str = ""
    if_: str | None = None
    uses: str = ""
    with_: dict[str, Any] | None = None
    run: str = ""
    shell: str = ""
    env: dict[str, Any] | None = None
    working_directory: str = ""
    continue_on_error: bool | None = None
    timeout_minutes: int | None = None
    outputs: dict[str, StepOutput] | None = None
