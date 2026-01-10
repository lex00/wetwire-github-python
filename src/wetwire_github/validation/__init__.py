"""Actionlint-based validation and reference validation for GitHub workflows.

This module provides validation of generated YAML using the actionlint tool
and reference validation for job dependencies, step IDs, and outputs.
"""

from .validation import (
    ReferenceError,
    ReferenceValidationResult,
    ValidationError,
    ValidationResult,
    is_actionlint_available,
    validate_job_dependencies,
    validate_step_ids,
    validate_step_outputs,
    validate_workflow,
    validate_yaml,
)

__all__ = [
    "ReferenceError",
    "ReferenceValidationResult",
    "ValidationError",
    "ValidationResult",
    "is_actionlint_available",
    "validate_job_dependencies",
    "validate_step_ids",
    "validate_step_outputs",
    "validate_workflow",
    "validate_yaml",
]
