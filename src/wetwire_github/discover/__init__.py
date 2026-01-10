"""AST-based resource discovery for wetwire-github.

This module provides Python AST-based discovery of Workflow and Job
definitions without requiring explicit registration.
"""

from .cache import DiscoveryCache
from .discover import (
    DiscoveredResource,
    DiscoveredReusableWorkflow,
    build_dependency_graph,
    discover_actions,
    discover_in_directory,
    discover_in_file,
    discover_reusable_workflows,
    validate_references,
)

__all__ = [
    "DiscoveredResource",
    "DiscoveredReusableWorkflow",
    "DiscoveryCache",
    "build_dependency_graph",
    "discover_actions",
    "discover_in_directory",
    "discover_in_file",
    "discover_reusable_workflows",
    "validate_references",
]
