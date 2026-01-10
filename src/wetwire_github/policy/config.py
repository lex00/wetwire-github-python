"""Policy configuration support.

Load policy settings from configuration files:
- .wetwire-policy.yaml (preferred)
- pyproject.toml [tool.wetwire.policies] (fallback)

Example .wetwire-policy.yaml:
    policies:
      require_checkout:
        enabled: true
      limit_job_count:
        enabled: true
        params:
          max_jobs: 5

Example pyproject.toml:
    [tool.wetwire.policies]
    require_checkout = { enabled = true }
    limit_job_count = { enabled = true, params = { max_jobs = 5 } }
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class PolicySettings:
    """Settings for a single policy."""

    enabled: bool = True
    """Whether this policy is enabled."""

    params: dict[str, Any] = field(default_factory=dict)
    """Custom parameters for this policy."""


@dataclass
class PolicyConfig:
    """Configuration for all policies."""

    require_checkout: PolicySettings = field(default_factory=PolicySettings)
    """Settings for RequireCheckout policy."""

    require_timeouts: PolicySettings = field(default_factory=PolicySettings)
    """Settings for RequireTimeouts policy."""

    no_hardcoded_secrets: PolicySettings = field(default_factory=PolicySettings)
    """Settings for NoHardcodedSecrets policy."""

    pin_actions: PolicySettings = field(default_factory=PolicySettings)
    """Settings for PinActions policy."""

    limit_job_count: PolicySettings = field(default_factory=PolicySettings)
    """Settings for LimitJobCount policy."""

    require_approval: PolicySettings = field(
        default_factory=lambda: PolicySettings(enabled=False)
    )
    """Settings for RequireApproval policy (disabled by default)."""


def _parse_policy_settings(data: dict[str, Any] | None) -> PolicySettings:
    """Parse policy settings from config data.

    Args:
        data: Dict with 'enabled' and optional 'params' keys

    Returns:
        PolicySettings instance
    """
    if data is None:
        return PolicySettings()

    return PolicySettings(
        enabled=data.get("enabled", True),
        params=data.get("params", {}),
    )


def _load_from_yaml(path: Path) -> PolicyConfig | None:
    """Load config from a YAML file.

    Args:
        path: Path to the YAML config file

    Returns:
        PolicyConfig or None if file doesn't exist

    Raises:
        ValueError: If YAML structure is invalid
    """
    if not path.exists():
        return None

    with open(path) as f:
        data = yaml.safe_load(f)

    if not data or "policies" not in data:
        return PolicyConfig()

    policies_data = data["policies"]
    if not isinstance(policies_data, dict):
        raise ValueError("policies section must be a mapping")

    return _build_config_from_dict(policies_data)


def _load_from_pyproject(path: Path) -> PolicyConfig | None:
    """Load config from pyproject.toml.

    Args:
        path: Path to pyproject.toml

    Returns:
        PolicyConfig or None if not found
    """
    if not path.exists():
        return None

    # Use tomllib for Python 3.11+
    try:
        import tomllib
    except ImportError:
        # Fall back to tomli for older Python
        try:
            import tomli as tomllib  # type: ignore[import-not-found]
        except ImportError:
            return None

    with open(path, "rb") as f:
        data = tomllib.load(f)

    # Navigate to [tool.wetwire.policies]
    tool = data.get("tool", {})
    wetwire = tool.get("wetwire", {})
    policies_data = wetwire.get("policies", {})

    if not policies_data:
        return None

    return _build_config_from_dict(policies_data)


def _build_config_from_dict(policies_data: dict[str, Any]) -> PolicyConfig:
    """Build PolicyConfig from a dictionary of policy settings.

    Args:
        policies_data: Dict mapping policy names to their settings

    Returns:
        PolicyConfig instance
    """
    # Map config keys to PolicyConfig field names
    policy_map = {
        "require_checkout": "require_checkout",
        "require_timeouts": "require_timeouts",
        "no_hardcoded_secrets": "no_hardcoded_secrets",
        "pin_actions": "pin_actions",
        "limit_job_count": "limit_job_count",
        "require_approval": "require_approval",
    }

    kwargs: dict[str, PolicySettings] = {}

    for key, field_name in policy_map.items():
        if key in policies_data:
            kwargs[field_name] = _parse_policy_settings(policies_data[key])

    return PolicyConfig(**kwargs)


def load_config(path: Path | None = None) -> PolicyConfig:
    """Load policy configuration from file.

    Configuration is loaded in this order of precedence:
    1. Explicit path to a .yaml file
    2. .wetwire-policy.yaml in the given directory
    3. pyproject.toml [tool.wetwire.policies] in the given directory
    4. Default configuration

    Args:
        path: Path to config file or directory containing config.
              If None, uses current directory.

    Returns:
        PolicyConfig instance

    Raises:
        ValueError: If config file has invalid format
    """
    if path is None:
        path = Path.cwd()

    # If path is a file, load it directly
    if path.is_file():
        if path.suffix in {".yaml", ".yml"}:
            config = _load_from_yaml(path)
            if config:
                return config
        elif path.name == "pyproject.toml":
            config = _load_from_pyproject(path)
            if config:
                return config
        return PolicyConfig()

    # If path is a directory, look for config files
    if path.is_dir():
        # Try .wetwire-policy.yaml first
        yaml_path = path / ".wetwire-policy.yaml"
        config = _load_from_yaml(yaml_path)
        if config:
            return config

        # Fall back to pyproject.toml
        pyproject_path = path / "pyproject.toml"
        config = _load_from_pyproject(pyproject_path)
        if config:
            return config

    # Return defaults if no config found
    return PolicyConfig()


def get_policy_presets() -> dict[str, PolicyConfig]:
    """Get predefined policy configuration presets.

    Returns:
        Dict mapping preset names to PolicyConfig instances
    """
    return {
        "minimal": PolicyConfig(
            require_checkout=PolicySettings(enabled=True),
            require_timeouts=PolicySettings(enabled=False),
            no_hardcoded_secrets=PolicySettings(enabled=True),
            pin_actions=PolicySettings(enabled=False),
            limit_job_count=PolicySettings(enabled=False),
            require_approval=PolicySettings(enabled=False),
        ),
        "standard": PolicyConfig(
            require_checkout=PolicySettings(enabled=True),
            require_timeouts=PolicySettings(enabled=True),
            no_hardcoded_secrets=PolicySettings(enabled=True),
            pin_actions=PolicySettings(enabled=True),
            limit_job_count=PolicySettings(enabled=True),
            require_approval=PolicySettings(enabled=False),
        ),
        "strict": PolicyConfig(
            require_checkout=PolicySettings(enabled=True),
            require_timeouts=PolicySettings(enabled=True),
            no_hardcoded_secrets=PolicySettings(enabled=True),
            pin_actions=PolicySettings(enabled=True),
            limit_job_count=PolicySettings(enabled=True, params={"max_jobs": 5}),
            require_approval=PolicySettings(enabled=True),
        ),
    }
