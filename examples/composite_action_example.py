"""Example: Creating a composite GitHub Action with wetwire-github.

This example demonstrates how to define a composite action in Python
that sets up a Python project with dependencies and caching.
"""

from wetwire_github.composite import (
    ActionInput,
    ActionOutput,
    CompositeAction,
    CompositeRuns,
)
from wetwire_github.workflow import Step
from wetwire_github.serialize import to_yaml

# Define a composite action for setting up a Python project
setup_python_action = CompositeAction(
    name="Setup Python Project",
    description="Sets up a Python project with dependencies and caching",
    inputs={
        "python-version": ActionInput(
            description="Python version to use",
            required=True,
        ),
        "cache-dependency-path": ActionInput(
            description="Path to dependency file for caching",
            default="requirements.txt",
        ),
    },
    outputs={
        "python-path": ActionOutput(
            description="Path to Python executable",
            value="${{ steps.setup-python.outputs.python-path }}",
        ),
    },
    runs=CompositeRuns(
        steps=[
            Step(
                id="setup-python",
                uses="actions/setup-python@v5",
                with_={
                    "python-version": "${{ inputs.python-version }}",
                },
            ),
            Step(
                name="Cache pip dependencies",
                uses="actions/cache@v4",
                with_={
                    "path": "~/.cache/pip",
                    "key": "${{ runner.os }}-pip-${{ hashFiles(inputs.cache-dependency-path) }}",
                },
            ),
            Step(
                name="Install dependencies",
                run="pip install -r ${{ inputs.cache-dependency-path }}",
                shell="bash",
            ),
        ]
    ),
)

# Print the generated action.yml
if __name__ == "__main__":
    print(to_yaml(setup_python_action))
