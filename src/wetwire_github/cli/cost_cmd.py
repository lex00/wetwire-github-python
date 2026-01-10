"""Cost command implementation.

Analyzes workflow costs using the CostCalculator.
"""

import json
from pathlib import Path

from wetwire_github.cli.path_validation import PathValidationError, validate_path
from wetwire_github.cost import CostCalculator, CostEstimate
from wetwire_github.discover import DiscoveryCache, discover_in_directory
from wetwire_github.runner import extract_workflows


def analyze_costs(
    package_path: str,
    output_format: str = "text",
    no_cache: bool = False,
) -> tuple[int, str]:
    """Analyze workflow costs in a package.

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
            return 1, json.dumps({"error": error_msg, "workflows": []})
        return 1, error_msg

    if not package.exists():
        error_msg = f"Error: Path does not exist: {package_path}"
        if output_format == "json":
            return 1, json.dumps({"error": error_msg, "workflows": []})
        return 1, error_msg

    # Initialize cache if not disabled
    cache = None if no_cache else DiscoveryCache()

    # Discover workflow files using AST
    discovered = discover_in_directory(str(package), cache=cache)
    workflow_files = {r.file_path for r in discovered if r.type == "Workflow"}

    if not workflow_files:
        msg = "No workflows found in package"
        if output_format == "json":
            return 1, json.dumps({"error": msg, "workflows": []})
        return 1, msg

    # Extract actual workflow objects
    all_workflows = []
    for file_path in workflow_files:
        try:
            extracted = extract_workflows(file_path)
            all_workflows.extend(extracted)
        except Exception:
            # Skip problematic files
            pass

    if not all_workflows:
        msg = "No workflows could be extracted"
        if output_format == "json":
            return 1, json.dumps({"error": msg, "workflows": []})
        return 1, msg

    # Calculate costs
    calculator = CostCalculator()

    workflow_costs: list[dict] = []
    total_cost = 0.0
    total_linux_minutes = 0.0
    total_windows_minutes = 0.0
    total_macos_minutes = 0.0

    for extracted in all_workflows:
        workflow = extracted.workflow
        workflow_name = workflow.name or extracted.name

        estimate = calculator.estimate(workflow)

        workflow_costs.append({
            "workflow_name": workflow_name,
            "file_path": extracted.file_path,
            "estimate": estimate,
        })

        total_cost += estimate.total_cost
        total_linux_minutes += estimate.linux_minutes
        total_windows_minutes += estimate.windows_minutes
        total_macos_minutes += estimate.macos_minutes

    # Format output
    if output_format == "json":
        return _format_json(
            workflow_costs,
            total_cost,
            total_linux_minutes,
            total_windows_minutes,
            total_macos_minutes,
        )
    elif output_format == "table":
        return _format_table(
            workflow_costs,
            total_cost,
            total_linux_minutes,
            total_windows_minutes,
            total_macos_minutes,
        )
    else:
        return _format_text(
            workflow_costs,
            total_cost,
            total_linux_minutes,
            total_windows_minutes,
            total_macos_minutes,
        )


def _format_json(
    workflow_costs: list[dict],
    total_cost: float,
    total_linux_minutes: float,
    total_windows_minutes: float,
    total_macos_minutes: float,
) -> tuple[int, str]:
    """Format cost results as JSON.

    Args:
        workflow_costs: List of workflow cost dictionaries
        total_cost: Total cost across all workflows
        total_linux_minutes: Total Linux minutes
        total_windows_minutes: Total Windows minutes
        total_macos_minutes: Total macOS minutes

    Returns:
        Tuple of (exit_code, json_string)
    """
    output = {
        "workflows": [
            {
                "workflow": wc["workflow_name"],
                "file": wc["file_path"],
                "total_cost": round(wc["estimate"].total_cost, 4),
                "linux_minutes": wc["estimate"].linux_minutes,
                "windows_minutes": wc["estimate"].windows_minutes,
                "macos_minutes": wc["estimate"].macos_minutes,
                "job_estimates": {
                    job: round(cost, 4)
                    for job, cost in wc["estimate"].job_estimates.items()
                },
            }
            for wc in workflow_costs
        ],
        "summary": {
            "total_cost": round(total_cost, 4),
            "total_linux_minutes": total_linux_minutes,
            "total_windows_minutes": total_windows_minutes,
            "total_macos_minutes": total_macos_minutes,
            "workflow_count": len(workflow_costs),
        },
    }

    return 0, json.dumps(output, indent=2)


def _format_text(
    workflow_costs: list[dict],
    total_cost: float,
    total_linux_minutes: float,
    total_windows_minutes: float,
    total_macos_minutes: float,
) -> tuple[int, str]:
    """Format cost results as text.

    Args:
        workflow_costs: List of workflow cost dictionaries
        total_cost: Total cost across all workflows
        total_linux_minutes: Total Linux minutes
        total_windows_minutes: Total Windows minutes
        total_macos_minutes: Total macOS minutes

    Returns:
        Tuple of (exit_code, text_string)
    """
    lines = []

    for wc in workflow_costs:
        workflow_name = wc["workflow_name"]
        file_path = Path(wc["file_path"]).name if wc["file_path"] else "unknown"
        estimate: CostEstimate = wc["estimate"]

        lines.append(f"Workflow: {workflow_name} ({file_path})")
        lines.append("-" * 60)
        lines.append(f"  Estimated cost: ${estimate.total_cost:.4f}")
        lines.append("")
        lines.append("  Runner minutes:")
        if estimate.linux_minutes > 0:
            lines.append(f"    Linux:   {estimate.linux_minutes:.1f} min")
        if estimate.windows_minutes > 0:
            lines.append(f"    Windows: {estimate.windows_minutes:.1f} min")
        if estimate.macos_minutes > 0:
            lines.append(f"    macOS:   {estimate.macos_minutes:.1f} min")

        if estimate.job_estimates:
            lines.append("")
            lines.append("  Per-job breakdown:")
            for job_name, job_cost in estimate.job_estimates.items():
                lines.append(f"    {job_name}: ${job_cost:.4f}")

        lines.append("")

    # Overall summary
    lines.append("=" * 60)
    lines.append("Summary")
    lines.append("=" * 60)
    lines.append(f"  Total workflows: {len(workflow_costs)}")
    lines.append(f"  Total estimated cost: ${total_cost:.4f}")
    lines.append("")
    lines.append("  Total runner minutes:")
    lines.append(f"    Linux:   {total_linux_minutes:.1f} min")
    lines.append(f"    Windows: {total_windows_minutes:.1f} min")
    lines.append(f"    macOS:   {total_macos_minutes:.1f} min")

    return 0, "\n".join(lines)


def _format_table(
    workflow_costs: list[dict],
    total_cost: float,
    total_linux_minutes: float,
    total_windows_minutes: float,
    total_macos_minutes: float,
) -> tuple[int, str]:
    """Format cost results as a table.

    Args:
        workflow_costs: List of workflow cost dictionaries
        total_cost: Total cost across all workflows
        total_linux_minutes: Total Linux minutes
        total_windows_minutes: Total Windows minutes
        total_macos_minutes: Total macOS minutes

    Returns:
        Tuple of (exit_code, text_string)
    """
    lines = []

    # Header for workflows
    lines.append(f"{'Workflow':<30} {'Cost':<12} {'Linux':<10} {'Windows':<10} {'macOS':<10}")
    lines.append("-" * 75)

    for wc in workflow_costs:
        workflow_name = wc["workflow_name"][:28]
        estimate: CostEstimate = wc["estimate"]

        cost_str = f"${estimate.total_cost:.4f}"
        linux_str = f"{estimate.linux_minutes:.1f}m"
        windows_str = f"{estimate.windows_minutes:.1f}m"
        macos_str = f"{estimate.macos_minutes:.1f}m"

        lines.append(f"{workflow_name:<30} {cost_str:<12} {linux_str:<10} {windows_str:<10} {macos_str:<10}")

    lines.append("-" * 75)

    # Total row
    total_str = f"${total_cost:.4f}"
    linux_total = f"{total_linux_minutes:.1f}m"
    windows_total = f"{total_windows_minutes:.1f}m"
    macos_total = f"{total_macos_minutes:.1f}m"
    lines.append(f"{'TOTAL':<30} {total_str:<12} {linux_total:<10} {windows_total:<10} {macos_total:<10}")

    lines.append("")

    # Per-job breakdown table
    lines.append("")
    lines.append("Per-Job Breakdown:")
    lines.append(f"{'Workflow':<25} {'Job':<25} {'Cost':<12}")
    lines.append("-" * 65)

    for wc in workflow_costs:
        workflow_name = wc["workflow_name"][:23]
        estimate: CostEstimate = wc["estimate"]
        first_job = True

        for job_name, job_cost in estimate.job_estimates.items():
            job_str = job_name[:23]
            cost_str = f"${job_cost:.4f}"

            if first_job:
                lines.append(f"{workflow_name:<25} {job_str:<25} {cost_str:<12}")
                first_job = False
            else:
                lines.append(f"{'':<25} {job_str:<25} {cost_str:<12}")

    return 0, "\n".join(lines)
