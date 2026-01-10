"""Standalone graph module for workflow dependency analysis.

This module provides centralized graph operations for workflows, jobs, and steps
including topological sorting, cycle detection, and visualization.
"""

from collections import deque
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wetwire_github.workflow import Workflow

__all__ = [
    "CycleError",
    "DependencyNode",
    "WorkflowGraph",
    "detect_cycles",
    "topological_sort",
]


class CycleError(Exception):
    """Error raised when a dependency cycle is detected."""

    def __init__(self, cycle: list[str]) -> None:
        self.cycle = cycle
        cycle_str = " -> ".join(cycle)
        super().__init__(f"Dependency cycle detected: {cycle_str}")


@dataclass
class DependencyNode:
    """A node in the dependency graph."""

    name: str
    type: str  # 'workflow', 'job', 'step'
    depends_on: list[str] = field(default_factory=list)
    file_path: str = ""
    line: int = 0
    has_matrix: bool = False
    has_condition: bool = False
    is_reusable: bool = False


def topological_sort(graph: dict[str, list[str]]) -> list[str]:
    """Topologically sort a dependency graph using Kahn's algorithm.

    Args:
        graph: Dict mapping node to list of dependencies (nodes it depends on)

    Returns:
        List of nodes in topological order (dependencies before dependents)

    Raises:
        CycleError: If the graph contains a cycle
    """
    if not graph:
        return []

    # Build in-degree map and reverse adjacency list
    in_degree: dict[str, int] = {node: 0 for node in graph}
    dependents: dict[str, list[str]] = {node: [] for node in graph}

    for node, dependencies in graph.items():
        for dep in dependencies:
            if dep in graph:  # Only count known nodes
                in_degree[node] += 1
                dependents[dep].append(node)

    # Start with nodes that have no dependencies
    queue = deque(node for node, degree in in_degree.items() if degree == 0)
    result = []

    while queue:
        node = queue.popleft()
        result.append(node)

        # Reduce in-degree for dependents
        for dependent in dependents[node]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    # If we didn't process all nodes, there's a cycle
    if len(result) != len(graph):
        cycles = detect_cycles(graph)
        if cycles:
            raise CycleError(cycles[0])
        raise CycleError(["unknown"])

    return result


def detect_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    """Detect cycles in a dependency graph.

    Args:
        graph: Dict mapping node to list of dependencies

    Returns:
        List of cycles found (each cycle is a list of nodes)
    """
    not_visited = 0
    visiting = 1  # Currently visiting (in stack)
    visited = 2  # Fully visited

    color = {node: not_visited for node in graph}
    cycles: list[list[str]] = []

    def dfs(node: str, path: list[str]) -> None:
        if color[node] == visited:
            return
        if color[node] == visiting:
            # Found a cycle - extract it
            cycle_start = path.index(node)
            cycle = path[cycle_start:] + [node]
            cycles.append(cycle)
            return

        color[node] = visiting
        path.append(node)

        for dep in graph.get(node, []):
            if dep in graph:
                dfs(dep, path)

        path.pop()
        color[node] = visited

    for node in graph:
        if color[node] == not_visited:
            dfs(node, [])

    return cycles


class WorkflowGraph:
    """Dependency graph for workflows, jobs, and steps.

    Provides methods for building, analyzing, and visualizing workflow
    dependency relationships.
    """

    def __init__(self) -> None:
        """Initialize an empty workflow graph."""
        self.nodes: dict[str, DependencyNode] = {}
        self.edges: list[tuple[str, str]] = []
        self._workflows: list[str] = []
        self.workflow_calls: list[tuple[str, str]] = []  # (caller, callee) pairs

    def add_workflow(self, workflow: "Workflow", file_path: str = "", line: int = 0) -> None:
        """Add a workflow and its jobs to the graph.

        Args:
            workflow: The Workflow object to add
            file_path: Optional source file path
            line: Optional line number in source
        """
        workflow_name = workflow.name or "unnamed"
        self._workflows.append(workflow_name)

        for job_id, job in workflow.jobs.items():
            node_name = f"{workflow_name}/{job_id}"

            # Parse job dependencies
            deps: list[str] = []
            if job.needs:
                if isinstance(job.needs, list):
                    deps = [f"{workflow_name}/{d}" for d in job.needs]
                else:
                    deps = [f"{workflow_name}/{job.needs}"]

            # Determine job characteristics
            has_matrix = job.strategy is not None and job.strategy.matrix is not None
            has_condition = job.if_ is not None

            self.nodes[node_name] = DependencyNode(
                name=node_name,
                type="job",
                depends_on=deps,
                file_path=file_path,
                line=line,
                has_matrix=has_matrix,
                has_condition=has_condition,
                is_reusable=False,
            )

            # Add edges
            for dep in deps:
                self.edges.append((dep, node_name))

    def add_workflow_call(self, caller: str, callee: str) -> None:
        """Track a workflow_call relationship.

        Args:
            caller: The workflow that calls another workflow
            callee: The reusable workflow being called
        """
        self.workflow_calls.append((caller, callee))

    def detect_cycles(self) -> list[list[str]]:
        """Find circular dependencies in the graph.

        Returns:
            List of cycles found (each cycle is a list of node names)
        """
        graph = {name: node.depends_on for name, node in self.nodes.items()}
        return detect_cycles(graph)

    def topological_sort(self) -> list[str]:
        """Return nodes in dependency order.

        Returns:
            List of node names in topological order

        Raises:
            CycleError: If the graph contains a cycle
        """
        graph = {name: node.depends_on for name, node in self.nodes.items()}
        return topological_sort(graph)

    def to_mermaid(self, filter_pattern: str | None = None, exclude_pattern: str | None = None) -> str:
        """Generate Mermaid diagram for the workflow graph.

        Args:
            filter_pattern: Optional glob pattern to filter jobs (only show matching)
            exclude_pattern: Optional glob pattern to exclude jobs (hide matching)

        Returns:
            Mermaid flowchart diagram as string
        """
        lines = ["graph TD"]

        # Apply filtering
        filtered_nodes = self._apply_filters(filter_pattern, exclude_pattern)

        # Group nodes by workflow
        workflows: dict[str, dict[str, DependencyNode]] = {}
        for name, node in filtered_nodes.items():
            parts = name.split("/", 1)
            workflow_name = parts[0] if len(parts) > 1 else "_default"
            if workflow_name not in workflows:
                workflows[workflow_name] = {}
            workflows[workflow_name][name] = node

        use_subgraphs = len(workflows) > 1
        edge_count = 0

        for workflow_name, nodes in workflows.items():
            if use_subgraphs:
                safe_name = self._sanitize_id(workflow_name)
                lines.append(f"    subgraph {safe_name}[{workflow_name}]")
                indent = "        "
            else:
                indent = "    "

            # Add nodes without dependencies first
            for name, node in nodes.items():
                safe_name = self._sanitize_id(name)
                display_name = name.split("/")[-1] if "/" in name else name
                if not node.depends_on or all(dep not in filtered_nodes for dep in node.depends_on):
                    # Add node if it has no dependencies OR all its dependencies are filtered out
                    lines.append(f"{indent}{safe_name}[{display_name}]")

            # Add edges for dependencies
            for name, node in nodes.items():
                safe_name = self._sanitize_id(name)
                for dep in node.depends_on:
                    # Only add edge if dep is in filtered nodes
                    if dep in filtered_nodes:
                        safe_dep = self._sanitize_id(dep)
                        lines.append(f"{indent}{safe_dep} --> {safe_name}")
                        edge_count += 1

            if use_subgraphs:
                lines.append("    end")

        # Add workflow_call edges (dashed lines)
        for caller, callee in self.workflow_calls:
            safe_caller = self._sanitize_id(caller)
            safe_callee = self._sanitize_id(callee)
            lines.append(f"    {safe_caller}([{caller}]) -.-> {safe_callee}([{callee}])")
            # Mark reusable workflow nodes
            callee_safe = self._sanitize_id(callee)
            lines.append(f"    style {callee_safe} fill:#9013FE,stroke:#333,stroke-width:2px")

        # Add color coding for job characteristics
        for name, node in filtered_nodes.items():
            safe_name = self._sanitize_id(name)
            # Priority: matrix > conditional
            if node.has_matrix:
                lines.append(f"    style {safe_name} fill:#4A90E2,stroke:#333,stroke-width:2px")
            elif node.has_condition:
                lines.append(f"    style {safe_name} fill:#F5A623,stroke:#333,stroke-width:2px")

        # Add edge styling for dependencies (orange)
        if edge_count > 0:
            for i in range(edge_count):
                lines.append(f"    linkStyle {i} stroke:#FF6B35,stroke-width:2px")

        return "\n".join(lines)

    def to_dot(self, filter_pattern: str | None = None, exclude_pattern: str | None = None) -> str:
        """Generate DOT/Graphviz diagram for the workflow graph.

        Args:
            filter_pattern: Optional glob pattern to filter jobs (only show matching)
            exclude_pattern: Optional glob pattern to exclude jobs (hide matching)

        Returns:
            DOT format diagram as string
        """
        lines = ["digraph G {"]
        lines.append("    rankdir=TB;")
        lines.append('    node [shape=box, style=filled];')

        # Apply filtering
        filtered_nodes = self._apply_filters(filter_pattern, exclude_pattern)

        # Group nodes by workflow
        workflows: dict[str, dict[str, DependencyNode]] = {}
        for name, node in filtered_nodes.items():
            parts = name.split("/", 1)
            workflow_name = parts[0] if len(parts) > 1 else "_default"
            if workflow_name not in workflows:
                workflows[workflow_name] = {}
            workflows[workflow_name][name] = node

        use_subgraphs = len(workflows) > 1

        for workflow_name, nodes in workflows.items():
            if use_subgraphs:
                safe_name = self._sanitize_id(workflow_name)
                lines.append(f"    subgraph cluster_{safe_name} {{")
                lines.append(f'        label="{workflow_name}";')
                indent = "        "
            else:
                indent = "    "

            # Add nodes with color coding
            for name, node in nodes.items():
                safe_name = self._sanitize_id(name)
                display_name = name.split("/")[-1] if "/" in name else name

                # Determine fill color based on job characteristics
                fill_color = "#FFFFFF"  # Default white
                if node.has_matrix:
                    fill_color = "#4A90E2"  # Blue for matrix
                elif node.has_condition:
                    fill_color = "#F5A623"  # Yellow for conditional
                elif node.is_reusable:
                    fill_color = "#9013FE"  # Purple for reusable

                lines.append(f'{indent}"{safe_name}" [label="{display_name}", fillcolor="{fill_color}"];')

            # Add edges with orange color for dependencies
            for name, node in nodes.items():
                safe_name = self._sanitize_id(name)
                for dep in node.depends_on:
                    # Only add edge if dep is in filtered nodes
                    if dep in filtered_nodes:
                        safe_dep = self._sanitize_id(dep)
                        lines.append(f'{indent}"{safe_dep}" -> "{safe_name}" [color="#FF6B35", penwidth=2];')

            if use_subgraphs:
                lines.append("    }")

        lines.append("}")
        return "\n".join(lines)

    def _apply_filters(
        self,
        filter_pattern: str | None = None,
        exclude_pattern: str | None = None,
    ) -> dict[str, DependencyNode]:
        """Apply filter and exclude patterns to nodes.

        Args:
            filter_pattern: Optional glob pattern to include only matching jobs
            exclude_pattern: Optional glob pattern to exclude matching jobs

        Returns:
            Filtered dictionary of nodes
        """
        from fnmatch import fnmatch

        filtered = dict(self.nodes)

        # Apply filter pattern (include only matching)
        if filter_pattern:
            filtered = {
                name: node
                for name, node in filtered.items()
                if fnmatch(name, filter_pattern) or fnmatch(name.split("/")[-1], filter_pattern)
            }

        # Apply exclude pattern (remove matching)
        if exclude_pattern:
            filtered = {
                name: node
                for name, node in filtered.items()
                if not (fnmatch(name, exclude_pattern) or fnmatch(name.split("/")[-1], exclude_pattern))
            }

        return filtered

    def generate_legend(self, format: str = "mermaid") -> str:
        """Generate a legend explaining the color scheme.

        Args:
            format: Output format ("mermaid" or "dot")

        Returns:
            Legend as string
        """
        # Determine which features are present in the graph
        has_matrix = any(node.has_matrix for node in self.nodes.values())
        has_conditional = any(node.has_condition for node in self.nodes.values())
        has_dependencies = any(node.depends_on for node in self.nodes.values())
        has_reusable = len(self.workflow_calls) > 0

        if format == "mermaid":
            lines = ["", "Legend:", ""]
            if has_matrix:
                lines.append("  Blue (#4A90E2) = Matrix builds")
            if has_conditional:
                lines.append("  Yellow (#F5A623) = Conditional jobs (if:)")
            if has_dependencies:
                lines.append("  Orange edges (#FF6B35) = Job dependencies (needs:)")
            if has_reusable:
                lines.append("  Purple (#9013FE) = Reusable workflows")
            if not any([has_matrix, has_conditional, has_dependencies, has_reusable]):
                lines.append("  No special features detected")
            return "\n".join(lines)
        else:  # dot format
            lines = ["", "/* Legend:", ""]
            if has_matrix:
                lines.append(" * Blue (#4A90E2) = Matrix builds")
            if has_conditional:
                lines.append(" * Yellow (#F5A623) = Conditional jobs (if:)")
            if has_dependencies:
                lines.append(" * Orange edges (#FF6B35) = Job dependencies (needs:)")
            if has_reusable:
                lines.append(" * Purple (#9013FE) = Reusable workflows")
            if not any([has_matrix, has_conditional, has_dependencies, has_reusable]):
                lines.append(" * No special features detected")
            lines.append(" */")
            return "\n".join(lines)

    def _sanitize_id(self, name: str) -> str:
        """Sanitize a name for use as graph node ID."""
        return name.replace("-", "_").replace(" ", "_").replace("/", "_")
