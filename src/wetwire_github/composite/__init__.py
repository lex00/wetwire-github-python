"""Composite action types.

Type-safe declarations for composite GitHub Actions.
"""

from wetwire_github.composite.types import (
    ActionInput,
    ActionOutput,
    CompositeAction,
    CompositeRuns,
)
from wetwire_github.composite.write import write_action

__all__ = [
    "ActionInput",
    "ActionOutput",
    "CompositeAction",
    "CompositeRuns",
    "write_action",
]
