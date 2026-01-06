"""Actionlint subprocess integration for workflow validation.

This module validates GitHub workflow YAML using the actionlint tool.
"""

import re
import subprocess
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wetwire_github.workflow import Workflow


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
