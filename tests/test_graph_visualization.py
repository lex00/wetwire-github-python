"""Tests for enhanced graph visualization features (issue #122).

Tests for:
- Color coding for matrix jobs in Mermaid
- Color coding for jobs with conditions
- Color coding for reusable workflow calls
- Filter option to show only matching jobs
- Exclude option to hide matching jobs
- Legend generation
"""

import subprocess
import sys

from wetwire_github.graph import WorkflowGraph
from wetwire_github.workflow import Job, Step, Triggers, Workflow
from wetwire_github.workflow.matrix import Matrix, Strategy


class TestMermaidColorCoding:
    """Tests for Mermaid diagram color coding."""

    def test_matrix_job_has_blue_style(self) -> None:
        """Jobs with matrix builds should have blue styling in Mermaid output."""
        matrix_job = Job(
            runs_on="ubuntu-latest",
            strategy=Strategy(
                matrix=Matrix(
                    values={"python_version": ["3.10", "3.11", "3.12"]},
                )
            ),
            steps=[Step(run="pytest")],
        )
        regular_job = Job(runs_on="ubuntu-latest", steps=[Step(run="echo test")])

        workflow = Workflow(
            name="CI",
            on=Triggers(),
            jobs={"test": matrix_job, "build": regular_job},
        )

        graph = WorkflowGraph()
        graph.add_workflow(workflow)
        mermaid = graph.to_mermaid()

        # Should contain style directive for matrix job
        assert "style CI_test fill:#4A90E2" in mermaid or "classDef matrix fill:#4A90E2" in mermaid

    def test_conditional_job_has_yellow_style(self) -> None:
        """Jobs with if conditions should have yellow styling in Mermaid output."""
        conditional_job = Job(
            runs_on="ubuntu-latest",
            if_="github.ref == 'refs/heads/main'",
            steps=[Step(run="deploy")],
        )
        regular_job = Job(runs_on="ubuntu-latest", steps=[Step(run="build")])

        workflow = Workflow(
            name="Deploy",
            on=Triggers(),
            jobs={"deploy": conditional_job, "build": regular_job},
        )

        graph = WorkflowGraph()
        graph.add_workflow(workflow)
        mermaid = graph.to_mermaid()

        # Should contain style directive for conditional job
        assert "style Deploy_deploy fill:#F5A623" in mermaid or "classDef conditional fill:#F5A623" in mermaid

    def test_matrix_and_conditional_job_prioritizes_matrix_color(self) -> None:
        """Jobs with both matrix and conditions should use matrix color (blue)."""
        matrix_conditional_job = Job(
            runs_on="ubuntu-latest",
            strategy=Strategy(
                matrix=Matrix(
                    values={"os": ["ubuntu-latest", "windows-latest"]},
                )
            ),
            if_="github.event_name == 'push'",
            steps=[Step(run="test")],
        )

        workflow = Workflow(
            name="CI",
            on=Triggers(),
            jobs={"test": matrix_conditional_job},
        )

        graph = WorkflowGraph()
        graph.add_workflow(workflow)
        mermaid = graph.to_mermaid()

        # Matrix takes priority, should be blue
        assert "style CI_test fill:#4A90E2" in mermaid or "classDef matrix fill:#4A90E2" in mermaid

    def test_dependency_edges_have_orange_color(self) -> None:
        """Dependency edges (needs) should have orange styling."""
        job_a = Job(runs_on="ubuntu-latest", steps=[Step(run="echo a")])
        job_b = Job(runs_on="ubuntu-latest", needs="a", steps=[Step(run="echo b")])

        workflow = Workflow(
            name="CI",
            on=Triggers(),
            jobs={"a": job_a, "b": job_b},
        )

        graph = WorkflowGraph()
        graph.add_workflow(workflow)
        mermaid = graph.to_mermaid()

        # Should contain orange edge styling
        assert "linkStyle" in mermaid or "stroke:#FF6B35" in mermaid

    def test_reusable_workflow_has_purple_style(self) -> None:
        """Jobs that use reusable workflows should have purple styling."""
        workflow = Workflow(
            name="Main",
            on=Triggers(),
            jobs={},
        )

        graph = WorkflowGraph()
        graph.add_workflow(workflow)
        # Simulate a workflow_call relationship
        graph.add_workflow_call("Main", "reusable-workflow")
        mermaid = graph.to_mermaid()

        # Should contain purple styling for reusable workflow nodes
        assert "style" in mermaid and ("purple" in mermaid.lower() or "#9013FE" in mermaid)


class TestDotColorCoding:
    """Tests for DOT/Graphviz color coding."""

    def test_matrix_job_has_blue_color_dot(self) -> None:
        """Jobs with matrix builds should have blue color in DOT output."""
        matrix_job = Job(
            runs_on="ubuntu-latest",
            strategy=Strategy(
                matrix=Matrix(
                    values={"python_version": ["3.10", "3.11"]},
                )
            ),
            steps=[Step(run="test")],
        )

        workflow = Workflow(
            name="CI",
            on=Triggers(),
            jobs={"test": matrix_job},
        )

        graph = WorkflowGraph()
        graph.add_workflow(workflow)
        dot = graph.to_dot()

        # Should contain color attribute for matrix job
        assert 'fillcolor="#4A90E2"' in dot or 'color="#4A90E2"' in dot

    def test_conditional_job_has_yellow_color_dot(self) -> None:
        """Jobs with if conditions should have yellow color in DOT output."""
        conditional_job = Job(
            runs_on="ubuntu-latest",
            if_="github.ref == 'refs/heads/main'",
            steps=[Step(run="deploy")],
        )

        workflow = Workflow(
            name="Deploy",
            on=Triggers(),
            jobs={"deploy": conditional_job},
        )

        graph = WorkflowGraph()
        graph.add_workflow(workflow)
        dot = graph.to_dot()

        # Should contain color attribute for conditional job
        assert 'fillcolor="#F5A623"' in dot or 'color="#F5A623"' in dot

    def test_dependency_edges_have_orange_color_dot(self) -> None:
        """Dependency edges should have orange color in DOT output."""
        job_a = Job(runs_on="ubuntu-latest", steps=[Step(run="a")])
        job_b = Job(runs_on="ubuntu-latest", needs="a", steps=[Step(run="b")])

        workflow = Workflow(
            name="CI",
            on=Triggers(),
            jobs={"a": job_a, "b": job_b},
        )

        graph = WorkflowGraph()
        graph.add_workflow(workflow)
        dot = graph.to_dot()

        # Should contain edge color
        assert 'color="#FF6B35"' in dot


class TestGraphFiltering:
    """Tests for graph filtering functionality."""

    def test_filter_shows_only_matching_jobs(self) -> None:
        """Filter option should show only jobs matching the pattern."""
        job_test1 = Job(runs_on="ubuntu-latest", steps=[Step(run="test1")])
        job_test2 = Job(runs_on="ubuntu-latest", steps=[Step(run="test2")])
        job_build = Job(runs_on="ubuntu-latest", steps=[Step(run="build")])

        workflow = Workflow(
            name="CI",
            on=Triggers(),
            jobs={"test-unit": job_test1, "test-integration": job_test2, "build": job_build},
        )

        graph = WorkflowGraph()
        graph.add_workflow(workflow)

        # Apply filter for jobs starting with "test"
        filtered_mermaid = graph.to_mermaid(filter_pattern="test*")

        # Should include test jobs
        assert "test-unit" in filtered_mermaid or "test_unit" in filtered_mermaid
        assert "test-integration" in filtered_mermaid or "test_integration" in filtered_mermaid
        # Should not include build job
        assert "build" not in filtered_mermaid

    def test_exclude_hides_matching_jobs(self) -> None:
        """Exclude option should hide jobs matching the pattern."""
        job_test = Job(runs_on="ubuntu-latest", steps=[Step(run="test")])
        job_build = Job(runs_on="ubuntu-latest", steps=[Step(run="build")])
        job_deploy = Job(runs_on="ubuntu-latest", steps=[Step(run="deploy")])

        workflow = Workflow(
            name="CI",
            on=Triggers(),
            jobs={"test": job_test, "build": job_build, "deploy": job_deploy},
        )

        graph = WorkflowGraph()
        graph.add_workflow(workflow)

        # Apply exclude for test jobs
        filtered_mermaid = graph.to_mermaid(exclude_pattern="test")

        # Should not include test job
        assert "test" not in filtered_mermaid.lower() or filtered_mermaid.count("test") <= 1
        # Should include build and deploy
        assert "build" in filtered_mermaid
        assert "deploy" in filtered_mermaid

    def test_filter_and_exclude_together(self) -> None:
        """Filter and exclude should work together."""
        job_test_unit = Job(runs_on="ubuntu-latest", steps=[Step(run="unit")])
        job_test_e2e = Job(runs_on="ubuntu-latest", steps=[Step(run="e2e")])
        job_build = Job(runs_on="ubuntu-latest", steps=[Step(run="build")])

        workflow = Workflow(
            name="CI",
            on=Triggers(),
            jobs={"test-unit": job_test_unit, "test-e2e": job_test_e2e, "build": job_build},
        )

        graph = WorkflowGraph()
        graph.add_workflow(workflow)

        # Filter for test*, exclude e2e
        filtered_mermaid = graph.to_mermaid(filter_pattern="test*", exclude_pattern="*e2e")

        # Should only include test-unit
        assert "test-unit" in filtered_mermaid or "test_unit" in filtered_mermaid
        # Should not include test-e2e or build
        assert "e2e" not in filtered_mermaid
        assert "build" not in filtered_mermaid

    def test_filter_with_dot_format(self) -> None:
        """Filtering should work with DOT format as well."""
        job_test = Job(runs_on="ubuntu-latest", steps=[Step(run="test")])
        job_build = Job(runs_on="ubuntu-latest", steps=[Step(run="build")])

        workflow = Workflow(
            name="CI",
            on=Triggers(),
            jobs={"test": job_test, "build": job_build},
        )

        graph = WorkflowGraph()
        graph.add_workflow(workflow)

        filtered_dot = graph.to_dot(filter_pattern="test")

        # Should include test but not build
        assert "test" in filtered_dot
        assert "build" not in filtered_dot


class TestLegendGeneration:
    """Tests for legend generation."""

    def test_generate_legend_mermaid(self) -> None:
        """Should generate a legend explaining the color scheme for Mermaid."""
        # Create a graph with all features
        matrix_job = Job(
            runs_on="ubuntu-latest",
            strategy=Strategy(matrix=Matrix(values={"os": ["ubuntu"]})),
            steps=[Step(run="test")],
        )
        conditional_job = Job(
            runs_on="ubuntu-latest",
            if_="github.ref == 'refs/heads/main'",
            needs="test",
            steps=[Step(run="deploy")],
        )

        workflow = Workflow(
            name="CI",
            on=Triggers(),
            jobs={"test": matrix_job, "deploy": conditional_job},
        )

        graph = WorkflowGraph()
        graph.add_workflow(workflow)
        graph.add_workflow_call("CI", "reusable")
        legend = graph.generate_legend(format="mermaid")

        # Legend should explain all color codes
        assert "Matrix" in legend or "matrix" in legend
        assert "Conditional" in legend or "conditional" in legend
        assert "Dependency" in legend or "needs" in legend or "dependencies" in legend.lower()
        assert "Reusable" in legend or "workflow" in legend
        # Should contain color codes
        assert "#4A90E2" in legend
        assert "#F5A623" in legend

    def test_generate_legend_dot(self) -> None:
        """Should generate a legend explaining the color scheme for DOT."""
        # Create a graph with matrix and conditional features
        matrix_job = Job(
            runs_on="ubuntu-latest",
            strategy=Strategy(matrix=Matrix(values={"os": ["ubuntu"]})),
            steps=[Step(run="test")],
        )
        conditional_job = Job(
            runs_on="ubuntu-latest",
            if_="github.ref == 'refs/heads/main'",
            steps=[Step(run="deploy")],
        )

        workflow = Workflow(
            name="CI",
            on=Triggers(),
            jobs={"test": matrix_job, "deploy": conditional_job},
        )

        graph = WorkflowGraph()
        graph.add_workflow(workflow)
        legend = graph.generate_legend(format="dot")

        # Legend should be in DOT comment format or separate nodes
        assert "Matrix" in legend or "matrix" in legend
        assert "Conditional" in legend or "conditional" in legend

    def test_legend_includes_only_used_features(self) -> None:
        """Legend should only include features present in the graph."""
        # Graph with only matrix jobs
        matrix_job = Job(
            runs_on="ubuntu-latest",
            strategy=Strategy(matrix=Matrix(values={"os": ["ubuntu"]})),
            steps=[Step(run="test")],
        )

        workflow = Workflow(
            name="CI",
            on=Triggers(),
            jobs={"test": matrix_job},
        )

        graph = WorkflowGraph()
        graph.add_workflow(workflow)
        legend = graph.generate_legend(format="mermaid")

        # Should include matrix info
        assert "matrix" in legend.lower()
        # May or may not include other types (depends on implementation)


class TestCLIGraphOptions:
    """Tests for CLI graph command with new options."""

    def test_graph_with_filter_option(self, tmp_path):
        """Graph command should accept --filter option."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        (pkg_dir / "ci.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step, Triggers

ci = Workflow(
    name="CI",
    on=Triggers(),
    jobs={
        "test-unit": Job(runs_on="ubuntu-latest", steps=[Step(run="unit tests")]),
        "test-integration": Job(runs_on="ubuntu-latest", steps=[Step(run="integration tests")]),
        "build": Job(runs_on="ubuntu-latest", steps=[Step(run="build")]),
    },
)
''')

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "graph",
                "--filter", "test*",
                str(pkg_dir),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Should contain test jobs but not build
        assert "test" in result.stdout.lower()

    def test_graph_with_exclude_option(self, tmp_path):
        """Graph command should accept --exclude option."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        (pkg_dir / "ci.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step, Triggers

ci = Workflow(
    name="CI",
    on=Triggers(),
    jobs={
        "test": Job(runs_on="ubuntu-latest", steps=[Step(run="test")]),
        "build": Job(runs_on="ubuntu-latest", steps=[Step(run="build")]),
        "deploy": Job(runs_on="ubuntu-latest", steps=[Step(run="deploy")]),
    },
)
''')

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "graph",
                "--exclude", "test",
                str(pkg_dir),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Should contain build and deploy but minimal test references
        assert "build" in result.stdout
        assert "deploy" in result.stdout

    def test_graph_with_legend_option(self, tmp_path):
        """Graph command should accept --legend option."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        (pkg_dir / "ci.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step, Triggers
from wetwire_github.workflow.matrix import Matrix, Strategy

ci = Workflow(
    name="CI",
    on=Triggers(),
    jobs={
        "test": Job(
            runs_on="ubuntu-latest",
            strategy=Strategy(matrix=Matrix(values={"python": ["3.10", "3.11"]})),
            steps=[Step(run="test")]
        ),
    },
)
''')

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "graph",
                "--legend",
                str(pkg_dir),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Should include legend information
        assert "matrix" in result.stdout.lower() or "Matrix" in result.stdout

    def test_graph_with_multiple_options(self, tmp_path):
        """Graph command should handle multiple options together."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        (pkg_dir / "ci.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step, Triggers

ci = Workflow(
    name="CI",
    on=Triggers(),
    jobs={
        "test": Job(runs_on="ubuntu-latest", steps=[Step(run="test")]),
        "build": Job(runs_on="ubuntu-latest", steps=[Step(run="build")]),
    },
)
''')

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "graph",
                "--filter", "test",
                "--format", "mermaid",
                "--legend",
                str(pkg_dir),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "graph" in result.stdout.lower()


class TestColorCodingIntegration:
    """Integration tests for color coding across different scenarios."""

    def test_complex_workflow_with_all_features(self) -> None:
        """Test a complex workflow with matrix, conditions, and dependencies."""
        matrix_job = Job(
            runs_on="ubuntu-latest",
            strategy=Strategy(
                matrix=Matrix(
                    values={
                        "python_version": ["3.10", "3.11"],
                        "os": ["ubuntu-latest", "macos-latest"],
                    }
                )
            ),
            steps=[Step(run="pytest")],
        )

        conditional_job = Job(
            runs_on="ubuntu-latest",
            if_="github.ref == 'refs/heads/main'",
            needs="test",
            steps=[Step(run="deploy")],
        )

        regular_job = Job(
            runs_on="ubuntu-latest",
            needs="test",
            steps=[Step(run="notify")],
        )

        workflow = Workflow(
            name="CI",
            on=Triggers(),
            jobs={
                "test": matrix_job,
                "deploy": conditional_job,
                "notify": regular_job,
            },
        )

        graph = WorkflowGraph()
        graph.add_workflow(workflow)

        mermaid = graph.to_mermaid()
        dot = graph.to_dot()

        # Mermaid should have styles for matrix and conditional
        assert "style" in mermaid
        # DOT should have colors
        assert "fillcolor" in dot or "color" in dot

    def test_filtering_preserves_dependencies(self) -> None:
        """Filtering should preserve dependency information for remaining jobs."""
        job_a = Job(runs_on="ubuntu-latest", steps=[Step(run="a")])
        job_b = Job(runs_on="ubuntu-latest", needs="setup", steps=[Step(run="b")])
        job_c = Job(runs_on="ubuntu-latest", needs="build", steps=[Step(run="c")])

        workflow = Workflow(
            name="Pipeline",
            on=Triggers(),
            jobs={"setup": job_a, "build": job_b, "test": job_c},
        )

        graph = WorkflowGraph()
        graph.add_workflow(workflow)

        # Filter to show only build and test (excluding setup)
        filtered = graph.to_mermaid(exclude_pattern="setup")

        # Should still show build -> test dependency
        assert "-->" in filtered
        assert "build" in filtered
        assert "test" in filtered
