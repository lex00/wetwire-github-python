"""Template builder for dependency-ordered YAML output.

This module provides topological sorting and dependency ordering
for building workflow YAML with proper job sequencing.
"""

from .template import (
    CycleError,
    detect_cycles,
    order_jobs,
    topological_sort,
)

__all__ = [
    "CycleError",
    "detect_cycles",
    "order_jobs",
    "topological_sort",
]
