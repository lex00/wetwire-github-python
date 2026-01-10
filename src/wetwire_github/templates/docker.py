"""Docker workflow template.

This template creates a Docker build and push workflow
using Docker Buildx for multi-platform builds.
"""

from wetwire_github.actions import (
    checkout,
    docker_build_push,
    docker_login,
    setup_buildx,
)
from wetwire_github.workflow import (
    Job,
    Permissions,
    PullRequestTrigger,
    PushTrigger,
    Secrets,
    Step,
    Triggers,
    Workflow,
)


def docker_workflow() -> Workflow:
    """Create a Docker build and push workflow.

    Returns:
        Workflow configured for Docker image builds.
    """
    build_job = Job(
        name="Build and Push",
        runs_on="ubuntu-latest",
        timeout_minutes=30,
        permissions=Permissions(
            contents="read",
            packages="write",
        ),
        steps=[
            checkout(),
            setup_buildx(),
            docker_login(
                registry="ghcr.io",
                username="${{ github.actor }}",
                password=Secrets.get("GITHUB_TOKEN"),
            ),
            Step(
                name="Extract metadata",
                id="meta",
                uses="docker/metadata-action@v5",
                with_={
                    "images": "ghcr.io/${{ github.repository }}",
                    "tags": (
                        "type=ref,event=branch\n"
                        "type=ref,event=pr\n"
                        "type=semver,pattern={{version}}\n"
                        "type=semver,pattern={{major}}.{{minor}}"
                    ),
                },
            ),
            docker_build_push(
                context=".",
                push=True,
                tags="${{ steps.meta.outputs.tags }}",
                labels="${{ steps.meta.outputs.labels }}",
                cache_from="type=gha",
                cache_to="type=gha,mode=max",
            ),
        ],
    )

    return Workflow(
        name="Docker",
        on=Triggers(
            push=PushTrigger(branches=["main"]),
            pull_request=PullRequestTrigger(branches=["main"]),
        ),
        jobs={"build": build_job},
    )
