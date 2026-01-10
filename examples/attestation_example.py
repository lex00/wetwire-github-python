"""Example: Using build provenance attestation in a workflow.

This example demonstrates how to use the attest_build_provenance action
wrapper to create signed attestations for build artifacts.
"""

from wetwire_github.actions import attest_build_provenance, checkout, upload_artifact
from wetwire_github.workflow import Job, Step, Triggers, Workflow
from wetwire_github.workflow.triggers import PushTrigger

# Example 1: Simple attestation for build artifacts
build_and_attest = Job(
    name="Build and Attest",
    runs_on="ubuntu-latest",
    permissions={
        "contents": "read",
        "id-token": "write",
        "attestations": "write",
    },
    steps=[
        checkout(),
        Step(
            name="Build artifact",
            run="make build",
        ),
        attest_build_provenance(
            subject_path="dist/*.tar.gz",
        ),
        upload_artifact(
            name="build-artifacts",
            path="dist/",
        ),
    ],
)

# Example 2: Container image attestation with registry push
container_attest = Job(
    name="Build and Attest Container",
    runs_on="ubuntu-latest",
    permissions={
        "contents": "read",
        "id-token": "write",
        "attestations": "write",
        "packages": "write",
    },
    steps=[
        checkout(),
        Step(
            name="Build container",
            run="docker build -t myapp:latest .",
        ),
        Step(
            name="Get image digest",
            id="digest",
            run='echo "digest=$(docker inspect --format=\'{{index .RepoDigests 0}}\' myapp:latest)" >> $GITHUB_OUTPUT',
        ),
        attest_build_provenance(
            subject_digest="${{ steps.digest.outputs.digest }}",
            subject_name="ghcr.io/${{ github.repository }}:latest",
            push_to_registry=True,
        ),
    ],
)

# Example 3: Multiple artifacts with checksums file
multi_artifact_attest = Job(
    name="Build Multiple Artifacts",
    runs_on="ubuntu-latest",
    permissions={
        "contents": "read",
        "id-token": "write",
        "attestations": "write",
    },
    steps=[
        checkout(),
        Step(
            name="Build artifacts",
            run="""
                make build-all
                sha256sum dist/* > checksums.txt
            """,
        ),
        attest_build_provenance(
            subject_checksums="checksums.txt",
            show_summary=True,
        ),
    ],
)

# Create the workflow
attestation_workflow = Workflow(
    name="Build Attestation Example",
    on=Triggers(
        push=PushTrigger(branches=["main"]),
    ),
    jobs={
        "simple-attest": build_and_attest,
        "container-attest": container_attest,
        "multi-attest": multi_artifact_attest,
    },
)
