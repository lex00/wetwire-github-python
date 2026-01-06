"""Tests for CLI framework."""

import subprocess
import sys


class TestCLIHelp:
    """Tests for CLI help output."""

    def test_help_flag(self):
        """CLI shows help with --help flag."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert (
            "wetwire-github" in result.stdout.lower()
            or "usage" in result.stdout.lower()
        )

    def test_h_flag(self):
        """CLI shows help with -h flag."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "-h"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestVersionCommand:
    """Tests for version command."""

    def test_version_flag(self):
        """CLI shows version with --version flag."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "0.1.0" in result.stdout or "0.1.0" in result.stderr


class TestBuildCommand:
    """Tests for build command stub."""

    def test_build_help(self):
        """Build command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "build", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "build" in result.stdout.lower()

    def test_build_stub(self):
        """Build command stub runs without error."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "build"],
            capture_output=True,
            text=True,
        )
        # Stub should exit with 0 or indicate not implemented
        assert result.returncode in (0, 1)


class TestValidateCommand:
    """Tests for validate command stub."""

    def test_validate_help(self):
        """Validate command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "validate", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "validate" in result.stdout.lower()


class TestListCommand:
    """Tests for list command stub."""

    def test_list_help(self):
        """List command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "list", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestLintCommand:
    """Tests for lint command stub."""

    def test_lint_help(self):
        """Lint command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "lint", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestImportCommand:
    """Tests for import command stub."""

    def test_import_help(self):
        """Import command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "import", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestInitCommand:
    """Tests for init command stub."""

    def test_init_help(self):
        """Init command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "init", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestDesignCommand:
    """Tests for design command stub."""

    def test_design_help(self):
        """Design command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "design", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestTestCommand:
    """Tests for test command stub."""

    def test_test_help(self):
        """Test command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "test", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestGraphCommand:
    """Tests for graph command stub."""

    def test_graph_help(self):
        """Graph command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "graph", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestExitCodes:
    """Tests for exit code semantics."""

    def test_success_exit_code(self):
        """Success returns exit code 0."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_unknown_command_exit_code(self):
        """Unknown command returns exit code 2."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "unknown-command"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2
