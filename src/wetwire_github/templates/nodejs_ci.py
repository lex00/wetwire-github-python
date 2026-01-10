"""Node.js CI workflow template.

This template creates a CI workflow for Node.js projects
using npm for package management.
"""

from wetwire_github.actions import checkout, setup_node
from wetwire_github.workflow import (
    Job,
    PullRequestTrigger,
    PushTrigger,
    Step,
    Triggers,
    Workflow,
)


def nodejs_ci_workflow() -> Workflow:
    """Create a Node.js CI workflow.

    Returns:
        Workflow configured for Node.js CI with npm.
    """
    build_job = Job(
        name="Build",
        runs_on="ubuntu-latest",
        timeout_minutes=15,
        steps=[
            checkout(),
            setup_node(
                node_version="20",
                cache="npm",
            ),
            Step(
                name="Install dependencies",
                run="npm ci",
            ),
            Step(
                name="Run linter",
                run="npm run lint --if-present",
            ),
            Step(
                name="Run tests",
                run="npm test",
            ),
            Step(
                name="Build",
                run="npm run build --if-present",
            ),
        ],
    )

    return Workflow(
        name="Node.js CI",
        on=Triggers(
            push=PushTrigger(branches=["main"]),
            pull_request=PullRequestTrigger(branches=["main"]),
        ),
        jobs={"build": build_job},
    )
