"""Generated wrapper for docker/setup-buildx-action."""

from wetwire_github.workflow import Step


def setup_buildx(
    version: str | None = None,
    driver: str | None = None,
    driver_opts: str | None = None,
    buildkitd_flags: str | None = None,
    install: bool | None = None,
    use: bool | None = None,
    platforms: str | None = None,
    config: str | None = None,
    config_inline: str | None = None,
    append: str | None = None,
    cleanup: bool | None = None,
) -> Step:
    """Set up Docker Buildx.

    This action sets up Docker Buildx for building multi-platform images
    and using advanced build features.

    Args:
        version: Buildx version (e.g., latest, v0.10.0).
        driver: Build driver to use (docker, docker-container, kubernetes, remote).
        driver_opts: Driver-specific options (newline-separated).
        buildkitd_flags: BuildKit daemon flags.
        install: Install Buildx as default builder.
        use: Set up builder to be the default.
        platforms: Fixed platforms for current node (comma-separated).
        config: BuildKit config file path.
        config_inline: Inline BuildKit config.
        append: Append additional nodes to the builder.
        cleanup: Cleanup builder when job completes.

    Returns:
        Step configured to use docker/setup-buildx-action
    """
    with_dict = {
        "version": version,
        "driver": driver,
        "driver-opts": driver_opts,
        "buildkitd-flags": buildkitd_flags,
        "install": "true" if install else ("false" if install is False else None),
        "use": "true" if use else ("false" if use is False else None),
        "platforms": platforms,
        "config": config,
        "config-inline": config_inline,
        "append": append,
        "cleanup": "true" if cleanup else ("false" if cleanup is False else None),
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="docker/setup-buildx-action@v3",
        with_=with_dict if with_dict else None,
    )
