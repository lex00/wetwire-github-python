"""Workflow template types for GitHub organization-level templates.

Type-safe declarations for organization workflow templates.
"""

from wetwire_github.workflow_templates.types import (
    TemplateCategory,
    TemplateConfig,
    WorkflowTemplate,
)

__all__ = [
    "WorkflowTemplate",
    "TemplateConfig",
    "TemplateCategory",
]
