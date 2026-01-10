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

    # Build workflow graph using the standalone graph module
    graph = WorkflowGraph()

    for file_path in workflow_files:
        extracted = extract_workflows(file_path)
        for ext in extracted:
            graph.add_workflow(ext.workflow, file_path=file_path)

    # Generate output using graph methods
    if output_format == "dot":
        output = graph.to_dot()
    else:
        output = graph.to_mermaid()

    # Write to file if specified
    if output_file:
        Path(output_file).write_text(output)
        return 0, f"Graph written to: {output_file}"

    return 0, output
