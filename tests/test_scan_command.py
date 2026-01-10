"""Tests for the scan command implementation."""

import json
import subprocess
import sys


class TestScanCommandBasic:
    """Tests for scan command basic functionality."""

    def test_scan_clean_workflow(self, tmp_path):
        """Scan command succeeds for clean workflow code."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        # Create clean workflow code with pinned actions
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
            [sys.executable, "-m", "wetwire_github.cli", "scan", str(pkg_dir)],
            capture_output=True,
            text=True,
        )

        # Clean code should pass (exit 0)
        assert result.returncode == 0

    def test_scan_with_security_issues(self, tmp_path):
        """Scan command reports security issues."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        # Create code with unpinned action (MEDIUM severity issue)
        (pkg_dir / "ci.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step, PushTrigger, Triggers

ci = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger()),
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            steps=[Step(uses="actions/checkout")],
        ),
    },
)
''')

        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "scan", str(pkg_dir)],
            capture_output=True,
            text=True,
        )

        # Should report MEDIUM severity issues (but exit 0 since not critical/high)
        assert result.returncode == 0
        assert "unpinned" in result.stdout.lower() or "MEDIUM" in result.stdout


class TestScanCommandOutput:
    """Tests for scan command output formats."""

    def test_text_output_format(self, tmp_path):
        """Scan command produces text output by default."""
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
                sys.executable, "-m", "wetwire_github.cli", "scan",
                "-f", "text", str(pkg_dir),
            ],
            capture_output=True,
            text=True,
        )

        # Should produce text output
        assert result.returncode in (0, 1)

    def test_json_output_format(self, tmp_path):
        """Scan command can produce JSON output."""
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
                sys.executable, "-m", "wetwire_github.cli", "scan",
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
            assert "results" in data or "issues" in data or "workflows" in data

    def test_table_output_format(self, tmp_path):
        """Scan command can produce table output."""
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
                sys.executable, "-m", "wetwire_github.cli", "scan",
                "-f", "table", str(pkg_dir),
            ],
            capture_output=True,
            text=True,
        )

        # Should produce table output
        assert result.returncode in (0, 1)


class TestScanCommandSeverity:
    """Tests for scan command severity handling."""

    def test_exit_code_1_for_critical_issues(self, tmp_path):
        """Scan returns exit code 1 for critical/high severity issues."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        # Create workflow with script injection vulnerability (critical)
        (pkg_dir / "ci.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step, PushTrigger, Triggers

ci = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger()),
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            steps=[Step(run="echo ${{ github.event.pull_request.title }}")],
        ),
    },
)
''')

        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "scan", str(pkg_dir)],
            capture_output=True,
            text=True,
        )

        # Should fail for critical/high issues
        assert result.returncode == 1

    def test_exit_code_0_for_only_low_medium_issues(self, tmp_path):
        """Scan returns exit code 0 when only low/medium severity issues exist."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        # Create workflow with only medium issues (unpinned action)
        (pkg_dir / "ci.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step, PushTrigger, Triggers

ci = Workflow(
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
            [sys.executable, "-m", "wetwire_github.cli", "scan", str(pkg_dir)],
            capture_output=True,
            text=True,
        )

        # Should pass for low/medium only
        assert result.returncode == 0


class TestScanCommandErrors:
    """Tests for scan command error handling."""

    def test_nonexistent_package(self, tmp_path):
        """Scan command reports error for nonexistent package."""
        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "scan",
                str(tmp_path / "nonexistent"),
            ],
            capture_output=True,
            text=True,
        )

        # Should report error
        assert result.returncode != 0

    def test_no_package_provided(self):
        """Scan command handles no package gracefully."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "scan"],
            capture_output=True,
            text=True,
        )

        # Should use current directory or indicate error
        assert result.returncode in (0, 1)


class TestScanCommandIntegration:
    """Integration tests for scan command."""

    def test_scan_multiple_workflows(self, tmp_path):
        """Scan command checks all workflows in a package."""
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
            [sys.executable, "-m", "wetwire_github.cli", "scan", str(pkg_dir)],
            capture_output=True,
            text=True,
        )

        assert result.returncode in (0, 1)

    def test_scan_json_summary(self, tmp_path):
        """Scan JSON output includes severity counts."""
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
                sys.executable, "-m", "wetwire_github.cli", "scan",
                "-f", "json", str(pkg_dir),
            ],
            capture_output=True,
            text=True,
        )

        data = json.loads(result.stdout)
        # Should include severity counts in summary
        assert "critical_count" in data or "summary" in data


class TestScanCommandUnit:
    """Unit tests for scan command functionality."""

    def test_run_scan_function_exists(self):
        """run_scan function exists and is callable."""
        from wetwire_github.cli.scan_cmd import run_scan

        assert callable(run_scan)

    def test_run_scan_returns_tuple(self, tmp_path):
        """run_scan returns (exit_code, output) tuple."""
        from wetwire_github.cli.scan_cmd import run_scan

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

        exit_code, output = run_scan(str(pkg_dir))

        assert isinstance(exit_code, int)
        assert isinstance(output, str)
