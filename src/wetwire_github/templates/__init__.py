"""Workflow templates for common CI/CD patterns.

This module provides pre-built workflow templates that can be
scaffolded into new projects.
"""

from .docker import docker_workflow
from .nodejs_ci import nodejs_ci_workflow
from .python_ci import python_ci_workflow
from .release import release_workflow

__all__ = [
    "python_ci_workflow",
    "nodejs_ci_workflow",
    "release_workflow",
    "docker_workflow",
]

# Template registry mapping CLI names to workflow functions
TEMPLATES = {
    "python-ci": python_ci_workflow,
    "nodejs-ci": nodejs_ci_workflow,
    "release": release_workflow,
    "docker": docker_workflow,
}
