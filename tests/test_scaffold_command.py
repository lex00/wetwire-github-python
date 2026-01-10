"""Tests for the scaffold command."""

import subprocess
import sys

import pytest

from wetwire_github.workflow import Job, Workflow


class TestScaffoldWorkflowFunction:
    """Tests for scaffold_workflow function."""

    def test_scaffold_python_ci_returns_workflow(self):
        """python-ci template returns a Workflow object."""
        from wetwire_github.cli.scaffold_cmd import scaffold_workflow

        workflow = scaffold_workflow("python-ci")
        assert isinstance(workflow, Workflow)
        assert workflow.name == "Python CI"

    def test_scaffold_python_ci_has_test_job(self):
        """python-ci template has a test job."""
        from wetwire_github.cli.scaffold_cmd import scaffold_workflow

        workflow = scaffold_workflow("python-ci")
        assert "test" in workflow.jobs
        job = workflow.jobs["test"]
        assert isinstance(job, Job)

    def test_scaffold_python_ci_has_matrix(self):
        """python-ci template has Python version matrix."""
        from wetwire_github.cli.scaffold_cmd import scaffold_workflow

        workflow = scaffold_workflow("python-ci")
        job = workflow.jobs["test"]
        assert job.strategy is not None
        assert job.strategy.matrix is not None
        # Should have Python 3.11, 3.12, 3.13
        python_versions = job.strategy.matrix.values.get("python-version")
        assert python_versions is not None
        assert "3.11" in python_versions
        assert "3.12" in python_versions
        assert "3.13" in python_versions

    def test_scaffold_python_ci_uses_typed_actions(self):
        """python-ci template uses typed action wrappers."""
        from wetwire_github.cli.scaffold_cmd import scaffold_workflow

        workflow = scaffold_workflow("python-ci")
        job = workflow.jobs["test"]
        # Should have checkout and setup-python steps
        uses_list = [step.uses for step in job.steps if step.uses]
        assert any("checkout" in uses for uses in uses_list)
        assert any("setup-python" in uses for uses in uses_list)

    def test_scaffold_python_ci_has_triggers(self):
        """python-ci template has push and pull_request triggers."""
        from wetwire_github.cli.scaffold_cmd import scaffold_workflow

        workflow = scaffold_workflow("python-ci")
        assert workflow.on.push is not None
        assert workflow.on.pull_request is not None

    def test_scaffold_nodejs_ci_returns_workflow(self):
        """nodejs-ci template returns a Workflow object."""
        from wetwire_github.cli.scaffold_cmd import scaffold_workflow

        workflow = scaffold_workflow("nodejs-ci")
        assert isinstance(workflow, Workflow)
        assert workflow.name == "Node.js CI"

    def test_scaffold_nodejs_ci_uses_setup_node(self):
        """nodejs-ci template uses setup-node action."""
        from wetwire_github.cli.scaffold_cmd import scaffold_workflow

        workflow = scaffold_workflow("nodejs-ci")
        job = workflow.jobs["build"]
        uses_list = [step.uses for step in job.steps if step.uses]
        assert any("setup-node" in uses for uses in uses_list)

    def test_scaffold_nodejs_ci_has_npm_steps(self):
        """nodejs-ci template has npm install and test steps."""
        from wetwire_github.cli.scaffold_cmd import scaffold_workflow

        workflow = scaffold_workflow("nodejs-ci")
        job = workflow.jobs["build"]
        run_commands = [step.run for step in job.steps if step.run]
        # Should have npm ci or npm install
        assert any("npm" in cmd for cmd in run_commands)

    def test_scaffold_release_returns_workflow(self):
        """release template returns a Workflow object."""
        from wetwire_github.cli.scaffold_cmd import scaffold_workflow

        workflow = scaffold_workflow("release")
        assert isinstance(workflow, Workflow)
        assert workflow.name == "Release"

    def test_scaffold_release_has_release_trigger(self):
        """release template triggers on release."""
        from wetwire_github.cli.scaffold_cmd import scaffold_workflow

        workflow = scaffold_workflow("release")
        # Should trigger on push tags (semver pattern)
        assert workflow.on.push is not None
        assert workflow.on.push.tags is not None
        # Tags should include semver pattern
        assert any("v*" in tag for tag in workflow.on.push.tags)

    def test_scaffold_release_has_publish_job(self):
        """release template has a release/publish job."""
        from wetwire_github.cli.scaffold_cmd import scaffold_workflow

        workflow = scaffold_workflow("release")
        # Should have release job
        assert "release" in workflow.jobs or "publish" in workflow.jobs

    def test_scaffold_docker_returns_workflow(self):
        """docker template returns a Workflow object."""
        from wetwire_github.cli.scaffold_cmd import scaffold_workflow

        workflow = scaffold_workflow("docker")
        assert isinstance(workflow, Workflow)
        assert workflow.name == "Docker"

    def test_scaffold_docker_uses_docker_actions(self):
        """docker template uses docker actions."""
        from wetwire_github.cli.scaffold_cmd import scaffold_workflow

        workflow = scaffold_workflow("docker")
        job = list(workflow.jobs.values())[0]
        uses_list = [step.uses for step in job.steps if step.uses]
        # Should use docker/login-action and docker/build-push-action
        assert any("docker/login-action" in uses for uses in uses_list)
        assert any("docker/build-push-action" in uses for uses in uses_list)

    def test_scaffold_docker_has_buildx_setup(self):
        """docker template sets up Docker Buildx."""
        from wetwire_github.cli.scaffold_cmd import scaffold_workflow

        workflow = scaffold_workflow("docker")
        job = list(workflow.jobs.values())[0]
        uses_list = [step.uses for step in job.steps if step.uses]
        assert any("setup-buildx" in uses for uses in uses_list)

    def test_scaffold_unknown_template_raises(self):
        """Unknown template raises ValueError."""
        from wetwire_github.cli.scaffold_cmd import scaffold_workflow

        with pytest.raises(ValueError, match="Unknown template"):
            scaffold_workflow("unknown-template")

    def test_scaffold_lists_available_templates(self):
        """Available templates can be listed."""
        from wetwire_github.cli.scaffold_cmd import get_available_templates

        templates = get_available_templates()
        assert "python-ci" in templates
        assert "nodejs-ci" in templates
        assert "release" in templates
        assert "docker" in templates


class TestScaffoldWriteOutput:
    """Tests for scaffold output writing."""

    def test_scaffold_writes_to_file(self, tmp_path):
        """Scaffold writes generated code to file."""
        from wetwire_github.cli.scaffold_cmd import scaffold_to_file

        output_file = tmp_path / "workflows.py"
        exit_code, messages = scaffold_to_file(
            template="python-ci",
            output=str(output_file),
        )

        assert exit_code == 0
        assert output_file.exists()
        content = output_file.read_text()
        # Should contain template import and usage
        assert "wetwire_github.templates" in content
        assert "python_ci_workflow" in content

    def test_scaffold_generates_valid_python(self, tmp_path):
        """Scaffold generates valid Python code."""
        from wetwire_github.cli.scaffold_cmd import scaffold_to_file

        output_file = tmp_path / "workflows.py"
        exit_code, messages = scaffold_to_file(
            template="python-ci",
            output=str(output_file),
        )

        assert exit_code == 0
        # Check it's valid Python by compiling it
        source = output_file.read_text()
        compile(source, str(output_file), "exec")

    def test_scaffold_generates_importable_code(self, tmp_path):
        """Scaffold generates importable Python code."""
        from wetwire_github.cli.scaffold_cmd import scaffold_to_file

        output_file = tmp_path / "workflows.py"
        exit_code, messages = scaffold_to_file(
            template="python-ci",
            output=str(output_file),
        )

        assert exit_code == 0
        # Try to execute the generated code
        source = output_file.read_text()
        exec(compile(source, str(output_file), "exec"), {"__name__": "__main__"})


class TestScaffoldCommandCLI:
    """Tests for scaffold command via CLI."""

    def test_scaffold_command_runs(self, tmp_path):
        """Scaffold command runs successfully."""
        output_file = tmp_path / "workflows.py"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_github.cli",
                "scaffold",
                "--template",
                "python-ci",
                "--output",
                str(output_file),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert output_file.exists()

    def test_scaffold_command_help(self):
        """Scaffold command has help text."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "scaffold", "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "--template" in result.stdout
        assert "--output" in result.stdout

    def test_scaffold_command_lists_templates(self):
        """Scaffold command can list available templates."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_github.cli",
                "scaffold",
                "--list-templates",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "python-ci" in result.stdout
        assert "nodejs-ci" in result.stdout
        assert "release" in result.stdout
        assert "docker" in result.stdout

    def test_scaffold_requires_template_or_list(self, tmp_path):
        """Scaffold requires --template or --list-templates."""
        output_file = tmp_path / "workflows.py"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_github.cli",
                "scaffold",
                "--output",
                str(output_file),
            ],
            capture_output=True,
            text=True,
        )

        # Should fail or show help
        assert result.returncode != 0 or "template" in result.stdout.lower()


class TestTemplateModules:
    """Tests for individual template modules."""

    def test_python_ci_template_module(self):
        """python_ci module returns valid workflow."""
        from wetwire_github.templates.python_ci import python_ci_workflow

        workflow = python_ci_workflow()
        assert isinstance(workflow, Workflow)
        assert len(workflow.jobs) > 0

    def test_nodejs_ci_template_module(self):
        """nodejs_ci module returns valid workflow."""
        from wetwire_github.templates.nodejs_ci import nodejs_ci_workflow

        workflow = nodejs_ci_workflow()
        assert isinstance(workflow, Workflow)
        assert len(workflow.jobs) > 0

    def test_release_template_module(self):
        """release module returns valid workflow."""
        from wetwire_github.templates.release import release_workflow

        workflow = release_workflow()
        assert isinstance(workflow, Workflow)
        assert len(workflow.jobs) > 0

    def test_docker_template_module(self):
        """docker module returns valid workflow."""
        from wetwire_github.templates.docker import docker_workflow

        workflow = docker_workflow()
        assert isinstance(workflow, Workflow)
        assert len(workflow.jobs) > 0

    def test_all_templates_have_timeout(self):
        """All templates should have reasonable timeouts set."""
        from wetwire_github.templates.docker import docker_workflow
        from wetwire_github.templates.nodejs_ci import nodejs_ci_workflow
        from wetwire_github.templates.python_ci import python_ci_workflow
        from wetwire_github.templates.release import release_workflow

        for workflow_fn in [
            python_ci_workflow,
            nodejs_ci_workflow,
            release_workflow,
            docker_workflow,
        ]:
            workflow = workflow_fn()
            for job in workflow.jobs.values():
                assert (
                    job.timeout_minutes is not None
                ), f"{workflow.name} job missing timeout"
