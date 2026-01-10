"""Value extraction from workflow modules.

Uses importlib to load modules and extract Workflow/Job instances.
"""

import importlib.util
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .exceptions import (
    WorkflowImportError,
    WorkflowRuntimeError,
    WorkflowSyntaxError,
)

if TYPE_CHECKING:
    from wetwire_github.workflow import Job, Workflow

logger = logging.getLogger(__name__)


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
    file_path_obj = Path(file_path)
    package_root_obj = Path(package_root)

    # Get relative path from package root
    try:
        rel_path = file_path_obj.relative_to(package_root_obj)
    except ValueError:
        # File is not under package root
        return file_path_obj.stem

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

    Raises:
        WorkflowSyntaxError: If the file has Python syntax errors
        WorkflowImportError: If the file cannot import required modules
        WorkflowRuntimeError: If the file raises an error during execution
    """
    # First, check for syntax errors by trying to compile the source
    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()
        compile(source, file_path, "exec")
    except SyntaxError as e:
        logger.error(
            "Syntax error in workflow file",
            extra={
                "file_path": file_path,
                "module_name": module_name,
                "line_number": e.lineno,
                "offset": e.offset,
                "error_message": str(e.msg),
            },
        )
        raise WorkflowSyntaxError(
            str(e.msg) if e.msg else "invalid syntax",
            file_path=file_path,
            module_name=module_name,
            line_number=e.lineno,
            offset=e.offset,
        ) from e

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        logger.error(
            "Cannot create module spec",
            extra={"file_path": file_path, "module_name": module_name},
        )
        raise WorkflowImportError(
            f"Cannot load module from {file_path}",
            file_path=file_path,
            module_name=module_name,
        )

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module

    try:
        spec.loader.exec_module(module)
    except ModuleNotFoundError as e:
        # Clean up on failure
        sys.modules.pop(module_name, None)
        logger.error(
            "Module import error in workflow file",
            extra={
                "file_path": file_path,
                "module_name": module_name,
                "missing_module": e.name,
                "error_message": str(e),
            },
        )
        raise WorkflowImportError(
            str(e),
            file_path=file_path,
            module_name=module_name,
            missing_module=e.name,
        ) from e
    except ImportError as e:
        # Clean up on failure
        sys.modules.pop(module_name, None)
        logger.error(
            "Import error in workflow file",
            extra={
                "file_path": file_path,
                "module_name": module_name,
                "error_message": str(e),
            },
        )
        raise WorkflowImportError(
            str(e),
            file_path=file_path,
            module_name=module_name,
        ) from e
    except Exception as e:
        # Clean up on failure
        sys.modules.pop(module_name, None)
        logger.error(
            "Runtime error in workflow file",
            extra={
                "file_path": file_path,
                "module_name": module_name,
                "exception_type": type(e).__name__,
                "error_message": str(e),
            },
        )
        raise WorkflowRuntimeError(
            str(e),
            file_path=file_path,
            module_name=module_name,
            original_exception=e,
        ) from e

    return module


def extract_workflows(file_path: str) -> list[ExtractedWorkflow]:
    """Extract all Workflow objects from a Python file.

    Args:
        file_path: Path to the Python file

    Returns:
        List of extracted workflows

    Raises:
        WorkflowSyntaxError: If the file has Python syntax errors
        WorkflowImportError: If the file cannot import required modules
        WorkflowRuntimeError: If the file raises an error during execution
    """
    from wetwire_github.workflow import Workflow

    package_root = find_package_root(file_path)
    if package_root:
        module_path = resolve_module_path(file_path, package_root)
    else:
        module_path = Path(file_path).stem

    # Let exceptions propagate for better error handling
    module = _load_module_from_file(file_path, module_path)

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

    Raises:
        WorkflowSyntaxError: If the file has Python syntax errors
        WorkflowImportError: If the file cannot import required modules
        WorkflowRuntimeError: If the file raises an error during execution
    """
    from wetwire_github.workflow import Job

    package_root = find_package_root(file_path)
    if package_root:
        module_path = resolve_module_path(file_path, package_root)
    else:
        module_path = Path(file_path).stem

    # Let exceptions propagate for better error handling
    module = _load_module_from_file(file_path, module_path)

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
