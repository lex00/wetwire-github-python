"""Path validation utilities for CLI commands.

Provides security validation for path arguments to prevent:
- Path traversal attacks (../)
- Symlink-based escapes
- Access to files outside allowed boundaries
"""

import re
from pathlib import Path


class PathValidationError(Exception):
    """Raised when path validation fails."""

    pass


# Pattern to detect path traversal attempts
_TRAVERSAL_PATTERN = re.compile(r"(^|[/\\])\.\.([/\\]|$)")

# Pattern to detect null bytes and control characters
_INVALID_CHARS_PATTERN = re.compile(r"[\x00-\x1f]")


def validate_path(
    path: str,
    base_dir: str | None = None,
    must_exist: bool = True,
    allow_absolute: bool = True,
) -> Path:
    """Validate a path for security and normalize it.

    Args:
        path: The path to validate (can be relative or absolute)
        base_dir: Base directory to resolve relative paths against.
                 If None, uses current working directory.
        must_exist: If True, raises error if path doesn't exist.
        allow_absolute: If True, absolute paths are allowed and only checked for
                       traversal patterns (not restricted to base_dir).

    Returns:
        Resolved absolute Path that has been validated.

    Raises:
        PathValidationError: If path fails validation (traversal, outside bounds, etc.)
    """
    if not path:
        raise PathValidationError("Path cannot be empty")

    # Check for null bytes and control characters
    if _INVALID_CHARS_PATTERN.search(path):
        raise PathValidationError("Path contains invalid control characters")

    # Check for URL-encoded traversal (basic check)
    if "%2f" in path.lower() or "%2e" in path.lower() or "%5c" in path.lower():
        # Decode and check for traversal
        decoded = path.replace("%2f", "/").replace("%2F", "/")
        decoded = decoded.replace("%2e", ".").replace("%2E", ".")
        decoded = decoded.replace("%5c", "\\").replace("%5C", "\\")
        if _TRAVERSAL_PATTERN.search(decoded):
            raise PathValidationError("Path contains encoded traversal patterns")

    # Normalize backslashes to forward slashes for consistent checking
    normalized_for_check = path.replace("\\", "/")

    # Check for traversal patterns before resolution
    if _TRAVERSAL_PATTERN.search(normalized_for_check):
        raise PathValidationError("Path traversal patterns (../) are not allowed")

    # Determine base directory
    if base_dir is None:
        base_path = Path.cwd()
    else:
        base_path = Path(base_dir).resolve()

    # Convert to Path and resolve
    path_obj = Path(path)
    is_absolute_path = path_obj.is_absolute()

    # Get the unresolved path first (for symlink detection)
    if is_absolute_path:
        unresolved = path_obj
    else:
        unresolved = base_path / path_obj

    # Resolve symlinks to get the real path
    resolved = unresolved.resolve()

    # Check if resolved path is within base directory
    # Skip this check for absolute paths if allow_absolute is True
    if not (is_absolute_path and allow_absolute):
        try:
            resolved.relative_to(base_path)
        except ValueError:
            raise PathValidationError(
                f"Path resolves to location outside allowed directory: {resolved}"
            )

    # Check for symlink escapes - the resolved path after symlink resolution
    # should still be within the appropriate boundary
    if unresolved.exists():
        # Check if the original path is a symlink (before resolution)
        if unresolved.is_symlink():
            target = resolved  # resolved already has the final target
            # For absolute paths, use the symlink's parent as the boundary
            symlink_base = unresolved.parent if (is_absolute_path and allow_absolute) else base_path
            try:
                target.relative_to(symlink_base)
            except ValueError:
                raise PathValidationError(
                    f"Symlink target is outside allowed directory: {target}"
                )
    elif must_exist:
        raise PathValidationError(f"Path does not exist: {resolved}")

    return resolved


def validate_paths(
    paths: list[str],
    base_dir: str | None = None,
    must_exist: bool = True,
) -> list[Path]:
    """Validate multiple paths.

    Args:
        paths: List of paths to validate
        base_dir: Base directory to resolve relative paths against
        must_exist: If True, raises error if any path doesn't exist

    Returns:
        List of validated Path objects

    Raises:
        PathValidationError: If any path fails validation
    """
    return [validate_path(p, base_dir=base_dir, must_exist=must_exist) for p in paths]
