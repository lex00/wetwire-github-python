"""Graph command implementation.

Generates DAG visualization of workflow jobs.
"""

from pathlib import Path

from wetwire_github.discover import discover_in_directory
from wetwire_github.graph import WorkflowGraph
from wetwire_github.runner import extract_workflows


def graph_workflows(
    package_path: str,
    output_format: str = "mermaid",
    output_file: str | None = None,
    filter_pattern: str | None = None,
    exclude_pattern: str | None = None,
    show_legend: bool = False,
) -> tuple[int, str]:
    """Generate dependency graph for workflows.

    Args:
        package_path: Path to package directory
        output_format: Output format ("mermaid" or "dot")
        output_file: Optional output file path
        filter_pattern: Optional glob pattern to filter jobs
        exclude_pattern: Optional glob pattern to exclude jobs
        show_legend: Whether to include a legend

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

    # Build workflow graph using the standalone graph module
    graph = WorkflowGraph()

    for file_path in workflow_files:
        extracted = extract_workflows(file_path)
        for ext in extracted:
            graph.add_workflow(ext.workflow, file_path=file_path)

    # Generate output using graph methods
    if output_format == "dot":
        output = graph.to_dot(filter_pattern=filter_pattern, exclude_pattern=exclude_pattern)
    else:
        output = graph.to_mermaid(filter_pattern=filter_pattern, exclude_pattern=exclude_pattern)

    # Add legend if requested
    if show_legend:
        legend = graph.generate_legend(format=output_format)
        output = output + legend

    # Write to file if specified
    if output_file:
        Path(output_file).write_text(output)
        return 0, f"Graph written to: {output_file}"

    return 0, output
