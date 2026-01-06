"""Tests for template builder with dependency ordering."""

import pytest

from wetwire_github.template import (
    CycleError,
    detect_cycles,
    order_jobs,
    topological_sort,
)


class TestTopologicalSort:
    """Tests for topological_sort function."""

    def test_simple_linear_graph(self):
        """Sort a simple linear dependency graph."""
        # A -> B -> C
        graph = {
            "A": [],
            "B": ["A"],
            "C": ["B"],
        }
        result = topological_sort(graph)
        assert result.index("A") < result.index("B")
        assert result.index("B") < result.index("C")

    def test_diamond_graph(self):
        """Sort a diamond dependency graph."""
        #     A
        #    / \
        #   B   C
        #    \ /
        #     D
        graph = {
            "A": [],
            "B": ["A"],
            "C": ["A"],
            "D": ["B", "C"],
        }
        result = topological_sort(graph)
        assert result.index("A") < result.index("B")
        assert result.index("A") < result.index("C")
        assert result.index("B") < result.index("D")
        assert result.index("C") < result.index("D")

    def test_multiple_roots(self):
        """Sort a graph with multiple roots."""
        graph = {
            "A": [],
            "B": [],
            "C": ["A"],
            "D": ["B"],
        }
        result = topological_sort(graph)
        assert result.index("A") < result.index("C")
        assert result.index("B") < result.index("D")

    def test_empty_graph(self):
        """Sort an empty graph."""
        result = topological_sort({})
        assert result == []

    def test_single_node(self):
        """Sort a single node graph."""
        result = topological_sort({"A": []})
        assert result == ["A"]

    def test_no_dependencies(self):
        """Sort nodes with no dependencies."""
        graph = {
            "A": [],
            "B": [],
            "C": [],
        }
        result = topological_sort(graph)
        assert set(result) == {"A", "B", "C"}


class TestDetectCycles:
    """Tests for detect_cycles function."""

    def test_no_cycle(self):
        """Detect no cycle in acyclic graph."""
        graph = {
            "A": [],
            "B": ["A"],
            "C": ["B"],
        }
        cycles = detect_cycles(graph)
        assert len(cycles) == 0

    def test_simple_cycle(self):
        """Detect simple two-node cycle."""
        # A -> B -> A
        graph = {
            "A": ["B"],
            "B": ["A"],
        }
        cycles = detect_cycles(graph)
        assert len(cycles) >= 1

    def test_self_loop(self):
        """Detect self-referencing cycle."""
        # A -> A
        graph = {
            "A": ["A"],
        }
        cycles = detect_cycles(graph)
        assert len(cycles) >= 1

    def test_longer_cycle(self):
        """Detect longer cycle."""
        # A -> B -> C -> A
        graph = {
            "A": ["B"],
            "B": ["C"],
            "C": ["A"],
        }
        cycles = detect_cycles(graph)
        assert len(cycles) >= 1


class TestCycleError:
    """Tests for CycleError exception."""

    def test_cycle_error_message(self):
        """CycleError includes cycle info in message."""
        error = CycleError(["A", "B", "C", "A"])
        assert "A" in str(error)
        assert "cycle" in str(error).lower()

    def test_cycle_error_has_cycle(self):
        """CycleError stores the cycle."""
        cycle = ["A", "B", "C", "A"]
        error = CycleError(cycle)
        assert error.cycle == cycle


class TestOrderJobs:
    """Tests for order_jobs function."""

    def test_order_jobs_by_needs(self):
        """Order jobs based on 'needs' dependencies."""
        from wetwire_github.workflow import Job

        jobs = {
            "test": Job(runs_on="ubuntu-latest", needs=["build"]),
            "build": Job(runs_on="ubuntu-latest"),
            "deploy": Job(runs_on="ubuntu-latest", needs=["test"]),
        }
        ordered = order_jobs(jobs)
        names = [name for name, _ in ordered]

        assert names.index("build") < names.index("test")
        assert names.index("test") < names.index("deploy")

    def test_order_jobs_with_no_deps(self):
        """Order jobs with no dependencies."""
        from wetwire_github.workflow import Job

        jobs = {
            "job1": Job(runs_on="ubuntu-latest"),
            "job2": Job(runs_on="ubuntu-latest"),
        }
        ordered = order_jobs(jobs)
        names = [name for name, _ in ordered]
        assert set(names) == {"job1", "job2"}

    def test_order_jobs_raises_on_cycle(self):
        """Raise CycleError when jobs have circular dependency."""
        from wetwire_github.workflow import Job

        jobs = {
            "a": Job(runs_on="ubuntu-latest", needs=["b"]),
            "b": Job(runs_on="ubuntu-latest", needs=["a"]),
        }
        with pytest.raises(CycleError):
            order_jobs(jobs)

    def test_order_jobs_returns_job_objects(self):
        """order_jobs returns tuples of (name, Job)."""
        from wetwire_github.workflow import Job

        jobs = {
            "build": Job(runs_on="ubuntu-latest"),
        }
        ordered = order_jobs(jobs)
        assert len(ordered) == 1
        name, job = ordered[0]
        assert name == "build"
        assert isinstance(job, Job)
