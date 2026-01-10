"""AST-based resource discovery implementation.

Uses Python's AST module to scan source files for Workflow and Job
definitions without importing them.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from wetwire_github.discover.cache import DiscoveryCache

# Resource types we discover
DISCOVERABLE_TYPES = {"Workflow", "Job"}
ACTION_TYPES = {"CompositeAction"}


@dataclass
class DiscoveredReusableWorkflow:
    """A discovered reusable workflow (with workflow_call trigger)."""

    name: str
    file_path: str
    inputs: dict[str, dict[str, Any]] = field(default_factory=dict)
    outputs: dict[str, str] = field(default_factory=dict)
    secrets: list[str] = field(default_factory=list)


@dataclass
class DiscoveredResource:
    """A discovered Workflow or Job resource."""

    name: str
    type: str
    file_path: str
    line_number: int
    module: str
    dependencies: list[str] | None = None


class ResourceVisitor(ast.NodeVisitor):
    """AST visitor that discovers Workflow and Job assignments."""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.module = Path(file_path).stem
        self.resources: list[DiscoveredResource] = []
        # Track import aliases: alias -> original name
        self.import_aliases: dict[str, str] = {}
        # Track what names refer to what types
        self.type_bindings: dict[str, str] = {}

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track imports from wetwire_github.workflow."""
        if node.module and "wetwire_github" in node.module:
            for alias in node.names:
                actual_name = alias.name
                bound_name = alias.asname if alias.asname else alias.name
                if actual_name in DISCOVERABLE_TYPES:
                    self.import_aliases[bound_name] = actual_name
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Check assignments for Workflow/Job instantiations."""
        # Only handle simple name assignments
        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            self.generic_visit(node)
            return

        target_name = node.targets[0].id

        # Check if RHS is a Call
        if not isinstance(node.value, ast.Call):
            self.generic_visit(node)
            return

        # Get the function being called
        func = node.value.func
        type_name = None

        if isinstance(func, ast.Name):
            # Direct call: Workflow(...) or WF(...)
            if func.id in self.import_aliases:
                type_name = self.import_aliases[func.id]
            elif func.id in DISCOVERABLE_TYPES:
                type_name = func.id
        elif isinstance(func, ast.Attribute):
            # Attribute call: workflow.Workflow(...)
            if func.attr in DISCOVERABLE_TYPES:
                type_name = func.attr

        if type_name:
            # Extract dependencies from the call arguments
            deps = self._extract_dependencies(node.value)

            self.resources.append(
                DiscoveredResource(
                    name=target_name,
                    type=type_name,
                    file_path=self.file_path,
                    line_number=node.lineno,
                    module=self.module,
                    dependencies=deps if deps else None,
                )
            )
            self.type_bindings[target_name] = type_name

        self.generic_visit(node)

    def _extract_dependencies(self, call: ast.Call) -> list[str]:
        """Extract variable references from a call's arguments."""
        deps = []

        for arg in call.args:
            deps.extend(self._get_names(arg))

        for keyword in call.keywords:
            deps.extend(self._get_names(keyword.value))

        return deps

    def _get_names(self, node: ast.expr) -> list[str]:
        """Get all Name references from an AST expression."""
        names = []

        if isinstance(node, ast.Name):
            names.append(node.id)
        elif isinstance(node, ast.Dict):
            for value in node.values:
                if value is not None:
                    names.extend(self._get_names(value))
        elif isinstance(node, ast.List):
            for elt in node.elts:
                names.extend(self._get_names(elt))
        elif isinstance(node, ast.Tuple):
            for elt in node.elts:
                names.extend(self._get_names(elt))
        elif isinstance(node, ast.Call):
            for arg in node.args:
                names.extend(self._get_names(arg))
            for kw in node.keywords:
                names.extend(self._get_names(kw.value))

        return names


def discover_in_file(
    file_path: str, cache: DiscoveryCache | None = None
) -> list[DiscoveredResource]:
    """Discover Workflow and Job resources in a Python file.

    Args:
        file_path: Path to a Python source file
        cache: Optional DiscoveryCache instance for caching results

    Returns:
        List of discovered resources
    """
    # Check cache first if available
    if cache is not None:
        cached = cache.get(file_path)
        if cached is not None:
            return cached

    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()
    except (OSError, UnicodeDecodeError):
        return []

    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError:
        return []

    visitor = ResourceVisitor(file_path)
    visitor.visit(tree)

    # Cache the results if cache is available
    if cache is not None:
        cache.set(file_path, visitor.resources)

    return visitor.resources


def discover_in_directory(
    directory: str,
    recursive: bool = True,
    exclude_hidden: bool = True,
    exclude_pycache: bool = True,
    cache: DiscoveryCache | None = None,
) -> list[DiscoveredResource]:
    """Discover resources in all Python files in a directory.

    Args:
        directory: Path to directory to scan
        recursive: Whether to scan subdirectories
        exclude_hidden: Whether to exclude hidden directories (starting with .)
        exclude_pycache: Whether to exclude __pycache__ directories
        cache: Optional DiscoveryCache instance for caching results

    Returns:
        List of all discovered resources
    """
    resources = []
    dir_path = Path(directory)

    def should_skip_dir(name: str) -> bool:
        """Check if a directory should be skipped."""
        if exclude_pycache and name == "__pycache__":
            return True
        if exclude_hidden and name.startswith("."):
            return True
        return False

    def scan_directory(path: Path) -> None:
        """Scan a directory for Python files."""
        try:
            entries = list(path.iterdir())
        except PermissionError:
            return

        for entry in entries:
            if entry.is_file() and entry.suffix == ".py":
                resources.extend(discover_in_file(str(entry), cache=cache))
            elif entry.is_dir() and recursive:
                if not should_skip_dir(entry.name):
                    scan_directory(entry)

    scan_directory(dir_path)
    return resources


def build_dependency_graph(
    resources: list[DiscoveredResource],
) -> dict[str, list[str]]:
    """Build a dependency graph from discovered resources.

    Args:
        resources: List of discovered resources

    Returns:
        Dict mapping resource name to list of dependency names
    """
    # Create a set of all resource names
    resource_names = {r.name for r in resources}

    # Build graph
    graph: dict[str, list[str]] = {}

    for resource in resources:
        deps = []
        if resource.dependencies:
            # Only include dependencies that are also discovered resources
            deps = [d for d in resource.dependencies if d in resource_names]
        graph[resource.name] = deps

    return graph


def validate_references(
    resources: list[DiscoveredResource],
) -> list[str]:
    """Validate that all references between resources are valid.

    Args:
        resources: List of discovered resources

    Returns:
        List of error messages for invalid references
    """
    errors = []
    # Note: resource_names could be used for more thorough validation
    # but we currently don't track undefined references at AST level

    for resource in resources:
        if resource.dependencies:
            for dep in resource.dependencies:
                # Only report errors for dependencies that look like they
                # should be resources (not built-in names, etc.)
                # For now, just check if it's in our resource set
                pass  # We don't track undefined references at AST level

    return errors


class ReusableWorkflowVisitor(ast.NodeVisitor):
    """AST visitor that discovers reusable workflows (with workflow_call trigger)."""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.reusable_workflows: list[DiscoveredReusableWorkflow] = []

    def visit_Assign(self, node: ast.Assign) -> None:
        """Check assignments for Workflow with workflow_call trigger."""
        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            self.generic_visit(node)
            return

        if not isinstance(node.value, ast.Call):
            self.generic_visit(node)
            return

        func = node.value.func
        is_workflow = False

        if isinstance(func, ast.Name) and func.id == "Workflow":
            is_workflow = True
        elif isinstance(func, ast.Attribute) and func.attr == "Workflow":
            is_workflow = True

        if not is_workflow:
            self.generic_visit(node)
            return

        # Check for workflow_call in triggers
        workflow_name = ""
        workflow_call_data: dict[str, Any] | None = None

        for keyword in node.value.keywords:
            if keyword.arg == "name" and isinstance(keyword.value, ast.Constant):
                workflow_name = str(keyword.value.value)
            elif keyword.arg == "on" and isinstance(keyword.value, ast.Call):
                workflow_call_data = self._extract_workflow_call(keyword.value)

        if workflow_call_data is not None:
            self.reusable_workflows.append(
                DiscoveredReusableWorkflow(
                    name=workflow_name,
                    file_path=self.file_path,
                    inputs=workflow_call_data.get("inputs", {}),
                    outputs=workflow_call_data.get("outputs", {}),
                    secrets=workflow_call_data.get("secrets", []),
                )
            )

        self.generic_visit(node)

    def _extract_workflow_call(self, triggers_call: ast.Call) -> dict[str, Any] | None:
        """Extract workflow_call configuration from Triggers call."""
        for keyword in triggers_call.keywords:
            if keyword.arg == "workflow_call":
                return self._parse_workflow_call_trigger(keyword.value)
        return None

    def _parse_workflow_call_trigger(self, node: ast.expr) -> dict[str, Any]:
        """Parse WorkflowCallTrigger arguments."""
        result: dict[str, Any] = {"inputs": {}, "outputs": {}, "secrets": []}

        if not isinstance(node, ast.Call):
            return result

        for keyword in node.keywords:
            if keyword.arg == "inputs" and isinstance(keyword.value, ast.Dict):
                result["inputs"] = self._parse_inputs(keyword.value)
            elif keyword.arg == "outputs" and isinstance(keyword.value, ast.Dict):
                result["outputs"] = self._parse_outputs(keyword.value)
            elif keyword.arg == "secrets" and isinstance(keyword.value, ast.List):
                result["secrets"] = self._parse_secrets(keyword.value)

        return result

    def _parse_inputs(self, dict_node: ast.Dict) -> dict[str, dict[str, Any]]:
        """Parse input configurations from AST dict."""
        inputs = {}
        for key, value in zip(dict_node.keys, dict_node.values, strict=False):
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                input_name = key.value
                # Just store the input name; detailed config parsing is optional
                inputs[input_name] = {}
                if isinstance(value, ast.Call):
                    for kw in value.keywords:
                        if kw.arg and isinstance(kw.value, ast.Constant):
                            inputs[input_name][kw.arg] = kw.value.value
        return inputs

    def _parse_outputs(self, dict_node: ast.Dict) -> dict[str, str]:
        """Parse output configurations from AST dict."""
        outputs = {}
        for key, value in zip(dict_node.keys, dict_node.values, strict=False):
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                output_name = key.value
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    outputs[output_name] = value.value
                else:
                    outputs[output_name] = ""
        return outputs

    def _parse_secrets(self, list_node: ast.List) -> list[str]:
        """Parse secret names from AST list."""
        secrets = []
        for elt in list_node.elts:
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                secrets.append(elt.value)
        return secrets


def discover_reusable_workflows(
    source: str, file_path: str = "<string>"
) -> list[DiscoveredReusableWorkflow]:
    """Discover reusable workflows (with workflow_call trigger) in source code.

    Args:
        source: Python source code
        file_path: Path to the source file (for error messages)

    Returns:
        List of discovered reusable workflows
    """
    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError:
        return []

    visitor = ReusableWorkflowVisitor(file_path)
    visitor.visit(tree)

    return visitor.reusable_workflows


class ActionVisitor(ast.NodeVisitor):
    """AST visitor that discovers CompositeAction assignments."""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.module = Path(file_path).stem
        self.resources: list[DiscoveredResource] = []
        # Track import aliases: alias -> original name
        self.import_aliases: dict[str, str] = {}

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track imports from wetwire_github.composite."""
        if node.module and "wetwire_github.composite" in node.module:
            for alias in node.names:
                actual_name = alias.name
                bound_name = alias.asname if alias.asname else alias.name
                if actual_name in ACTION_TYPES:
                    self.import_aliases[bound_name] = actual_name
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Check assignments for CompositeAction instantiations."""
        # Only handle simple name assignments
        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            self.generic_visit(node)
            return

        target_name = node.targets[0].id

        # Check if RHS is a Call
        if not isinstance(node.value, ast.Call):
            self.generic_visit(node)
            return

        # Get the function being called
        func = node.value.func
        type_name = None

        if isinstance(func, ast.Name):
            # Direct call: CompositeAction(...)
            if func.id in self.import_aliases:
                type_name = self.import_aliases[func.id]
            elif func.id in ACTION_TYPES:
                type_name = func.id
        elif isinstance(func, ast.Attribute):
            # Attribute call: composite.CompositeAction(...)
            if func.attr in ACTION_TYPES:
                type_name = func.attr

        if type_name:
            self.resources.append(
                DiscoveredResource(
                    name=target_name,
                    type=type_name,
                    file_path=self.file_path,
                    line_number=node.lineno,
                    module=self.module,
                )
            )

        self.generic_visit(node)


def discover_actions(
    directory: str,
    recursive: bool = True,
    exclude_hidden: bool = True,
    exclude_pycache: bool = True,
    cache: DiscoveryCache | None = None,
) -> list[DiscoveredResource]:
    """Discover CompositeAction resources in all Python files in a directory.

    Args:
        directory: Path to directory to scan
        recursive: Whether to scan subdirectories
        exclude_hidden: Whether to exclude hidden directories (starting with .)
        exclude_pycache: Whether to exclude __pycache__ directories
        cache: Optional DiscoveryCache instance for caching results

    Returns:
        List of all discovered CompositeAction resources
    """
    resources = []
    dir_path = Path(directory)

    def should_skip_dir(name: str) -> bool:
        """Check if a directory should be skipped."""
        if exclude_pycache and name == "__pycache__":
            return True
        if exclude_hidden and name.startswith("."):
            return True
        return False

    def scan_directory(path: Path) -> None:
        """Scan a directory for Python files."""
        try:
            entries = list(path.iterdir())
        except PermissionError:
            return

        for entry in entries:
            if entry.is_file() and entry.suffix == ".py":
                # Check cache first
                cached_resources = None
                if cache is not None:
                    cached_resources = cache.get(str(entry))

                if cached_resources is not None:
                    # Filter for CompositeAction resources from cache
                    action_resources = [
                        r for r in cached_resources if r.type == "CompositeAction"
                    ]
                    resources.extend(action_resources)
                else:
                    # Discover actions in this file
                    try:
                        with open(entry, encoding="utf-8") as f:
                            source = f.read()
                    except (OSError, UnicodeDecodeError):
                        continue

                    try:
                        tree = ast.parse(source, filename=str(entry))
                    except SyntaxError:
                        continue

                    visitor = ActionVisitor(str(entry))
                    visitor.visit(tree)
                    resources.extend(visitor.resources)

                    # Cache the results
                    if cache is not None:
                        cache.set(str(entry), visitor.resources)
            elif entry.is_dir() and recursive:
                if not should_skip_dir(entry.name):
                    scan_directory(entry)

    scan_directory(dir_path)
    return resources
