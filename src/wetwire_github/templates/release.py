"""Release workflow template.

This template creates a release workflow that triggers on
semantic version tags and publishes releases.
"""

from wetwire_github.actions import checkout, gh_release
from wetwire_github.workflow import (
    Job,
    Permissions,
    PushTrigger,
    Step,
    Triggers,
    Workflow,
)


def release_workflow() -> Workflow:
    """Create a release workflow with semantic versioning.

    Returns:
        Workflow configured for release publishing on tag push.
    """
    release_job = Job(
        name="Release",
        runs_on="ubuntu-latest",
        timeout_minutes=15,
        permissions=Permissions(
            contents="write",
        ),
        steps=[
            checkout(fetch_depth="0"),
            Step(
                name="Generate changelog",
                id="changelog",
                run="echo 'changelog=Auto-generated release' >> $GITHUB_OUTPUT",
            ),
            gh_release(
                generate_release_notes=True,
            ),
        ],
    )

    return Workflow(
        name="Release",
        on=Triggers(
            push=PushTrigger(tags=["v*.*.*", "v*"]),
        ),
        permissions=Permissions(
            contents="write",
        ),
        jobs={"release": release_job},
    )
