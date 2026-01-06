"""List command implementation.

Lists discovered workflows and jobs from Python packages.
"""

import json
from pathlib import Path

from wetwire_github.discover import DiscoveredResource, discover_in_directory


def list_resources(
    package_path: str,
    output_format: str = "table",
) -> tuple[int, str]:
    """List discovered workflows and jobs.

    Args:
        package_path: Path to package directory
        output_format: Output format ("table" or "json")

    Returns:
        Tuple of (exit_code, output_string)
    """
    path = Path(package_path)

    if not path.exists():
        error_msg = f"Error: Path does not exist: {package_path}"
        if output_format == "json":
            return 1, json.dumps({"error": error_msg})
        return 1, error_msg

    # Discover resources
    resources = discover_in_directory(str(path))

    # Separate by type
    workflows = [r for r in resources if r.type == "Workflow"]
    jobs = [r for r in resources if r.type == "Job"]

    # Format output
    if output_format == "json":
        return _format_json(workflows, jobs)
    else:
        return _format_table(workflows, jobs)


def _format_json(
    workflows: list[DiscoveredResource],
    jobs: list[DiscoveredResource],
) -> tuple[int, str]:
    """Format resources as JSON."""
    output = {
        "workflows": [
            {
                "name": w.name,
                "file": w.file_path,
                "line": w.line_number,
                "module": w.module,
            }
            for w in workflows
        ],
        "jobs": [
            {
                "name": j.name,
                "file": j.file_path,
                "line": j.line_number,
                "module": j.module,
            }
            for j in jobs
        ],
        "summary": {
            "total_workflows": len(workflows),
            "total_jobs": len(jobs),
        },
    }
    return 0, json.dumps(output, indent=2)


def _format_table(
    workflows: list[DiscoveredResource],
    jobs: list[DiscoveredResource],
) -> tuple[int, str]:
    """Format resources as text table."""
    lines = []

    if workflows:
        lines.append("Workflows:")
        lines.append("-" * 60)
        for w in workflows:
            rel_path = Path(w.file_path).name
            lines.append(f"  {w.name:20} {rel_path}:{w.line_number}")
        lines.append("")

    if jobs:
        lines.append("Jobs:")
        lines.append("-" * 60)
        for j in jobs:
            rel_path = Path(j.file_path).name
            lines.append(f"  {j.name:20} {rel_path}:{j.line_number}")
        lines.append("")

    if not workflows and not jobs:
        lines.append("No workflows or jobs found")

    # Summary
    lines.append(f"Found {len(workflows)} workflow(s) and {len(jobs)} job(s)")

    return 0, "\n".join(lines)
