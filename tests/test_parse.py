"""Tests for schema parsing."""

import sys
from pathlib import Path

# Add codegen to path
sys.path.insert(0, str(Path(__file__).parent.parent / "codegen"))

from parse import (
    ActionInput,
    ActionOutput,
    ActionSchema,
    WorkflowProperty,
    WorkflowSchema,
    parse_action_yml,
    parse_workflow_schema,
)


class TestActionInput:
    """Tests for ActionInput dataclass."""

    def test_action_input_required(self):
        """ActionInput stores required flag."""
        inp = ActionInput(
            name="token",
            description="GitHub token",
            required=True,
            default=None,
        )
        assert inp.name == "token"
        assert inp.description == "GitHub token"
        assert inp.required is True
        assert inp.default is None

    def test_action_input_with_default(self):
        """ActionInput stores default value."""
        inp = ActionInput(
            name="fetch-depth",
            description="Number of commits to fetch",
            required=False,
            default="1",
        )
        assert inp.default == "1"
        assert inp.required is False


class TestActionOutput:
    """Tests for ActionOutput dataclass."""

    def test_action_output(self):
        """ActionOutput stores output info."""
        out = ActionOutput(
            name="version",
            description="The version that was set up",
        )
        assert out.name == "version"
        assert out.description == "The version that was set up"


class TestActionSchema:
    """Tests for ActionSchema dataclass."""

    def test_action_schema(self):
        """ActionSchema stores parsed action data."""
        schema = ActionSchema(
            name="Checkout",
            description="Checkout a repository",
            author="GitHub",
            inputs=[
                ActionInput("ref", "The branch/tag/SHA", False, None),
                ActionInput("token", "Auth token", False, "${{ github.token }}"),
            ],
            outputs=[
                ActionOutput("ref", "The ref that was checked out"),
            ],
        )
        assert schema.name == "Checkout"
        assert len(schema.inputs) == 2
        assert len(schema.outputs) == 1


class TestParseActionYml:
    """Tests for parse_action_yml function."""

    def test_parse_checkout_action(self):
        """Parse actions/checkout action.yml."""
        yml_content = """
name: 'Checkout'
description: 'Checkout a Git repository at a particular version'
author: 'GitHub'
inputs:
  repository:
    description: 'Repository name with owner'
    required: false
    default: ${{ github.repository }}
  ref:
    description: 'The branch, tag or SHA to checkout'
    required: false
  token:
    description: 'Token for authentication'
    required: false
    default: ${{ github.token }}
  fetch-depth:
    description: 'Number of commits to fetch'
    required: false
    default: '1'
outputs:
  ref:
    description: 'The branch, tag or SHA that was checked out'
  commit:
    description: 'The commit SHA that was checked out'
runs:
  using: 'node20'
  main: 'dist/index.js'
"""
        schema = parse_action_yml(yml_content)
        assert schema.name == "Checkout"
        assert schema.author == "GitHub"
        assert len(schema.inputs) == 4
        assert len(schema.outputs) == 2

        # Check specific input
        repo_input = next(i for i in schema.inputs if i.name == "repository")
        assert repo_input.default == "${{ github.repository }}"

        # Check output
        ref_output = next(o for o in schema.outputs if o.name == "ref")
        assert "checked out" in ref_output.description

    def test_parse_action_without_inputs(self):
        """Parse action.yml without inputs."""
        yml_content = """
name: 'Simple Action'
description: 'An action without inputs'
runs:
  using: 'node20'
  main: 'index.js'
"""
        schema = parse_action_yml(yml_content)
        assert schema.name == "Simple Action"
        assert len(schema.inputs) == 0
        assert len(schema.outputs) == 0

    def test_parse_action_with_required_input(self):
        """Parse action.yml with required input."""
        yml_content = """
name: 'Test Action'
description: 'Test'
inputs:
  required-input:
    description: 'This is required'
    required: true
runs:
  using: 'node20'
  main: 'index.js'
"""
        schema = parse_action_yml(yml_content)
        assert len(schema.inputs) == 1
        assert schema.inputs[0].required is True


class TestWorkflowProperty:
    """Tests for WorkflowProperty dataclass."""

    def test_workflow_property(self):
        """WorkflowProperty stores property info."""
        prop = WorkflowProperty(
            name="runs-on",
            description="The type of machine to run the job on",
            type="string",
            required=True,
            default=None,
            enum=None,
        )
        assert prop.name == "runs-on"
        assert prop.type == "string"
        assert prop.required is True

    def test_workflow_property_with_enum(self):
        """WorkflowProperty stores enum values."""
        prop = WorkflowProperty(
            name="shell",
            description="Shell to use",
            type="string",
            required=False,
            default=None,
            enum=["bash", "pwsh", "python", "sh", "cmd"],
        )
        assert prop.enum is not None
        assert "bash" in prop.enum


class TestWorkflowSchema:
    """Tests for WorkflowSchema dataclass."""

    def test_workflow_schema(self):
        """WorkflowSchema stores parsed workflow schema."""
        schema = WorkflowSchema(
            properties={
                "name": WorkflowProperty(
                    "name", "Workflow name", "string", False, None, None
                ),
            },
            definitions={},
        )
        assert "name" in schema.properties


class TestParseWorkflowSchema:
    """Tests for parse_workflow_schema function."""

    def test_parse_minimal_schema(self):
        """Parse minimal workflow schema."""
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the workflow",
                }
            },
        }
        schema = parse_workflow_schema(json_schema)
        assert "name" in schema.properties
        assert schema.properties["name"].type == "string"

    def test_parse_schema_with_required(self):
        """Parse workflow schema with required properties."""
        json_schema = {
            "type": "object",
            "required": ["on"],
            "properties": {
                "name": {"type": "string"},
                "on": {"type": "object"},
            },
        }
        schema = parse_workflow_schema(json_schema)
        assert schema.properties["on"].required is True
        assert schema.properties["name"].required is False

    def test_parse_schema_with_definitions(self):
        """Parse workflow schema with definitions."""
        json_schema = {
            "type": "object",
            "properties": {},
            "definitions": {
                "job": {
                    "type": "object",
                    "properties": {
                        "runs-on": {"type": "string"},
                    },
                }
            },
        }
        schema = parse_workflow_schema(json_schema)
        assert "job" in schema.definitions
