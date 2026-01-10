"""Tests for composite GitHub Actions support."""

import yaml


class TestCompositeActionTypes:
    """Tests for composite action dataclass types."""

    def test_composite_action_dataclass_exists(self):
        """CompositeAction dataclass can be imported."""
        from wetwire_github.composite import CompositeAction

        assert CompositeAction is not None

    def test_action_input_dataclass_exists(self):
        """ActionInput dataclass can be imported."""
        from wetwire_github.composite import ActionInput

        assert ActionInput is not None

    def test_action_output_dataclass_exists(self):
        """ActionOutput dataclass can be imported."""
        from wetwire_github.composite import ActionOutput

        assert ActionOutput is not None

    def test_composite_runs_dataclass_exists(self):
        """CompositeRuns dataclass can be imported."""
        from wetwire_github.composite import CompositeRuns

        assert CompositeRuns is not None


class TestActionInput:
    """Tests for ActionInput dataclass."""

    def test_basic_input(self):
        """Basic input can be created."""
        from wetwire_github.composite import ActionInput

        input_field = ActionInput(description="A test input")
        assert input_field.description == "A test input"
        assert input_field.required is None
        assert input_field.default is None

    def test_required_input(self):
        """Required input can be created."""
        from wetwire_github.composite import ActionInput

        input_field = ActionInput(description="A required input", required=True)
        assert input_field.required is True

    def test_input_with_default(self):
        """Input with default value can be created."""
        from wetwire_github.composite import ActionInput

        input_field = ActionInput(
            description="Input with default", default="default-value"
        )
        assert input_field.default == "default-value"

    def test_input_all_fields(self):
        """Input with all fields can be created."""
        from wetwire_github.composite import ActionInput

        input_field = ActionInput(
            description="Complete input", required=True, default="value"
        )
        assert input_field.description == "Complete input"
        assert input_field.required is True
        assert input_field.default == "value"


class TestActionOutput:
    """Tests for ActionOutput dataclass."""

    def test_basic_output(self):
        """Basic output can be created."""
        from wetwire_github.composite import ActionOutput

        output = ActionOutput(description="A test output", value="${{ steps.test.outputs.result }}")
        assert output.description == "A test output"
        assert output.value == "${{ steps.test.outputs.result }}"

    def test_output_with_expression(self):
        """Output with expression can be created."""
        from wetwire_github.composite import ActionOutput

        output = ActionOutput(
            description="Step output", value="${{ steps.build.outputs.artifact-path }}"
        )
        assert output.value == "${{ steps.build.outputs.artifact-path }}"


class TestCompositeRuns:
    """Tests for CompositeRuns dataclass."""

    def test_basic_runs(self):
        """Basic runs configuration can be created."""
        from wetwire_github.composite import CompositeRuns
        from wetwire_github.workflow import Step

        runs = CompositeRuns(steps=[Step(run="echo 'Hello'")])
        assert runs.using == "composite"
        assert len(runs.steps) == 1

    def test_runs_with_multiple_steps(self):
        """Runs with multiple steps can be created."""
        from wetwire_github.composite import CompositeRuns
        from wetwire_github.workflow import Step

        runs = CompositeRuns(
            steps=[
                Step(uses="actions/checkout@v4"),
                Step(run="make build"),
                Step(run="make test"),
            ]
        )
        assert len(runs.steps) == 3

    def test_runs_default_using(self):
        """Runs defaults to 'composite' for using field."""
        from wetwire_github.composite import CompositeRuns
        from wetwire_github.workflow import Step

        runs = CompositeRuns(steps=[Step(run="echo test")])
        assert runs.using == "composite"


class TestCompositeAction:
    """Tests for CompositeAction dataclass."""

    def test_minimal_composite_action(self):
        """Minimal composite action can be created."""
        from wetwire_github.composite import CompositeAction, CompositeRuns
        from wetwire_github.workflow import Step

        action = CompositeAction(
            name="Test Action",
            description="A test composite action",
            runs=CompositeRuns(steps=[Step(run="echo 'test'")]),
        )
        assert action.name == "Test Action"
        assert action.description == "A test composite action"

    def test_composite_action_with_inputs(self):
        """Composite action with inputs can be created."""
        from wetwire_github.composite import (
            ActionInput,
            CompositeAction,
            CompositeRuns,
        )
        from wetwire_github.workflow import Step

        action = CompositeAction(
            name="Action With Inputs",
            description="An action with inputs",
            inputs={
                "version": ActionInput(description="Version to use", required=True),
                "config": ActionInput(description="Config file", default="config.yml"),
            },
            runs=CompositeRuns(steps=[Step(run="echo ${{ inputs.version }}")]),
        )
        assert "version" in action.inputs
        assert "config" in action.inputs
        assert action.inputs["version"].required is True

    def test_composite_action_with_outputs(self):
        """Composite action with outputs can be created."""
        from wetwire_github.composite import (
            ActionOutput,
            CompositeAction,
            CompositeRuns,
        )
        from wetwire_github.workflow import Step

        action = CompositeAction(
            name="Action With Outputs",
            description="An action with outputs",
            outputs={
                "result": ActionOutput(
                    description="Build result", value="${{ steps.build.outputs.result }}"
                ),
            },
            runs=CompositeRuns(
                steps=[Step(id="build", run="echo 'result=success' >> $GITHUB_OUTPUT")]
            ),
        )
        assert "result" in action.outputs
        assert action.outputs["result"].description == "Build result"

    def test_complete_composite_action(self):
        """Complete composite action with all fields can be created."""
        from wetwire_github.composite import (
            ActionInput,
            ActionOutput,
            CompositeAction,
            CompositeRuns,
        )
        from wetwire_github.workflow import Step

        action = CompositeAction(
            name="Complete Action",
            description="A complete composite action",
            inputs={
                "version": ActionInput(description="Version", required=True),
            },
            outputs={
                "result": ActionOutput(description="Result", value="${{ steps.test.outputs.result }}"),
            },
            runs=CompositeRuns(
                steps=[
                    Step(uses="actions/checkout@v4"),
                    Step(id="test", run="echo 'result=pass' >> $GITHUB_OUTPUT"),
                ]
            ),
        )
        assert action.name == "Complete Action"
        assert action.inputs is not None
        assert action.outputs is not None
        assert len(action.runs.steps) == 2


class TestCompositeActionSerialization:
    """Tests for composite action YAML serialization."""

    def test_serialize_minimal_action(self):
        """Minimal composite action serializes to valid YAML."""
        from wetwire_github.composite import CompositeAction, CompositeRuns
        from wetwire_github.serialize import to_dict
        from wetwire_github.workflow import Step

        action = CompositeAction(
            name="Test Action",
            description="A test action",
            runs=CompositeRuns(steps=[Step(run="echo 'test'")]),
        )

        result = to_dict(action)
        assert result["name"] == "Test Action"
        assert result["description"] == "A test action"
        assert result["runs"]["using"] == "composite"
        assert len(result["runs"]["steps"]) == 1

    def test_serialize_action_with_inputs(self):
        """Action with inputs serializes correctly."""
        from wetwire_github.composite import (
            ActionInput,
            CompositeAction,
            CompositeRuns,
        )
        from wetwire_github.serialize import to_dict
        from wetwire_github.workflow import Step

        action = CompositeAction(
            name="Action With Inputs",
            description="Test",
            inputs={
                "version": ActionInput(description="Version to use", required=True),
                "config": ActionInput(description="Config file", default="config.yml"),
            },
            runs=CompositeRuns(steps=[Step(run="echo test")]),
        )

        result = to_dict(action)
        assert "inputs" in result
        assert "version" in result["inputs"]
        assert result["inputs"]["version"]["description"] == "Version to use"
        assert result["inputs"]["version"]["required"] is True
        assert "config" in result["inputs"]
        assert result["inputs"]["config"]["default"] == "config.yml"

    def test_serialize_action_with_outputs(self):
        """Action with outputs serializes correctly."""
        from wetwire_github.composite import (
            ActionOutput,
            CompositeAction,
            CompositeRuns,
        )
        from wetwire_github.serialize import to_dict
        from wetwire_github.workflow import Step

        action = CompositeAction(
            name="Action With Outputs",
            description="Test",
            outputs={
                "result": ActionOutput(
                    description="Build result", value="${{ steps.build.outputs.result }}"
                ),
            },
            runs=CompositeRuns(steps=[Step(id="build", run="echo test")]),
        )

        result = to_dict(action)
        assert "outputs" in result
        assert "result" in result["outputs"]
        assert result["outputs"]["result"]["description"] == "Build result"
        assert result["outputs"]["result"]["value"] == "${{ steps.build.outputs.result }}"

    def test_serialize_to_yaml_string(self):
        """Composite action can be converted to YAML string."""
        from wetwire_github.composite import (
            ActionInput,
            ActionOutput,
            CompositeAction,
            CompositeRuns,
        )
        from wetwire_github.serialize import to_yaml
        from wetwire_github.workflow import Step

        action = CompositeAction(
            name="Setup Tool",
            description="Sets up a tool",
            inputs={
                "version": ActionInput(description="Tool version", required=True),
            },
            outputs={
                "path": ActionOutput(description="Tool path", value="${{ steps.setup.outputs.path }}"),
            },
            runs=CompositeRuns(
                steps=[
                    Step(
                        id="setup",
                        run="echo 'path=/usr/local/bin' >> $GITHUB_OUTPUT",
                        shell="bash",
                    ),
                ]
            ),
        )

        yaml_str = to_yaml(action)
        assert "name: Setup Tool" in yaml_str
        assert "description: Sets up a tool" in yaml_str
        assert "inputs:" in yaml_str
        assert "outputs:" in yaml_str
        assert "runs:" in yaml_str
        assert "using: composite" in yaml_str

    def test_yaml_structure_matches_github_format(self):
        """Generated YAML matches GitHub composite action format."""
        from wetwire_github.composite import (
            ActionInput,
            CompositeAction,
            CompositeRuns,
        )
        from wetwire_github.serialize import to_yaml
        from wetwire_github.workflow import Step

        action = CompositeAction(
            name="My Action",
            description="Does something",
            inputs={
                "input1": ActionInput(description="First input", required=True),
            },
            runs=CompositeRuns(
                steps=[
                    Step(uses="actions/checkout@v4"),
                    Step(run="echo 'Hello'", shell="bash"),
                ]
            ),
        )

        yaml_str = to_yaml(action)
        parsed = yaml.safe_load(yaml_str)

        assert parsed["name"] == "My Action"
        assert parsed["description"] == "Does something"
        assert "input1" in parsed["inputs"]
        assert parsed["inputs"]["input1"]["required"] is True
        assert parsed["runs"]["using"] == "composite"
        assert len(parsed["runs"]["steps"]) == 2

    def test_optional_input_fields_omitted_when_default(self):
        """Optional fields are omitted when they have default values."""
        from wetwire_github.composite import (
            ActionInput,
            CompositeAction,
            CompositeRuns,
        )
        from wetwire_github.serialize import to_dict
        from wetwire_github.workflow import Step

        action = CompositeAction(
            name="Test",
            description="Test",
            inputs={
                "optional": ActionInput(description="Optional input"),
            },
            runs=CompositeRuns(steps=[Step(run="echo test")]),
        )

        result = to_dict(action)
        # required=False should be omitted (it's the default)
        # default=None should be omitted
        assert "required" not in result["inputs"]["optional"]
        assert "default" not in result["inputs"]["optional"]

    def test_steps_serialize_with_shell(self):
        """Steps in composite actions include shell when specified."""
        from wetwire_github.composite import CompositeAction, CompositeRuns
        from wetwire_github.serialize import to_dict
        from wetwire_github.workflow import Step

        action = CompositeAction(
            name="Test",
            description="Test",
            runs=CompositeRuns(
                steps=[
                    Step(run="echo 'test'", shell="bash"),
                ]
            ),
        )

        result = to_dict(action)
        assert result["runs"]["steps"][0]["shell"] == "bash"
