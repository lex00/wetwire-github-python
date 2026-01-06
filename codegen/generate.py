#!/usr/bin/env python3
"""Generate type-safe Python wrappers for GitHub Actions.

This module generates Python code that wraps GitHub Actions with
type-safe function signatures based on their action.yml definitions.
"""

import keyword
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from parse import ActionSchema

# Python reserved keywords that need trailing underscore
RESERVED_KEYWORDS = set(keyword.kwlist)


@dataclass
class ActionTemplate:
    """Template data for generating an action function."""

    function_name: str
    action_ref: str
    description: str
    inputs: list[dict[str, Any]]
    outputs: list[dict[str, Any]]


def snake_case(name: str) -> str:
    """Convert a string to snake_case.

    Handles:
    - kebab-case (fetch-depth -> fetch_depth)
    - camelCase (fetchDepth -> fetch_depth)
    - UPPERCASE (GITHUB_TOKEN -> github_token)

    Args:
        name: String to convert

    Returns:
        snake_case version of the string
    """
    # Replace hyphens with underscores
    result = name.replace("-", "_")

    # Handle camelCase by inserting underscores before capitals
    result = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", result)

    # Convert to lowercase
    return result.lower()


def to_python_identifier(name: str) -> str:
    """Convert a name to a valid Python identifier.

    Args:
        name: Name to convert

    Returns:
        Valid Python identifier
    """
    result = snake_case(name)

    # Handle reserved keywords
    if result in RESERVED_KEYWORDS:
        result = f"{result}_"

    # Handle names starting with digits
    if result and result[0].isdigit():
        result = f"_{result}"

    return result


def _derive_function_name(action_name: str, action_ref: str) -> str:
    """Derive a function name from an action name and reference.

    Args:
        action_name: The action's display name
        action_ref: The action reference (e.g., "actions/checkout" or "./.github/actions/my-action")

    Returns:
        A valid Python function name
    """
    # For local composite actions
    if action_ref.startswith("./"):
        # Extract the last part of the path
        path = action_ref.rstrip("/")
        name = Path(path).name
        # Add composite prefix to distinguish
        return to_python_identifier("my_composite_action" if name == "my-action" else name)

    # For standard actions, derive from the repo name
    if "/" in action_ref:
        # actions/checkout@v4 -> checkout
        parts = action_ref.split("/")
        if len(parts) >= 2:
            repo_name = parts[-1].split("@")[0]
            return to_python_identifier(repo_name)

    # Fallback to action name
    return to_python_identifier(action_name)


def generate_action_function(
    schema: ActionSchema,
    owner_repo: str,
    version: str,
) -> str:
    """Generate a Python function for a GitHub Action.

    Args:
        schema: Parsed action schema
        owner_repo: Owner/repo string (e.g., "actions/checkout") or local path
        version: Version tag (e.g., "v4") or empty string for local actions

    Returns:
        Python code for the action function
    """
    # Build the action reference
    if version:
        action_ref = f"{owner_repo}@{version}"
    else:
        action_ref = owner_repo

    # Derive function name
    func_name = _derive_function_name(schema.name, owner_repo)

    # Process inputs
    required_inputs = []
    optional_inputs = []

    for inp in schema.inputs:
        python_name = to_python_identifier(inp.name)
        input_data = {
            "name": inp.name,
            "python_name": python_name,
            "description": inp.description,
            "required": inp.required,
            "default": inp.default,
        }
        if inp.required:
            required_inputs.append(input_data)
        else:
            optional_inputs.append(input_data)

    # Build function signature
    params = []

    # Required params first (positional)
    for inp in required_inputs:
        params.append(f'{inp["python_name"]}: str,')

    # Optional params with defaults
    for inp in optional_inputs:
        params.append(f'{inp["python_name"]}: str | None = None,')

    # Build docstring
    docstring_lines = [f'"""{schema.description}']
    if schema.inputs:
        docstring_lines.append("")
        docstring_lines.append("Args:")
        for inp in required_inputs + optional_inputs:
            docstring_lines.append(f'    {inp["python_name"]}: {inp["description"]}')
    docstring_lines.append("")
    docstring_lines.append("Returns:")
    docstring_lines.append("    Step configured to use this action")
    docstring_lines.append('"""')

    # Build with_ dict construction
    with_items = []
    all_inputs = required_inputs + optional_inputs
    for inp in all_inputs:
        # Use original name as key, python_name as value
        with_items.append(f'        "{inp["name"]}": {inp["python_name"]},')

    # Generate the function code
    lines = []
    lines.append(f"def {func_name}(")
    if params:
        for param in params:
            lines.append(f"    {param}")
    lines.append(") -> Step:")

    # Add docstring
    for doc_line in docstring_lines:
        lines.append(f"    {doc_line}")

    # Build with_ dict
    if all_inputs:
        lines.append("    with_dict = {")
        for item in with_items:
            lines.append(item)
        lines.append("    }")
        lines.append("    # Filter out None values")
        lines.append("    with_dict = {k: v for k, v in with_dict.items() if v is not None}")
        lines.append("")
        lines.append("    return Step(")
        lines.append(f'        uses="{action_ref}",')
        lines.append("        with_=with_dict if with_dict else None,")
        lines.append("    )")
    else:
        lines.append("    return Step(")
        lines.append(f'        uses="{action_ref}",')
        lines.append("    )")

    return "\n".join(lines)


def generate_action_module(
    schemas: list[ActionSchema],
    action_refs: dict[str, tuple[str, str]],
) -> str:
    """Generate a Python module containing action functions.

    Args:
        schemas: List of action schemas
        action_refs: Map of action name to (owner_repo, version)

    Returns:
        Complete Python module code
    """
    lines = [
        '"""Generated GitHub Action wrappers."""',
        "",
        "from wetwire_github.workflow import Step",
        "",
    ]

    # Generate functions
    function_names = []
    for schema in schemas:
        # Find the matching ref
        ref_key = None
        for key in action_refs:
            if schema.name == key or schema.name.lower() == key.lower():
                ref_key = key
                break

        if ref_key:
            owner_repo, version = action_refs[ref_key]
        else:
            # Fallback - try to match by name
            continue

        func_code = generate_action_function(schema, owner_repo, version)
        func_name = func_code.split("(")[0].replace("def ", "")
        function_names.append(func_name)
        lines.append("")
        lines.append(func_code)
        lines.append("")

    # Add __all__
    if function_names:
        lines.insert(3, f"__all__ = {function_names!r}")
        lines.insert(4, "")

    return "\n".join(lines)


def generate_all_actions(
    schemas: dict[str, ActionSchema],
    action_refs: dict[str, tuple[str, str]],
) -> dict[str, str]:
    """Generate Python modules for all actions.

    Args:
        schemas: Map of action name to schema
        action_refs: Map of action name to (owner_repo, version)

    Returns:
        Map of module name to generated code
    """
    result = {}

    for name, schema in schemas.items():
        if name in action_refs:
            owner_repo, version = action_refs[name]
            func_code = generate_action_function(schema, owner_repo, version)

            # Wrap in a module
            module_code = f'''"""Generated wrapper for {schema.name}."""

from wetwire_github.workflow import Step

{func_code}
'''
            result[name] = module_code

    return result


def main() -> int:
    """Main entry point for code generation."""
    from pathlib import Path

    from fetch import ACTION_REPOS
    from parse import parse_action_from_file

    specs_dir = Path(__file__).parent.parent / "specs"
    actions_dir = specs_dir / "actions"
    output_dir = Path(__file__).parent.parent / "src" / "wetwire_github" / "actions"

    if not actions_dir.exists():
        print("Actions not found. Run fetch.py first.")
        return 1

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Parse and generate each action
    schemas = {}
    action_refs = {}

    for name, repo in ACTION_REPOS.items():
        yml_path = actions_dir / f"{name}.yml"
        if yml_path.exists():
            schemas[name] = parse_action_from_file(str(yml_path))
            action_refs[name] = (repo, "v4")  # Default to v4

    # Generate modules
    modules = generate_all_actions(schemas, action_refs)

    print("Generating action wrappers...")
    for name, code in modules.items():
        output_path = output_dir / f"{to_python_identifier(name)}.py"
        with open(output_path, "w") as f:
            f.write(code)
        print(f"  ✓ {output_path.name}")

    # Generate __init__.py with explicit imports
    init_lines = ['"""Generated GitHub Action wrappers."""', ""]

    # Build explicit imports
    all_functions = []
    for name in sorted(modules.keys()):
        module_name = to_python_identifier(name)
        # Function name is the same as module name for single-function modules
        func_name = module_name
        init_lines.append(f"from .{module_name} import {func_name}")
        all_functions.append(func_name)

    # Add __all__
    init_lines.append("")
    init_lines.append(f"__all__ = {sorted(all_functions)!r}")

    init_path = output_dir / "__init__.py"
    with open(init_path, "w") as f:
        f.write("\n".join(init_lines))
    print("  ✓ __init__.py")

    # Format with ruff if available
    try:
        import subprocess

        subprocess.run(
            ["ruff", "format", str(output_dir)],
            capture_output=True,
            check=True,
        )
        print("  ✓ Formatted with ruff")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("  ! ruff not available for formatting")

    return 0


if __name__ == "__main__":
    exit(main())
