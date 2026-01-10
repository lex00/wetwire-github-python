"""Job dataclass for workflow definitions."""

from dataclasses import dataclass, field
from typing import Any

from .job_output import JobOutput
from .matrix import Strategy
from .runner import SelfHostedRunner
from .step import Step
from .types import Concurrency, Container, Environment, Permissions, Service


@dataclass
class Job:
    """A job in a GitHub Actions workflow."""

    name: str = ""
    runs_on: str | list[str] | SelfHostedRunner = "ubuntu-latest"
    needs: list[Any] | None = None  # List of Job references
    if_: str | None = None
    environment: Environment | None = None
    concurrency: Concurrency | None = None
    strategy: Strategy | None = None
    container: Container | None = None
    services: dict[str, Service] | None = None
    steps: list[Step] = field(default_factory=list)
    timeout_minutes: int | None = None
    outputs: dict[str, str | JobOutput] = field(default_factory=dict)
    permissions: Permissions | None = None
    env: dict[str, Any] | None = None
    defaults: Any | None = None  # Defaults type
