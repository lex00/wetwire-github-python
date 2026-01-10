"""Action build command implementation.

Discovers composite actions in Python packages and generates action.yml output.
"""

from pathlib import Path

from wetwire_github.composite import write_action
from wetwire_github.discover import DiscoveryCache, discover_actions


def _sanitize_dirname(name: str) -> str:
    """Convert an action name to a safe directory name.

    Args:
        name: Action name (may contain spaces, special chars)

    Returns:
        Sanitized directory name
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

    return result or "action"


def build_actions(
    package_path: str,
    output_dir: str,
    no_cache: bool = False,
) -> tuple[int, list[str]]:
    """Build composite actions from a Python package.

    Args:
        package_path: Path to Python package containing action definitions
        output_dir: Directory to write output files
        no_cache: If True, bypass discovery cache

    Returns:
        Tuple of (exit_code, list of generated file paths or error messages)
    """
    package = Path(package_path)
    output = Path(output_dir)

    # Check if package exists
    if not package.exists():
        return 1, [f"Error: Package path does not exist: {package_path}"]

    # Create output directory if needed
    output.mkdir(parents=True, exist_ok=True)

    # Initialize cache if not disabled
    cache = None if no_cache else DiscoveryCache()

    # Discover action files using AST
    discovered = discover_actions(str(package), cache=cache)

    if not discovered:
        return 1, ["No composite actions found in package"]

    # Extract actual action objects
    import importlib.util
    import sys

    from wetwire_github.composite import CompositeAction

    all_actions = []
    for resource in discovered:
        # Import the file and extract the action
        file_path = resource.file_path
        var_name = resource.name

        try:
            # Load the module
            spec = importlib.util.spec_from_file_location(resource.module, file_path)
            if spec is None or spec.loader is None:
                continue

            module = importlib.util.module_from_spec(spec)
            sys.modules[resource.module] = module
            spec.loader.exec_module(module)

            # Get the action object
            if hasattr(module, var_name):
                action_obj = getattr(module, var_name)
                if isinstance(action_obj, CompositeAction):
                    all_actions.append((var_name, action_obj))

            # Clean up
            if resource.module in sys.modules:
                del sys.modules[resource.module]
        except Exception:
            # Skip actions that can't be imported
            continue

    if not all_actions:
        return 1, ["No composite actions could be extracted"]

    # Generate output files
    generated_files = []
    for var_name, action in all_actions:
        # Create a subdirectory for each action
        action_dir_name = _sanitize_dirname(var_name)
        action_dir = output / action_dir_name

        # Create the directory
        action_dir.mkdir(parents=True, exist_ok=True)

        # Write action.yml to the directory
        action_file = action_dir / "action.yml"
        write_action(action, str(action_file))

        generated_files.append(str(action_file))

    return 0, generated_files
