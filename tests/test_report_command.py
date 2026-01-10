"""Tests for report CLI command."""

import json

from wetwire_github.cli.report_cmd import generate_report


class TestReportCommand:
    """Tests for the report command."""

    def test_generate_report_basic(self, tmp_path):
        """Generate a basic report for a simple workflow."""
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
                Step(run="make build"),
            ],
        ),
    },
)
""")

        exit_code, output = generate_report(
            package_path=str(tmp_path),
            output_format="text",
        )

        assert exit_code == 0
        # Should contain summary information
        assert "workflow" in output.lower() or "report" in output.lower()
        # Should contain health score
        assert "health" in output.lower() or "score" in output.lower()

    def test_generate_report_health_score_calculation(self, tmp_path):
        """Health score should reflect issues found."""
        # Create a clean workflow
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
                Step(run="make build"),
            ],
        ),
    },
)
""")

        exit_code, output = generate_report(
            package_path=str(tmp_path),
            output_format="json",
        )

        result = json.loads(output)
        assert "health_score" in result
        # Clean workflow should have high health score
        assert result["health_score"] >= 70

    def test_generate_report_health_score_low_for_issues(self, tmp_path):
        """Health score should be lower when issues are found."""
        # Create a workflow with issues (missing checkout, no timeout)
        workflow_file = tmp_path / "workflow.py"
        workflow_file.write_text("""
from wetwire_github.workflow import Workflow, Job, Step

ci = Workflow(
    name="CI",
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

        exit_code, output = generate_report(
            package_path=str(tmp_path),
            output_format="json",
        )

        result = json.loads(output)
        assert "health_score" in result
        # Workflow with issues should have lower health score
        assert result["health_score"] < 100

    def test_generate_report_json_format(self, tmp_path):
        """Generate report in JSON format."""
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
                Step(run="make build"),
            ],
        ),
    },
)
""")

        exit_code, output = generate_report(
            package_path=str(tmp_path),
            output_format="json",
        )

        # Should be valid JSON
        result = json.loads(output)
        assert "workflow_count" in result
        assert "health_score" in result
        assert "lint_issues" in result
        assert "policy_results" in result
        assert "security_issues" in result
        assert "cost_estimate" in result

    def test_generate_report_text_format(self, tmp_path):
        """Generate report in text format."""
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
                Step(run="make build"),
            ],
        ),
    },
)
""")

        exit_code, output = generate_report(
            package_path=str(tmp_path),
            output_format="text",
        )

        assert exit_code == 0
        # Text format should have readable sections
        assert "Workflow" in output or "workflow" in output
        assert "Health" in output or "Score" in output or "health" in output.lower()

    def test_generate_report_with_problematic_workflow(self, tmp_path):
        """Report should include issues for problematic workflows."""
        workflow_file = tmp_path / "workflow.py"
        workflow_file.write_text("""
from wetwire_github.workflow import Workflow, Job, Step

ci = Workflow(
    name="BadWorkflow",
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            steps=[
                Step(run="echo no checkout and no timeout"),
            ],
        ),
    },
)
""")

        exit_code, output = generate_report(
            package_path=str(tmp_path),
            output_format="json",
        )

        result = json.loads(output)
        # Should show policy failures
        assert "policy_results" in result
        # Policy should show failures since checkout and timeout are missing
        policy_results = result["policy_results"]
        assert (
            policy_results["failed_count"] > 0 or policy_results["total_failures"] > 0
        )

    def test_generate_report_nonexistent_path(self, tmp_path):
        """Report on non-existent path."""
        nonexistent = tmp_path / "nonexistent"

        exit_code, output = generate_report(
            package_path=str(nonexistent),
            output_format="text",
        )

        assert exit_code == 1
        assert "error" in output.lower() or "not exist" in output.lower()

    def test_generate_report_no_workflows(self, tmp_path):
        """Report on a package with no workflows."""
        empty_file = tmp_path / "empty.py"
        empty_file.write_text("# No workflows here\n")

        exit_code, output = generate_report(
            package_path=str(tmp_path),
            output_format="text",
        )

        # Should indicate no workflows found
        assert "no workflow" in output.lower() or exit_code != 0

    def test_generate_report_path_traversal_rejected(self):
        """Path traversal in package path should be rejected."""
        exit_code, output = generate_report(
            package_path="../../../etc",
            output_format="text",
        )

        assert exit_code == 1
        assert "traversal" in output.lower() or "invalid" in output.lower()

    def test_generate_report_multiple_workflows(self, tmp_path):
        """Report on multiple workflows."""
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

        exit_code, output = generate_report(
            package_path=str(tmp_path),
            output_format="json",
        )

        assert exit_code == 0
        result = json.loads(output)
        assert result["workflow_count"] == 2

    def test_generate_report_includes_cost_estimate(self, tmp_path):
        """Report should include cost estimation."""
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
                Step(run="make build"),
            ],
        ),
    },
)
""")

        exit_code, output = generate_report(
            package_path=str(tmp_path),
            output_format="json",
        )

        result = json.loads(output)
        assert "cost_estimate" in result
        cost = result["cost_estimate"]
        assert "total_cost" in cost or "cost" in str(cost).lower()

    def test_generate_report_includes_security_by_severity(self, tmp_path):
        """Report should include security issues by severity."""
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
                Step(run="make build"),
            ],
        ),
    },
)
""")

        exit_code, output = generate_report(
            package_path=str(tmp_path),
            output_format="json",
        )

        result = json.loads(output)
        assert "security_issues" in result
        security = result["security_issues"]
        # Should have severity breakdown
        assert "critical" in security or "high" in security or "total" in security

    def test_generate_report_lint_issues_count(self, tmp_path):
        """Report should include lint issue counts."""
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
                Step(run="make build"),
            ],
        ),
    },
)
""")

        exit_code, output = generate_report(
            package_path=str(tmp_path),
            output_format="json",
        )

        result = json.loads(output)
        assert "lint_issues" in result
        lint = result["lint_issues"]
        assert "total" in lint or "count" in str(lint).lower() or isinstance(lint, int)


class TestReportCommandCLIIntegration:
    """Integration tests for report command via CLI."""

    def test_report_command_in_main(self):
        """Report command should be registered in main CLI."""
        from wetwire_github.cli.main import create_parser

        parser = create_parser()

        # Check that report subcommand exists
        args = parser.parse_args(["report", "."])
        assert args.command == "report"
        assert args.package == "."

    def test_report_command_format_option(self):
        """Report command should accept --format option."""
        from wetwire_github.cli.main import create_parser

        parser = create_parser()

        args = parser.parse_args(["report", "--format", "json", "."])
        assert args.format == "json"

        args = parser.parse_args(["report", "-f", "text", "."])
        assert args.format == "text"

    def test_report_command_no_cache_option(self):
        """Report command should accept --no-cache option."""
        from wetwire_github.cli.main import create_parser

        parser = create_parser()

        args = parser.parse_args(["report", "--no-cache", "."])
        assert args.no_cache is True
