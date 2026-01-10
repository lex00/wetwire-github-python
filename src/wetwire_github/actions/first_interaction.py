"""Generated wrapper for actions/first-interaction."""

from wetwire_github.workflow import Step


def first_interaction(
    *,
    repo_token: str,
    issue_message: str | None = None,
    pr_message: str | None = None,
) -> Step:
    """Create a step that welcomes first-time contributors.

    Args:
        repo_token: GitHub token for authentication
        issue_message: Message to post on first issues
        pr_message: Message to post on first PRs

    Returns:
        Step configured for first-interaction action
    """
    with_dict = {
        "repo-token": repo_token,
        "issue-message": issue_message,
        "pr-message": pr_message,
    }
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="actions/first-interaction@v1",
        with_=with_dict if with_dict else None,
    )
