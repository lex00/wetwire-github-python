"""Tests for policy configuration support."""

import tempfile
from pathlib import Path

import pytest

from wetwire_github.policy.config import (
    PolicyConfig,
    PolicySettings,
    get_policy_presets,
    load_config,
)


class TestPolicySettings:
    """Tests for PolicySettings dataclass."""

    def test_default_policy_settings(self):
        """PolicySettings has correct defaults."""
        settings = PolicySettings()
        assert settings.enabled is True
        assert settings.params == {}

    def test_policy_settings_with_params(self):
        """PolicySettings stores custom parameters."""
        settings = PolicySettings(enabled=True, params={"max_jobs": 5})
        assert settings.enabled is True
        assert settings.params["max_jobs"] == 5

    def test_policy_settings_disabled(self):
        """PolicySettings can be disabled."""
        settings = PolicySettings(enabled=False)
        assert settings.enabled is False


class TestPolicyConfig:
    """Tests for PolicyConfig dataclass."""

    def test_default_policy_config(self):
        """PolicyConfig has correct defaults for all policies."""
        config = PolicyConfig()
        # Core policies should be enabled by default
        assert config.require_checkout.enabled is True
        assert config.require_timeouts.enabled is True
        assert config.no_hardcoded_secrets.enabled is True
        assert config.pin_actions.enabled is True
        assert config.limit_job_count.enabled is True
        # RequireApproval is disabled by default (not in default policy set)
        assert config.require_approval.enabled is False

    def test_policy_config_custom_settings(self):
        """PolicyConfig accepts custom settings."""
        config = PolicyConfig(
            require_checkout=PolicySettings(enabled=False),
            limit_job_count=PolicySettings(enabled=True, params={"max_jobs": 5}),
        )
        assert config.require_checkout.enabled is False
        assert config.limit_job_count.params["max_jobs"] == 5


class TestLoadConfigFromYaml:
    """Tests for loading config from YAML files."""

    def test_load_yaml_config_file(self):
        """load_config reads .wetwire-policy.yaml file."""
        yaml_content = """
policies:
  require_checkout:
    enabled: true
  require_timeouts:
    enabled: false
  limit_job_count:
    enabled: true
    params:
      max_jobs: 5
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".wetwire-policy.yaml"
            config_path.write_text(yaml_content)

            config = load_config(Path(tmpdir))

            assert config.require_checkout.enabled is True
            assert config.require_timeouts.enabled is False
            assert config.limit_job_count.enabled is True
            assert config.limit_job_count.params["max_jobs"] == 5

    def test_load_yaml_config_explicit_path(self):
        """load_config accepts explicit path to config file."""
        yaml_content = """
policies:
  pin_actions:
    enabled: false
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "custom-policy.yaml"
            config_path.write_text(yaml_content)

            config = load_config(config_path)

            assert config.pin_actions.enabled is False

    def test_load_yaml_partial_config(self):
        """load_config uses defaults for missing policies."""
        yaml_content = """
policies:
  require_checkout:
    enabled: false
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".wetwire-policy.yaml"
            config_path.write_text(yaml_content)

            config = load_config(Path(tmpdir))

            # Explicitly configured
            assert config.require_checkout.enabled is False
            # Defaults for unspecified policies
            assert config.require_timeouts.enabled is True
            assert config.pin_actions.enabled is True


class TestLoadConfigFromPyproject:
    """Tests for loading config from pyproject.toml."""

    def test_load_pyproject_config(self):
        """load_config reads [tool.wetwire.policies] from pyproject.toml."""
        toml_content = """
[project]
name = "test-project"

[tool.wetwire.policies]
require_checkout = { enabled = true }
require_timeouts = { enabled = false }
limit_job_count = { enabled = true, params = { max_jobs = 8 } }
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = Path(tmpdir) / "pyproject.toml"
            pyproject_path.write_text(toml_content)

            config = load_config(Path(tmpdir))

            assert config.require_checkout.enabled is True
            assert config.require_timeouts.enabled is False
            assert config.limit_job_count.params["max_jobs"] == 8

    def test_yaml_takes_precedence_over_pyproject(self):
        """When both exist, .wetwire-policy.yaml takes precedence."""
        yaml_content = """
policies:
  require_checkout:
    enabled: false
"""
        toml_content = """
[project]
name = "test-project"

[tool.wetwire.policies]
require_checkout = { enabled = true }
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_yaml = Path(tmpdir) / ".wetwire-policy.yaml"
            config_yaml.write_text(yaml_content)
            pyproject_path = Path(tmpdir) / "pyproject.toml"
            pyproject_path.write_text(toml_content)

            config = load_config(Path(tmpdir))

            # YAML should take precedence
            assert config.require_checkout.enabled is False


class TestLoadConfigDefaults:
    """Tests for default config behavior."""

    def test_no_config_returns_defaults(self):
        """load_config returns defaults when no config file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = load_config(Path(tmpdir))

            # Core policies enabled by default
            assert config.require_checkout.enabled is True
            assert config.require_timeouts.enabled is True
            assert config.no_hardcoded_secrets.enabled is True
            assert config.pin_actions.enabled is True
            assert config.limit_job_count.enabled is True
            # RequireApproval disabled by default
            assert config.require_approval.enabled is False
            # Default limit_job_count max_jobs
            assert config.limit_job_count.params.get("max_jobs", 10) == 10

    def test_load_config_none_path(self):
        """load_config with None uses current directory."""
        # This tests the fallback behavior
        config = load_config(None)
        assert isinstance(config, PolicyConfig)


class TestPolicyPresets:
    """Tests for policy presets."""

    def test_get_minimal_preset(self):
        """Minimal preset enables only essential policies."""
        presets = get_policy_presets()
        minimal = presets["minimal"]

        # Only essential policies enabled
        assert minimal.require_checkout.enabled is True
        assert minimal.no_hardcoded_secrets.enabled is True
        # Others disabled
        assert minimal.require_timeouts.enabled is False
        assert minimal.pin_actions.enabled is False
        assert minimal.limit_job_count.enabled is False
        assert minimal.require_approval.enabled is False

    def test_get_standard_preset(self):
        """Standard preset enables common policies."""
        presets = get_policy_presets()
        standard = presets["standard"]

        # Standard set
        assert standard.require_checkout.enabled is True
        assert standard.require_timeouts.enabled is True
        assert standard.no_hardcoded_secrets.enabled is True
        assert standard.pin_actions.enabled is True
        assert standard.limit_job_count.enabled is True
        # More strict policies disabled
        assert standard.require_approval.enabled is False

    def test_get_strict_preset(self):
        """Strict preset enables all policies."""
        presets = get_policy_presets()
        strict = presets["strict"]

        # All policies enabled
        assert strict.require_checkout.enabled is True
        assert strict.require_timeouts.enabled is True
        assert strict.no_hardcoded_secrets.enabled is True
        assert strict.pin_actions.enabled is True
        assert strict.limit_job_count.enabled is True
        assert strict.require_approval.enabled is True
        # Stricter limits
        assert strict.limit_job_count.params.get("max_jobs", 10) == 5


class TestPolicyConfigValidation:
    """Tests for config validation."""

    def test_invalid_yaml_raises_error(self):
        """Invalid YAML raises appropriate error."""
        invalid_yaml = """
policies:
  - this is invalid
  - yaml structure
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".wetwire-policy.yaml"
            config_path.write_text(invalid_yaml)

            with pytest.raises(ValueError):
                load_config(Path(tmpdir))

    def test_unknown_policy_ignored(self):
        """Unknown policies in config are ignored."""
        yaml_content = """
policies:
  require_checkout:
    enabled: true
  unknown_policy:
    enabled: true
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".wetwire-policy.yaml"
            config_path.write_text(yaml_content)

            # Should not raise, just ignore unknown
            config = load_config(Path(tmpdir))
            assert config.require_checkout.enabled is True
