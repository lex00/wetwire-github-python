"""Validate command implementation.

Validates workflow YAML files using actionlint.
"""

import json
from dataclasses import asdict
from pathlib import Path

from wetwire_github.cli.path_validation import PathValidationError, validate_path
from wetwire_github.validation import (
    ValidationResult,
    is_actionlint_available,
    validate_yaml,
)


def validate_files(
    file_paths: list[str],
    output_format: str = "text",
) -> tuple[int, str]:
    """Validate workflow YAML files.

    Args:
        file_paths: List of YAML file paths to validate
        output_format: Output format ("text" or "json")

    Returns:
        Tuple of (exit_code, output_string)
    """
    if not file_paths:
        if output_format == "json":
            return 0, json.dumps({"results": [], "valid": True})
        return 0, "No files to validate"

    # Validate all paths for security first
    validated_paths: list[Path] = []
    path_errors: list[tuple[str, str]] = []

    for file_path in file_paths:
        try:
            validated = validate_path(file_path, must_exist=False)
            validated_paths.append(validated)
        except PathValidationError as e:
            path_errors.append((file_path, str(e)))

    # If there are path validation errors, report them
    if path_errors:
        if output_format == "json":
            error_results = {
                path: {"valid": False, "errors": [{"message": f"Invalid path: {error}"}]}
                for path, error in path_errors
            }
            return 1, json.dumps({"valid": False, "results": error_results}, indent=2)
        else:
            lines = []
            for path, error in path_errors:
                lines.append(f"Error: Invalid path '{path}': {error}")
            return 1, "\n".join(lines)

    # Check if actionlint is available
    actionlint_available = is_actionlint_available()

    results: dict[str, ValidationResult] = {}
    all_valid = True

    for path in validated_paths:
        path_str = str(path)

        if not path.exists():
            results[path_str] = ValidationResult(
                valid=False,
                errors=[],
                actionlint_available=actionlint_available,
            )
            all_valid = False
            continue

        try:
            yaml_content = path.read_text()
        except (OSError, UnicodeDecodeError):
            results[path_str] = ValidationResult(
                valid=False,
                errors=[],
                actionlint_available=actionlint_available,
            )
            all_valid = False
            continue

        result = validate_yaml(yaml_content)
        results[path_str] = result

        if not result.valid:
            all_valid = False

    # Format output
    if output_format == "json":
        return _format_json(results, actionlint_available, all_valid)
    else:
        return _format_text(results, actionlint_available, all_valid)


def _format_json(
    results: dict[str, ValidationResult],
    actionlint_available: bool,
    all_valid: bool,
) -> tuple[int, str]:
    """Format validation results as JSON.

    Args:
        results: Dict mapping file path to validation result
        actionlint_available: Whether actionlint is available
        all_valid: Whether all files are valid

    Returns:
        Tuple of (exit_code, json_string)
    """
    results_dict: dict[str, dict] = {}
    for file_path, result in results.items():
        results_dict[file_path] = {
            "valid": result.valid,
            "errors": [asdict(e) for e in result.errors],
        }

    output = {
        "valid": all_valid,
        "actionlint_available": actionlint_available,
        "results": results_dict,
    }

    exit_code = 0 if all_valid else 1
    return exit_code, json.dumps(output, indent=2)


def _format_text(
    results: dict[str, ValidationResult],
    actionlint_available: bool,
    all_valid: bool,
) -> tuple[int, str]:
    """Format validation results as text.

    Args:
        results: Dict mapping file path to validation result
        actionlint_available: Whether actionlint is available
        all_valid: Whether all files are valid

    Returns:
        Tuple of (exit_code, text_string)
    """
    lines = []

    if not actionlint_available:
        lines.append("Warning: actionlint is not installed. Install it for full validation.")
        lines.append("")

    for file_path, result in results.items():
        if result.valid:
            lines.append(f"✓ {file_path}")
        else:
            lines.append(f"✗ {file_path}")
            for error in result.errors:
                location = f"{error.line}:{error.column}"
                rule_str = f" [{error.rule}]" if error.rule else ""
                lines.append(f"  {location}: {error.message}{rule_str}")

    if all_valid:
        if results:
            lines.append("")
            lines.append(f"All {len(results)} file(s) valid")
    else:
        error_count = sum(len(r.errors) for r in results.values())
        lines.append("")
        lines.append(f"Found {error_count} error(s)")

    exit_code = 0 if all_valid else 1
    return exit_code, "\n".join(lines)
