"""Tests for the init command."""

import subprocess
import sys

from wetwire_github.cli.init_cmd import _sanitize_name, init_project


class TestSanitizeName:
    """Tests for name sanitization."""

    def test_sanitize_simple_name(self):
        """Simple names pass through."""
        assert _sanitize_name("myproject") == "myproject"

    def test_sanitize_hyphen_to_underscore(self):
        """Hyphens convert to underscores."""
        assert _sanitize_name("my-project") == "my_project"

    def test_sanitize_space_to_underscore(self):
        """Spaces convert to underscores."""
        assert _sanitize_name("my project") == "my_project"

    def test_sanitize_removes_invalid_chars(self):
        """Invalid characters are removed."""
        assert _sanitize_name("my@project!") == "myproject"

    def test_sanitize_leading_digit(self):
        """Leading digits get underscore prefix."""
        assert _sanitize_name("123project") == "_123project"

    def test_sanitize_empty_returns_default(self):
        """Empty string returns default name."""
        assert _sanitize_name("") == "my_project"
        assert _sanitize_name("@#$") == "my_project"


class TestInitProject:
    """Tests for init_project function."""

    def test_init_creates_structure(self, tmp_path):
        """Init creates expected directory structure."""
        exit_code, messages = init_project(
            name="test-project",
            output_dir=str(tmp_path),
        )

        assert exit_code == 0
        assert (tmp_path / "ci").is_dir()
        assert (tmp_path / "ci" / "__init__.py").is_file()
        assert (tmp_path / "ci" / "workflows.py").is_file()
        assert (tmp_path / ".github" / "workflows").is_dir()
        assert (tmp_path / "pyproject.toml").is_file()
        assert (tmp_path / "README.md").is_file()

    def test_init_uses_directory_name_when_no_name(self, tmp_path):
        """Init uses output directory name when no name given."""
        project_dir = tmp_path / "my-awesome-project"
        project_dir.mkdir()

        exit_code, messages = init_project(
            name=None,
            output_dir=str(project_dir),
        )

        assert exit_code == 0
        # Check pyproject.toml contains the directory name
        pyproject = (project_dir / "pyproject.toml").read_text()
        assert 'name = "my-awesome-project"' in pyproject

    def test_init_skips_existing_files(self, tmp_path):
        """Init doesn't overwrite existing files."""
        # Create existing pyproject.toml
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("existing content")

        exit_code, messages = init_project(
            name="test-project",
            output_dir=str(tmp_path),
        )

        assert exit_code == 0
        assert pyproject.read_text() == "existing content"
        assert any("Skipped" in msg for msg in messages)

    def test_init_creates_gitkeep(self, tmp_path):
        """Init creates .gitkeep in workflows directory."""
        exit_code, messages = init_project(
            name="test-project",
            output_dir=str(tmp_path),
        )

        assert exit_code == 0
        assert (tmp_path / ".github" / "workflows" / ".gitkeep").is_file()

    def test_init_workflows_template_valid_python(self, tmp_path):
        """Generated workflows.py is valid Python."""
        exit_code, messages = init_project(
            name="test-project",
            output_dir=str(tmp_path),
        )

        assert exit_code == 0

        # Check it's valid Python by compiling it
        workflows_file = tmp_path / "ci" / "workflows.py"
        source = workflows_file.read_text()
        compile(source, str(workflows_file), "exec")

    def test_init_messages_contain_next_steps(self, tmp_path):
        """Init output includes next steps."""
        exit_code, messages = init_project(
            name="test-project",
            output_dir=str(tmp_path),
        )

        assert exit_code == 0
        message_text = "\n".join(messages)
        assert "Next steps" in message_text


class TestInitCommandCLI:
    """Tests for init command via CLI."""

    def test_init_command_runs(self, tmp_path):
        """Init command runs successfully."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_github.cli",
                "init",
                "--output",
                str(tmp_path),
                "my-project",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert (tmp_path / "ci" / "workflows.py").exists()

    def test_init_command_help(self):
        """Init command has help text."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "init", "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Create new project" in result.stdout or "Scaffold" in result.stdout
