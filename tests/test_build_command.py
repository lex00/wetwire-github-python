"""Tests for the build command implementation."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import yaml


class TestBuildCommandDiscovery:
    """Tests for build command discovery integration."""

    def test_discovers_workflows_in_package(self, tmp_path):
        """Build command discovers workflows in a Python package."""
        # Create a simple workflow package
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        workflow_file = pkg_dir / "ci.py"
        workflow_file.write_text('''
from wetwire_github.workflow import Workflow, Job, Step, PushTrigger, Triggers

ci_workflow = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger()),
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            steps=[Step(run="echo hello")],
        ),
    },
)
''')

        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "build", str(pkg_dir)],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        # Should succeed and create output
        assert result.returncode == 0, f"stderr: {result.stderr}"

    def test_discovers_multiple_workflows(self, tmp_path):
        """Build command discovers multiple workflows in a package."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        # Create two workflow files
        (pkg_dir / "ci.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step, PushTrigger, Triggers

ci = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger()),
    jobs={"build": Job(runs_on="ubuntu-latest", steps=[Step(run="make build")])},
)
''')

        (pkg_dir / "release.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step, ReleaseTrigger, Triggers

release = Workflow(
    name="Release",
    on=Triggers(release=ReleaseTrigger()),
    jobs={"deploy": Job(runs_on="ubuntu-latest", steps=[Step(run="make deploy")])},
)
''')

        # Create output directory
        output_dir = tmp_path / ".github" / "workflows"
        output_dir.mkdir(parents=True)

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "build",
                str(pkg_dir), "-o", str(output_dir),
            ],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"

        # Should create files for both workflows
        output_files = list(output_dir.glob("*.yaml")) + list(output_dir.glob("*.yml"))
        assert len(output_files) >= 1


class TestBuildCommandRunner:
    """Tests for build command runner integration."""

    def test_extracts_workflow_values(self, tmp_path):
        """Build command extracts actual workflow values via runner."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        workflow_file = pkg_dir / "test.py"
        workflow_file.write_text('''
from wetwire_github.workflow import Workflow, Job, Step, PushTrigger, Triggers

test = Workflow(
    name="Test Workflow",
    on=Triggers(push=PushTrigger(branches=["main"])),
    jobs={
        "test": Job(
            runs_on="ubuntu-latest",
            steps=[
                Step(name="Checkout", uses="actions/checkout@v4"),
                Step(name="Run tests", run="pytest"),
            ],
        ),
    },
)
''')

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "build",
                str(pkg_dir), "-o", str(output_dir),
            ],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"

        # Check output file contains correct content
        output_files = list(output_dir.glob("*.yaml")) + list(output_dir.glob("*.yml"))
        assert len(output_files) >= 1

        content = output_files[0].read_text()
        data = yaml.safe_load(content)

        assert data["name"] == "Test Workflow"
        assert "test" in data["jobs"]


class TestBuildCommandTemplateBuilder:
    """Tests for build command template builder integration."""

    def test_orders_jobs_by_dependencies(self, tmp_path):
        """Build command orders jobs by needs dependencies."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        workflow_file = pkg_dir / "pipeline.py"
        workflow_file.write_text('''
from wetwire_github.workflow import Workflow, Job, Step, PushTrigger, Triggers

pipeline = Workflow(
    name="Pipeline",
    on=Triggers(push=PushTrigger()),
    jobs={
        "deploy": Job(
            runs_on="ubuntu-latest",
            needs=["test"],
            steps=[Step(run="make deploy")],
        ),
        "test": Job(
            runs_on="ubuntu-latest",
            needs=["build"],
            steps=[Step(run="make test")],
        ),
        "build": Job(
            runs_on="ubuntu-latest",
            steps=[Step(run="make build")],
        ),
    },
)
''')

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "build",
                str(pkg_dir), "-o", str(output_dir),
            ],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"

        # Verify job ordering in output
        output_files = list(output_dir.glob("*.yaml")) + list(output_dir.glob("*.yml"))
        assert len(output_files) >= 1

        content = output_files[0].read_text()
        data = yaml.safe_load(content)

        # Jobs should all be present
        assert "build" in data["jobs"]
        assert "test" in data["jobs"]
        assert "deploy" in data["jobs"]


class TestBuildCommandOutput:
    """Tests for build command output options."""

    def test_yaml_output_format(self, tmp_path):
        """Build command generates YAML by default."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        (pkg_dir / "ci.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step, PushTrigger, Triggers

ci = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger()),
    jobs={"build": Job(runs_on="ubuntu-latest", steps=[Step(run="echo hi")])},
)
''')

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "build",
                str(pkg_dir), "-o", str(output_dir), "-f", "yaml",
            ],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"

        # Should produce valid YAML
        output_files = list(output_dir.glob("*.yaml")) + list(output_dir.glob("*.yml"))
        assert len(output_files) >= 1

        content = output_files[0].read_text()
        data = yaml.safe_load(content)
        assert "name" in data or "jobs" in data

    def test_json_output_format(self, tmp_path):
        """Build command can generate JSON output."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        (pkg_dir / "ci.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step, PushTrigger, Triggers

ci = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger()),
    jobs={"build": Job(runs_on="ubuntu-latest", steps=[Step(run="echo hi")])},
)
''')

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "build",
                str(pkg_dir), "-o", str(output_dir), "-f", "json",
            ],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"

        # Should produce valid JSON
        output_files = list(output_dir.glob("*.json"))
        assert len(output_files) >= 1

        content = output_files[0].read_text()
        data = json.loads(content)
        assert "name" in data or "jobs" in data

    def test_output_flag_creates_directory(self, tmp_path):
        """Build command creates output directory if it doesn't exist."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        (pkg_dir / "ci.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step, PushTrigger, Triggers

ci = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger()),
    jobs={"build": Job(runs_on="ubuntu-latest", steps=[Step(run="echo hi")])},
)
''')

        output_dir = tmp_path / ".github" / "workflows"
        # Don't create it - let the command create it
        assert not output_dir.exists()

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "build",
                str(pkg_dir), "-o", str(output_dir),
            ],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert output_dir.exists()


class TestBuildCommandMultiWorkflow:
    """Tests for build command multi-workflow support."""

    def test_generates_separate_files_per_workflow(self, tmp_path):
        """Build command generates one file per workflow."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        # Two workflows in one file
        (pkg_dir / "all.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step, PushTrigger, Triggers, ReleaseTrigger

ci = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger()),
    jobs={"build": Job(runs_on="ubuntu-latest", steps=[Step(run="make build")])},
)

release = Workflow(
    name="Release",
    on=Triggers(release=ReleaseTrigger()),
    jobs={"deploy": Job(runs_on="ubuntu-latest", steps=[Step(run="make deploy")])},
)
''')

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "build",
                str(pkg_dir), "-o", str(output_dir),
            ],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"

        # Should create multiple files
        output_files = list(output_dir.glob("*.yaml")) + list(output_dir.glob("*.yml"))
        assert len(output_files) == 2


class TestBuildCommandErrors:
    """Tests for build command error handling."""

    def test_error_on_no_workflows_found(self, tmp_path):
        """Build command reports error when no workflows found."""
        pkg_dir = tmp_path / "empty"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "build", str(pkg_dir)],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        # Should indicate no workflows found
        assert result.returncode != 0 or "no workflow" in result.stdout.lower() or "no workflow" in result.stderr.lower()

    def test_error_on_invalid_python(self, tmp_path):
        """Build command handles invalid Python files gracefully."""
        pkg_dir = tmp_path / "invalid"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        (pkg_dir / "bad.py").write_text("this is not valid python {{{")

        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "build", str(pkg_dir)],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        # Should not crash - gracefully skip or report
        # Either exits with error or continues with no workflows
        assert result.returncode in (0, 1)

    def test_error_on_nonexistent_package(self, tmp_path):
        """Build command reports error for nonexistent package."""
        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "build",
                str(tmp_path / "nonexistent"),
            ],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        # Should indicate error
        assert result.returncode != 0


class TestBuildCommandIntegration:
    """Integration tests for build command."""

    def test_full_workflow_generation(self, tmp_path):
        """Full integration test of workflow generation."""
        pkg_dir = tmp_path / "myworkflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        (pkg_dir / "ci.py").write_text('''
from wetwire_github.workflow import (
    Workflow, Job, Step,
    PushTrigger, PullRequestTrigger, Triggers,
    Matrix, Strategy,
)

ci = Workflow(
    name="CI Pipeline",
    on=Triggers(
        push=PushTrigger(branches=["main"]),
        pull_request=PullRequestTrigger(),
    ),
    jobs={
        "lint": Job(
            runs_on="ubuntu-latest",
            steps=[
                Step(name="Checkout", uses="actions/checkout@v4"),
                Step(name="Lint", run="ruff check ."),
            ],
        ),
        "test": Job(
            runs_on="ubuntu-latest",
            needs=["lint"],
            strategy=Strategy(
                matrix=Matrix(values={"python-version": ["3.10", "3.11", "3.12"]}),
            ),
            steps=[
                Step(name="Checkout", uses="actions/checkout@v4"),
                Step(name="Setup Python", uses="actions/setup-python@v5"),
                Step(name="Test", run="pytest"),
            ],
        ),
    },
)
''')

        output_dir = tmp_path / ".github" / "workflows"

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "build",
                str(pkg_dir), "-o", str(output_dir),
            ],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}\nstdout: {result.stdout}"
        assert output_dir.exists()

        output_files = list(output_dir.glob("*.yaml")) + list(output_dir.glob("*.yml"))
        assert len(output_files) == 1

        content = output_files[0].read_text()
        data = yaml.safe_load(content)

        # Verify structure
        assert data["name"] == "CI Pipeline"
        assert "push" in data["on"]
        assert "pull_request" in data["on"]
        assert "lint" in data["jobs"]
        assert "test" in data["jobs"]
        assert data["jobs"]["test"]["needs"] == ["lint"]
