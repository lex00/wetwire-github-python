"""Tests to verify conftest.py fixtures work correctly."""

from pathlib import Path

import yaml

from wetwire_github.workflow import Job, Step, Workflow


class TestSimpleWorkflowFixture:
    """Test the simple_workflow fixture."""

    def test_simple_workflow_exists(self, simple_workflow):
        """Simple workflow fixture provides a Workflow instance."""
        assert isinstance(simple_workflow, Workflow)
        assert simple_workflow.name == "Test Workflow"

    def test_simple_workflow_has_basic_structure(self, simple_workflow):
        """Simple workflow has basic job and step structure."""
        assert simple_workflow.jobs is not None
        assert "test" in simple_workflow.jobs


class TestSimpleJobFixture:
    """Test the simple_job fixture."""

    def test_simple_job_exists(self, simple_job):
        """Simple job fixture provides a Job instance."""
        assert isinstance(simple_job, Job)

    def test_simple_job_has_steps(self, simple_job):
        """Simple job has steps."""
        assert simple_job.steps is not None
        assert len(simple_job.steps) > 0

    def test_simple_job_has_runner(self, simple_job):
        """Simple job has a runner specified."""
        assert simple_job.runs_on == "ubuntu-latest"


class TestSimpleStepFixture:
    """Test the simple_step fixture."""

    def test_simple_step_exists(self, simple_step):
        """Simple step fixture provides a Step instance."""
        assert isinstance(simple_step, Step)

    def test_simple_step_has_command(self, simple_step):
        """Simple step has a run command."""
        assert simple_step.run is not None


class TestTempWorkflowDirFixture:
    """Test the temp_workflow_dir fixture."""

    def test_temp_workflow_dir_exists(self, temp_workflow_dir):
        """Temp workflow dir fixture creates a directory."""
        assert isinstance(temp_workflow_dir, Path)
        assert temp_workflow_dir.exists()
        assert temp_workflow_dir.is_dir()

    def test_temp_workflow_dir_has_structure(self, temp_workflow_dir):
        """Temp workflow dir has expected directory structure."""
        # Should have a workflows subdir
        workflows_dir = temp_workflow_dir / "workflows"
        assert workflows_dir.exists()
        assert workflows_dir.is_dir()

        # Should have an __init__.py in workflows
        init_file = workflows_dir / "__init__.py"
        assert init_file.exists()

    def test_temp_workflow_dir_has_output_dir(self, temp_workflow_dir):
        """Temp workflow dir has .github/workflows output directory."""
        github_dir = temp_workflow_dir / ".github"
        workflows_dir = github_dir / "workflows"

        assert github_dir.exists()
        assert workflows_dir.exists()


class TestWorkflowPackageDirFixture:
    """Test the workflow_package_dir fixture."""

    def test_workflow_package_dir_exists(self, workflow_package_dir):
        """Workflow package dir fixture creates a Python package."""
        assert isinstance(workflow_package_dir, Path)
        assert workflow_package_dir.exists()
        assert workflow_package_dir.is_dir()

    def test_workflow_package_dir_has_init(self, workflow_package_dir):
        """Workflow package dir has __init__.py."""
        init_file = workflow_package_dir / "__init__.py"
        assert init_file.exists()

    def test_workflow_package_dir_is_importable(self, workflow_package_dir):
        """Workflow package dir structure is importable."""
        # Should be a valid Python package structure
        init_file = workflow_package_dir / "__init__.py"
        assert init_file.exists()
        assert init_file.read_text() == ""


class TestYamlParserFixture:
    """Test the yaml_parser fixture."""

    def test_yaml_parser_exists(self, yaml_parser):
        """YAML parser fixture provides yaml module."""
        assert yaml_parser is yaml

    def test_yaml_parser_can_parse(self, yaml_parser):
        """YAML parser can parse YAML content."""
        content = "name: Test\nvalue: 42"
        result = yaml_parser.safe_load(content)
        assert result["name"] == "Test"
        assert result["value"] == 42
