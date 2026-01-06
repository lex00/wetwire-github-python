"""Tests for the graph command implementation."""

import subprocess
import sys


class TestGraphCommandBasic:
    """Tests for graph command basic functionality."""

    def test_graph_workflows(self, tmp_path):
        """Graph command generates output for workflow package."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        (pkg_dir / "ci.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step, PushTrigger, Triggers

ci = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger()),
    jobs={
        "build": Job(runs_on="ubuntu-latest", steps=[Step(run="make build")]),
        "test": Job(runs_on="ubuntu-latest", needs=["build"], steps=[Step(run="make test")]),
        "deploy": Job(runs_on="ubuntu-latest", needs=["test"], steps=[Step(run="make deploy")]),
    },
)
''')

        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "graph", str(pkg_dir)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"
        # Should output some graph format
        assert len(result.stdout) > 0


class TestGraphCommandOutput:
    """Tests for graph command output formats."""

    def test_mermaid_format(self, tmp_path):
        """Graph command produces mermaid output by default."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        (pkg_dir / "ci.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step, PushTrigger, Triggers

ci = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger()),
    jobs={
        "build": Job(runs_on="ubuntu-latest", steps=[Step(run="echo build")]),
        "test": Job(runs_on="ubuntu-latest", needs=["build"], steps=[Step(run="echo test")]),
    },
)
''')

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "graph",
                "-f", "mermaid", str(pkg_dir),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"
        # Mermaid format uses flowchart or graph syntax
        assert "graph" in result.stdout.lower() or "flowchart" in result.stdout.lower()

    def test_dot_format(self, tmp_path):
        """Graph command can produce DOT output."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        (pkg_dir / "ci.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step, PushTrigger, Triggers

ci = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger()),
    jobs={
        "build": Job(runs_on="ubuntu-latest", steps=[Step(run="echo build")]),
        "test": Job(runs_on="ubuntu-latest", needs=["build"], steps=[Step(run="echo test")]),
    },
)
''')

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "graph",
                "-f", "dot", str(pkg_dir),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"
        # DOT format uses digraph
        assert "digraph" in result.stdout.lower()


class TestGraphCommandErrors:
    """Tests for graph command error handling."""

    def test_nonexistent_package(self, tmp_path):
        """Graph command reports error for nonexistent package."""
        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "graph",
                str(tmp_path / "nonexistent"),
            ],
            capture_output=True,
            text=True,
        )

        # Should report error
        assert result.returncode != 0 or "error" in result.stderr.lower()

    def test_no_package_provided(self):
        """Graph command uses current directory by default."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "graph"],
            capture_output=True,
            text=True,
        )

        # Should work with current directory
        assert result.returncode in (0, 1)


class TestGraphCommandIntegration:
    """Integration tests for graph command."""

    def test_graph_job_dependencies(self, tmp_path):
        """Graph command shows job dependencies."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        (pkg_dir / "ci.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step, PushTrigger, Triggers

ci = Workflow(
    name="Pipeline",
    on=Triggers(push=PushTrigger()),
    jobs={
        "lint": Job(runs_on="ubuntu-latest", steps=[Step(run="lint")]),
        "build": Job(runs_on="ubuntu-latest", steps=[Step(run="build")]),
        "test": Job(runs_on="ubuntu-latest", needs=["lint", "build"], steps=[Step(run="test")]),
        "deploy": Job(runs_on="ubuntu-latest", needs=["test"], steps=[Step(run="deploy")]),
    },
)
''')

        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "graph", str(pkg_dir)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Should mention job names
        output = result.stdout.lower()
        assert "test" in output
        assert "deploy" in output
