"""Actionlint subprocess integration and reference validation for workflows.

This module validates GitHub workflow YAML using the actionlint tool and
provides reference validation for job dependencies, step IDs, and outputs.
"""

import re
import subprocess
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wetwire_github.workflow import Workflow

# Pattern to match steps.id.outputs.name references
_STEP_OUTPUT_PATTERN = re.compile(r"steps\.(\w+)\.outputs\.(\w+)")


@dataclass
class ValidationError:
    """A validation error from actionlint."""

    line: int
    column: int
    message: str
    severity: str = "error"
    rule: str | None = None


@dataclass
class ValidationResult:
    """Result of validating a workflow."""

    valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    actionlint_available: bool = True


@dataclass
class ReferenceError:
    """A reference validation error."""

    message: str
    job_id: str | None = None
    step_id: str | None = None
    reference: str | None = None


@dataclass
class ReferenceValidationResult:
    """Result of reference validation."""

    valid: bool
    errors: list[ReferenceError] = field(default_factory=list)


# Pattern to parse actionlint output
# Format: file:line:column: message [rule]
_ACTIONLINT_PATTERN = re.compile(
    r"^(?P<file>[^:]+):(?P<line>\d+):(?P<column>\d+): (?P<message>.+?)(?:\s+\[(?P<rule>[^\]]+)\])?$"
)


def is_actionlint_available() -> bool:
    """Check if actionlint is available in PATH.

    Returns:
        True if actionlint is installed and available
    """
    try:
        subprocess.run(
            ["actionlint", "--version"],
            capture_output=True,
            check=False,
        )
        return True
    except FileNotFoundError:
        return False


def _parse_actionlint_output(output: str) -> list[ValidationError]:
    """Parse actionlint output into ValidationError objects.

    Args:
        output: Raw stdout from actionlint

    Returns:
        List of parsed validation errors
    """
    errors = []

    for line in output.strip().split("\n"):
        if not line:
            continue

        match = _ACTIONLINT_PATTERN.match(line)
        if match:
            errors.append(
                ValidationError(
                    line=int(match.group("line")),
                    column=int(match.group("column")),
                    message=match.group("message").strip(),
                    severity="error",
                    rule=match.group("rule"),
                )
            )

    return errors


def validate_yaml(yaml_content: str) -> ValidationResult:
    """Validate YAML content using actionlint.

    Args:
        yaml_content: YAML content to validate

    Returns:
        ValidationResult with validation status and any errors
    """
    try:
        # actionlint can read from stdin with -
        result = subprocess.run(
            ["actionlint", "-"],
            input=yaml_content,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            return ValidationResult(valid=True, errors=[])

        errors = _parse_actionlint_output(result.stdout)
        return ValidationResult(valid=False, errors=errors)

    except FileNotFoundError:
        # actionlint not installed - return valid with flag
        return ValidationResult(
            valid=True,
            errors=[],
            actionlint_available=False,
        )


def validate_workflow(workflow: "Workflow") -> ValidationResult:
    """Validate a Workflow object using actionlint.

    Args:
        workflow: Workflow object to validate

    Returns:
        ValidationResult with validation status and any errors
    """
    from wetwire_github.serialize import to_yaml

    yaml_content = to_yaml(workflow)
    return validate_yaml(yaml_content)


def validate_job_dependencies(workflow: "Workflow") -> ReferenceValidationResult:
    """Validate that all job dependencies (needs) reference defined jobs.

    Args:
        workflow: Workflow object to validate

    Returns:
        ReferenceValidationResult with validation status and any errors
    """
    errors: list[ReferenceError] = []
    defined_jobs = set(workflow.jobs.keys())

    for job_id, job in workflow.jobs.items():
        if job.needs is None:
            continue

        # needs can be a list of job names
        needs_list = job.needs if isinstance(job.needs, list) else [job.needs]

        for needed_job in needs_list:
            # Convert to string in case it's a reference
            needed_job_str = str(needed_job)
            if needed_job_str not in defined_jobs:
                errors.append(
                    ReferenceError(
                        message=f"Job '{job_id}' depends on undefined job '{needed_job_str}'",
                        job_id=job_id,
                        reference=needed_job_str,
                    )
                )

    return ReferenceValidationResult(valid=len(errors) == 0, errors=errors)


def validate_step_ids(workflow: "Workflow") -> ReferenceValidationResult:
    """Validate that step IDs are unique within each job.

    Args:
        workflow: Workflow object to validate

    Returns:
        ReferenceValidationResult with validation status and any errors
    """
    errors: list[ReferenceError] = []

    for job_id, job in workflow.jobs.items():
        seen_ids: dict[str, int] = {}  # step_id -> first occurrence index

        for step_idx, step in enumerate(job.steps):
            if not step.id:
                continue

            if step.id in seen_ids:
                errors.append(
                    ReferenceError(
                        message=f"Duplicate step ID '{step.id}' in job '{job_id}'",
                        job_id=job_id,
                        step_id=step.id,
                    )
                )
            else:
                seen_ids[step.id] = step_idx

    return ReferenceValidationResult(valid=len(errors) == 0, errors=errors)


def _find_step_refs_in_string(text: str) -> list[str]:
    """Find all step ID references in a string.

    Args:
        text: String to search for step references

    Returns:
        List of step IDs referenced in the string
    """
    return [match.group(1) for match in _STEP_OUTPUT_PATTERN.finditer(text)]


def _find_step_refs_in_value(value: object) -> list[str]:
    """Find all step ID references in a value (string or dict).

    Args:
        value: Value to search (string, dict, or other)

    Returns:
        List of step IDs referenced in the value
    """
    refs: list[str] = []

    if isinstance(value, str):
        refs.extend(_find_step_refs_in_string(value))
    elif isinstance(value, dict):
        for v in value.values():
            refs.extend(_find_step_refs_in_value(v))

    return refs


def validate_step_outputs(workflow: "Workflow") -> ReferenceValidationResult:
    """Validate that step output references point to valid step IDs.

    Checks that:
    - Step output references point to existing step IDs
    - References don't point to steps defined after the current step (forward refs)

    Args:
        workflow: Workflow object to validate

    Returns:
        ReferenceValidationResult with validation status and any errors
    """
    errors: list[ReferenceError] = []

    for job_id, job in workflow.jobs.items():
        # Build map of step IDs to their indices
        step_id_indices: dict[str, int] = {}
        for step_idx, step in enumerate(job.steps):
            if step.id:
                step_id_indices[step.id] = step_idx

        # Check step references in each step
        for step_idx, step in enumerate(job.steps):
            # Valid step IDs are those defined before this step
            valid_step_ids = {
                sid for sid, idx in step_id_indices.items() if idx < step_idx
            }

            # Collect all step references from this step
            step_refs: list[str] = []

            # Check run command
            if step.run:
                step_refs.extend(_find_step_refs_in_string(step.run))

            # Check env
            if step.env:
                step_refs.extend(_find_step_refs_in_value(step.env))

            # Check if_ condition
            if step.if_:
                step_refs.extend(_find_step_refs_in_string(step.if_))

            # Check with_ (action inputs)
            if step.with_:
                step_refs.extend(_find_step_refs_in_value(step.with_))

            # Report invalid references
            for ref in step_refs:
                if ref not in valid_step_ids:
                    errors.append(
                        ReferenceError(
                            message=f"Reference to undefined or forward step ID '{ref}' in job '{job_id}'",
                            job_id=job_id,
                            reference=ref,
                        )
                    )

        # Check job outputs for step references
        all_step_ids = set(step_id_indices.keys())
        for output_name, output_value in job.outputs.items():
            output_refs = _find_step_refs_in_string(output_value)
            for ref in output_refs:
                if ref not in all_step_ids:
                    errors.append(
                        ReferenceError(
                            message=f"Job output '{output_name}' references undefined step ID '{ref}'",
                            job_id=job_id,
                            reference=ref,
                        )
                    )

    return ReferenceValidationResult(valid=len(errors) == 0, errors=errors)
