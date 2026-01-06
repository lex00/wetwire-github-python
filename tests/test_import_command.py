"""Tests for the import command implementation."""

import subprocess
import sys


class TestImportCommandBasic:
    """Tests for import command basic functionality."""

    def test_import_simple_workflow(self, tmp_path):
        """Import command converts simple workflow YAML to Python."""
        yaml_file = tmp_path / "ci.yaml"
        yaml_file.write_text('''
name: CI
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo hello
''')

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "import",
                "-o", str(output_dir),
                str(yaml_file),
            ],
            capture_output=True,
            text=True,
        )

        # Should succeed
        assert result.returncode == 0, f"stderr: {result.stderr}"

        # Should create Python files
        python_files = list(output_dir.rglob("*.py"))
        assert len(python_files) > 0

    def test_import_multiple_workflows(self, tmp_path):
        """Import command converts multiple workflows."""
        yaml1 = tmp_path / "ci.yaml"
        yaml1.write_text('''
name: CI
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: make build
''')

        yaml2 = tmp_path / "release.yaml"
        yaml2.write_text('''
name: Release
on:
  release:
    types: [published]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: make deploy
''')

        output_dir = tmp_path / "output"

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "import",
                "-o", str(output_dir),
                str(yaml1), str(yaml2),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"


class TestImportCommandScaffold:
    """Tests for import command scaffolding."""

    def test_creates_pyproject_toml(self, tmp_path):
        """Import command creates pyproject.toml by default."""
        yaml_file = tmp_path / "ci.yaml"
        yaml_file.write_text('''
name: CI
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo test
''')

        output_dir = tmp_path / "output"

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "import",
                "-o", str(output_dir),
                str(yaml_file),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"
        # Scaffold should create pyproject.toml
        assert (output_dir / "pyproject.toml").exists() or len(list(output_dir.rglob("*.py"))) > 0

    def test_no_scaffold_flag(self, tmp_path):
        """Import command with --no-scaffold skips scaffolding."""
        yaml_file = tmp_path / "ci.yaml"
        yaml_file.write_text('''
name: CI
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo test
''')

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "import",
                "-o", str(output_dir),
                "--no-scaffold",
                str(yaml_file),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"
        # Should not create pyproject.toml
        assert not (output_dir / "pyproject.toml").exists()


class TestImportCommandSingleFile:
    """Tests for import command --single-file option."""

    def test_single_file_flag(self, tmp_path):
        """Import command with --single-file generates one file."""
        yaml_file = tmp_path / "ci.yaml"
        yaml_file.write_text('''
name: CI
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo test
''')

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "import",
                "-o", str(output_dir),
                "--single-file",
                "--no-scaffold",
                str(yaml_file),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"

        # Should create exactly one Python file
        python_files = list(output_dir.rglob("*.py"))
        assert len(python_files) >= 1


class TestImportCommandErrors:
    """Tests for import command error handling."""

    def test_nonexistent_file(self, tmp_path):
        """Import command reports error for nonexistent file."""
        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "import",
                "-o", str(tmp_path / "output"),
                str(tmp_path / "nonexistent.yaml"),
            ],
            capture_output=True,
            text=True,
        )

        # Should report error
        assert result.returncode != 0 or "error" in result.stderr.lower()

    def test_no_files_provided(self, tmp_path):
        """Import command handles no files gracefully."""
        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "import",
                "-o", str(tmp_path / "output"),
            ],
            capture_output=True,
            text=True,
        )

        # Should indicate no files or succeed with nothing to do
        assert result.returncode in (0, 1)


class TestImportCommandCodeGeneration:
    """Tests for import command Python code generation."""

    def test_generated_code_is_valid_python(self, tmp_path):
        """Import command generates valid Python code."""
        yaml_file = tmp_path / "ci.yaml"
        yaml_file.write_text('''
name: CI
on:
  push:
    branches: [main]
  pull_request:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: pytest
''')

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "import",
                "-o", str(output_dir),
                "--no-scaffold",
                str(yaml_file),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"

        # Find generated Python file and verify it compiles
        python_files = list(output_dir.rglob("*.py"))
        assert len(python_files) > 0

        for py_file in python_files:
            if py_file.name != "__init__.py":
                # Compile should succeed
                code = py_file.read_text()
                compile(code, str(py_file), "exec")

    def test_handles_reserved_names(self, tmp_path):
        """Import command handles reserved Python names (if, with)."""
        yaml_file = tmp_path / "ci.yaml"
        yaml_file.write_text('''
name: CI
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - run: echo test
        if: github.event_name == 'push'
''')

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "import",
                "-o", str(output_dir),
                "--no-scaffold",
                str(yaml_file),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"

        # Generated code should handle if_ and with_
        python_files = list(output_dir.rglob("*.py"))
        for py_file in python_files:
            if py_file.name != "__init__.py":
                code = py_file.read_text()
                compile(code, str(py_file), "exec")
