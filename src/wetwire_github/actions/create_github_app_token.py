"""Generated wrapper for Create GitHub App Token."""

from wetwire_github.workflow import Step


def create_github_app_token(
    app_id: str,
    private_key: str,
    owner: str | None = None,
    repositories: list[str] | str | None = None,
    skip_token_revoke: bool | None = None,
) -> Step:
    """Create a GitHub App installation access token.

    Args:
        app_id: The GitHub App ID.
        private_key: The GitHub App private key.
        owner: The owner of the GitHub App installation (organization or user).
        repositories: Repositories to grant access to. Can be a comma-separated
            string or a list of repository names.
        skip_token_revoke: Whether to skip token revocation before creating a
            new token.

    Returns:
        Step configured to use this action
    """
    # Convert boolean values to string
    skip_token_revoke_str = None
    if skip_token_revoke is not None:
        skip_token_revoke_str = "true" if skip_token_revoke else "false"

    # Convert list to comma-separated string
    repositories_str = None
    if repositories is not None:
        if isinstance(repositories, list):
            repositories_str = ",".join(repositories)
        else:
            repositories_str = repositories

    with_dict = {
        "app-id": app_id,
        "private-key": private_key,
        "owner": owner,
        "repositories": repositories_str,
        "skip-token-revoke": skip_token_revoke_str,
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="actions/create-github-app-token@v1",
        with_=with_dict if with_dict else None,
    )
