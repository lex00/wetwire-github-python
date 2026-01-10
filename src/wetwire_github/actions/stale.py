"""Generated wrapper for actions/stale."""

from wetwire_github.workflow import Step


def stale(
    *,
    repo_token: str,
    stale_issue_message: str | None = None,
    stale_pr_message: str | None = None,
    days_before_stale: int | None = None,
    days_before_close: int | None = None,
    stale_issue_label: str | None = None,
    stale_pr_label: str | None = None,
    exempt_issue_labels: str | None = None,
    exempt_pr_labels: str | None = None,
) -> Step:
    """Create a step that manages stale issues and PRs.

    Args:
        repo_token: GitHub token for authentication
        stale_issue_message: Message when marking issues stale
        stale_pr_message: Message when marking PRs stale
        days_before_stale: Days of inactivity before marking stale
        days_before_close: Days after stale before closing
        stale_issue_label: Label for stale issues
        stale_pr_label: Label for stale PRs
        exempt_issue_labels: Comma-separated labels that exempt issues
        exempt_pr_labels: Comma-separated labels that exempt PRs

    Returns:
        Step configured for stale action
    """
    with_dict = {
        "repo-token": repo_token,
        "stale-issue-message": stale_issue_message,
        "stale-pr-message": stale_pr_message,
        "days-before-stale": str(days_before_stale) if days_before_stale is not None else None,
        "days-before-close": str(days_before_close) if days_before_close is not None else None,
        "stale-issue-label": stale_issue_label,
        "stale-pr-label": stale_pr_label,
        "exempt-issue-labels": exempt_issue_labels,
        "exempt-pr-labels": exempt_pr_labels,
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="actions/stale@v9",
        with_=with_dict if with_dict else None,
    )
