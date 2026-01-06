"""Template builder with topological sorting.

Implements Kahn's algorithm for dependency ordering.
"""

from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wetwire_github.workflow import Job


class CycleError(Exception):
    """Error raised when a dependency cycle is detected."""

    def __init__(self, cycle: list[str]) -> None:
        self.cycle = cycle
        cycle_str = " -> ".join(cycle)
        super().__init__(f"Dependency cycle detected: {cycle_str}")


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
        # Find a cycle for the error message
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


def order_jobs(jobs: dict[str, "Job"]) -> list[tuple[str, "Job"]]:
    """Order jobs based on their 'needs' dependencies.

    Args:
        jobs: Dict mapping job name to Job object

    Returns:
        List of (name, Job) tuples in dependency order

    Raises:
        CycleError: If jobs have circular dependencies
    """
    # Build dependency graph from needs
    graph: dict[str, list[str]] = {}

    for name, job in jobs.items():
        if job.needs:
            # Handle both list and single string needs
            if isinstance(job.needs, list):
                graph[name] = list(job.needs)
            else:
                graph[name] = [job.needs]
        else:
            graph[name] = []

    # Get topological order
    ordered_names = topological_sort(graph)

    # Return jobs in order
    return [(name, jobs[name]) for name in ordered_names]
