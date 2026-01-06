"""Matrix and Strategy dataclasses for workflow definitions."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Matrix:
    """Matrix configuration for parallel job execution."""

    values: dict[str, list[Any]] = field(default_factory=dict)
    include: list[dict[str, Any]] | None = None
    exclude: list[dict[str, Any]] | None = None


@dataclass
class Strategy:
    """Strategy configuration for a job."""

    matrix: Matrix | None = None
    fail_fast: bool | None = None
    max_parallel: int | None = None
