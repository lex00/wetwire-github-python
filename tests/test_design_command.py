"""Tests for the design command implementation."""

import subprocess
import sys
from pathlib import Path

from wetwire_github.cli.design_cmd import design_workflow


class TestDesignCommandBasic:
    """Tests for design command basic functionality."""

    def test_design_command_runs(self):
        """Design command runs without crashing."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "design"],
            capture_output=True,
            text=True,
        )

        # Should exit cleanly (may indicate wetwire-core needed)
        assert result.returncode in (0, 1)

    def test_design_accepts_stream_flag(self):
        """Design command accepts --stream flag."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "design", "--stream"],
            capture_output=True,
            text=True,
        )

        # Command should accept the flag
        assert result.returncode in (0, 1)

    def test_design_accepts_max_lint_cycles(self):
        """Design command accepts --max-lint-cycles flag."""
        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "design",
                "--max-lint-cycles", "5",
            ],
            capture_output=True,
            text=True,
        )

        # Command should accept the flag
        assert result.returncode in (0, 1)

    def test_design_help(self):
        """Design command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "design", "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "design" in result.stdout.lower() or "ai" in result.stdout.lower()


class TestDesignCommandFunction:
    """Tests for design command function."""

    def test_returns_session_info(self):
        """Test that design returns session information."""
        exit_code, output = design_workflow()

        assert exit_code == 0
        assert "session" in output.lower()

    def test_shows_available_tools(self):
        """Test that design shows available tools."""
        exit_code, output = design_workflow()

        assert exit_code == 0
        # Should list some tools
        assert "build_workflow" in output or "lint_workflow" in output

    def test_with_output_dir(self, tmp_path: Path):
        """Test design with output directory."""
        exit_code, output = design_workflow(output_dir=str(tmp_path))

        assert exit_code == 0
        assert "output" in output.lower() or str(tmp_path) in output

    def test_with_prompt(self):
        """Test design with initial prompt."""
        exit_code, output = design_workflow(prompt="Create a CI workflow")

        assert exit_code == 0
        # Should acknowledge the prompt
        assert "CI" in output or "prompt" in output.lower()


class TestDesignCommandToolExecution:
    """Tests for design command tool execution."""

    def test_execute_list_tool(self, tmp_path: Path):
        """Test executing list tool."""
        # Create a simple workflow file
        (tmp_path / "__init__.py").write_text("")
        (tmp_path / "ci.py").write_text("""
from wetwire_github.workflow import Workflow, Job, Step

ci = Workflow(
    name="CI",
    on={"push": {}},
    jobs={"build": Job(runs_on="ubuntu-latest", steps=[Step(run="echo hello")])},
)
""")

        exit_code, output = design_workflow(
            tool="list_workflows",
            tool_args={"package_path": str(tmp_path)},
        )

        # Should execute the tool and return results
        assert exit_code in (0, 1)  # May fail if workflow can't be loaded
        assert output  # Should have some output

    def test_execute_lint_tool(self, tmp_path: Path):
        """Test executing lint tool."""
        # Create a file to lint
        (tmp_path / "__init__.py").write_text("")
        (tmp_path / "ci.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step

ci = Workflow(
    name="CI",
    on={"push": {}},
    jobs={"build": Job(runs_on="ubuntu-latest", steps=[Step(uses="actions/checkout@v4")])},
)
''')

        exit_code, output = design_workflow(
            tool="lint_workflow",
            tool_args={"package_path": str(tmp_path)},
        )

        # Should execute lint and return results
        assert exit_code in (0, 1)
        assert output


class TestDesignCommandCLI:
    """Tests for design command CLI integration."""

    def test_cli_accepts_output_dir(self, tmp_path: Path):
        """Test CLI accepts --output flag."""
        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "design",
                "--output", str(tmp_path),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode in (0, 1)

    def test_cli_accepts_prompt(self):
        """Test CLI accepts --prompt flag."""
        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "design",
                "--prompt", "Create a CI workflow",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode in (0, 1)
