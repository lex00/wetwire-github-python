"""Lint command implementation.

Runs Python code quality rules for workflow declarations.
"""

import json
from dataclasses import asdict
from pathlib import Path

from wetwire_github.linter import LintResult, lint_directory, lint_file


def lint_package(
    package_path: str,
    output_format: str = "text",
    fix: bool = False,
) -> tuple[int, str]:
    """Lint Python workflow code in a package.

    Args:
        package_path: Path to package directory or Python file
        output_format: Output format ("text" or "json")
        fix: Whether to auto-fix issues (not yet implemented)

    Returns:
        Tuple of (exit_code, output_string)
    """
    path = Path(package_path)

    if not path.exists():
        error_msg = f"Error: Path does not exist: {package_path}"
        if output_format == "json":
            return 1, json.dumps({"error": error_msg, "results": []})
        return 1, error_msg

    # Lint file or directory
    if path.is_file():
        results = [lint_file(str(path))]
    else:
        results = lint_directory(str(path))

    if not results:
        if output_format == "json":
            return 0, json.dumps({"results": [], "total_errors": 0})
        return 0, "No Python files to lint"

    # Format output
    if output_format == "json":
        return _format_json(results)
    else:
        return _format_text(results, fix)


def _format_json(results: list[LintResult]) -> tuple[int, str]:
    """Format lint results as JSON.

    Args:
        results: List of lint results

    Returns:
        Tuple of (exit_code, json_string)
    """
    all_errors = []
    for result in results:
        for error in result.errors:
            all_errors.append({
                "file": result.file_path,
                "rule_id": error.rule_id,
                "message": error.message,
                "line": error.line,
                "column": error.column,
                "suggestion": error.suggestion,
            })

    output = {
        "results": [
            {
                "file": r.file_path,
                "errors": [asdict(e) for e in r.errors],
            }
            for r in results
        ],
        "total_errors": len(all_errors),
    }

    exit_code = 0 if len(all_errors) == 0 else 1
    return exit_code, json.dumps(output, indent=2)


def _format_text(results: list[LintResult], fix: bool) -> tuple[int, str]:
    """Format lint results as text.

    Args:
        results: List of lint results
        fix: Whether fix mode was requested

    Returns:
        Tuple of (exit_code, text_string)
    """
    lines = []
    total_errors = 0

    for result in results:
        if result.errors:
            for error in result.errors:
                location = f"{result.file_path}:{error.line}:{error.column}"
                lines.append(f"{error.rule_id} {location}: {error.message}")
                if error.suggestion:
                    lines.append(f"  Suggestion: {error.suggestion}")
                total_errors += 1

    if total_errors == 0:
        clean_count = len(results)
        lines.append(f"✓ {clean_count} file(s) checked, no issues found")
    else:
        lines.append("")
        lines.append(f"Found {total_errors} issue(s)")
        if fix:
            lines.append("Note: Auto-fix is not yet implemented")

    exit_code = 0 if total_errors == 0 else 1
    return exit_code, "\n".join(lines)
