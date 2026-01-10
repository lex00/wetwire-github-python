"""Policy command implementation.

Runs policy checks against discovered workflows.
"""

import json
from pathlib import Path

from wetwire_github.cli.path_validation import PathValidationError, validate_path
from wetwire_github.discover import DiscoveryCache, discover_in_directory
from wetwire_github.policy import (
    LimitJobCount,
    NoHardcodedSecrets,
    PinActions,
    Policy,
    PolicyEngine,
    RequireCheckout,
    RequireTimeouts,
)
from wetwire_github.runner import extract_workflows


def get_default_policies() -> list[Policy]:
    """Get the list of default built-in policies.

    Returns:
        List of Policy instances
    """
    return [
        RequireCheckout(),
        RequireTimeouts(),
        NoHardcodedSecrets(),
        PinActions(),
        LimitJobCount(max_jobs=10),
    ]


def run_policies(
    package_path: str,
    output_format: str = "text",
    no_cache: bool = False,
) -> tuple[int, str]:
    """Run policies against workflows in a package.

    Args:
        package_path: Path to package directory containing workflow definitions
        output_format: Output format ("text", "json", or "table")
        no_cache: If True, bypass discovery cache

    Returns:
        Tuple of (exit_code, output_string)
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
            return 1, json.dumps({"error": msg, "results": []})
        return 1, msg

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
            return 1, json.dumps({"error": msg, "results": []})
        return 1, msg

    # Run policies
    policies = get_default_policies()
    engine = PolicyEngine(policies=policies)

    # Collect results per workflow
    workflow_results: list[dict] = []
    any_failures = False

    for extracted in all_workflows:
        workflow = extracted.workflow
        workflow_name = workflow.name or extracted.name

        results = engine.evaluate(workflow)
        passed_count = sum(1 for r in results if r.passed)
        failed_count = len(results) - passed_count

        if failed_count > 0:
            any_failures = True

        workflow_results.append({
            "workflow_name": workflow_name,
            "file_path": extracted.file_path,
            "results": results,
            "passed_count": passed_count,
            "failed_count": failed_count,
        })

    # Format output
    if output_format == "json":
        return _format_json(workflow_results, any_failures)
    elif output_format == "table":
        return _format_table(workflow_results, any_failures)
    else:
        return _format_text(workflow_results, any_failures)


def _format_json(
    workflow_results: list[dict],
    any_failures: bool,
) -> tuple[int, str]:
    """Format policy results as JSON.

    Args:
        workflow_results: List of workflow result dictionaries
        any_failures: Whether any policies failed

    Returns:
        Tuple of (exit_code, json_string)
    """
    output = {
        "results": [
            {
                "workflow": wr["workflow_name"],
                "file": wr["file_path"],
                "passed_count": wr["passed_count"],
                "failed_count": wr["failed_count"],
                "policies": [
                    {
                        "policy_name": r.policy_name,
                        "passed": r.passed,
                        "message": r.message,
                    }
                    for r in wr["results"]
                ],
            }
            for wr in workflow_results
        ],
        "total_workflows": len(workflow_results),
        "total_failures": sum(wr["failed_count"] for wr in workflow_results),
    }

    exit_code = 1 if any_failures else 0
    return exit_code, json.dumps(output, indent=2)


def _format_text(
    workflow_results: list[dict],
    any_failures: bool,
) -> tuple[int, str]:
    """Format policy results as text.

    Args:
        workflow_results: List of workflow result dictionaries
        any_failures: Whether any policies failed

    Returns:
        Tuple of (exit_code, text_string)
    """
    lines = []

    for wr in workflow_results:
        workflow_name = wr["workflow_name"]
        file_path = Path(wr["file_path"]).name if wr["file_path"] else "unknown"

        lines.append(f"Workflow: {workflow_name} ({file_path})")
        lines.append("-" * 60)

        for result in wr["results"]:
            status = "PASS" if result.passed else "FAIL"
            lines.append(f"  [{status}] {result.policy_name}: {result.message}")

        lines.append(f"  Summary: {wr['passed_count']} passed, {wr['failed_count']} failed")
        lines.append("")

    # Overall summary
    total_workflows = len(workflow_results)
    total_failures = sum(wr["failed_count"] for wr in workflow_results)

    if total_failures == 0:
        lines.append(f"All policies passed for {total_workflows} workflow(s)")
    else:
        lines.append(f"Policy check failed: {total_failures} failure(s) across {total_workflows} workflow(s)")

    exit_code = 1 if any_failures else 0
    return exit_code, "\n".join(lines)


def _format_table(
    workflow_results: list[dict],
    any_failures: bool,
) -> tuple[int, str]:
    """Format policy results as a table.

    Args:
        workflow_results: List of workflow result dictionaries
        any_failures: Whether any policies failed

    Returns:
        Tuple of (exit_code, text_string)
    """
    lines = []

    # Header
    lines.append(f"{'Workflow':<30} {'Policy':<25} {'Status':<8} {'Message'}")
    lines.append("-" * 100)

    for wr in workflow_results:
        workflow_name = wr["workflow_name"][:28]
        first_row = True

        for result in wr["results"]:
            status = "PASS" if result.passed else "FAIL"
            message = result.message[:40] if result.message else ""

            if first_row:
                lines.append(f"{workflow_name:<30} {result.policy_name:<25} {status:<8} {message}")
                first_row = False
            else:
                lines.append(f"{'':<30} {result.policy_name:<25} {status:<8} {message}")

        lines.append("")

    # Summary
    total_workflows = len(workflow_results)
    total_passed = sum(wr["passed_count"] for wr in workflow_results)
    total_failed = sum(wr["failed_count"] for wr in workflow_results)

    lines.append(f"Total: {total_workflows} workflow(s), {total_passed} passed, {total_failed} failed")

    exit_code = 1 if any_failures else 0
    return exit_code, "\n".join(lines)
