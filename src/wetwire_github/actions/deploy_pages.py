"""Generated wrapper for Deploy to GitHub Pages."""

from wetwire_github.workflow import Step


def deploy_pages(
    token: str | None = None,
    timeout: str | None = None,
    error_count: str | None = None,
    reporting_interval: str | None = None,
    artifact_name: str | None = None,
    preview: str | None = None,
) -> Step:
    """Deploy an artifact to GitHub Pages.

    Args:
        token: GitHub token
        timeout: Time in milliseconds before deployment times out. Default is 600000 (10 minutes).
        error_count: Maximum status report errors allowed before cancellation. Default is 10.
        reporting_interval: Time in milliseconds between deployment status reports. Default is 5000 (5 seconds).
        artifact_name: Name of the artifact to deploy. Default is 'github-pages'.
        preview: Deploys a pull request as a GitHub Pages preview site. Default is false.

    Returns:
        Step configured to use this action
    """
    with_dict = {
        "token": token,
        "timeout": timeout,
        "error_count": error_count,
        "reporting_interval": reporting_interval,
        "artifact_name": artifact_name,
        "preview": preview,
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="actions/deploy-pages@v4",
        with_=with_dict if with_dict else None,
    )
