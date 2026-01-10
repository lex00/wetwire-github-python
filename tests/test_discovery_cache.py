"""Tests for discovery caching functionality."""

import time
from pathlib import Path

from wetwire_github.discover import discover_in_directory, discover_in_file
from wetwire_github.discover.cache import DiscoveryCache


class TestDiscoveryCache:
    """Tests for DiscoveryCache class."""

    def test_cache_stores_discovered_resources(self, tmp_path):
        """Cache stores discovered resources from a file."""
        cache_dir = tmp_path / ".wetwire-cache"
        cache = DiscoveryCache(cache_dir=str(cache_dir))

        # Create a test file
        test_file = tmp_path / "workflows.py"
        test_file.write_text('''
from wetwire_github.workflow import Workflow

ci = Workflow(name="CI")
''')

        # First discovery - should cache
        resources = discover_in_file(str(test_file), cache=cache)
        assert len(resources) == 1
        assert resources[0].name == "ci"

        # Verify cache was populated
        cached_result = cache.get(str(test_file))
        assert cached_result is not None
        assert len(cached_result) == 1
        assert cached_result[0].name == "ci"

    def test_cache_returns_cached_resources_on_second_call(self, tmp_path):
        """Cache returns cached resources without re-parsing file."""
        cache_dir = tmp_path / ".wetwire-cache"
        cache = DiscoveryCache(cache_dir=str(cache_dir))

        test_file = tmp_path / "workflows.py"
        test_file.write_text('''
from wetwire_github.workflow import Workflow

ci = Workflow(name="CI")
''')

        # First call - parses and caches
        resources1 = discover_in_file(str(test_file), cache=cache)

        # Modify file content but not the file itself (simulate reading from cache)
        # Second call should return cached results
        resources2 = discover_in_file(str(test_file), cache=cache)

        assert len(resources1) == 1
        assert len(resources2) == 1
        assert resources1[0].name == resources2[0].name

    def test_cache_invalidated_on_file_modification(self, tmp_path):
        """Cache is invalidated when file is modified."""
        cache_dir = tmp_path / ".wetwire-cache"
        cache = DiscoveryCache(cache_dir=str(cache_dir))

        test_file = tmp_path / "workflows.py"
        test_file.write_text('''
from wetwire_github.workflow import Workflow

ci = Workflow(name="CI")
''')

        # First discovery
        resources1 = discover_in_file(str(test_file), cache=cache)
        assert len(resources1) == 1
        assert resources1[0].name == "ci"

        # Wait a bit to ensure mtime changes
        time.sleep(0.01)

        # Modify file
        test_file.write_text('''
from wetwire_github.workflow import Workflow

ci = Workflow(name="CI")
deploy = Workflow(name="Deploy")
''')

        # Second discovery should detect change and re-parse
        resources2 = discover_in_file(str(test_file), cache=cache)
        assert len(resources2) == 2
        names = {r.name for r in resources2}
        assert names == {"ci", "deploy"}

    def test_cache_key_based_on_path_mtime_and_size(self, tmp_path):
        """Cache key includes file path, modification time, and size."""
        cache_dir = tmp_path / ".wetwire-cache"
        cache = DiscoveryCache(cache_dir=str(cache_dir))

        test_file = tmp_path / "workflows.py"
        test_file.write_text('''
from wetwire_github.workflow import Workflow

ci = Workflow(name="CI")
''')

        # Get initial cache key
        key1 = cache._get_cache_key(str(test_file))

        # Wait and modify file
        time.sleep(0.01)
        test_file.write_text('''
from wetwire_github.workflow import Workflow

ci = Workflow(name="CI")
deploy = Workflow(name="Deploy")
''')

        # Cache key should be different
        key2 = cache._get_cache_key(str(test_file))
        assert key1 != key2

    def test_cache_bypassed_when_cache_is_none(self, tmp_path):
        """Discovery works without cache when cache=None."""
        test_file = tmp_path / "workflows.py"
        test_file.write_text('''
from wetwire_github.workflow import Workflow

ci = Workflow(name="CI")
''')

        # Call without cache (default behavior)
        resources = discover_in_file(str(test_file), cache=None)
        assert len(resources) == 1
        assert resources[0].name == "ci"

    def test_cache_handles_syntax_errors(self, tmp_path):
        """Cache handles files with syntax errors gracefully."""
        cache_dir = tmp_path / ".wetwire-cache"
        cache = DiscoveryCache(cache_dir=str(cache_dir))

        test_file = tmp_path / "broken.py"
        test_file.write_text('''
def incomplete(
''')

        # Should return empty list without crashing
        resources = discover_in_file(str(test_file), cache=cache)
        assert len(resources) == 0

    def test_cache_creates_cache_directory(self, tmp_path):
        """Cache creates cache directory if it doesn't exist."""
        cache_dir = tmp_path / ".wetwire-cache"
        assert not cache_dir.exists()

        cache = DiscoveryCache(cache_dir=str(cache_dir))
        test_file = tmp_path / "workflows.py"
        test_file.write_text('''
from wetwire_github.workflow import Workflow

ci = Workflow(name="CI")
''')

        discover_in_file(str(test_file), cache=cache)

        # Cache directory should be created
        assert cache_dir.exists()
        assert cache_dir.is_dir()


class TestDiscoverInDirectoryWithCache:
    """Tests for discover_in_directory with caching."""

    def test_discover_directory_with_cache(self, tmp_path):
        """Discover resources in directory with caching enabled."""
        cache_dir = tmp_path / ".wetwire-cache"
        cache = DiscoveryCache(cache_dir=str(cache_dir))

        # Create multiple Python files
        (tmp_path / "workflows.py").write_text('''
from wetwire_github.workflow import Workflow

ci = Workflow(name="CI")
''')
        (tmp_path / "jobs.py").write_text('''
from wetwire_github.workflow import Job

build = Job(runs_on="ubuntu-latest")
''')

        # First discovery with cache
        resources = discover_in_directory(str(tmp_path), cache=cache)
        assert len(resources) == 2

        # Second call should use cache
        resources2 = discover_in_directory(str(tmp_path), cache=cache)
        assert len(resources2) == 2

    def test_discover_directory_cache_invalidation(self, tmp_path):
        """Cache invalidation works for directory discovery."""
        cache_dir = tmp_path / ".wetwire-cache"
        cache = DiscoveryCache(cache_dir=str(cache_dir))

        workflows_file = tmp_path / "workflows.py"
        workflows_file.write_text('''
from wetwire_github.workflow import Workflow

ci = Workflow(name="CI")
''')

        # First discovery
        resources1 = discover_in_directory(str(tmp_path), cache=cache)
        assert len(resources1) == 1

        # Add new file
        time.sleep(0.01)
        (tmp_path / "jobs.py").write_text('''
from wetwire_github.workflow import Job

build = Job(runs_on="ubuntu-latest")
''')

        # Second discovery should find new file
        resources2 = discover_in_directory(str(tmp_path), cache=cache)
        assert len(resources2) == 2

    def test_discover_directory_without_cache(self, tmp_path):
        """Directory discovery works without cache."""
        (tmp_path / "workflows.py").write_text('''
from wetwire_github.workflow import Workflow

ci = Workflow(name="CI")
''')

        resources = discover_in_directory(str(tmp_path), cache=None)
        assert len(resources) == 1


class TestCachePersistence:
    """Tests for cache persistence across sessions."""

    def test_cache_persists_between_instances(self, tmp_path):
        """Cache persists between different DiscoveryCache instances."""
        cache_dir = tmp_path / ".wetwire-cache"

        test_file = tmp_path / "workflows.py"
        test_file.write_text('''
from wetwire_github.workflow import Workflow

ci = Workflow(name="CI")
''')

        # First cache instance
        cache1 = DiscoveryCache(cache_dir=str(cache_dir))
        resources1 = discover_in_file(str(test_file), cache=cache1)
        assert len(resources1) == 1

        # Second cache instance (simulating new session)
        cache2 = DiscoveryCache(cache_dir=str(cache_dir))
        cached_result = cache2.get(str(test_file))

        # Should load from persisted cache
        assert cached_result is not None
        assert len(cached_result) == 1
        assert cached_result[0].name == "ci"

    def test_cache_file_format(self, tmp_path):
        """Cache uses appropriate file format for storage."""
        cache_dir = tmp_path / ".wetwire-cache"
        cache = DiscoveryCache(cache_dir=str(cache_dir))

        test_file = tmp_path / "workflows.py"
        test_file.write_text('''
from wetwire_github.workflow import Workflow

ci = Workflow(name="CI")
''')

        discover_in_file(str(test_file), cache=cache)

        # Check that cache files were created
        cache_files = list(Path(cache_dir).glob("*.json"))
        assert len(cache_files) > 0
