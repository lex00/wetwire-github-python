"""Tests for the design command implementation."""

import subprocess
import sys


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
