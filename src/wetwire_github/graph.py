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

            self.nodes[node_name] = DependencyNode(
                name=node_name,
                type="job",
                depends_on=deps,
                file_path=file_path,
                line=line,
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

    def to_mermaid(self) -> str:
        """Generate Mermaid diagram for the workflow graph.

        Returns:
            Mermaid flowchart diagram as string
        """
        lines = ["graph TD"]

        # Group nodes by workflow
        workflows: dict[str, dict[str, DependencyNode]] = {}
        for name, node in self.nodes.items():
            parts = name.split("/", 1)
            workflow_name = parts[0] if len(parts) > 1 else "_default"
            if workflow_name not in workflows:
                workflows[workflow_name] = {}
            workflows[workflow_name][name] = node

        use_subgraphs = len(workflows) > 1

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
                if not node.depends_on:
                    lines.append(f"{indent}{safe_name}[{display_name}]")

            # Add edges for dependencies
            for name, node in nodes.items():
                safe_name = self._sanitize_id(name)
                for dep in node.depends_on:
                    safe_dep = self._sanitize_id(dep)
                    lines.append(f"{indent}{safe_dep} --> {safe_name}")

            if use_subgraphs:
                lines.append("    end")

        # Add workflow_call edges (dashed lines)
        for caller, callee in self.workflow_calls:
            safe_caller = self._sanitize_id(caller)
            safe_callee = self._sanitize_id(callee)
            lines.append(f"    {safe_caller}([{caller}]) -.-> {safe_callee}([{callee}])")

        return "\n".join(lines)

    def to_dot(self) -> str:
        """Generate DOT/Graphviz diagram for the workflow graph.

        Returns:
            DOT format diagram as string
        """
        lines = ["digraph G {"]
        lines.append("    rankdir=TB;")
        lines.append("    node [shape=box];")

        # Group nodes by workflow
        workflows: dict[str, dict[str, DependencyNode]] = {}
        for name, node in self.nodes.items():
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

            # Add nodes
            for name in nodes:
                safe_name = self._sanitize_id(name)
                display_name = name.split("/")[-1] if "/" in name else name
                lines.append(f'{indent}"{safe_name}" [label="{display_name}"];')

            # Add edges
            for name, node in nodes.items():
                safe_name = self._sanitize_id(name)
                for dep in node.depends_on:
                    safe_dep = self._sanitize_id(dep)
                    lines.append(f'{indent}"{safe_dep}" -> "{safe_name}";')

            if use_subgraphs:
                lines.append("    }")

        lines.append("}")
        return "\n".join(lines)

    def _sanitize_id(self, name: str) -> str:
        """Sanitize a name for use as graph node ID."""
        return name.replace("-", "_").replace(" ", "_").replace("/", "_")
