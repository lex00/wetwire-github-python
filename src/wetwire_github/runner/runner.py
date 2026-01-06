"""Value extraction from workflow modules.

Uses importlib to load modules and extract Workflow/Job instances.
"""

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from wetwire_github.workflow import Job, Workflow


@dataclass
class ExtractedWorkflow:
    """An extracted Workflow object with metadata."""

    name: str
    module: str
    workflow: "Workflow"
    file_path: str | None = None


@dataclass
class ExtractedJob:
    """An extracted Job object with metadata."""

    name: str
    module: str
    job: "Job"
    file_path: str | None = None


def find_package_root(start_path: str) -> str | None:
    """Find the package root directory.

    Looks for pyproject.toml or setup.py going up from start_path.

    Args:
        start_path: Starting directory path

    Returns:
        Path to package root, or None if not found
    """
    current = Path(start_path)
    if current.is_file():
        current = current.parent

    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return str(current)
        if (current / "setup.py").exists():
            return str(current)
        current = current.parent

    return None


def resolve_module_path(file_path: str, package_root: str) -> str:
    """Resolve a file path to a Python module path.

    Args:
        file_path: Absolute path to the Python file
        package_root: Path to the package root directory

    Returns:
        Dotted module path (e.g., "mypackage.workflows.ci")
    """
    file_path = Path(file_path)
    package_root = Path(package_root)

    # Get relative path from package root
    try:
        rel_path = file_path.relative_to(package_root)
    except ValueError:
        # File is not under package root
        return file_path.stem

    # Convert path to module path
    parts = list(rel_path.parts)

    # Remove .py extension from last part
    if parts and parts[-1].endswith(".py"):
        parts[-1] = parts[-1][:-3]

    # Remove __init__ if present
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]

    return ".".join(parts)


def _load_module_from_file(file_path: str, module_name: str) -> Any:
    """Load a Python module from a file path.

    Args:
        file_path: Path to the Python file
        module_name: Name to use for the module

    Returns:
        Loaded module object
    """
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {file_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module

    try:
        spec.loader.exec_module(module)
    except Exception:
        # Clean up on failure
        sys.modules.pop(module_name, None)
        raise

    return module


def extract_workflows(file_path: str) -> list[ExtractedWorkflow]:
    """Extract all Workflow objects from a Python file.

    Args:
        file_path: Path to the Python file

    Returns:
        List of extracted workflows
    """
    from wetwire_github.workflow import Workflow

    package_root = find_package_root(file_path)
    if package_root:
        module_path = resolve_module_path(file_path, package_root)
    else:
        module_path = Path(file_path).stem

    try:
        module = _load_module_from_file(file_path, module_path)
    except Exception:
        return []

    workflows = []
    for name in dir(module):
        if name.startswith("_"):
            continue
        value = getattr(module, name)
        if isinstance(value, Workflow):
            workflows.append(
                ExtractedWorkflow(
                    name=name,
                    module=module_path,
                    workflow=value,
                    file_path=file_path,
                )
            )

    return workflows


def extract_jobs(file_path: str) -> list[ExtractedJob]:
    """Extract all Job objects from a Python file.

    Args:
        file_path: Path to the Python file

    Returns:
        List of extracted jobs
    """
    from wetwire_github.workflow import Job

    package_root = find_package_root(file_path)
    if package_root:
        module_path = resolve_module_path(file_path, package_root)
    else:
        module_path = Path(file_path).stem

    try:
        module = _load_module_from_file(file_path, module_path)
    except Exception:
        return []

    jobs = []
    for name in dir(module):
        if name.startswith("_"):
            continue
        value = getattr(module, name)
        if isinstance(value, Job):
            jobs.append(
                ExtractedJob(
                    name=name,
                    module=module_path,
                    job=value,
                    file_path=file_path,
                )
            )

    return jobs
