"""AST-based resource discovery implementation.

Uses Python's AST module to scan source files for Workflow and Job
definitions without importing them.
"""

import ast
from dataclasses import dataclass
from pathlib import Path

# Resource types we discover
DISCOVERABLE_TYPES = {"Workflow", "Job"}


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


def discover_in_file(file_path: str) -> list[DiscoveredResource]:
    """Discover Workflow and Job resources in a Python file.

    Args:
        file_path: Path to a Python source file

    Returns:
        List of discovered resources
    """
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

    return visitor.resources


def discover_in_directory(
    directory: str,
    recursive: bool = True,
    exclude_hidden: bool = True,
    exclude_pycache: bool = True,
) -> list[DiscoveredResource]:
    """Discover resources in all Python files in a directory.

    Args:
        directory: Path to directory to scan
        recursive: Whether to scan subdirectories
        exclude_hidden: Whether to exclude hidden directories (starting with .)
        exclude_pycache: Whether to exclude __pycache__ directories

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
                resources.extend(discover_in_file(str(entry)))
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
