"""Workflow dataclass for workflow definitions."""

from dataclasses import dataclass, field
from typing import Any

from .job import Job
from .triggers import Triggers
from .types import Concurrency, Defaults, Permissions


@dataclass
class Workflow:
    """A GitHub Actions workflow."""

    name: str = ""
    on: Triggers = field(default_factory=Triggers)
    env: dict[str, Any] | None = None
    defaults: Defaults | None = None
    concurrency: Concurrency | None = None
    permissions: Permissions | None = None
    jobs: dict[str, Job] = field(default_factory=dict)
