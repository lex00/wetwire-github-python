"""Tests for step output definitions."""

import yaml

from wetwire_github.serialize import to_dict, to_yaml
from wetwire_github.workflow import Job, Step


class TestStepOutput:
    """Tests for StepOutput dataclass."""

    def test_step_output_creation_with_all_fields(self):
        """StepOutput can be created with description and value."""
        from wetwire_github.workflow import StepOutput

        output = StepOutput(
            description="The version number",
            value="${{ steps.version.outputs.value }}",
        )
        assert output.description == "The version number"
        assert output.value == "${{ steps.version.outputs.value }}"

    def test_step_output_creation_with_value_only(self):
        """StepOutput can be created with just value."""
        from wetwire_github.workflow import StepOutput

        output = StepOutput(value="${{ steps.build.outputs.artifact }}")
        assert output.value == "${{ steps.build.outputs.artifact }}"
        assert output.description is None

    def test_step_output_creation_with_description_only(self):
        """StepOutput can be created with just description."""
        from wetwire_github.workflow import StepOutput

        output = StepOutput(description="Build artifact path")
        assert output.description == "Build artifact path"
        assert output.value is None

    def test_step_output_creation_empty(self):
        """StepOutput can be created with no parameters."""
        from wetwire_github.workflow import StepOutput

        output = StepOutput()
        assert output.description is None
        assert output.value is None


class TestStepWithOutputs:
    """Tests for Step with outputs field."""

    def test_step_with_single_output(self):
        """Step can have a single output."""
        from wetwire_github.workflow import StepOutput

        step = Step(
            id="version",
            run="echo version=1.0.0 >> $GITHUB_OUTPUT",
            outputs={
                "version": StepOutput(
                    description="The version number",
                    value="${{ steps.version.outputs.version }}",
                )
            },
        )
        assert "version" in step.outputs
        assert step.outputs["version"].description == "The version number"

    def test_step_with_multiple_outputs(self):
        """Step can have multiple outputs."""
        from wetwire_github.workflow import StepOutput

        step = Step(
            id="build",
            run="echo artifact=build.tar.gz >> $GITHUB_OUTPUT",
            outputs={
                "artifact": StepOutput(
                    description="Build artifact path",
                    value="${{ steps.build.outputs.artifact }}",
                ),
                "checksum": StepOutput(
                    description="SHA256 checksum",
                    value="${{ steps.build.outputs.checksum }}",
                ),
            },
        )
        assert len(step.outputs) == 2
        assert "artifact" in step.outputs
        assert "checksum" in step.outputs

    def test_step_without_outputs(self):
        """Step can be created without outputs."""
        step = Step(run="echo hello")
        assert step.outputs is None


class TestStepOutputSerialization:
    """Tests for StepOutput serialization."""

    def test_step_output_serializes_both_fields(self):
        """StepOutput with both fields serializes correctly."""
        from wetwire_github.workflow import StepOutput

        output = StepOutput(
            description="The version number",
            value="${{ steps.version.outputs.version }}",
        )
        result = to_dict(output)
        assert result["description"] == "The version number"
        assert result["value"] == "${{ steps.version.outputs.version }}"

    def test_step_output_serializes_value_only(self):
        """StepOutput with only value serializes correctly."""
        from wetwire_github.workflow import StepOutput

        output = StepOutput(value="${{ steps.build.outputs.artifact }}")
        result = to_dict(output)
        assert result["value"] == "${{ steps.build.outputs.artifact }}"
        assert "description" not in result

    def test_step_output_serializes_description_only(self):
        """StepOutput with only description serializes correctly."""
        from wetwire_github.workflow import StepOutput

        output = StepOutput(description="Build artifact path")
        result = to_dict(output)
        assert result["description"] == "Build artifact path"
        assert "value" not in result

    def test_step_output_empty_omitted(self):
        """Empty StepOutput is omitted from serialization."""
        from wetwire_github.workflow import StepOutput

        output = StepOutput()
        result = to_dict(output)
        # Empty dataclass should serialize to empty dict
        assert result == {}

    def test_step_with_outputs_serializes(self):
        """Step with outputs field serializes correctly."""
        from wetwire_github.workflow import StepOutput

        step = Step(
            id="version",
            run="echo version=1.0.0 >> $GITHUB_OUTPUT",
            outputs={
                "version": StepOutput(
                    description="The version number",
                    value="${{ steps.version.outputs.version }}",
                )
            },
        )
        result = to_dict(step)
        assert result["id"] == "version"
        assert "outputs" in result
        assert "version" in result["outputs"]
        assert result["outputs"]["version"]["description"] == "The version number"
        assert (
            result["outputs"]["version"]["value"]
            == "${{ steps.version.outputs.version }}"
        )

    def test_step_with_multiple_outputs_serializes(self):
        """Step with multiple outputs serializes correctly."""
        from wetwire_github.workflow import StepOutput

        step = Step(
            id="build",
            run="build.sh",
            outputs={
                "artifact": StepOutput(
                    description="Build artifact path",
                    value="${{ steps.build.outputs.artifact }}",
                ),
                "checksum": StepOutput(value="${{ steps.build.outputs.checksum }}"),
            },
        )
        result = to_dict(step)
        assert len(result["outputs"]) == 2
        assert result["outputs"]["artifact"]["description"] == "Build artifact path"
        assert (
            result["outputs"]["artifact"]["value"]
            == "${{ steps.build.outputs.artifact }}"
        )
        # checksum has no description, so it should only have value
        assert (
            result["outputs"]["checksum"]["value"]
            == "${{ steps.build.outputs.checksum }}"
        )
        assert "description" not in result["outputs"]["checksum"]

    def test_step_without_outputs_omits_field(self):
        """Step without outputs omits the outputs field."""
        step = Step(run="echo hello")
        result = to_dict(step)
        assert "outputs" not in result

    def test_step_with_empty_outputs_dict_omits_field(self):
        """Step with empty outputs dict omits the outputs field."""
        step = Step(run="echo hello", outputs={})
        result = to_dict(step)
        assert "outputs" not in result


class TestStepOutputYAML:
    """Tests for StepOutput YAML generation."""

    def test_step_with_outputs_to_yaml(self):
        """Step with outputs generates valid YAML."""
        from wetwire_github.workflow import StepOutput

        step = Step(
            id="version",
            run="echo version=1.0.0 >> $GITHUB_OUTPUT",
            outputs={
                "version": StepOutput(
                    description="The version number",
                    value="${{ steps.version.outputs.version }}",
                )
            },
        )
        result = to_yaml(step)
        parsed = yaml.safe_load(result)
        assert parsed["id"] == "version"
        assert "outputs" in parsed
        assert "version" in parsed["outputs"]
        assert parsed["outputs"]["version"]["description"] == "The version number"

    def test_job_with_step_outputs_to_yaml(self):
        """Job containing steps with outputs generates valid YAML."""
        from wetwire_github.workflow import StepOutput

        job = Job(
            name="build",
            runs_on="ubuntu-latest",
            steps=[
                Step(uses="actions/checkout@v4"),
                Step(
                    id="version",
                    run="echo version=1.0.0 >> $GITHUB_OUTPUT",
                    outputs={
                        "version": StepOutput(
                            description="The version number",
                            value="${{ steps.version.outputs.version }}",
                        )
                    },
                ),
                Step(
                    id="artifact",
                    run="build.sh",
                    outputs={
                        "path": StepOutput(value="${{ steps.artifact.outputs.path }}"),
                    },
                ),
            ],
        )
        result = to_yaml(job)
        parsed = yaml.safe_load(result)
        assert parsed["name"] == "build"
        assert len(parsed["steps"]) == 3
        # First step has no outputs
        assert "outputs" not in parsed["steps"][0]
        # Second step has outputs with description and value
        assert "outputs" in parsed["steps"][1]
        assert "version" in parsed["steps"][1]["outputs"]
        # Third step has outputs with value only
        assert "outputs" in parsed["steps"][2]
        assert "path" in parsed["steps"][2]["outputs"]


class TestStepOutputEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_step_output_with_complex_expression(self):
        """StepOutput can contain complex GitHub expressions."""
        from wetwire_github.workflow import StepOutput

        output = StepOutput(
            description="Computed result",
            value="${{ fromJSON(steps.compute.outputs.result).value }}",
        )
        assert output.value == "${{ fromJSON(steps.compute.outputs.result).value }}"
        result = to_dict(output)
        assert result["value"] == "${{ fromJSON(steps.compute.outputs.result).value }}"

    def test_step_output_with_multiline_description(self):
        """StepOutput can have multiline description."""
        from wetwire_github.workflow import StepOutput

        output = StepOutput(
            description="Line 1\nLine 2\nLine 3",
            value="${{ steps.test.outputs.result }}",
        )
        assert output.description == "Line 1\nLine 2\nLine 3"
        result = to_yaml(output)
        parsed = yaml.safe_load(result)
        assert parsed["description"] == "Line 1\nLine 2\nLine 3"

    def test_step_output_consistency_with_workflow_output(self):
        """StepOutput structure is consistent with WorkflowOutput."""
        from wetwire_github.workflow import StepOutput, WorkflowOutput

        # Both should have description and value fields
        step_out = StepOutput(description="test", value="${{ steps.x.outputs.y }}")
        workflow_out = WorkflowOutput(
            description="test", value="${{ jobs.x.outputs.y }}"
        )

        step_dict = to_dict(step_out)
        workflow_dict = to_dict(workflow_out)

        # Both should have same field names
        assert set(step_dict.keys()) == set(workflow_dict.keys())
        assert "description" in step_dict
        assert "value" in step_dict
