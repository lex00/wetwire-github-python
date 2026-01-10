"""Advanced caching strategies for GitHub Actions workflows."""

from dataclasses import dataclass

from wetwire_github.workflow import Step
from wetwire_github.workflow.expressions import Expression


def hash_files(*files: str | list[str]) -> Expression:
    """Generate a hashFiles() expression for cache key generation.

    Args:
        *files: File paths or glob patterns to hash. Can be individual strings
               or a single list of strings.

    Returns:
        Expression that evaluates to ${{ hashFiles(...) }}

    Examples:
        >>> hash_files("requirements.txt")
        Expression: ${{ hashFiles('requirements.txt') }}

        >>> hash_files("package.json", "package-lock.json")
        Expression: ${{ hashFiles('package.json', 'package-lock.json') }}

        >>> hash_files(["*.json", "*.yaml"])
        Expression: ${{ hashFiles('*.json', '*.yaml') }}
    """
    # Handle case where a list is passed as the first argument
    if len(files) == 1 and isinstance(files[0], list):
        file_list = files[0]
    else:
        file_list = list(files)

    # Quote each file path and join with commas
    quoted_files = ", ".join(f"'{file}'" for file in file_list)
    return Expression(f"hashFiles({quoted_files})")


@dataclass
class CacheStrategy:
    """Defines a caching strategy with path, key, and restore keys.

    Attributes:
        path: The file path or directory to cache
        key: The cache key (can include expressions)
        restore_keys: Optional list of fallback key prefixes

    Examples:
        >>> strategy = CacheStrategy(
        ...     path="~/.cache/pip",
        ...     key="pip-${{ runner.os }}-${{ hashFiles('requirements.txt') }}",
        ...     restore_keys=["pip-${{ runner.os }}-"],
        ... )
    """

    path: str
    key: str
    restore_keys: list[str] | None = None

    def to_step(self, name: str | None = None) -> Step:
        """Convert this cache strategy to a Step using actions/cache@v4.

        Args:
            name: Optional step name

        Returns:
            Step configured with this cache strategy

        Examples:
            >>> strategy = CacheStrategy(path="~/.cache/pip", key="pip-cache")
            >>> step = strategy.to_step(name="Cache pip dependencies")
        """
        with_dict = {
            "path": self.path,
            "key": self.key,
        }

        # Add restore-keys if present (join list with newlines per cache spec)
        if self.restore_keys:
            with_dict["restore-keys"] = "\n".join(self.restore_keys)

        return Step(
            name=name,
            uses="actions/cache@v4",
            with_=with_dict,
        )


def cache_pip(
    python_version: str | None = None,
    hash_files: list[str] | None = None,
) -> CacheStrategy:
    """Create a smart pip caching strategy.

    Args:
        python_version: Python version to include in cache key
        hash_files: Files to hash for cache key (e.g., requirements.txt, setup.py)

    Returns:
        CacheStrategy configured for pip caching

    Examples:
        >>> cache_pip(python_version="3.11", hash_files=["requirements.txt"])
        CacheStrategy(
            path="~/.cache/pip",
            key="pip-3.11-${{ runner.os }}-${{ hashFiles('requirements.txt') }}",
            restore_keys=["pip-3.11-${{ runner.os }}-"],
        )
    """
    # Build cache key components
    key_parts = ["pip"]

    if python_version:
        key_parts.append(python_version)

    key_parts.append("${{ runner.os }}")

    # Add file hashing if specified
    if hash_files:
        hash_expr = hash_files_helper(*hash_files)
        key_parts.append(str(hash_expr))

    cache_key = "-".join(key_parts)

    # Build restore keys (progressively more general)
    restore_keys = []
    if python_version:
        restore_keys.append(f"pip-{python_version}-${{{{ runner.os }}}}-")
        restore_keys.append(f"pip-{python_version}-")
    restore_keys.append("pip-")

    return CacheStrategy(
        path="~/.cache/pip",
        key=cache_key,
        restore_keys=restore_keys,
    )


def cache_npm(
    node_version: str | None = None,
    hash_files: list[str] | None = None,
) -> CacheStrategy:
    """Create a smart npm caching strategy.

    Args:
        node_version: Node.js version to include in cache key
        hash_files: Files to hash for cache key (defaults to package-lock.json)

    Returns:
        CacheStrategy configured for npm caching

    Examples:
        >>> cache_npm(node_version="18")
        CacheStrategy(
            path="~/.npm",
            key="npm-18-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}",
            restore_keys=["npm-18-${{ runner.os }}-"],
        )
    """
    # Default to hashing package-lock.json if not specified
    if hash_files is None:
        hash_files = ["**/package-lock.json"]

    # Build cache key components
    key_parts = ["npm"]

    if node_version:
        key_parts.append(node_version)

    key_parts.append("${{ runner.os }}")

    # Add file hashing
    hash_expr = hash_files_helper(*hash_files)
    key_parts.append(str(hash_expr))

    cache_key = "-".join(key_parts)

    # Build restore keys (progressively more general)
    restore_keys = []
    if node_version:
        restore_keys.append(f"npm-{node_version}-${{{{ runner.os }}}}-")
        restore_keys.append(f"npm-{node_version}-")
    restore_keys.append("npm-")

    return CacheStrategy(
        path="~/.npm",
        key=cache_key,
        restore_keys=restore_keys,
    )


def hash_files_helper(*files: str) -> Expression:
    """Internal helper that handles hash_files with variable arguments.

    This is used internally by cache_pip and cache_npm to avoid
    list wrapping issues.
    """
    quoted_files = ", ".join(f"'{file}'" for file in files)
    return Expression(f"hashFiles({quoted_files})")
