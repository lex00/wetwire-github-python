"""Write composite action metadata to action.yml files."""

from pathlib import Path

from wetwire_github.composite.types import CompositeAction
from wetwire_github.serialize import to_yaml


def write_action(action: CompositeAction, path: str) -> None:
    """Write a CompositeAction to an action.yml file.

    Args:
        action: CompositeAction instance to write
        path: File path to write to (if directory, writes action.yml inside it)

    Example:
        >>> from wetwire_github.composite import CompositeAction, write_action
        >>> action = CompositeAction(...)
        >>> write_action(action, "./my-action/action.yml")
    """
    output_path = Path(path)

    # If path is a directory, write action.yml inside it
    if output_path.is_dir():
        output_path = output_path / "action.yml"

    # Create parent directories if they don't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Serialize action to YAML
    yaml_content = to_yaml(action)

    # Write to file
    output_path.write_text(yaml_content)
