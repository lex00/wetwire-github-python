"""Build command implementation.

Discovers workflows in Python packages and generates YAML/JSON output.
"""

import json
from pathlib import Path

from wetwire_github.discover import discover_in_directory
from wetwire_github.runner import extract_workflows
from wetwire_github.serialize import to_dict, to_yaml
from wetwire_github.template import order_jobs


def build_workflows(
    package_path: str,
    output_dir: str,
    output_format: str = "yaml",
) -> tuple[int, list[str]]:
    """Build workflows from a Python package.

    Args:
        package_path: Path to Python package containing workflow definitions
        output_dir: Directory to write output files
        output_format: Output format ("yaml" or "json")

    Returns:
        Tuple of (exit_code, list of generated file paths)
    """
    package = Path(package_path)
    output = Path(output_dir)

    # Check if package exists
    if not package.exists():
        return 1, [f"Error: Package path does not exist: {package_path}"]

    # Create output directory if needed
    output.mkdir(parents=True, exist_ok=True)

    # Discover workflow files using AST
    discovered = discover_in_directory(str(package))
    workflow_files = {r.file_path for r in discovered if r.type == "Workflow"}

    if not workflow_files:
        return 1, ["No workflows found in package"]

    # Extract actual workflow objects
    all_workflows = []
    for file_path in workflow_files:
        extracted = extract_workflows(file_path)
        all_workflows.extend(extracted)

    if not all_workflows:
        return 1, ["No workflows could be extracted"]

    # Generate output files
    generated_files = []
    for extracted in all_workflows:
        workflow = extracted.workflow

        # Order jobs by dependencies
        if workflow.jobs:
            ordered_jobs = order_jobs(workflow.jobs)
            # Rebuild jobs dict in ordered form
            workflow.jobs = {name: job for name, job in ordered_jobs}

        # Convert to dict
        workflow_dict = to_dict(workflow)

        # Determine output filename
        # Use workflow name (sanitized) or variable name as filename
        base_name = workflow.name or extracted.name
        safe_name = _sanitize_filename(base_name)

        if output_format == "json":
            output_file = output / f"{safe_name}.json"
            content = json.dumps(workflow_dict, indent=2)
        else:
            output_file = output / f"{safe_name}.yaml"
            content = to_yaml(workflow)

        output_file.write_text(content)
        generated_files.append(str(output_file))

    return 0, generated_files


def _sanitize_filename(name: str) -> str:
    """Convert a workflow name to a safe filename.

    Args:
        name: Workflow name (may contain spaces, special chars)

    Returns:
        Sanitized filename without extension
    """
    # Replace spaces and common separators with hyphens
    result = name.lower()
    result = result.replace(" ", "-")
    result = result.replace("_", "-")

    # Remove any non-alphanumeric characters except hyphens
    result = "".join(c for c in result if c.isalnum() or c == "-")

    # Collapse multiple hyphens
    while "--" in result:
        result = result.replace("--", "-")

    # Remove leading/trailing hyphens
    result = result.strip("-")

    return result or "workflow"
