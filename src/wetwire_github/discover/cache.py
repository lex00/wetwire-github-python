"""File-based caching for workflow discovery.

Caches AST parsing results to improve performance when scanning large monorepos.
Cache keys are based on file path, modification time, and size.
"""

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from wetwire_github.discover.discover import DiscoveredResource


class DiscoveryCache:
    """File-based cache for discovered resources."""

    def __init__(self, cache_dir: str = ".wetwire-cache") -> None:
        """Initialize the discovery cache.

        Args:
            cache_dir: Directory to store cache files (default: .wetwire-cache)
        """
        self.cache_dir = Path(cache_dir)

    def _ensure_cache_dir(self) -> None:
        """Ensure cache directory exists."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, file_path: str) -> str:
        """Generate cache key based on file path, mtime, and size.

        Args:
            file_path: Path to the file

        Returns:
            Cache key string (hash of path + mtime + size)
        """
        try:
            path = Path(file_path)
            stat = path.stat()

            # Create key from path, mtime, and size
            key_parts = f"{file_path}:{stat.st_mtime}:{stat.st_size}"
            key_hash = hashlib.sha256(key_parts.encode()).hexdigest()

            return key_hash
        except (OSError, FileNotFoundError):
            # If file doesn't exist or can't be accessed, return a key based on path only
            return hashlib.sha256(file_path.encode()).hexdigest()

    def _get_cache_file_path(self, cache_key: str) -> Path:
        """Get the cache file path for a given cache key.

        Args:
            cache_key: Cache key hash

        Returns:
            Path to cache file
        """
        return self.cache_dir / f"{cache_key}.json"

    def get(self, file_path: str) -> list[DiscoveredResource] | None:
        """Get cached resources for a file.

        Args:
            file_path: Path to the file to check cache for

        Returns:
            List of discovered resources if cached, None if not in cache or stale
        """
        try:
            cache_key = self._get_cache_key(file_path)
            cache_file = self._get_cache_file_path(cache_key)

            if not cache_file.exists():
                return None

            # Load cache data
            with open(cache_file, encoding="utf-8") as f:
                cache_data = json.load(f)

            # Verify the cache is for the same file
            if cache_data.get("file_path") != file_path:
                return None

            # Deserialize resources
            resources = []
            for resource_dict in cache_data.get("resources", []):
                resource = DiscoveredResource(**resource_dict)
                resources.append(resource)

            return resources
        except (OSError, json.JSONDecodeError, KeyError, TypeError):
            # If cache is corrupted or unreadable, treat as cache miss
            return None

    def set(self, file_path: str, resources: list[DiscoveredResource]) -> None:
        """Cache discovered resources for a file.

        Args:
            file_path: Path to the file
            resources: List of discovered resources to cache
        """
        try:
            self._ensure_cache_dir()

            cache_key = self._get_cache_key(file_path)
            cache_file = self._get_cache_file_path(cache_key)

            # Serialize resources
            cache_data: dict[str, Any] = {
                "file_path": file_path,
                "resources": [asdict(r) for r in resources],
            }

            # Write cache file
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2)
        except (OSError, TypeError):
            # If we can't write cache, fail silently
            pass

    def clear(self) -> None:
        """Clear all cached data."""
        try:
            if self.cache_dir.exists():
                for cache_file in self.cache_dir.glob("*.json"):
                    cache_file.unlink()
        except OSError:
            # If we can't clear cache, fail silently
            pass
