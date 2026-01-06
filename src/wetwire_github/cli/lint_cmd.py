"""Lint command implementation.

Runs Python code quality rules for workflow declarations.
"""

import json
from dataclasses import asdict
from pathlib import Path

from wetwire_github.linter import (
    FixResult,
    Linter,
    LintResult,
    lint_directory,
    lint_file,
)


def lint_package(
    package_path: str,
    output_format: str = "text",
    fix: bool = False,
) -> tuple[int, str]:
    """Lint Python workflow code in a package.

    Args:
        package_path: Path to package directory or Python file
        output_format: Output format ("text" or "json")
        fix: Whether to auto-fix issues

    Returns:
        Tuple of (exit_code, output_string)
    """
    path = Path(package_path)

    if not path.exists():
        error_msg = f"Error: Path does not exist: {package_path}"
        if output_format == "json":
            return 1, json.dumps({"error": error_msg, "results": []})
        return 1, error_msg

    # Handle fix mode
    if fix:
        return _fix_package(path, output_format)

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
        return _format_text(results)


def _fix_package(path: Path, output_format: str) -> tuple[int, str]:
    """Apply auto-fixes to files in a package.

    Args:
        path: Path to file or directory
        output_format: Output format ("text" or "json")

    Returns:
        Tuple of (exit_code, output_string)
    """
    linter = Linter()
    fix_results: list[FixResult] = []
    files_modified = 0

    # Get list of files to process
    if path.is_file():
        files = [path]
    else:
        files = list(path.rglob("*.py"))
        # Exclude common directories
        files = [
            f
            for f in files
            if "__pycache__" not in f.parts and not any(p.startswith(".") for p in f.parts)
        ]

    for file_path in files:
        try:
            source = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        fix_result = linter.fix(source, str(file_path))

        if fix_result.fixed_count > 0:
            # Write fixed source back to file
            file_path.write_text(fix_result.source, encoding="utf-8")
            files_modified += 1

        fix_result.file_path = str(file_path)
        fix_results.append(fix_result)

    # Format output
    if output_format == "json":
        return _format_fix_json(fix_results)
    else:
        return _format_fix_text(fix_results, files_modified)


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


def _format_text(results: list[LintResult]) -> tuple[int, str]:
    """Format lint results as text.

    Args:
        results: List of lint results

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
        lines.append(f"All {clean_count} file(s) checked, no issues found")
    else:
        lines.append("")
        lines.append(f"Found {total_errors} issue(s)")

    exit_code = 0 if total_errors == 0 else 1
    return exit_code, "\n".join(lines)


def _format_fix_text(
    fix_results: list[FixResult], files_modified: int
) -> tuple[int, str]:
    """Format fix results as text.

    Args:
        fix_results: List of fix results
        files_modified: Number of files modified

    Returns:
        Tuple of (exit_code, text_string)
    """
    lines = []
    total_fixed = sum(r.fixed_count for r in fix_results)
    total_remaining = sum(len(r.remaining_errors) for r in fix_results)

    if total_fixed > 0:
        lines.append(f"Fixed {total_fixed} issue(s) in {files_modified} file(s)")

    if total_remaining > 0:
        lines.append("")
        lines.append(f"Remaining issues ({total_remaining}) that require manual fixing:")
        for result in fix_results:
            for error in result.remaining_errors:
                location = f"{result.file_path}:{error.line}:{error.column}"
                lines.append(f"  {error.rule_id} {location}: {error.message}")
                if error.suggestion:
                    lines.append(f"    Suggestion: {error.suggestion}")
    elif total_fixed == 0:
        lines.append("No issues to fix")

    exit_code = 0 if total_remaining == 0 else 1
    return exit_code, "\n".join(lines)


def _format_fix_json(fix_results: list[FixResult]) -> tuple[int, str]:
    """Format fix results as JSON.

    Args:
        fix_results: List of fix results

    Returns:
        Tuple of (exit_code, json_string)
    """
    total_fixed = sum(r.fixed_count for r in fix_results)
    total_remaining = sum(len(r.remaining_errors) for r in fix_results)

    output = {
        "fixed_count": total_fixed,
        "remaining_count": total_remaining,
        "results": [
            {
                "file": r.file_path,
                "fixed_count": r.fixed_count,
                "remaining_errors": [asdict(e) for e in r.remaining_errors],
            }
            for r in fix_results
        ],
    }

    exit_code = 0 if total_remaining == 0 else 1
    return exit_code, json.dumps(output, indent=2)
