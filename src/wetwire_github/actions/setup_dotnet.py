"""Generated wrapper for actions/setup-dotnet."""

from wetwire_github.workflow import Step


def setup_dotnet(
    dotnet_version: str | None = None,
    dotnet_quality: str | None = None,
    global_json_file: str | None = None,
    source_url: str | None = None,
    owner: str | None = None,
    config_file: str | None = None,
    cache: bool | None = None,
    cache_dependency_path: str | None = None,
) -> Step:
    """Set up a .NET SDK environment.

    This action sets up a .NET CLI environment for use in actions by adding
    dotnet to PATH and optionally authenticating with package registries.

    Args:
        dotnet_version: SDK version to use. Examples: 6.0.x, 7.0.x, 8.0.x.
            Supports semver syntax. Newline-separate multiple versions.
        dotnet_quality: Rollforward policy for the SDK version (daily, preview,
            ga, validated).
        global_json_file: Path to global.json file for version specification.
        source_url: URL for authenticated package source.
        owner: Owner of the package source (for GitHub Packages).
        config_file: Path to NuGet.config file.
        cache: Whether to cache packages. Set to true to enable.
        cache_dependency_path: Path to dependency file for cache key.

    Returns:
        Step configured to use actions/setup-dotnet
    """
    with_dict = {
        "dotnet-version": dotnet_version,
        "dotnet-quality": dotnet_quality,
        "global-json-file": global_json_file,
        "source-url": source_url,
        "owner": owner,
        "config-file": config_file,
        "cache": "true" if cache else ("false" if cache is False else None),
        "cache-dependency-path": cache_dependency_path,
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="actions/setup-dotnet@v4",
        with_=with_dict if with_dict else None,
    )
