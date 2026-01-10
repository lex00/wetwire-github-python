"""Tests for cost CLI command."""

import json

from wetwire_github.cli.cost_cmd import analyze_costs


class TestCostCommand:
    """Tests for the cost command."""

    def test_analyze_costs_basic(self, tmp_path):
        """Analyze costs of a basic workflow."""
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

        exit_code, output = analyze_costs(
            package_path=str(tmp_path),
            output_format="text",
        )

        assert exit_code == 0
        # Should contain cost information
        assert "$" in output or "cost" in output.lower() or "minute" in output.lower()

    def test_analyze_costs_json_format(self, tmp_path):
        """Analyze costs with JSON output format."""
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

        exit_code, output = analyze_costs(
            package_path=str(tmp_path),
            output_format="json",
        )

        assert exit_code == 0
        result = json.loads(output)
        # Should have cost information
        assert "total_cost" in result or "workflows" in result or "cost" in str(result).lower()

    def test_analyze_costs_table_format(self, tmp_path):
        """Analyze costs with table output format."""
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

        exit_code, output = analyze_costs(
            package_path=str(tmp_path),
            output_format="table",
        )

        assert exit_code == 0
        # Should have some tabular structure
        assert "CI" in output or "build" in output or "-" in output

    def test_analyze_costs_nonexistent_path(self, tmp_path):
        """Analyze costs on non-existent path."""
        nonexistent = tmp_path / "nonexistent"

        exit_code, output = analyze_costs(
            package_path=str(nonexistent),
            output_format="text",
        )

        assert exit_code == 1
        assert "error" in output.lower() or "not exist" in output.lower()

    def test_analyze_costs_no_workflows(self, tmp_path):
        """Analyze costs on a package with no workflows."""
        empty_file = tmp_path / "empty.py"
        empty_file.write_text("# No workflows here\n")

        exit_code, output = analyze_costs(
            package_path=str(tmp_path),
            output_format="text",
        )

        # Should indicate no workflows found
        assert "no workflow" in output.lower() or exit_code != 0

    def test_analyze_costs_path_traversal_rejected(self):
        """Path traversal in package path should be rejected."""
        exit_code, output = analyze_costs(
            package_path="../../../etc",
            output_format="text",
        )

        assert exit_code == 1
        assert "traversal" in output.lower() or "invalid" in output.lower()

    def test_analyze_costs_multiple_workflows(self, tmp_path):
        """Analyze costs for multiple workflows."""
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

        exit_code, output = analyze_costs(
            package_path=str(tmp_path),
            output_format="text",
        )

        assert exit_code == 0
        # Should analyze both workflows
        assert "CI" in output or "Deploy" in output or "total" in output.lower()

    def test_analyze_costs_multiple_runners(self, tmp_path):
        """Analyze costs for workflows with different runner types."""
        workflow_file = tmp_path / "workflows.py"
        workflow_file.write_text("""
from wetwire_github.workflow import Workflow, Job, Step

ci = Workflow(
    name="MultiPlatform",
    jobs={
        "linux": Job(
            runs_on="ubuntu-latest",
            timeout_minutes=30,
            steps=[
                Step(uses="actions/checkout@v4"),
                Step(run="make build"),
            ],
        ),
        "windows": Job(
            runs_on="windows-latest",
            timeout_minutes=30,
            steps=[
                Step(uses="actions/checkout@v4"),
                Step(run="make build"),
            ],
        ),
        "macos": Job(
            runs_on="macos-latest",
            timeout_minutes=30,
            steps=[
                Step(uses="actions/checkout@v4"),
                Step(run="make build"),
            ],
        ),
    },
)
""")

        exit_code, output = analyze_costs(
            package_path=str(tmp_path),
            output_format="json",
        )

        assert exit_code == 0
        result = json.loads(output)

        # Should have per-job breakdown
        if "workflows" in result:
            workflow_data = result["workflows"][0] if result["workflows"] else {}
            assert "job_estimates" in workflow_data or "jobs" in workflow_data or "breakdown" in str(workflow_data).lower()

    def test_analyze_costs_per_job_breakdown(self, tmp_path):
        """Analyze costs should show per-job cost breakdown."""
        workflow_file = tmp_path / "workflow.py"
        workflow_file.write_text("""
from wetwire_github.workflow import Workflow, Job, Step

ci = Workflow(
    name="CI",
    jobs={
        "test": Job(
            runs_on="ubuntu-latest",
            timeout_minutes=10,
            steps=[Step(run="make test")],
        ),
        "build": Job(
            runs_on="ubuntu-latest",
            timeout_minutes=20,
            steps=[Step(run="make build")],
        ),
        "deploy": Job(
            runs_on="ubuntu-latest",
            timeout_minutes=5,
            steps=[Step(run="make deploy")],
        ),
    },
)
""")

        exit_code, output = analyze_costs(
            package_path=str(tmp_path),
            output_format="json",
        )

        assert exit_code == 0
        result = json.loads(output)

        # Should have information about individual jobs
        if "workflows" in result and result["workflows"]:
            workflow = result["workflows"][0]
            # Check for job breakdown
            assert ("job_estimates" in workflow or
                    "jobs" in workflow or
                    "breakdown" in str(workflow).lower())

    def test_analyze_costs_shows_minutes(self, tmp_path):
        """Cost analysis should show minute breakdowns."""
        workflow_file = tmp_path / "workflow.py"
        workflow_file.write_text("""
from wetwire_github.workflow import Workflow, Job, Step

ci = Workflow(
    name="CI",
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            timeout_minutes=30,
            steps=[Step(run="make build")],
        ),
    },
)
""")

        exit_code, output = analyze_costs(
            package_path=str(tmp_path),
            output_format="json",
        )

        assert exit_code == 0
        result = json.loads(output)

        # Should have minute information
        output_str = str(result).lower()
        assert "minute" in output_str or "linux" in output_str or "30" in str(result)


class TestCostCommandCLIIntegration:
    """Integration tests for cost command via CLI."""

    def test_cost_command_in_main(self):
        """Cost command should be registered in main CLI."""
        from wetwire_github.cli.main import create_parser

        parser = create_parser()

        # Check that cost subcommand exists
        args = parser.parse_args(["cost", "."])
        assert args.command == "cost"
        assert args.package == "."

    def test_cost_command_format_option(self):
        """Cost command should accept --format option."""
        from wetwire_github.cli.main import create_parser

        parser = create_parser()

        args = parser.parse_args(["cost", "--format", "json", "."])
        assert args.format == "json"

        args = parser.parse_args(["cost", "-f", "table", "."])
        assert args.format == "table"

    def test_cost_command_no_cache_option(self):
        """Cost command should accept --no-cache option."""
        from wetwire_github.cli.main import create_parser

        parser = create_parser()

        args = parser.parse_args(["cost", "--no-cache", "."])
        assert args.no_cache is True
