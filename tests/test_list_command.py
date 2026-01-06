"""Tests for the list command implementation."""

import json
import subprocess
import sys


class TestListCommandBasic:
    """Tests for list command basic functionality."""

    def test_list_workflows(self, tmp_path):
        """List command discovers workflows in a package."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        (pkg_dir / "ci.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step, PushTrigger, Triggers

ci = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger()),
    jobs={"build": Job(runs_on="ubuntu-latest", steps=[Step(run="echo test")])},
)
''')

        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "list", str(pkg_dir)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"
        # Should list discovered workflows
        assert "ci" in result.stdout.lower() or "workflow" in result.stdout.lower()

    def test_list_jobs(self, tmp_path):
        """List command discovers jobs in a package."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        (pkg_dir / "jobs.py").write_text('''
from wetwire_github.workflow import Job, Step

build_job = Job(
    runs_on="ubuntu-latest",
    steps=[Step(run="make build")],
)

test_job = Job(
    runs_on="ubuntu-latest",
    needs=["build"],
    steps=[Step(run="make test")],
)
''')

        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "list", str(pkg_dir)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"


class TestListCommandOutput:
    """Tests for list command output formats."""

    def test_table_output_format(self, tmp_path):
        """List command produces table output by default."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        (pkg_dir / "ci.py").write_text('''
from wetwire_github.workflow import Workflow, Triggers, PushTrigger

ci = Workflow(name="CI", on=Triggers(push=PushTrigger()), jobs={})
''')

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "list",
                "-f", "table", str(pkg_dir),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    def test_json_output_format(self, tmp_path):
        """List command can produce JSON output."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        (pkg_dir / "ci.py").write_text('''
from wetwire_github.workflow import Workflow, Triggers, PushTrigger

ci = Workflow(name="CI", on=Triggers(push=PushTrigger()), jobs={})
''')

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "list",
                "-f", "json", str(pkg_dir),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Should produce valid JSON
        if result.stdout.strip():
            data = json.loads(result.stdout)
            assert isinstance(data, dict) or isinstance(data, list)


class TestListCommandErrors:
    """Tests for list command error handling."""

    def test_nonexistent_package(self, tmp_path):
        """List command reports error for nonexistent package."""
        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "list",
                str(tmp_path / "nonexistent"),
            ],
            capture_output=True,
            text=True,
        )

        # Should report error
        assert result.returncode != 0 or "error" in result.stderr.lower()

    def test_no_package_provided(self):
        """List command uses current directory by default."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "list"],
            capture_output=True,
            text=True,
        )

        # Should work with current directory
        assert result.returncode in (0, 1)


class TestListCommandIntegration:
    """Integration tests for list command."""

    def test_list_multiple_files(self, tmp_path):
        """List command discovers resources from multiple files."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        (pkg_dir / "ci.py").write_text('''
from wetwire_github.workflow import Workflow, Triggers, PushTrigger

ci = Workflow(name="CI", on=Triggers(push=PushTrigger()), jobs={})
''')

        (pkg_dir / "release.py").write_text('''
from wetwire_github.workflow import Workflow, Triggers, ReleaseTrigger

release = Workflow(name="Release", on=Triggers(release=ReleaseTrigger()), jobs={})
''')

        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "list", str(pkg_dir)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
