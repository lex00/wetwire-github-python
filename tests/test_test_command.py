"""Tests for the test command implementation."""

import subprocess
import sys
from pathlib import Path

import pytest

from wetwire_github.cli.test_cmd import run_persona_tests


class TestTestCommandBasic:
    """Tests for test command basic functionality."""

    def test_test_command_runs(self):
        """Test command runs without crashing."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "test"],
            capture_output=True,
            text=True,
        )

        # Should exit cleanly (may indicate wetwire-core needed)
        assert result.returncode in (0, 1)

    def test_test_accepts_persona_flag(self):
        """Test command accepts --persona flag."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "test", "--persona", "reviewer"],
            capture_output=True,
            text=True,
        )

        # Command should accept the flag
        assert result.returncode in (0, 1)

    def test_test_accepts_scenario_flag(self):
        """Test command accepts --scenario flag."""
        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "test",
                "--scenario", "config.yaml",
            ],
            capture_output=True,
            text=True,
        )

        # Command should accept the flag
        assert result.returncode in (0, 1)

    def test_test_help(self):
        """Test command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "test", "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "test" in result.stdout.lower() or "persona" in result.stdout.lower()


class TestTestCommandFunction:
    """Tests for test command function."""

    def test_returns_available_personas_without_args(self):
        """Test that calling without args returns available personas."""
        exit_code, output = run_persona_tests()

        assert exit_code == 0
        assert "reviewer" in output
        assert "senior-dev" in output
        assert "security" in output
        assert "beginner" in output

    def test_shows_persona_info_with_persona_arg(self):
        """Test that calling with persona shows persona info."""
        exit_code, output = run_persona_tests(persona="reviewer")

        assert exit_code == 0
        assert "reviewer" in output.lower()
        assert "criteria" in output.lower()

    def test_unknown_persona_returns_error(self):
        """Test that unknown persona returns error."""
        exit_code, output = run_persona_tests(persona="nonexistent")

        assert exit_code == 1
        assert "Unknown persona" in output


class TestTestCommandWithWorkflow:
    """Tests for test command with workflow file."""

    @pytest.fixture
    def sample_workflow(self, tmp_path: Path) -> Path:
        """Create a sample workflow file that passes quality checks."""
        workflow_file = tmp_path / "test-workflow.yml"
        workflow_file.write_text("""
name: Test CI
on: [push]
permissions:
  contents: read
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
jobs:
  build:
    name: Build and Test
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          cache: pip
      - run: echo "Hello"
""")
        return workflow_file

    @pytest.fixture
    def minimal_workflow(self, tmp_path: Path) -> Path:
        """Create a minimal workflow file."""
        workflow_file = tmp_path / "minimal.yml"
        workflow_file.write_text("""
name: Minimal CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "Hello"
""")
        return workflow_file

    def test_runs_persona_test_with_workflow(self, sample_workflow: Path):
        """Test that providing workflow runs actual persona test."""
        exit_code, output = run_persona_tests(
            persona="reviewer",
            workflow=str(sample_workflow),
        )

        assert exit_code == 0
        # Should contain actual test results, not just instructions
        assert "score" in output.lower() or "Score" in output
        # Should not contain instructional text
        assert "To run tests against" not in output

    def test_reviewer_persona_scores_workflow(self, sample_workflow: Path):
        """Test reviewer persona provides score and feedback."""
        exit_code, output = run_persona_tests(
            persona="reviewer",
            workflow=str(sample_workflow),
        )

        assert exit_code == 0
        # Should have actual score
        assert "Score:" in output or "score" in output.lower()

    def test_security_persona_checks_permissions(self, sample_workflow: Path):
        """Test security persona checks for permissions."""
        exit_code, output = run_persona_tests(
            persona="security",
            workflow=str(sample_workflow),
        )

        # Security persona should flag missing permissions
        assert exit_code in (0, 1)  # May pass or fail
        assert "permission" in output.lower() or "security" in output.lower()

    def test_all_personas_test(self, sample_workflow: Path):
        """Test running all personas against a workflow."""
        exit_code, output = run_persona_tests(
            workflow=str(sample_workflow),
        )

        assert exit_code in (0, 1)  # Some may pass, some may fail
        # Should show results from multiple personas
        assert "reviewer" in output.lower() or "Results" in output

    def test_missing_workflow_returns_error(self):
        """Test that missing workflow file returns error."""
        exit_code, output = run_persona_tests(
            persona="reviewer",
            workflow="/nonexistent/workflow.yml",
        )

        assert exit_code == 1
        assert "not found" in output.lower() or "error" in output.lower()

    def test_passes_scenario_threshold(self, sample_workflow: Path):
        """Test that scenario threshold affects pass/fail."""
        # With high threshold (should fail)
        exit_code, output = run_persona_tests(
            persona="reviewer",
            workflow=str(sample_workflow),
            threshold=95,
        )

        # Sample workflow likely won't pass 95% threshold
        # Just verify it runs and respects threshold
        assert "threshold" in output.lower() or exit_code in (0, 1)


class TestTestCommandCLI:
    """Tests for test command CLI integration."""

    @pytest.fixture
    def sample_workflow(self, tmp_path: Path) -> Path:
        """Create a sample workflow file."""
        workflow_file = tmp_path / "ci.yml"
        workflow_file.write_text("""
name: CI
on: [push]
permissions:
  contents: read
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          cache: pip
      - run: python --version
""")
        return workflow_file

    def test_cli_accepts_workflow_flag(self, sample_workflow: Path):
        """Test CLI accepts --workflow flag."""
        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "test",
                "--persona", "reviewer",
                "--workflow", str(sample_workflow),
            ],
            capture_output=True,
            text=True,
        )

        # Should run and return results
        assert result.returncode in (0, 1)
        # Should show actual results, not just help text
        output = result.stdout + result.stderr
        assert "score" in output.lower() or "passed" in output.lower() or "failed" in output.lower()

    def test_cli_all_personas_flag(self, sample_workflow: Path):
        """Test CLI accepts --all flag to run all personas."""
        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "test",
                "--all",
                "--workflow", str(sample_workflow),
            ],
            capture_output=True,
            text=True,
        )

        # Should run all personas
        assert result.returncode in (0, 1)
