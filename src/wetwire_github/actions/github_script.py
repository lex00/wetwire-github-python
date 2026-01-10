"""Generated wrapper for actions/github-script."""

from wetwire_github.workflow import Step


def github_script(
    script: str | None = None,
    github_token: str | None = None,
    debug: str | None = None,
    user_agent: str | None = None,
    previews: str | None = None,
    result_encoding: str | None = None,
    retries: str | None = None,
    retry_exempt_status_codes: str | None = None,
) -> Step:
    """Run JavaScript using the GitHub API and workflow contexts.

    This action makes it easy to quickly write a script in your workflow that
    uses the GitHub API and the workflow run context.

    Args:
        script: The script to run. Required.
        github_token: The GitHub token used to create an authenticated client.
            Defaults to GITHUB_TOKEN.
        debug: Whether to print debug output.
        user_agent: The user agent to use for API requests.
        previews: A comma-separated list of API previews to accept.
        result_encoding: How the result will be encoded. Can be 'string' or 'json'.
            Defaults to 'json'.
        retries: The number of times to retry a request.
        retry_exempt_status_codes: A comma-separated list of status codes that
            will NOT be retried.

    Returns:
        Step configured to use actions/github-script
    """
    with_dict = {
        "script": script,
        "github-token": github_token,
        "debug": debug,
        "user-agent": user_agent,
        "previews": previews,
        "result-encoding": result_encoding,
        "retries": retries,
        "retry-exempt-status-codes": retry_exempt_status_codes,
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="actions/github-script@v7",
        with_=with_dict if with_dict else None,
    )
