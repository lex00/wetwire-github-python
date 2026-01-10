"""Tests for reference validation in workflows.

Tests for detecting:
- Undefined job dependencies
- Orphaned outputs (outputs defined but never used)
- Duplicate step IDs
- Invalid step output references
"""

from wetwire_github.validation import (
    ReferenceValidationResult,
    validate_job_dependencies,
    validate_step_ids,
    validate_step_outputs,
)
from wetwire_github.workflow import Job, Step, Workflow


class TestValidateJobDependencies:
    """Tests for validate_job_dependencies function."""

    def test_valid_job_dependencies(self):
        """Jobs with valid needs references pass validation."""
        build_job = Job(runs_on="ubuntu-latest", steps=[Step(run="make build")])
        test_job = Job(
            runs_on="ubuntu-latest",
            needs=["build"],
            steps=[Step(run="make test")],
        )
        workflow = Workflow(
            name="CI",
            jobs={"build": build_job, "test": test_job},
        )

        result = validate_job_dependencies(workflow)

        assert result.valid is True
        assert len(result.errors) == 0

    def test_undefined_job_dependency(self):
        """Detect when a job needs a job that doesn't exist."""
        test_job = Job(
            runs_on="ubuntu-latest",
            needs=["nonexistent"],
            steps=[Step(run="make test")],
        )
        workflow = Workflow(name="CI", jobs={"test": test_job})

        result = validate_job_dependencies(workflow)

        assert result.valid is False
        assert len(result.errors) == 1
        assert "nonexistent" in result.errors[0].message
        assert result.errors[0].job_id == "test"

    def test_multiple_undefined_dependencies(self):
        """Detect multiple undefined job dependencies."""
        deploy_job = Job(
            runs_on="ubuntu-latest",
            needs=["build", "test", "lint"],
            steps=[Step(run="make deploy")],
        )
        workflow = Workflow(name="Deploy", jobs={"deploy": deploy_job})

        result = validate_job_dependencies(workflow)

        assert result.valid is False
        assert len(result.errors) == 3

    def test_partial_valid_dependencies(self):
        """Detect only invalid dependencies when some are valid."""
        build_job = Job(runs_on="ubuntu-latest", steps=[Step(run="make build")])
        deploy_job = Job(
            runs_on="ubuntu-latest",
            needs=["build", "nonexistent"],
            steps=[Step(run="make deploy")],
        )
        workflow = Workflow(
            name="CI",
            jobs={"build": build_job, "deploy": deploy_job},
        )

        result = validate_job_dependencies(workflow)

        assert result.valid is False
        assert len(result.errors) == 1
        assert "nonexistent" in result.errors[0].message

    def test_job_with_no_dependencies(self):
        """Jobs without needs pass validation."""
        build_job = Job(runs_on="ubuntu-latest", steps=[Step(run="make build")])
        workflow = Workflow(name="CI", jobs={"build": build_job})

        result = validate_job_dependencies(workflow)

        assert result.valid is True

    def test_empty_workflow(self):
        """Empty workflow passes validation."""
        workflow = Workflow(name="Empty")

        result = validate_job_dependencies(workflow)

        assert result.valid is True


class TestValidateStepIds:
    """Tests for validate_step_ids function."""

    def test_unique_step_ids(self):
        """Steps with unique IDs pass validation."""
        job = Job(
            runs_on="ubuntu-latest",
            steps=[
                Step(id="checkout", uses="actions/checkout@v4"),
                Step(id="build", run="make build"),
                Step(id="test", run="make test"),
            ],
        )
        workflow = Workflow(name="CI", jobs={"build": job})

        result = validate_step_ids(workflow)

        assert result.valid is True
        assert len(result.errors) == 0

    def test_duplicate_step_ids_in_job(self):
        """Detect duplicate step IDs within a job."""
        job = Job(
            runs_on="ubuntu-latest",
            steps=[
                Step(id="setup", run="echo setup"),
                Step(id="setup", run="echo another setup"),  # Duplicate
            ],
        )
        workflow = Workflow(name="CI", jobs={"build": job})

        result = validate_step_ids(workflow)

        assert result.valid is False
        assert len(result.errors) == 1
        assert "setup" in result.errors[0].message
        assert result.errors[0].job_id == "build"

    def test_same_step_id_in_different_jobs(self):
        """Same step ID in different jobs is allowed."""
        build_job = Job(
            runs_on="ubuntu-latest",
            steps=[Step(id="checkout", uses="actions/checkout@v4")],
        )
        test_job = Job(
            runs_on="ubuntu-latest",
            steps=[Step(id="checkout", uses="actions/checkout@v4")],
        )
        workflow = Workflow(
            name="CI",
            jobs={"build": build_job, "test": test_job},
        )

        result = validate_step_ids(workflow)

        assert result.valid is True

    def test_multiple_duplicate_step_ids(self):
        """Detect multiple sets of duplicate step IDs."""
        job = Job(
            runs_on="ubuntu-latest",
            steps=[
                Step(id="a", run="echo 1"),
                Step(id="a", run="echo 2"),
                Step(id="b", run="echo 3"),
                Step(id="b", run="echo 4"),
            ],
        )
        workflow = Workflow(name="CI", jobs={"build": job})

        result = validate_step_ids(workflow)

        assert result.valid is False
        assert len(result.errors) == 2

    def test_steps_without_ids(self):
        """Steps without IDs pass validation."""
        job = Job(
            runs_on="ubuntu-latest",
            steps=[
                Step(run="echo 1"),
                Step(run="echo 2"),
            ],
        )
        workflow = Workflow(name="CI", jobs={"build": job})

        result = validate_step_ids(workflow)

        assert result.valid is True

    def test_mixed_steps_with_and_without_ids(self):
        """Mix of steps with and without IDs validates correctly."""
        job = Job(
            runs_on="ubuntu-latest",
            steps=[
                Step(id="checkout", uses="actions/checkout@v4"),
                Step(run="echo no id"),
                Step(id="checkout", run="duplicate"),  # Duplicate
            ],
        )
        workflow = Workflow(name="CI", jobs={"build": job})

        result = validate_step_ids(workflow)

        assert result.valid is False
        assert len(result.errors) == 1


class TestValidateStepOutputs:
    """Tests for validate_step_outputs function."""

    def test_valid_step_output_reference(self):
        """Valid step output references pass validation."""
        job = Job(
            runs_on="ubuntu-latest",
            steps=[
                Step(id="version", run="echo 'version=1.0' >> $GITHUB_OUTPUT"),
                Step(run="echo ${{ steps.version.outputs.version }}"),
            ],
        )
        workflow = Workflow(name="CI", jobs={"build": job})

        result = validate_step_outputs(workflow)

        assert result.valid is True
        assert len(result.errors) == 0

    def test_invalid_step_output_reference(self):
        """Detect references to undefined step IDs."""
        job = Job(
            runs_on="ubuntu-latest",
            steps=[
                Step(run="echo ${{ steps.nonexistent.outputs.value }}"),
            ],
        )
        workflow = Workflow(name="CI", jobs={"build": job})

        result = validate_step_outputs(workflow)

        assert result.valid is False
        assert len(result.errors) == 1
        assert "nonexistent" in result.errors[0].message

    def test_forward_reference_to_step(self):
        """Detect forward references to steps defined later."""
        job = Job(
            runs_on="ubuntu-latest",
            steps=[
                Step(run="echo ${{ steps.later.outputs.value }}"),  # Forward ref
                Step(id="later", run="echo 'value=test' >> $GITHUB_OUTPUT"),
            ],
        )
        workflow = Workflow(name="CI", jobs={"build": job})

        result = validate_step_outputs(workflow)

        assert result.valid is False
        assert len(result.errors) == 1
        assert "later" in result.errors[0].message

    def test_valid_job_output_reference(self):
        """Job outputs referencing step outputs are validated."""
        job = Job(
            runs_on="ubuntu-latest",
            steps=[
                Step(id="version", run="echo 'version=1.0' >> $GITHUB_OUTPUT"),
            ],
            outputs={"version": "${{ steps.version.outputs.version }}"},
        )
        workflow = Workflow(name="CI", jobs={"build": job})

        result = validate_step_outputs(workflow)

        assert result.valid is True

    def test_invalid_job_output_reference(self):
        """Detect job outputs referencing undefined step IDs."""
        job = Job(
            runs_on="ubuntu-latest",
            steps=[
                Step(id="actual", run="echo test"),
            ],
            outputs={"version": "${{ steps.wrong.outputs.version }}"},
        )
        workflow = Workflow(name="CI", jobs={"build": job})

        result = validate_step_outputs(workflow)

        assert result.valid is False
        assert "wrong" in result.errors[0].message

    def test_step_reference_in_env(self):
        """Detect invalid step references in step env."""
        job = Job(
            runs_on="ubuntu-latest",
            steps=[
                Step(
                    run="echo $VERSION",
                    env={"VERSION": "${{ steps.missing.outputs.version }}"},
                ),
            ],
        )
        workflow = Workflow(name="CI", jobs={"build": job})

        result = validate_step_outputs(workflow)

        assert result.valid is False
        assert "missing" in result.errors[0].message

    def test_step_reference_in_if_condition(self):
        """Detect invalid step references in if conditions."""
        job = Job(
            runs_on="ubuntu-latest",
            steps=[
                Step(
                    if_="steps.missing.outputs.result == 'success'",
                    run="echo success",
                ),
            ],
        )
        workflow = Workflow(name="CI", jobs={"build": job})

        result = validate_step_outputs(workflow)

        assert result.valid is False
        assert "missing" in result.errors[0].message


class TestReferenceValidationResult:
    """Tests for ReferenceValidationResult dataclass."""

    def test_result_with_no_errors(self):
        """Result with no errors is valid."""
        result = ReferenceValidationResult(valid=True, errors=[])

        assert result.valid is True
        assert len(result.errors) == 0

    def test_result_with_errors(self):
        """Result with errors is invalid."""
        from wetwire_github.validation import ReferenceError

        errors = [
            ReferenceError(
                message="Undefined job 'test'",
                job_id="deploy",
                reference="test",
            )
        ]
        result = ReferenceValidationResult(valid=False, errors=errors)

        assert result.valid is False
        assert len(result.errors) == 1
        assert result.errors[0].job_id == "deploy"
