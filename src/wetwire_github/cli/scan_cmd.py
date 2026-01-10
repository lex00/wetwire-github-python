"""Scan command implementation.

Runs security scans against discovered workflows.
"""

import json
from pathlib import Path

from wetwire_github.cli.path_validation import PathValidationError, validate_path
from wetwire_github.discover import DiscoveryCache, discover_in_directory
from wetwire_github.runner import extract_workflows
from wetwire_github.security import SecurityScanner, Severity


def run_scan(
    package_path: str,
    output_format: str = "text",
    no_cache: bool = False,
) -> tuple[int, str]:
    """Run security scans against workflows in a package.

    Args:
        package_path: Path to package directory containing workflow definitions
        output_format: Output format ("text", "json", or "table")
        no_cache: If True, bypass discovery cache

    Returns:
        Tuple of (exit_code, output_string)
        Exit code is 1 if critical or high severity issues found, 0 otherwise.
    """
    # Validate input path for security
    try:
        package = validate_path(package_path, must_exist=True)
    except PathValidationError as e:
        error_msg = f"Error: Invalid package path: {e}"
        if output_format == "json":
            return 1, json.dumps({"error": error_msg, "results": []})
        return 1, error_msg

    if not package.exists():
        error_msg = f"Error: Path does not exist: {package_path}"
        if output_format == "json":
            return 1, json.dumps({"error": error_msg, "results": []})
        return 1, error_msg

    # Initialize cache if not disabled
    cache = None if no_cache else DiscoveryCache()

    # Discover workflow files using AST
    discovered = discover_in_directory(str(package), cache=cache)
    workflow_files = {r.file_path for r in discovered if r.type == "Workflow"}

    if not workflow_files:
        msg = "No workflows found in package"
        if output_format == "json":
            return 0, json.dumps({"message": msg, "results": []})
        return 0, msg

    # Extract actual workflow objects
    all_workflows = []
    for file_path in workflow_files:
        try:
            extracted = extract_workflows(file_path)
            all_workflows.extend(extracted)
        except Exception:
            # Skip problematic files and continue with others
            pass

    if not all_workflows:
        msg = "No workflows could be extracted"
        if output_format == "json":
            return 0, json.dumps({"message": msg, "results": []})
        return 0, msg

    # Run security scanner
    scanner = SecurityScanner()

    # Collect results per workflow
    workflow_results: list[dict] = []
    has_critical_or_high = False

    for extracted in all_workflows:
        workflow = extracted.workflow
        workflow_name = workflow.name or extracted.name

        report = scanner.scan(workflow)

        # Check for critical or high severity issues
        if report.critical_count > 0 or report.high_count > 0:
            has_critical_or_high = True

        workflow_results.append({
            "workflow_name": workflow_name,
            "file_path": extracted.file_path,
            "report": report,
            "critical_count": report.critical_count,
            "high_count": report.high_count,
            "medium_count": report.medium_count,
            "low_count": report.low_count,
            "total_count": report.total_count,
        })

    # Format output
    if output_format == "json":
        return _format_json(workflow_results, has_critical_or_high)
    elif output_format == "table":
        return _format_table(workflow_results, has_critical_or_high)
    else:
        return _format_text(workflow_results, has_critical_or_high)


def _format_json(
    workflow_results: list[dict],
    has_critical_or_high: bool,
) -> tuple[int, str]:
    """Format scan results as JSON.

    Args:
        workflow_results: List of workflow result dictionaries
        has_critical_or_high: Whether any critical/high issues were found

    Returns:
        Tuple of (exit_code, json_string)
    """
    total_critical = sum(wr["critical_count"] for wr in workflow_results)
    total_high = sum(wr["high_count"] for wr in workflow_results)
    total_medium = sum(wr["medium_count"] for wr in workflow_results)
    total_low = sum(wr["low_count"] for wr in workflow_results)

    output = {
        "results": [
            {
                "workflow": wr["workflow_name"],
                "file": wr["file_path"],
                "critical_count": wr["critical_count"],
                "high_count": wr["high_count"],
                "medium_count": wr["medium_count"],
                "low_count": wr["low_count"],
                "issues": [
                    {
                        "title": issue.title,
                        "description": issue.description,
                        "severity": issue.severity.value,
                        "recommendation": issue.recommendation,
                        "location": issue.location,
                    }
                    for issue in wr["report"].issues
                ],
            }
            for wr in workflow_results
        ],
        "summary": {
            "total_workflows": len(workflow_results),
            "critical_count": total_critical,
            "high_count": total_high,
            "medium_count": total_medium,
            "low_count": total_low,
        },
        "critical_count": total_critical,
        "high_count": total_high,
    }

    exit_code = 1 if has_critical_or_high else 0
    return exit_code, json.dumps(output, indent=2)


def _format_text(
    workflow_results: list[dict],
    has_critical_or_high: bool,
) -> tuple[int, str]:
    """Format scan results as text.

    Args:
        workflow_results: List of workflow result dictionaries
        has_critical_or_high: Whether any critical/high issues were found

    Returns:
        Tuple of (exit_code, text_string)
    """
    lines = []

    for wr in workflow_results:
        workflow_name = wr["workflow_name"]
        file_path = Path(wr["file_path"]).name if wr["file_path"] else "unknown"

        lines.append(f"Workflow: {workflow_name} ({file_path})")
        lines.append("-" * 60)

        report = wr["report"]
        if report.issues:
            # Group issues by severity
            for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
                severity_issues = [i for i in report.issues if i.severity == severity]
                for issue in severity_issues:
                    lines.append(f"  [{severity.value.upper()}] {issue.title}")
                    lines.append(f"    {issue.description}")
                    lines.append(f"    Location: {issue.location}")
                    lines.append(f"    Recommendation: {issue.recommendation}")
                    lines.append("")
        else:
            lines.append("  No security issues found")

        lines.append(f"  Summary: CRITICAL={wr['critical_count']}, HIGH={wr['high_count']}, MEDIUM={wr['medium_count']}, LOW={wr['low_count']}")
        lines.append("")

    # Overall summary
    total_critical = sum(wr["critical_count"] for wr in workflow_results)
    total_high = sum(wr["high_count"] for wr in workflow_results)
    total_medium = sum(wr["medium_count"] for wr in workflow_results)
    total_low = sum(wr["low_count"] for wr in workflow_results)
    total_workflows = len(workflow_results)

    if total_critical == 0 and total_high == 0 and total_medium == 0 and total_low == 0:
        lines.append(f"Security scan passed: No issues found in {total_workflows} workflow(s)")
    else:
        lines.append(f"Security scan complete: {total_workflows} workflow(s) scanned")
        lines.append(f"  CRITICAL: {total_critical}, HIGH: {total_high}, MEDIUM: {total_medium}, LOW: {total_low}")
        if has_critical_or_high:
            lines.append("  Status: FAILED (critical or high severity issues found)")
        else:
            lines.append("  Status: PASSED (no critical or high severity issues)")

    exit_code = 1 if has_critical_or_high else 0
    return exit_code, "\n".join(lines)


def _format_table(
    workflow_results: list[dict],
    has_critical_or_high: bool,
) -> tuple[int, str]:
    """Format scan results as a table.

    Args:
        workflow_results: List of workflow result dictionaries
        has_critical_or_high: Whether any critical/high issues were found

    Returns:
        Tuple of (exit_code, text_string)
    """
    lines = []

    # Header
    lines.append(f"{'Workflow':<30} {'Severity':<12} {'Issue':<40} {'Location'}")
    lines.append("-" * 100)

    for wr in workflow_results:
        workflow_name = wr["workflow_name"][:28]
        report = wr["report"]
        first_row = True

        if report.issues:
            for issue in report.issues:
                severity = issue.severity.value.upper()
                title = issue.title[:38] if issue.title else ""
                location = issue.location[:20] if issue.location else ""

                if first_row:
                    lines.append(f"{workflow_name:<30} {severity:<12} {title:<40} {location}")
                    first_row = False
                else:
                    lines.append(f"{'':<30} {severity:<12} {title:<40} {location}")
        else:
            lines.append(f"{workflow_name:<30} {'OK':<12} {'No issues found':<40}")

        lines.append("")

    # Summary
    total_critical = sum(wr["critical_count"] for wr in workflow_results)
    total_high = sum(wr["high_count"] for wr in workflow_results)
    total_medium = sum(wr["medium_count"] for wr in workflow_results)
    total_low = sum(wr["low_count"] for wr in workflow_results)
    total_workflows = len(workflow_results)

    lines.append(f"Total: {total_workflows} workflow(s), CRITICAL={total_critical}, HIGH={total_high}, MEDIUM={total_medium}, LOW={total_low}")

    exit_code = 1 if has_critical_or_high else 0
    return exit_code, "\n".join(lines)
