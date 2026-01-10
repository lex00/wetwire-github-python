"""Generated wrapper for peter-evans/create-pull-request."""

from wetwire_github.workflow import Step


def create_pull_request(
    token: str | None = None,
    path: str | None = None,
    add_paths: str | None = None,
    commit_message: str | None = None,
    committer: str | None = None,
    author: str | None = None,
    signoff: bool | None = None,
    branch: str | None = None,
    delete_branch: bool | None = None,
    branch_suffix: str | None = None,
    base: str | None = None,
    push_to_fork: str | None = None,
    title: str | None = None,
    body: str | None = None,
    body_path: str | None = None,
    labels: str | None = None,
    assignees: str | None = None,
    reviewers: str | None = None,
    team_reviewers: str | None = None,
    milestone: str | None = None,
    draft: bool | None = None,
) -> Step:
    """Create a pull request for changes made in the workflow.

    This action creates a pull request with changes made during
    the workflow run.

    Args:
        token: GitHub token for authentication.
        path: Relative path under $GITHUB_WORKSPACE to the repository.
        add_paths: A comma or newline-separated list of file paths to add.
        commit_message: The message to use when committing changes.
        committer: The committer name and email.
        author: The author name and email.
        signoff: Add Signed-off-by line at the end of the commit log message.
        branch: The pull request branch name.
        delete_branch: Delete the branch after merge.
        branch_suffix: The branch suffix type (random, timestamp, short-commit-hash).
        base: The base branch for the pull request.
        push_to_fork: Push branch to a fork (owner/repo).
        title: The title of the pull request.
        body: The body of the pull request.
        body_path: Path to a file containing the pull request body.
        labels: A comma or newline-separated list of labels.
        assignees: A comma or newline-separated list of assignees.
        reviewers: A comma or newline-separated list of reviewers.
        team_reviewers: A comma or newline-separated list of team reviewers.
        milestone: The milestone number to associate with the PR.
        draft: Create a draft pull request.

    Returns:
        Step configured to use peter-evans/create-pull-request
    """
    with_dict = {
        "token": token,
        "path": path,
        "add-paths": add_paths,
        "commit-message": commit_message,
        "committer": committer,
        "author": author,
        "signoff": "true" if signoff else ("false" if signoff is False else None),
        "branch": branch,
        "delete-branch": "true" if delete_branch else ("false" if delete_branch is False else None),
        "branch-suffix": branch_suffix,
        "base": base,
        "push-to-fork": push_to_fork,
        "title": title,
        "body": body,
        "body-path": body_path,
        "labels": labels,
        "assignees": assignees,
        "reviewers": reviewers,
        "team-reviewers": team_reviewers,
        "milestone": milestone,
        "draft": "true" if draft else ("false" if draft is False else None),
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="peter-evans/create-pull-request@v6",
        with_=with_dict if with_dict else None,
    )
