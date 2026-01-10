"""Generated wrapper for codecov/codecov-action."""

from wetwire_github.workflow import Step


def codecov(
    token: str | None = None,
    files: str | None = None,
    directory: str | None = None,
    flags: str | None = None,
    name: str | None = None,
    fail_ci_if_error: bool | None = None,
    verbose: bool | None = None,
    env_vars: str | None = None,
    slug: str | None = None,
    override_branch: str | None = None,
    override_build: str | None = None,
    override_commit: str | None = None,
    override_pr: str | None = None,
    override_tag: str | None = None,
) -> Step:
    """Upload coverage reports to Codecov.

    This action uploads code coverage reports to Codecov for
    visualization and analysis.

    Args:
        token: Codecov upload token.
        files: Comma-separated list of coverage report files.
        directory: Directory to search for coverage reports.
        flags: Comma-separated list of flag names.
        name: Custom name for the upload.
        fail_ci_if_error: Fail CI if Codecov upload fails.
        verbose: Enable verbose logging.
        env_vars: Comma-separated list of environment variables to include.
        slug: Owner/repo slug (for forks).
        override_branch: Specify the branch name.
        override_build: Specify the build number.
        override_commit: Specify the commit SHA.
        override_pr: Specify the pull request number.
        override_tag: Specify the git tag.

    Returns:
        Step configured to use codecov/codecov-action
    """
    with_dict = {
        "token": token,
        "files": files,
        "directory": directory,
        "flags": flags,
        "name": name,
        "fail_ci_if_error": "true" if fail_ci_if_error else ("false" if fail_ci_if_error is False else None),
        "verbose": "true" if verbose else ("false" if verbose is False else None),
        "env_vars": env_vars,
        "slug": slug,
        "override_branch": override_branch,
        "override_build": override_build,
        "override_commit": override_commit,
        "override_pr": override_pr,
        "override_tag": override_tag,
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="codecov/codecov-action@v4",
        with_=with_dict if with_dict else None,
    )
