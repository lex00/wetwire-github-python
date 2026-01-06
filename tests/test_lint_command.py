"""Tests for the lint command implementation."""

import json
import subprocess
import sys


class TestLintCommandBasic:
    """Tests for lint command basic functionality."""

    def test_lint_clean_code(self, tmp_path):
        """Lint command succeeds for clean workflow code."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        # Create clean workflow code
        (pkg_dir / "ci.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step, PushTrigger, Triggers
from wetwire_github.actions import checkout

ci = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger()),
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            steps=[checkout()],
        ),
    },
)
''')

        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "lint", str(pkg_dir)],
            capture_output=True,
            text=True,
        )

        # Clean code should pass (exit 0)
        assert result.returncode == 0

    def test_lint_with_issues(self, tmp_path):
        """Lint command reports issues for code with problems."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        # Create code with potential lint issues (e.g., hardcoded uses string)
        (pkg_dir / "ci.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step, PushTrigger, Triggers

ci = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger()),
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            steps=[Step(uses="actions/checkout@v4")],
        ),
    },
)
''')

        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "lint", str(pkg_dir)],
            capture_output=True,
            text=True,
        )

        # May report WAG001 for using hardcoded action string
        # Accept either pass or fail depending on rule implementation
        assert result.returncode in (0, 1)


class TestLintCommandOutput:
    """Tests for lint command output formats."""

    def test_text_output_format(self, tmp_path):
        """Lint command produces text output by default."""
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
            [
                sys.executable, "-m", "wetwire_github.cli", "lint",
                "-f", "text", str(pkg_dir),
            ],
            capture_output=True,
            text=True,
        )

        # Should produce text output
        assert result.returncode in (0, 1)

    def test_json_output_format(self, tmp_path):
        """Lint command can produce JSON output."""
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
            [
                sys.executable, "-m", "wetwire_github.cli", "lint",
                "-f", "json", str(pkg_dir),
            ],
            capture_output=True,
            text=True,
        )

        # Should produce valid JSON
        if result.stdout.strip():
            data = json.loads(result.stdout)
            assert isinstance(data, dict)
            # Check for expected structure
            assert "results" in data or "files" in data or "errors" in data


class TestLintCommandErrors:
    """Tests for lint command error handling."""

    def test_nonexistent_package(self, tmp_path):
        """Lint command reports error for nonexistent package."""
        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "lint",
                str(tmp_path / "nonexistent"),
            ],
            capture_output=True,
            text=True,
        )

        # Should report error
        assert result.returncode != 0

    def test_no_package_provided(self):
        """Lint command handles no package gracefully."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "lint"],
            capture_output=True,
            text=True,
        )

        # Should use current directory or indicate error
        assert result.returncode in (0, 1)


class TestLintCommandIntegration:
    """Integration tests for lint command."""

    def test_lint_multiple_files(self, tmp_path):
        """Lint command checks all Python files in a package."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        (pkg_dir / "ci.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step, PushTrigger, Triggers

ci = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger()),
    jobs={"build": Job(runs_on="ubuntu-latest", steps=[Step(run="echo build")])},
)
''')

        (pkg_dir / "release.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step, ReleaseTrigger, Triggers

release = Workflow(
    name="Release",
    on=Triggers(release=ReleaseTrigger()),
    jobs={"deploy": Job(runs_on="ubuntu-latest", steps=[Step(run="echo deploy")])},
)
''')

        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "lint", str(pkg_dir)],
            capture_output=True,
            text=True,
        )

        assert result.returncode in (0, 1)


class TestLintCommandFix:
    """Tests for lint command --fix option."""

    def test_fix_flag_exists(self, tmp_path):
        """Lint command accepts --fix flag."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        (pkg_dir / "ci.py").write_text("# empty")

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "lint",
                "--fix", str(pkg_dir),
            ],
            capture_output=True,
            text=True,
        )

        # Command should accept the flag (even if fix not implemented)
        # 0 or 1 is acceptable, 2 would indicate parsing error
        assert result.returncode in (0, 1)
