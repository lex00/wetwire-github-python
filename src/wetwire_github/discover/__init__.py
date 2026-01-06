"""AST-based resource discovery for wetwire-github.

This module provides Python AST-based discovery of Workflow and Job
definitions without requiring explicit registration.
"""

from .discover import (
    DiscoveredResource,
    build_dependency_graph,
    discover_in_directory,
    discover_in_file,
    validate_references,
)

__all__ = [
    "DiscoveredResource",
    "build_dependency_graph",
    "discover_in_directory",
    "discover_in_file",
    "validate_references",
]
