"""Graph command implementation.

Generates DAG visualization of workflow jobs.
"""

from pathlib import Path

from wetwire_github.discover import discover_in_directory
from wetwire_github.runner import extract_workflows


def graph_workflows(
    package_path: str,
    output_format: str = "mermaid",
    output_file: str | None = None,
) -> tuple[int, str]:
    """Generate dependency graph for workflows.

    Args:
        package_path: Path to package directory
        output_format: Output format ("mermaid" or "dot")
        output_file: Optional output file path

    Returns:
        Tuple of (exit_code, output_string)
    """
    path = Path(package_path)

    if not path.exists():
        return 1, f"Error: Path does not exist: {package_path}"

    # Discover workflow files
    discovered = discover_in_directory(str(path))
    workflow_files = {r.file_path for r in discovered if r.type == "Workflow"}

    if not workflow_files:
        return 1, "No workflows found"

    # Extract workflows and build dependency graph
    all_jobs: dict[str, dict[str, list[str]]] = {}  # workflow -> {job -> deps}

    for file_path in workflow_files:
        extracted = extract_workflows(file_path)
        for ext in extracted:
            workflow = ext.workflow
            workflow_name = workflow.name or ext.name

            job_deps: dict[str, list[str]] = {}
            for job_id, job in workflow.jobs.items():
                if job.needs:
                    if isinstance(job.needs, list):
                        job_deps[job_id] = list(job.needs)
                    else:
                        job_deps[job_id] = [job.needs]
                else:
                    job_deps[job_id] = []

            all_jobs[workflow_name] = job_deps

    # Generate output
    if output_format == "dot":
        output = _generate_dot(all_jobs)
    else:
        output = _generate_mermaid(all_jobs)

    # Write to file if specified
    if output_file:
        Path(output_file).write_text(output)
        return 0, f"Graph written to: {output_file}"

    return 0, output


def _generate_mermaid(workflows: dict[str, dict[str, list[str]]]) -> str:
    """Generate Mermaid flowchart diagram."""
    lines = ["graph TD"]

    for workflow_name, jobs in workflows.items():
        # Add subgraph for each workflow
        if len(workflows) > 1:
            safe_name = _sanitize_id(workflow_name)
            lines.append(f"    subgraph {safe_name}[{workflow_name}]")
            indent = "        "
        else:
            indent = "    "

        # Add nodes for jobs without dependencies first
        for job_id, deps in jobs.items():
            safe_job = _sanitize_id(job_id)
            if not deps:
                lines.append(f"{indent}{safe_job}[{job_id}]")

        # Add edges for dependencies
        for job_id, deps in jobs.items():
            safe_job = _sanitize_id(job_id)
            for dep in deps:
                safe_dep = _sanitize_id(dep)
                lines.append(f"{indent}{safe_dep} --> {safe_job}")

        if len(workflows) > 1:
            lines.append("    end")

    return "\n".join(lines)


def _generate_dot(workflows: dict[str, dict[str, list[str]]]) -> str:
    """Generate GraphViz DOT format."""
    lines = ["digraph G {"]
    lines.append("    rankdir=TB;")
    lines.append("    node [shape=box];")

    for workflow_name, jobs in workflows.items():
        # Add subgraph for each workflow
        if len(workflows) > 1:
            safe_name = _sanitize_id(workflow_name)
            lines.append(f'    subgraph cluster_{safe_name} {{')
            lines.append(f'        label="{workflow_name}";')
            indent = "        "
        else:
            indent = "    "

        # Add nodes
        for job_id in jobs:
            safe_job = _sanitize_id(job_id)
            lines.append(f'{indent}"{safe_job}" [label="{job_id}"];')

        # Add edges
        for job_id, deps in jobs.items():
            safe_job = _sanitize_id(job_id)
            for dep in deps:
                safe_dep = _sanitize_id(dep)
                lines.append(f'{indent}"{safe_dep}" -> "{safe_job}";')

        if len(workflows) > 1:
            lines.append("    }")

    lines.append("}")
    return "\n".join(lines)


def _sanitize_id(name: str) -> str:
    """Sanitize a name for use as graph node ID."""
    return name.replace("-", "_").replace(" ", "_")
