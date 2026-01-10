"""Tests for the standalone graph module (issue #95)."""

import pytest

from wetwire_github.graph import (
    CycleError,
    DependencyNode,
    WorkflowGraph,
    detect_cycles,
    topological_sort,
)
from wetwire_github.workflow import Job, Step, Triggers, Workflow


class TestDependencyNode:
    """Tests for DependencyNode dataclass."""

    def test_create_node(self) -> None:
        """Test creating a dependency node."""
        node = DependencyNode(
            name="build",
            type="job",
            depends_on=["checkout"],
            file_path="workflows.py",
            line=10,
        )

        assert node.name == "build"
        assert node.type == "job"
        assert node.depends_on == ["checkout"]
        assert node.file_path == "workflows.py"
        assert node.line == 10

    def test_node_with_empty_deps(self) -> None:
        """Test node with no dependencies."""
        node = DependencyNode(
            name="checkout",
            type="job",
            depends_on=[],
            file_path="workflows.py",
            line=5,
        )

        assert node.depends_on == []


class TestTopologicalSort:
    """Tests for topological_sort function."""

    def test_empty_graph(self) -> None:
        """Test sorting an empty graph."""
        result = topological_sort({})
        assert result == []

    def test_single_node(self) -> None:
        """Test graph with single node."""
        result = topological_sort({"a": []})
        assert result == ["a"]

    def test_linear_chain(self) -> None:
        """Test linear dependency chain: a -> b -> c."""
        graph = {
            "c": ["b"],
            "b": ["a"],
            "a": [],
        }
        result = topological_sort(graph)
        assert result.index("a") < result.index("b") < result.index("c")

    def test_diamond_dependency(self) -> None:
        """Test diamond dependency pattern."""
        graph = {
            "d": ["b", "c"],
            "b": ["a"],
            "c": ["a"],
            "a": [],
        }
        result = topological_sort(graph)
        assert result.index("a") < result.index("b")
        assert result.index("a") < result.index("c")
        assert result.index("b") < result.index("d")
        assert result.index("c") < result.index("d")

    def test_cycle_raises_error(self) -> None:
        """Test that cycle detection raises CycleError."""
        graph = {
            "a": ["b"],
            "b": ["c"],
            "c": ["a"],
        }
        with pytest.raises(CycleError):
            topological_sort(graph)


class TestDetectCycles:
    """Tests for detect_cycles function."""

    def test_no_cycles(self) -> None:
        """Test graph without cycles."""
        graph = {
            "a": [],
            "b": ["a"],
            "c": ["b"],
        }
        cycles = detect_cycles(graph)
        assert cycles == []

    def test_simple_cycle(self) -> None:
        """Test detecting a simple cycle."""
        graph = {
            "a": ["b"],
            "b": ["a"],
        }
        cycles = detect_cycles(graph)
        assert len(cycles) >= 1

    def test_self_cycle(self) -> None:
        """Test detecting self-reference cycle."""
        graph = {
            "a": ["a"],
        }
        cycles = detect_cycles(graph)
        assert len(cycles) >= 1

    def test_multiple_cycles(self) -> None:
        """Test detecting multiple cycles."""
        graph = {
            "a": ["b"],
            "b": ["a"],
            "c": ["d"],
            "d": ["c"],
        }
        cycles = detect_cycles(graph)
        assert len(cycles) >= 2


class TestWorkflowGraph:
    """Tests for WorkflowGraph class."""

    def test_create_empty_graph(self) -> None:
        """Test creating an empty graph."""
        graph = WorkflowGraph()
        assert graph.nodes == {}
        assert graph.edges == []

    def test_add_workflow(self) -> None:
        """Test adding a workflow to the graph."""
        build_job = Job(runs_on="ubuntu-latest", steps=[Step(run="make build")])
        test_job = Job(runs_on="ubuntu-latest", steps=[Step(run="make test")], needs="build")

        workflow = Workflow(
            name="CI",
            on=Triggers(),
            jobs={"build": build_job, "test": test_job},
        )

        graph = WorkflowGraph()
        graph.add_workflow(workflow)

        assert "CI/build" in graph.nodes
        assert "CI/test" in graph.nodes
        assert graph.nodes["CI/test"].depends_on == ["CI/build"]

    def test_workflow_with_complex_deps(self) -> None:
        """Test workflow with multiple job dependencies."""
        job_a = Job(runs_on="ubuntu-latest", steps=[Step(run="echo a")])
        job_b = Job(runs_on="ubuntu-latest", steps=[Step(run="echo b")], needs="a")
        job_c = Job(runs_on="ubuntu-latest", steps=[Step(run="echo c")], needs="a")
        job_d = Job(runs_on="ubuntu-latest", steps=[Step(run="echo d")], needs=["b", "c"])

        workflow = Workflow(
            name="Pipeline",
            on=Triggers(),
            jobs={"a": job_a, "b": job_b, "c": job_c, "d": job_d},
        )

        graph = WorkflowGraph()
        graph.add_workflow(workflow)

        assert len(graph.nodes) == 4
        assert len(graph.edges) == 4  # a->b, a->c, b->d, c->d

    def test_topological_sort(self) -> None:
        """Test getting topological sort of workflow graph."""
        job_a = Job(runs_on="ubuntu-latest", steps=[Step(run="echo a")])
        job_b = Job(runs_on="ubuntu-latest", steps=[Step(run="echo b")], needs="a")
        job_c = Job(runs_on="ubuntu-latest", steps=[Step(run="echo c")], needs="b")

        workflow = Workflow(
            name="CI",
            on=Triggers(),
            jobs={"a": job_a, "b": job_b, "c": job_c},
        )

        graph = WorkflowGraph()
        graph.add_workflow(workflow)
        order = graph.topological_sort()

        assert order.index("CI/a") < order.index("CI/b") < order.index("CI/c")

    def test_detect_cycles(self) -> None:
        """Test cycle detection in workflow graph."""
        # Note: GitHub Actions jobs can't have cycles, but we test the detection
        graph = WorkflowGraph()
        graph.nodes["a"] = DependencyNode(name="a", type="job", depends_on=["b"], file_path="", line=0)
        graph.nodes["b"] = DependencyNode(name="b", type="job", depends_on=["a"], file_path="", line=0)
        graph.edges = [("a", "b"), ("b", "a")]

        cycles = graph.detect_cycles()
        assert len(cycles) >= 1


class TestMermaidGeneration:
    """Tests for Mermaid diagram generation."""

    def test_to_mermaid_single_workflow(self) -> None:
        """Test generating Mermaid diagram for single workflow."""
        job_a = Job(runs_on="ubuntu-latest", steps=[Step(run="echo a")])
        job_b = Job(runs_on="ubuntu-latest", steps=[Step(run="echo b")], needs="build")

        workflow = Workflow(
            name="CI",
            on=Triggers(),
            jobs={"build": job_a, "test": job_b},
        )

        graph = WorkflowGraph()
        graph.add_workflow(workflow)
        mermaid = graph.to_mermaid()

        assert "graph TD" in mermaid
        assert "CI_build" in mermaid or "build" in mermaid
        assert "-->" in mermaid

    def test_to_mermaid_multiple_workflows(self) -> None:
        """Test generating Mermaid diagram for multiple workflows."""
        job_a = Job(runs_on="ubuntu-latest", steps=[Step(run="echo a")])
        job_b = Job(runs_on="ubuntu-latest", steps=[Step(run="echo b")])

        workflow1 = Workflow(name="CI", on=Triggers(), jobs={"build": job_a})
        workflow2 = Workflow(name="Deploy", on=Triggers(), jobs={"deploy": job_b})

        graph = WorkflowGraph()
        graph.add_workflow(workflow1)
        graph.add_workflow(workflow2)
        mermaid = graph.to_mermaid()

        assert "subgraph" in mermaid
        assert "CI" in mermaid
        assert "Deploy" in mermaid


class TestDotGeneration:
    """Tests for DOT/Graphviz generation."""

    def test_to_dot_single_workflow(self) -> None:
        """Test generating DOT diagram for single workflow."""
        job_a = Job(runs_on="ubuntu-latest", steps=[Step(run="echo a")])
        job_b = Job(runs_on="ubuntu-latest", steps=[Step(run="echo b")], needs="build")

        workflow = Workflow(
            name="CI",
            on=Triggers(),
            jobs={"build": job_a, "test": job_b},
        )

        graph = WorkflowGraph()
        graph.add_workflow(workflow)
        dot = graph.to_dot()

        assert "digraph G {" in dot
        assert "}" in dot
        assert "->" in dot

    def test_to_dot_multiple_workflows(self) -> None:
        """Test generating DOT diagram for multiple workflows."""
        job_a = Job(runs_on="ubuntu-latest", steps=[Step(run="echo a")])
        job_b = Job(runs_on="ubuntu-latest", steps=[Step(run="echo b")])

        workflow1 = Workflow(name="CI", on=Triggers(), jobs={"build": job_a})
        workflow2 = Workflow(name="Deploy", on=Triggers(), jobs={"deploy": job_b})

        graph = WorkflowGraph()
        graph.add_workflow(workflow1)
        graph.add_workflow(workflow2)
        dot = graph.to_dot()

        assert "subgraph cluster_" in dot
