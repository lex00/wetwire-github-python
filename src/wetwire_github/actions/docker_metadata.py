"""Generated wrapper for docker/metadata-action."""

from wetwire_github.workflow import Step


def docker_metadata(
    images: str | None = None,
    tags: str | None = None,
    flavor: str | None = None,
    labels: str | None = None,
    sep_tags: str | None = None,
    sep_labels: str | None = None,
    bake_target: str | None = None,
    github_token: str | None = None,
) -> Step:
    """Extract metadata for Docker images.

    This action extracts metadata from Git reference and GitHub events
    for use in Docker build and push actions.

    Args:
        images: List of Docker images to use as base name for tags (newline-separated).
        tags: List of tags as key-value pairs (newline-separated).
            Examples: type=sha, type=ref,event=branch
        flavor: Flavor to apply globally (newline-separated).
        labels: List of custom labels (newline-separated).
        sep_tags: Separator to use for tags output.
        sep_labels: Separator to use for labels output.
        bake_target: Bake target name.
        github_token: GitHub token for event payload.

    Returns:
        Step configured to use docker/metadata-action
    """
    with_dict = {
        "images": images,
        "tags": tags,
        "flavor": flavor,
        "labels": labels,
        "sep-tags": sep_tags,
        "sep-labels": sep_labels,
        "bake-target": bake_target,
        "github-token": github_token,
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="docker/metadata-action@v5",
        with_=with_dict if with_dict else None,
    )
