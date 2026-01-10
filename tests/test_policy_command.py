"""Tests for policy CLI command."""

import json

from wetwire_github.cli.policy_cmd import run_policies


class TestPolicyCommand:
    """Tests for the policy command."""

    def test_run_policies_on_valid_package(self, tmp_path):
        """Run policies on a package with valid workflows."""
        # Create a minimal valid workflow file
        workflow_file = tmp_path / "workflow.py"
        workflow_file.write_text("""
from wetwire_github.workflow import Workflow, Job, Step

ci = Workflow(
    name="CI",
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            timeout_minutes=30,
            steps=[
                Step(uses="actions/checkout@v4"),
                Step(run="echo hello"),
            ],
        ),
    },
)
""")

        exit_code, output = run_policies(
            package_path=str(tmp_path),
            output_format="text",
        )

        # Should pass basic policies
        assert exit_code == 0
        assert "CI" in output or "PASS" in output.upper() or "passed" in output.lower()

    def test_run_policies_on_invalid_workflow(self, tmp_path):
        """Run policies on a workflow that violates policies."""
        # Create a workflow missing checkout and timeout
        workflow_file = tmp_path / "workflow.py"
        workflow_file.write_text("""
from wetwire_github.workflow import Workflow, Job, Step

ci = Workflow(
    name="CI",
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            steps=[
                Step(run="echo hello"),
            ],
        ),
    },
)
""")

        exit_code, output = run_policies(
            package_path=str(tmp_path),
            output_format="text",
        )

        # Should fail because missing checkout and timeout
        assert exit_code == 1
        assert "FAIL" in output.upper() or "failed" in output.lower() or "missing" in output.lower()

    def test_run_policies_json_format(self, tmp_path):
        """Run policies with JSON output format."""
        workflow_file = tmp_path / "workflow.py"
        workflow_file.write_text("""
from wetwire_github.workflow import Workflow, Job, Step

ci = Workflow(
    name="CI",
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            timeout_minutes=30,
            steps=[
                Step(uses="actions/checkout@v4"),
                Step(run="echo hello"),
            ],
        ),
    },
)
""")

        exit_code, output = run_policies(
            package_path=str(tmp_path),
            output_format="json",
        )

        # Output should be valid JSON
        result = json.loads(output)
        assert "workflows" in result or "results" in result
        assert exit_code == 0

    def test_run_policies_nonexistent_path(self, tmp_path):
        """Run policies on non-existent path."""
        nonexistent = tmp_path / "nonexistent"

        exit_code, output = run_policies(
            package_path=str(nonexistent),
            output_format="text",
        )

        assert exit_code == 1
        assert "error" in output.lower() or "not exist" in output.lower()

    def test_run_policies_no_workflows(self, tmp_path):
        """Run policies on a package with no workflows."""
        # Create an empty Python file
        empty_file = tmp_path / "empty.py"
        empty_file.write_text("# No workflows here\n")

        exit_code, output = run_policies(
            package_path=str(tmp_path),
            output_format="text",
        )

        # Should indicate no workflows found
        assert "no workflow" in output.lower() or exit_code != 0

    def test_run_policies_path_traversal_rejected(self):
        """Path traversal in package path should be rejected."""
        exit_code, output = run_policies(
            package_path="../../../etc",
            output_format="text",
        )

        assert exit_code == 1
        assert "traversal" in output.lower() or "invalid" in output.lower()

    def test_run_policies_table_format(self, tmp_path):
        """Run policies with table output format."""
        workflow_file = tmp_path / "workflow.py"
        workflow_file.write_text("""
from wetwire_github.workflow import Workflow, Job, Step

ci = Workflow(
    name="CI",
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            timeout_minutes=30,
            steps=[
                Step(uses="actions/checkout@v4"),
                Step(run="echo hello"),
            ],
        ),
    },
)
""")

        exit_code, output = run_policies(
            package_path=str(tmp_path),
            output_format="table",
        )

        # Should have formatted output
        assert exit_code == 0
        # Table format should have some structure
        assert "CI" in output or "Workflow" in output or "Policy" in output

    def test_run_policies_multiple_workflows(self, tmp_path):
        """Run policies on multiple workflows."""
        workflow_file = tmp_path / "workflows.py"
        workflow_file.write_text("""
from wetwire_github.workflow import Workflow, Job, Step

ci = Workflow(
    name="CI",
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            timeout_minutes=30,
            steps=[
                Step(uses="actions/checkout@v4"),
                Step(run="make build"),
            ],
        ),
    },
)

deploy = Workflow(
    name="Deploy",
    jobs={
        "deploy": Job(
            runs_on="ubuntu-latest",
            timeout_minutes=60,
            steps=[
                Step(uses="actions/checkout@v4"),
                Step(run="make deploy"),
            ],
        ),
    },
)
""")

        exit_code, output = run_policies(
            package_path=str(tmp_path),
            output_format="text",
        )

        # Both workflows should be evaluated
        assert exit_code == 0
        # Output should mention both workflows or show 2 workflows checked
        assert "CI" in output or "Deploy" in output or "2" in output

    def test_run_policies_with_policy_failures_json(self, tmp_path):
        """Run policies with failures in JSON format."""
        workflow_file = tmp_path / "workflow.py"
        workflow_file.write_text("""
from wetwire_github.workflow import Workflow, Job, Step

ci = Workflow(
    name="BadWorkflow",
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            steps=[
                Step(run="echo no checkout"),
            ],
        ),
    },
)
""")

        exit_code, output = run_policies(
            package_path=str(tmp_path),
            output_format="json",
        )

        assert exit_code == 1
        result = json.loads(output)
        # Should contain failure information
        assert "results" in result or "workflows" in result
        # Check for failures in the result
        has_failure = False
        if "results" in result:
            for r in result.get("results", []):
                if isinstance(r, dict) and not r.get("passed", True):
                    has_failure = True
                    break
        assert has_failure or result.get("total_failures", 0) > 0


class TestPolicyCommandCLIIntegration:
    """Integration tests for policy command via CLI."""

    def test_policy_command_in_main(self):
        """Policy command should be registered in main CLI."""
        from wetwire_github.cli.main import create_parser

        parser = create_parser()

        # Check that policy check subcommand exists
        # Parse with policy check command to verify it's registered
        args = parser.parse_args(["policy", "check"])
        assert args.command == "policy"
        assert args.policy_command == "check"
        # Package defaults to None in argparse, CLI defaults to "." when None
        assert args.package is None

    def test_policy_command_format_option(self):
        """Policy command should accept --format option."""
        from wetwire_github.cli.main import create_parser

        parser = create_parser()

        args = parser.parse_args(["policy", "check", "--format", "json", "."])
        assert args.format == "json"

        args = parser.parse_args(["policy", "check", "-f", "table", "."])
        assert args.format == "table"

    def test_policy_command_no_cache_option(self):
        """Policy command should accept --no-cache option."""
        from wetwire_github.cli.main import create_parser

        parser = create_parser()

        args = parser.parse_args(["policy", "check", "--no-cache", "."])
        assert args.no_cache is True
