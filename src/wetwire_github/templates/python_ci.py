"""Python CI workflow template.

This template creates a CI workflow with a Python testing matrix
that tests against Python 3.11, 3.12, and 3.13.
"""

from wetwire_github.actions import checkout, setup_python
from wetwire_github.workflow import (
    Job,
    Matrix,
    MatrixContext,
    PullRequestTrigger,
    PushTrigger,
    Step,
    Strategy,
    Triggers,
    Workflow,
)


def python_ci_workflow() -> Workflow:
    """Create a Python CI workflow with testing matrix.

    Returns:
        Workflow configured for Python CI with matrix testing.
    """
    test_job = Job(
        name="Test",
        runs_on="ubuntu-latest",
        timeout_minutes=15,
        strategy=Strategy(
            matrix=Matrix(
                values={
                    "python-version": ["3.11", "3.12", "3.13"],
                }
            ),
            fail_fast=False,
        ),
        steps=[
            checkout(),
            setup_python(
                python_version=MatrixContext.get("python-version"),
                cache="pip",
            ),
            Step(
                name="Install dependencies",
                run="pip install -e .[dev]",
            ),
            Step(
                name="Run tests",
                run="pytest",
            ),
        ],
    )

    return Workflow(
        name="Python CI",
        on=Triggers(
            push=PushTrigger(branches=["main"]),
            pull_request=PullRequestTrigger(branches=["main"]),
        ),
        jobs={"test": test_job},
    )
