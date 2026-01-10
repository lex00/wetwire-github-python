"""Type-safe job output definitions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class JobOutput:
    """
    Represents a job-level output with optional documentation.

    The description field is for IDE/documentation support only and does not
    appear in the serialized YAML output.
    """

    value: str
    description: str | None = None
