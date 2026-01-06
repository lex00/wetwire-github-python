"""Validate command implementation.

Validates workflow YAML files using actionlint.
"""

import json
from dataclasses import asdict
from pathlib import Path

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

    # Check if actionlint is available
    actionlint_available = is_actionlint_available()

    results: dict[str, ValidationResult] = {}
    all_valid = True

    for file_path in file_paths:
        path = Path(file_path)

        if not path.exists():
            results[file_path] = ValidationResult(
                valid=False,
                errors=[],
                actionlint_available=actionlint_available,
            )
            all_valid = False
            continue

        try:
            yaml_content = path.read_text()
        except (OSError, UnicodeDecodeError):
            results[file_path] = ValidationResult(
                valid=False,
                errors=[],
                actionlint_available=actionlint_available,
            )
            all_valid = False
            continue

        result = validate_yaml(yaml_content)
        results[file_path] = result

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
