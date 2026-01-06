"""Generated wrapper for Setup Python."""

from wetwire_github.workflow import Step


def setup_python(
    python_version: str | None = None,
    python_version_file: str | None = None,
    cache: str | None = None,
    architecture: str | None = None,
    check_latest: str | None = None,
    token: str | None = None,
    cache_dependency_path: str | None = None,
    update_environment: str | None = None,
    allow_prereleases: str | None = None,
    freethreaded: str | None = None,
    pip_version: str | None = None,
    pip_install: str | None = None,
) -> Step:
    """Set up a specific version of Python and add the command-line tools to the PATH.

    Args:
        python_version: Version range or exact version of Python or PyPy to use, using SemVer's version range syntax. Reads from .python-version if unset.
        python_version_file: File containing the Python version to use. Example: .python-version
        cache: Used to specify a package manager for caching in the default directory. Supported values: pip, pipenv, poetry.
        architecture: The target architecture (x86, x64, arm64) of the Python or PyPy interpreter.
        check_latest: Set this option if you want the action to check for the latest available version that satisfies the version spec.
        token: The token used to authenticate when fetching Python distributions from https://github.com/actions/python-versions. When running this action on github.com, the default value is sufficient. When running on GHES, you can pass a personal access token for github.com if you are experiencing rate limiting.
        cache_dependency_path: Used to specify the path to dependency files. Supports wildcards or a list of file names for caching multiple dependencies.
        update_environment: Set this option if you want the action to update environment variables.
        allow_prereleases: When 'true', a version range passed to 'python-version' input will match prerelease versions if no GA versions are found. Only 'x.y' version range is supported for CPython.
        freethreaded: When 'true', use the freethreaded version of Python.
        pip_version: Used to specify the version of pip to install with the Python. Supported format: major[.minor][.patch].
        pip_install: Used to specify the packages to install with pip after setting up Python. Can be a requirements file or package names.

    Returns:
        Step configured to use this action
    """
    with_dict = {
        "python-version": python_version,
        "python-version-file": python_version_file,
        "cache": cache,
        "architecture": architecture,
        "check-latest": check_latest,
        "token": token,
        "cache-dependency-path": cache_dependency_path,
        "update-environment": update_environment,
        "allow-prereleases": allow_prereleases,
        "freethreaded": freethreaded,
        "pip-version": pip_version,
        "pip-install": pip_install,
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="actions/setup-python@v4",
        with_=with_dict if with_dict else None,
    )
