"""Scaffold command for generating workflow templates."""

from pathlib import Path

from wetwire_github.templates import TEMPLATES
from wetwire_github.workflow import Workflow


def get_available_templates() -> list[str]:
    """Get list of available template names.

    Returns:
        List of template names that can be scaffolded.
    """
    return list(TEMPLATES.keys())


def scaffold_workflow(template: str) -> Workflow:
    """Create a Workflow from a template.

    Args:
        template: Name of the template to use.

    Returns:
        Workflow object configured from the template.

    Raises:
        ValueError: If template name is not recognized.
    """
    if template not in TEMPLATES:
        available = ", ".join(get_available_templates())
        raise ValueError(
            f"Unknown template: {template}. Available templates: {available}"
        )

    return TEMPLATES[template]()


def _generate_workflow_code(workflow: Workflow, template: str) -> str:
    """Generate Python code for a workflow.

    Args:
        workflow: The Workflow object to generate code for.
        template: Template name used to generate the workflow.

    Returns:
        Python source code string.
    """
    # Map templates to their import paths
    template_to_import = {
        "python-ci": "python_ci_workflow",
        "nodejs-ci": "nodejs_ci_workflow",
        "release": "release_workflow",
        "docker": "docker_workflow",
    }

    func_name = template_to_import.get(template, "workflow")

    # Generate code that uses the template function
    code = f'''"""Generated workflow using {template} template.

This file was scaffolded by wetwire-github.
Customize as needed for your project.
"""

from wetwire_github.templates import {func_name}

# Create the workflow from template
{template.replace("-", "_")} = {func_name}()

# Export for wetwire-github build to discover
__all__ = ["{template.replace("-", "_")}"]
'''
    return code


def scaffold_to_file(
    template: str,
    output: str,
) -> tuple[int, list[str]]:
    """Scaffold a workflow template to a file.

    Args:
        template: Name of the template to use.
        output: Path to output file.

    Returns:
        Tuple of (exit_code, messages).
    """
    messages: list[str] = []

    try:
        workflow = scaffold_workflow(template)
    except ValueError as e:
        return 1, [str(e)]

    code = _generate_workflow_code(workflow, template)

    output_path = Path(output)

    # Create parent directories if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the file
    output_path.write_text(code)
    messages.append(f"Created {output_path}")
    messages.append(f"Workflow: {workflow.name}")

    return 0, messages


def list_templates() -> tuple[int, str]:
    """List available templates.

    Returns:
        Tuple of (exit_code, output_text).
    """
    lines = ["Available templates:", ""]
    for name in get_available_templates():
        workflow = TEMPLATES[name]()
        lines.append(f"  {name:<15} - {workflow.name}")
    lines.append("")
    lines.append("Usage: wetwire-github scaffold --template <name> --output <file>")
    return 0, "\n".join(lines)
