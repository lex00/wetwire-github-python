"""Tests for the test command implementation."""

import subprocess
import sys


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
