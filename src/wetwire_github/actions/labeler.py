"""Generated wrapper for Labeler."""

from wetwire_github.workflow import Step


def labeler(
    repo_token: str | None = None,
    configuration_path: str | None = None,
    sync_labels: bool | None = None,
    dot: bool | None = None,
) -> Step:
    """Automatically label pull requests based on file changes.

    The labeler action automatically applies labels to pull requests based on
    the files that have changed. This helps with organizing and categorizing
    PRs automatically based on which parts of the codebase are affected.

    Args:
        repo_token: GitHub token for authentication. Defaults to the workflow's
            GITHUB_TOKEN if not specified.
        configuration_path: Path to the labeler configuration file. Defaults to
            .github/labeler.yml if not specified.
        sync_labels: Whether to remove labels that no longer match the PR's file
            changes. When true, labels will be removed if they no longer apply.
            Defaults to false.
        dot: Whether to include dotfiles in pattern matching. When true, dotfiles
            (files starting with .) will be matched by glob patterns. Defaults to
            false.

    Returns:
        Step configured to use this action

    Example:
        Basic usage with defaults:
            labeler()

        Custom configuration path:
            labeler(configuration_path=".github/custom-labeler.yml")

        Enable label synchronization:
            labeler(sync_labels=True)

        All options:
            labeler(
                repo_token="${{ secrets.GITHUB_TOKEN }}",
                configuration_path=".github/labeler.yml",
                sync_labels=True,
                dot=True,
            )
    """
    with_dict = {
        "repo-token": repo_token,
        "configuration-path": configuration_path,
        "sync-labels": "true" if sync_labels is True else ("false" if sync_labels is False else None),
        "dot": "true" if dot is True else ("false" if dot is False else None),
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="actions/labeler@v5",
        with_=with_dict if with_dict else None,
    )
