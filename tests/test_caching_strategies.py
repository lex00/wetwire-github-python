"""Tests for advanced caching strategies module (issue #142)."""

from wetwire_github.caching import (
    CacheStrategy,
    cache_npm,
    cache_pip,
    hash_files,
)
from wetwire_github.workflow import Step


class TestHashFiles:
    """Tests for hash_files() helper function."""

    def test_single_file(self) -> None:
        """Test hashing a single file."""
        result = hash_files("requirements.txt")

        assert str(result) == "${{ hashFiles('requirements.txt') }}"

    def test_multiple_files(self) -> None:
        """Test hashing multiple files."""
        result = hash_files("requirements.txt", "setup.py")

        assert str(result) == "${{ hashFiles('requirements.txt', 'setup.py') }}"

    def test_glob_pattern(self) -> None:
        """Test hashing with glob pattern."""
        result = hash_files("**/*.json")

        assert str(result) == "${{ hashFiles('**/*.json') }}"

    def test_list_input(self) -> None:
        """Test hashing with list of files."""
        files = ["package.json", "package-lock.json"]
        result = hash_files(files)

        assert str(result) == "${{ hashFiles('package.json', 'package-lock.json') }}"


class TestCacheStrategy:
    """Tests for CacheStrategy dataclass."""

    def test_basic_creation(self) -> None:
        """Test creating a basic cache strategy."""
        strategy = CacheStrategy(
            path="~/.cache/pip",
            key="pip-cache-${{ runner.os }}",
        )

        assert strategy.path == "~/.cache/pip"
        assert strategy.key == "pip-cache-${{ runner.os }}"
        assert strategy.restore_keys is None

    def test_with_restore_keys(self) -> None:
        """Test cache strategy with restore keys."""
        strategy = CacheStrategy(
            path="~/.cache/pip",
            key="pip-${{ hashFiles('requirements.txt') }}",
            restore_keys=["pip-"],
        )

        assert strategy.restore_keys == ["pip-"]

    def test_to_step(self) -> None:
        """Test converting cache strategy to Step."""
        strategy = CacheStrategy(
            path="~/.cache/pip",
            key="pip-cache",
        )

        step = strategy.to_step()

        assert isinstance(step, Step)
        assert step.uses == "actions/cache@v4"
        assert step.with_ is not None
        assert step.with_["path"] == "~/.cache/pip"
        assert step.with_["key"] == "pip-cache"

    def test_to_step_with_restore_keys(self) -> None:
        """Test converting cache strategy with restore keys to Step."""
        strategy = CacheStrategy(
            path="~/.cache/custom",
            key="custom-cache-v1",
            restore_keys=["custom-cache-", "custom-"],
        )

        step = strategy.to_step()

        assert step.with_["restore-keys"] == "custom-cache-\ncustom-"

    def test_to_step_with_name(self) -> None:
        """Test converting cache strategy to Step with custom name."""
        strategy = CacheStrategy(
            path="~/.cache/pip",
            key="pip-cache",
        )

        step = strategy.to_step(name="Cache pip dependencies")

        assert step.name == "Cache pip dependencies"


class TestCachePip:
    """Tests for cache_pip() convenience function."""

    def test_basic_pip_cache(self) -> None:
        """Test basic pip caching."""
        strategy = cache_pip()

        assert "pip" in strategy.path.lower()
        assert strategy.key is not None
        assert "${{ runner.os }}" in strategy.key

    def test_pip_cache_with_python_version(self) -> None:
        """Test pip cache with specific Python version."""
        strategy = cache_pip(python_version="3.11")

        assert "3.11" in strategy.key

    def test_pip_cache_with_hash_files(self) -> None:
        """Test pip cache with file hashing."""
        strategy = cache_pip(
            python_version="3.11",
            hash_files=["requirements.txt", "setup.py"],
        )

        assert "hashFiles" in strategy.key
        assert "requirements.txt" in strategy.key

    def test_pip_cache_has_restore_keys(self) -> None:
        """Test pip cache includes restore keys."""
        strategy = cache_pip(python_version="3.11")

        assert strategy.restore_keys is not None
        assert len(strategy.restore_keys) > 0

    def test_pip_cache_to_step(self) -> None:
        """Test converting pip cache to step."""
        strategy = cache_pip(python_version="3.11")
        step = strategy.to_step()

        assert isinstance(step, Step)
        assert step.uses == "actions/cache@v4"


class TestCacheNpm:
    """Tests for cache_npm() convenience function."""

    def test_basic_npm_cache(self) -> None:
        """Test basic npm caching."""
        strategy = cache_npm()

        assert "npm" in strategy.path.lower()
        assert strategy.key is not None
        assert "${{ runner.os }}" in strategy.key

    def test_npm_cache_with_node_version(self) -> None:
        """Test npm cache with specific Node version."""
        strategy = cache_npm(node_version="18")

        assert "18" in strategy.key

    def test_npm_cache_with_hash_files(self) -> None:
        """Test npm cache with file hashing."""
        strategy = cache_npm(
            node_version="18",
            hash_files=["package-lock.json"],
        )

        assert "hashFiles" in strategy.key
        assert "package-lock.json" in strategy.key

    def test_npm_cache_default_hash_files(self) -> None:
        """Test npm cache includes package-lock.json by default."""
        strategy = cache_npm(node_version="18")

        # Should include hash of package-lock.json by default
        assert "hashFiles" in strategy.key
        assert "package-lock.json" in strategy.key

    def test_npm_cache_has_restore_keys(self) -> None:
        """Test npm cache includes restore keys."""
        strategy = cache_npm(node_version="18")

        assert strategy.restore_keys is not None
        assert len(strategy.restore_keys) > 0

    def test_npm_cache_to_step(self) -> None:
        """Test converting npm cache to step."""
        strategy = cache_npm(node_version="18")
        step = strategy.to_step()

        assert isinstance(step, Step)
        assert step.uses == "actions/cache@v4"


class TestCacheIntegration:
    """Integration tests for caching strategies."""

    def test_custom_strategy_with_hash_files(self) -> None:
        """Test creating custom cache strategy with hash_files helper."""
        key_expr = hash_files("config/*.json")
        strategy = CacheStrategy(
            path="~/.cache/custom",
            key=f"custom-cache-{key_expr}",
            restore_keys=["custom-cache-"],
        )

        step = strategy.to_step()

        assert "hashFiles('config/*.json')" in step.with_["key"]

    def test_multiple_cache_strategies(self) -> None:
        """Test using multiple cache strategies in a workflow."""
        pip_cache = cache_pip(python_version="3.11")
        npm_cache = cache_npm(node_version="18")

        pip_step = pip_cache.to_step(name="Cache pip")
        npm_step = npm_cache.to_step(name="Cache npm")

        assert pip_step.name == "Cache pip"
        assert npm_step.name == "Cache npm"
        assert "pip" in pip_step.with_["path"].lower()
        assert "npm" in npm_step.with_["path"].lower()
