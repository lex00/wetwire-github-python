"""Generated wrapper for Setup Go environment."""

from wetwire_github.workflow import Step


def setup_go(
    go_version: str | None = None,
    go_version_file: str | None = None,
    check_latest: str | None = None,
    token: str | None = None,
    cache: str | None = None,
    cache_dependency_path: str | None = None,
    architecture: str | None = None,
) -> Step:
    """Setup a Go environment and add it to the PATH

    Args:
        go_version: The Go version to download (if necessary) and use. Supports semver spec and ranges. Be sure to enclose this option in single quotation marks.
        go_version_file: Path to the go.mod, go.work, .go-version, or .tool-versions file.
        check_latest: Set this option to true if you want the action to always check for the latest available version that satisfies the version spec
        token: Used to pull Go distributions from go-versions. Since there's a default, this is typically not supplied by the user. When running this action on github.com, the default value is sufficient. When running on GHES, you can pass a personal access token for github.com if you are experiencing rate limiting.
        cache: Used to specify whether caching is needed. Set to true, if you'd like to enable caching.
        cache_dependency_path: Used to specify the path to a dependency file - go.sum
        architecture: Target architecture for Go to use. Examples: x86, x64. Will use system architecture by default.

    Returns:
        Step configured to use this action
    """
    with_dict = {
        "go-version": go_version,
        "go-version-file": go_version_file,
        "check-latest": check_latest,
        "token": token,
        "cache": cache,
        "cache-dependency-path": cache_dependency_path,
        "architecture": architecture,
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="actions/setup-go@v4",
        with_=with_dict if with_dict else None,
    )
