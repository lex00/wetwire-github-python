"""Generated wrapper for Setup Node.js environment."""

from wetwire_github.workflow import Step


def setup_node(
    node_version: str | None = None,
    node_version_file: str | None = None,
    architecture: str | None = None,
    check_latest: str | None = None,
    registry_url: str | None = None,
    scope: str | None = None,
    token: str | None = None,
    cache: str | None = None,
    package_manager_cache: str | None = None,
    cache_dependency_path: str | None = None,
    mirror: str | None = None,
    mirror_token: str | None = None,
) -> Step:
    """Setup a Node.js environment by adding problem matchers and optionally downloading and adding it to the PATH.

    Args:
        node_version: Version Spec of the version to use. Examples: 12.x, 10.15.1, >=10.15.0.
        node_version_file: File containing the version Spec of the version to use.  Examples: package.json, .nvmrc, .node-version, .tool-versions.
        architecture: Target architecture for Node to use. Examples: x86, x64. Will use system architecture by default.
        check_latest: Set this option if you want the action to check for the latest available version that satisfies the version spec.
        registry_url: Optional registry to set up for auth. Will set the registry in a project level .npmrc and .yarnrc file, and set up auth to read in from env.NODE_AUTH_TOKEN.
        scope: Optional scope for authenticating against scoped registries. Will fall back to the repository owner when using the GitHub Packages registry (https://npm.pkg.github.com/).
        token: Used to pull node distributions from node-versions. Since there's a default, this is typically not supplied by the user. When running this action on github.com, the default value is sufficient. When running on GHES, you can pass a personal access token for github.com if you are experiencing rate limiting.
        cache: Used to specify a package manager for caching in the default directory. Supported values: npm, yarn, pnpm.
        package_manager_cache: Set to false to disable automatic caching. By default, caching is enabled when either devEngines.packageManager or the top-level packageManager field in package.json specifies npm as the package manager.
        cache_dependency_path: Used to specify the path to a dependency file: package-lock.json, yarn.lock, etc. Supports wildcards or a list of file names for caching multiple dependencies.
        mirror: Used to specify an alternative mirror to downlooad Node.js binaries from
        mirror_token: The token used as Authorization header when fetching from the mirror

    Returns:
        Step configured to use this action
    """
    with_dict = {
        "node-version": node_version,
        "node-version-file": node_version_file,
        "architecture": architecture,
        "check-latest": check_latest,
        "registry-url": registry_url,
        "scope": scope,
        "token": token,
        "cache": cache,
        "package-manager-cache": package_manager_cache,
        "cache-dependency-path": cache_dependency_path,
        "mirror": mirror,
        "mirror-token": mirror_token,
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="actions/setup-node@v4",
        with_=with_dict if with_dict else None,
    )
