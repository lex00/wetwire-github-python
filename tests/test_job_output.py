"""Tests for JobOutput type."""

import pytest
from wetwire_github.workflow import Job, JobOutput
from wetwire_github.serialize import to_dict


def test_basic_job_output_creation():
    """Test creating a basic JobOutput."""
    output = JobOutput(value="${{ steps.build.outputs.version }}")
    assert output.value == "${{ steps.build.outputs.version }}"
    assert output.description is None


def test_job_output_with_description():
    """Test JobOutput with description."""
    output = JobOutput(
        value="${{ steps.build.outputs.version }}",
        description="The built version number"
    )
    assert output.value == "${{ steps.build.outputs.version }}"
    assert output.description == "The built version number"


def test_job_with_job_output_in_outputs_dict():
    """Test Job with JobOutput objects in outputs dict."""
    job = Job(
        runs_on="ubuntu-latest",
        steps=[],
        outputs={
            "version": JobOutput(
                value="${{ steps.build.outputs.version }}",
                description="The built version number"
            ),
            "artifact_id": JobOutput(
                value="${{ steps.build.outputs.artifact_id }}",
                description="The artifact identifier"
            )
        }
    )

    assert "version" in job.outputs
    assert "artifact_id" in job.outputs
    assert isinstance(job.outputs["version"], JobOutput)
    assert isinstance(job.outputs["artifact_id"], JobOutput)


def test_job_with_mixed_outputs():
    """Test Job with mixed JobOutput and raw strings in outputs."""
    job = Job(
        runs_on="ubuntu-latest",
        steps=[],
        outputs={
            "version": JobOutput(
                value="${{ steps.build.outputs.version }}",
                description="The built version number"
            ),
            "status": "${{ steps.build.outputs.status }}"
        }
    )

    assert isinstance(job.outputs["version"], JobOutput)
    assert isinstance(job.outputs["status"], str)


def test_job_output_serialization_to_yaml():
    """Test that JobOutput serializes correctly to YAML (only value, not description)."""
    job = Job(
        runs_on="ubuntu-latest",
        steps=[],
        outputs={
            "version": JobOutput(
                value="${{ steps.build.outputs.version }}",
                description="The built version number"
            ),
            "status": "${{ steps.build.outputs.status }}"
        }
    )

    job_dict = to_dict(job)

    # Both should serialize to just the string value
    assert job_dict["outputs"]["version"] == "${{ steps.build.outputs.version }}"
    assert job_dict["outputs"]["status"] == "${{ steps.build.outputs.status }}"

    # Description should not appear in serialized output
    assert "description" not in str(job_dict)


def test_empty_outputs_handling():
    """Test that empty outputs dict is handled correctly."""
    job = Job(
        runs_on="ubuntu-latest",
        steps=[],
        outputs={}
    )

    job_dict = to_dict(job)

    # Empty outputs should not appear in serialized output
    assert "outputs" not in job_dict


def test_none_outputs_handling():
    """Test that None outputs is handled correctly."""
    job = Job(
        runs_on="ubuntu-latest",
        steps=[]
    )

    job_dict = to_dict(job)

    # None outputs should not appear in serialized output
    assert "outputs" not in job_dict
