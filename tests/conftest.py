"""Shared pytest fixtures for wetwire-github tests.

This module provides common fixtures used across test files to reduce
duplication and ensure consistent test data.

Available fixtures:
- simple_step: A basic Step with a run command
- simple_job: A basic Job with ubuntu-latest runner and steps
- simple_workflow: A complete Workflow with push trigger and test job
- temp_workflow_dir: Temporary directory with workflows/ and .github/workflows/ structure
- workflow_package_dir: Temporary Python package directory for workflow definitions
- yaml_parser: The yaml module for parsing YAML content

Usage example:
    def test_workflow_serialization(simple_workflow, yaml_parser):
        from wetwire_github.serialize import to_yaml
        yaml_output = to_yaml(simple_workflow)
        parsed = yaml_parser.safe_load(yaml_output)
        assert parsed["name"] == "Test Workflow"
"""

import pytest
import yaml

from wetwire_github.workflow import (
    Job,
    PushTrigger,
    Step,
    Triggers,
    Workflow,
)


@pytest.fixture
def simple_step():
    """Provide a simple Step for testing.

    Returns:
        Step: A basic Step with a run command.
    """
    return Step(run="echo 'Hello, World!'")


@pytest.fixture
def simple_job():
    """Provide a simple Job for testing.

    Returns:
        Job: A basic Job with ubuntu-latest runner and a simple step.
    """
    return Job(
        runs_on="ubuntu-latest",
        steps=[
            Step(uses="actions/checkout@v4"),
            Step(run="echo 'Running tests'"),
        ],
    )


@pytest.fixture
def simple_workflow():
    """Provide a simple Workflow for testing.

    Returns:
        Workflow: A basic Workflow with push trigger and test job.
    """
    return Workflow(
        name="Test Workflow",
        on=Triggers(push=PushTrigger(branches=["main"])),
        jobs={
            "test": Job(
                runs_on="ubuntu-latest",
                steps=[
                    Step(uses="actions/checkout@v4"),
                    Step(run="pytest"),
                ],
            ),
        },
    )


@pytest.fixture
def temp_workflow_dir(tmp_path):
    """Provide a temporary directory structure for workflow testing.

    Creates:
        - workflows/ directory with __init__.py
        - .github/workflows/ directory for output

    Args:
        tmp_path: pytest's tmp_path fixture.

    Returns:
        Path: The temporary directory path.
    """
    # Create workflows package directory
    workflows_dir = tmp_path / "workflows"
    workflows_dir.mkdir()
    (workflows_dir / "__init__.py").write_text("")

    # Create .github/workflows output directory
    github_dir = tmp_path / ".github"
    github_dir.mkdir()
    workflows_output_dir = github_dir / "workflows"
    workflows_output_dir.mkdir()

    return tmp_path


@pytest.fixture
def workflow_package_dir(tmp_path):
    """Provide a temporary Python package directory for workflows.

    Creates a minimal Python package structure suitable for workflow
    definitions.

    Args:
        tmp_path: pytest's tmp_path fixture.

    Returns:
        Path: The package directory path.
    """
    pkg_dir = tmp_path / "workflows"
    pkg_dir.mkdir()
    (pkg_dir / "__init__.py").write_text("")
    return pkg_dir


@pytest.fixture
def yaml_parser():
    """Provide the yaml module for parsing YAML content.

    Returns:
        module: The yaml module.
    """
    return yaml
