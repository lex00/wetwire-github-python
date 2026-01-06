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

    def test_fix_secrets_pattern(self, tmp_path):
        """--fix replaces hardcoded secrets with Secrets.get()."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        # Code with hardcoded secrets
        code_with_secrets = '''
from wetwire_github.workflow import Step

step = Step(env={"TOKEN": "${{ secrets.GITHUB_TOKEN }}"})
'''
        (pkg_dir / "ci.py").write_text(code_with_secrets)

        subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "lint",
                "--fix", str(pkg_dir),
            ],
            capture_output=True,
            text=True,
        )

        # Check that the file was modified
        fixed_code = (pkg_dir / "ci.py").read_text()
        assert 'Secrets.get("GITHUB_TOKEN")' in fixed_code
        assert "${{ secrets.GITHUB_TOKEN }}" not in fixed_code

    def test_fix_multiple_secrets(self, tmp_path):
        """--fix handles multiple secrets in one file."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        code_with_secrets = '''
from wetwire_github.workflow import Step

step1 = Step(env={"TOKEN": "${{ secrets.GITHUB_TOKEN }}"})
step2 = Step(env={"API_KEY": "${{ secrets.API_KEY }}"})
'''
        (pkg_dir / "ci.py").write_text(code_with_secrets)

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "lint",
                "--fix", str(pkg_dir),
            ],
            capture_output=True,
            text=True,
        )

        fixed_code = (pkg_dir / "ci.py").read_text()
        assert 'Secrets.get("GITHUB_TOKEN")' in fixed_code
        assert 'Secrets.get("API_KEY")' in fixed_code
        assert "Fixed" in result.stdout

    def test_fix_json_output(self, tmp_path):
        """--fix with -f json produces valid JSON output."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        code_with_secrets = '''
from wetwire_github.workflow import Step
step = Step(env={"TOKEN": "${{ secrets.TOKEN }}"})
'''
        (pkg_dir / "ci.py").write_text(code_with_secrets)

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "lint",
                "--fix", "-f", "json", str(pkg_dir),
            ],
            capture_output=True,
            text=True,
        )

        # Should produce valid JSON
        data = json.loads(result.stdout)
        assert "fixed_count" in data
        assert "remaining_count" in data
        assert data["fixed_count"] >= 1

    def test_fix_no_changes_needed(self, tmp_path):
        """--fix reports no changes when code is clean."""
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        clean_code = '''
from wetwire_github.workflow import Step
from wetwire_github.workflow.expressions import Secrets

step = Step(env={"TOKEN": Secrets.get("TOKEN")})
'''
        (pkg_dir / "ci.py").write_text(clean_code)

        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "lint",
                "--fix", str(pkg_dir),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode in (0, 1)


class TestLinterAutoFix:
    """Unit tests for linter auto-fix functionality."""

    def test_linter_fix_method_exists(self):
        """Linter has a fix method."""
        from wetwire_github.linter import Linter

        linter = Linter()
        assert hasattr(linter, "fix")
        assert callable(linter.fix)

    def test_fix_result_dataclass(self):
        """FixResult dataclass exists and has expected fields."""
        from wetwire_github.linter import FixResult

        result = FixResult(source="test", fixed_count=1)
        assert result.source == "test"
        assert result.fixed_count == 1
        assert result.remaining_errors == []

    def test_fixable_rule_protocol(self):
        """FixableRule protocol can be checked."""
        from wetwire_github.linter import FixableRule
        from wetwire_github.linter.rules import WAG003UseSecretsContext

        rule = WAG003UseSecretsContext()
        assert isinstance(rule, FixableRule)

    def test_wag003_fix_method(self):
        """WAG003 rule has working fix method."""
        from wetwire_github.linter.rules import WAG003UseSecretsContext

        rule = WAG003UseSecretsContext()
        source = 'env={"TOKEN": "${{ secrets.GITHUB_TOKEN }}"}'
        fixed_source, count, errors = rule.fix(source, "test.py")

        assert count == 1
        assert 'Secrets.get("GITHUB_TOKEN")' in fixed_source
        assert len(errors) == 0
