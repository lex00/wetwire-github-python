"""Generated wrapper for docker/build-push-action."""

from wetwire_github.workflow import Step


def docker_build_push(
    context: str | None = None,
    file: str | None = None,
    push: bool | None = None,
    tags: str | None = None,
    labels: str | None = None,
    platforms: str | None = None,
    build_args: str | None = None,
    target: str | None = None,
    cache_from: str | None = None,
    cache_to: str | None = None,
    load: bool | None = None,
    no_cache: bool | None = None,
    pull: bool | None = None,
    secrets: str | None = None,
    ssh: str | None = None,
    outputs: str | None = None,
    provenance: str | None = None,
    sbom: str | None = None,
) -> Step:
    """Build and push Docker images with Buildx.

    This action builds and pushes Docker images using BuildKit. It supports
    multi-platform builds, caching, and various registry outputs.

    Args:
        context: Build's context is the set of files located in the specified PATH.
        file: Path to the Dockerfile.
        push: Push is a shorthand for --output=type=registry.
        tags: List of tags (newline or comma separated).
        labels: List of metadata for an image (newline separated).
        platforms: List of target platforms for build (comma separated).
        build_args: List of build-time variables (newline separated).
        target: Sets the target stage to build.
        cache_from: External cache sources (e.g., type=gha).
        cache_to: Cache export destinations (e.g., type=gha,mode=max).
        load: Load is a shorthand for --output=type=docker.
        no_cache: Do not use cache when building the image.
        pull: Always attempt to pull a newer version of the image.
        secrets: List of secrets to expose to the build (newline separated).
        ssh: List of SSH agent socket or keys to expose to the build.
        outputs: List of output destinations.
        provenance: Generate provenance attestation for the build.
        sbom: Generate SBOM attestation for the build.

    Returns:
        Step configured to use docker/build-push-action
    """
    with_dict = {
        "context": context,
        "file": file,
        "push": "true" if push else ("false" if push is False else None),
        "tags": tags,
        "labels": labels,
        "platforms": platforms,
        "build-args": build_args,
        "target": target,
        "cache-from": cache_from,
        "cache-to": cache_to,
        "load": "true" if load else ("false" if load is False else None),
        "no-cache": "true" if no_cache else ("false" if no_cache is False else None),
        "pull": "true" if pull else ("false" if pull is False else None),
        "secrets": secrets,
        "ssh": ssh,
        "outputs": outputs,
        "provenance": provenance,
        "sbom": sbom,
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="docker/build-push-action@v6",
        with_=with_dict if with_dict else None,
    )
