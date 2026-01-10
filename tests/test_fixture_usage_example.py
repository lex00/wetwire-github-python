"""Example tests demonstrating usage of conftest.py fixtures.

This file shows how the shared fixtures can simplify test writing
by providing common test data and temporary directories.
"""

from wetwire_github.serialize import to_dict, to_yaml
from wetwire_github.workflow import Job, Step, Workflow


class TestFixtureUsageExamples:
    """Examples of using the shared fixtures."""

    def test_simple_step_fixture_usage(self, simple_step):
        """Show how to use simple_step fixture."""
        # The simple_step fixture provides a ready-to-use Step
        assert isinstance(simple_step, Step)
        assert simple_step.run is not None

        # Can use it directly in tests
        result = to_dict(simple_step)
        assert "run" in result

    def test_simple_job_fixture_usage(self, simple_job):
        """Show how to use simple_job fixture."""
        # The simple_job fixture provides a Job with steps
        assert isinstance(simple_job, Job)
        assert len(simple_job.steps) > 0

        # Can serialize and verify structure
        result = to_dict(simple_job)
        assert result["runs-on"] == "ubuntu-latest"
        assert len(result["steps"]) >= 2

    def test_simple_workflow_fixture_usage(self, simple_workflow, yaml_parser):
        """Show how to use simple_workflow and yaml_parser fixtures together."""
        # The simple_workflow fixture provides a complete Workflow
        assert isinstance(simple_workflow, Workflow)
        assert simple_workflow.name == "Test Workflow"

        # Can serialize to YAML and parse it back
        yaml_output = to_yaml(simple_workflow)
        parsed = yaml_parser.safe_load(yaml_output)

        assert parsed["name"] == "Test Workflow"
        assert "test" in parsed["jobs"]

    def test_temp_workflow_dir_usage(self, temp_workflow_dir):
        """Show how to use temp_workflow_dir fixture."""
        # The temp_workflow_dir fixture provides a complete directory structure
        workflows_dir = temp_workflow_dir / "workflows"
        assert workflows_dir.exists()
        assert (workflows_dir / "__init__.py").exists()

        # Can create workflow files
        workflow_file = workflows_dir / "ci.py"
        workflow_file.write_text('''
from wetwire_github.workflow import Workflow

ci = Workflow(name="CI")
''')
        assert workflow_file.exists()

        # Output directory is ready
        output_dir = temp_workflow_dir / ".github" / "workflows"
        assert output_dir.exists()

    def test_workflow_package_dir_usage(self, workflow_package_dir):
        """Show how to use workflow_package_dir fixture."""
        # The workflow_package_dir fixture provides a Python package
        assert workflow_package_dir.exists()
        assert (workflow_package_dir / "__init__.py").exists()

        # Can create multiple workflow files
        (workflow_package_dir / "ci.py").write_text(
            'from wetwire_github.workflow import Workflow\n'
            'ci = Workflow(name="CI")\n'
        )
        (workflow_package_dir / "deploy.py").write_text(
            'from wetwire_github.workflow import Workflow\n'
            'deploy = Workflow(name="Deploy")\n'
        )

        # Verify files were created
        assert len(list(workflow_package_dir.glob("*.py"))) == 3  # __init__.py + 2 workflows
