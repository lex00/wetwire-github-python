"""Generated wrapper for docker/login-action."""

from wetwire_github.workflow import Step


def docker_login(
    registry: str | None = None,
    username: str | None = None,
    password: str | None = None,
    ecr: str | None = None,
    logout: bool | None = None,
) -> Step:
    """Log in to a Docker registry.

    This action logs in to a Docker registry such as Docker Hub, GitHub
    Container Registry (ghcr.io), Amazon ECR, or other registries.

    Args:
        registry: Server address of Docker registry. Defaults to Docker Hub.
        username: Username used to log against the Docker registry.
        password: Password or personal access token used to log against the
            Docker registry.
        ecr: Specifies whether the given registry is ECR (auto, true, or false).
        logout: Log out from the Docker registry at the end of a job.

    Returns:
        Step configured to use docker/login-action
    """
    with_dict = {
        "registry": registry,
        "username": username,
        "password": password,
        "ecr": ecr,
        "logout": "true" if logout else ("false" if logout is False else None),
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="docker/login-action@v3",
        with_=with_dict if with_dict else None,
    )
