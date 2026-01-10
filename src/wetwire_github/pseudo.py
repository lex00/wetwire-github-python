"""GitHub context pseudo-parameters.

This module provides constants for commonly used GitHub Actions context values,
following the pattern of AWS pseudo-parameters (AWS_REGION, AWS_ACCOUNT_ID, etc.).

These constants can be used in workflow definitions instead of raw strings,
providing:
- IDE autocomplete and discovery
- Type safety through static analysis
- Consistency with wetwire patterns

Example:
    from wetwire_github.pseudo import GITHUB_REF, GITHUB_SHA

    step = Step(
        run="echo $REF",
        env={"REF": GITHUB_REF, "SHA": GITHUB_SHA},
    )
"""

__all__ = [
    # Core references
    "GITHUB_REF",
    "GITHUB_REF_NAME",
    "GITHUB_SHA",
    # Repository context
    "GITHUB_REPOSITORY",
    "GITHUB_REPOSITORY_OWNER",
    "GITHUB_ACTOR",
    # Workflow context
    "GITHUB_WORKFLOW",
    "GITHUB_RUN_ID",
    "GITHUB_RUN_NUMBER",
    "GITHUB_JOB",
    # PR context
    "GITHUB_HEAD_REF",
    "GITHUB_BASE_REF",
    # Event context
    "GITHUB_EVENT_NAME",
    "GITHUB_EVENT_PATH",
    # Environment
    "GITHUB_WORKSPACE",
    "GITHUB_ACTION",
    "GITHUB_ACTION_PATH",
]

# Core references
GITHUB_REF = "${{ github.ref }}"
"""The fully-formed ref of the branch or tag that triggered the workflow run."""

GITHUB_REF_NAME = "${{ github.ref_name }}"
"""The short ref name of the branch or tag that triggered the workflow run."""

GITHUB_SHA = "${{ github.sha }}"
"""The commit SHA that triggered the workflow."""

# Repository context
GITHUB_REPOSITORY = "${{ github.repository }}"
"""The owner and repository name. For example, octocat/Hello-World."""

GITHUB_REPOSITORY_OWNER = "${{ github.repository_owner }}"
"""The repository owner's name. For example, octocat."""

GITHUB_ACTOR = "${{ github.actor }}"
"""The name of the person or app that initiated the workflow."""

# Workflow context
GITHUB_WORKFLOW = "${{ github.workflow }}"
"""The name of the workflow."""

GITHUB_RUN_ID = "${{ github.run_id }}"
"""A unique number for each workflow run within a repository."""

GITHUB_RUN_NUMBER = "${{ github.run_number }}"
"""A unique number for each run of a particular workflow in a repository."""

GITHUB_JOB = "${{ github.job }}"
"""The job_id of the current job."""

# Pull request context
GITHUB_HEAD_REF = "${{ github.head_ref }}"
"""The head ref or source branch of the pull request in a workflow run."""

GITHUB_BASE_REF = "${{ github.base_ref }}"
"""The base ref or target branch of the pull request in a workflow run."""

# Event context
GITHUB_EVENT_NAME = "${{ github.event_name }}"
"""The name of the event that triggered the workflow."""

GITHUB_EVENT_PATH = "${{ github.event_path }}"
"""The path to the file on the runner that contains the full event webhook payload."""

# Environment paths
GITHUB_WORKSPACE = "${{ github.workspace }}"
"""The default working directory on the runner for steps."""

GITHUB_ACTION = "${{ github.action }}"
"""The name of the action currently running, or the id of a step."""

GITHUB_ACTION_PATH = "${{ github.action_path }}"
"""The path where an action is located."""
