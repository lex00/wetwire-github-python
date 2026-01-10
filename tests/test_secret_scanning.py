"""Tests for Secret Scanning configuration support."""

import pytest
import re


class TestSecretScanningTypes:
    """Tests for Secret Scanning dataclass types."""

    def test_secret_scanning_config_dataclass_exists(self):
        """SecretScanningConfig dataclass can be imported."""
        from wetwire_github.secret_scanning import SecretScanningConfig

        assert SecretScanningConfig is not None

    def test_custom_pattern_dataclass_exists(self):
        """CustomPattern dataclass can be imported."""
        from wetwire_github.secret_scanning import CustomPattern

        assert CustomPattern is not None

    def test_alert_settings_dataclass_exists(self):
        """AlertSettings dataclass can be imported."""
        from wetwire_github.secret_scanning import AlertSettings

        assert AlertSettings is not None


class TestCustomPattern:
    """Tests for CustomPattern dataclass."""

    def test_basic_custom_pattern(self):
        """Basic custom pattern can be created."""
        from wetwire_github.secret_scanning import CustomPattern

        pattern = CustomPattern(
            name="API Key Pattern",
            pattern=r"api[_-]?key[_-]?[a-zA-Z0-9]{32}",
        )
        assert pattern.name == "API Key Pattern"
        assert pattern.pattern == r"api[_-]?key[_-]?[a-zA-Z0-9]{32}"

    def test_custom_pattern_with_secret_type(self):
        """Custom pattern with secret type can be created."""
        from wetwire_github.secret_scanning import CustomPattern

        pattern = CustomPattern(
            name="AWS Access Key",
            pattern=r"AKIA[0-9A-Z]{16}",
            secret_type="aws_access_key",
        )
        assert pattern.secret_type == "aws_access_key"

    def test_custom_pattern_with_valid_regex(self):
        """Custom pattern validates regex pattern."""
        from wetwire_github.secret_scanning import CustomPattern

        pattern = CustomPattern(
            name="Valid Regex",
            pattern=r"[a-zA-Z0-9]+",
        )
        # Pattern should compile without errors
        compiled = re.compile(pattern.pattern)
        assert compiled is not None

    def test_custom_pattern_defaults(self):
        """Custom pattern has proper defaults."""
        from wetwire_github.secret_scanning import CustomPattern

        pattern = CustomPattern(
            name="Test Pattern",
            pattern=r"test_\d+",
        )
        assert pattern.secret_type is None


class TestAlertSettings:
    """Tests for AlertSettings dataclass."""

    def test_basic_alert_settings(self):
        """Basic alert settings can be created."""
        from wetwire_github.secret_scanning import AlertSettings

        settings = AlertSettings(push_protection=True)
        assert settings.push_protection is True

    def test_alert_settings_with_notifications(self):
        """Alert settings with notification settings can be created."""
        from wetwire_github.secret_scanning import AlertSettings

        settings = AlertSettings(
            push_protection=True,
            alert_notifications=True,
        )
        assert settings.alert_notifications is True

    def test_alert_settings_defaults(self):
        """Alert settings has proper defaults."""
        from wetwire_github.secret_scanning import AlertSettings

        settings = AlertSettings()
        assert settings.push_protection is False
        assert settings.alert_notifications is True


class TestSecretScanningConfig:
    """Tests for SecretScanningConfig dataclass."""

    def test_basic_secret_scanning_config(self):
        """Basic secret scanning config can be created."""
        from wetwire_github.secret_scanning import SecretScanningConfig

        config = SecretScanningConfig()
        assert config.enabled is True

    def test_secret_scanning_with_disabled(self):
        """Secret scanning can be disabled."""
        from wetwire_github.secret_scanning import SecretScanningConfig

        config = SecretScanningConfig(enabled=False)
        assert config.enabled is False

    def test_secret_scanning_with_push_protection(self):
        """Secret scanning with push protection can be created."""
        from wetwire_github.secret_scanning import SecretScanningConfig

        config = SecretScanningConfig(push_protection=True)
        assert config.push_protection is True

    def test_secret_scanning_with_single_pattern(self):
        """Secret scanning with single custom pattern can be created."""
        from wetwire_github.secret_scanning import (
            CustomPattern,
            SecretScanningConfig,
        )

        pattern = CustomPattern(
            name="API Key",
            pattern=r"api_key_[a-zA-Z0-9]{32}",
        )
        config = SecretScanningConfig(patterns=[pattern])
        assert len(config.patterns) == 1
        assert config.patterns[0].name == "API Key"

    def test_secret_scanning_with_multiple_patterns(self):
        """Secret scanning with multiple custom patterns can be created."""
        from wetwire_github.secret_scanning import (
            CustomPattern,
            SecretScanningConfig,
        )

        patterns = [
            CustomPattern(name="API Key", pattern=r"api_key_[a-zA-Z0-9]{32}"),
            CustomPattern(name="Secret Token", pattern=r"secret_[a-zA-Z0-9]{40}"),
            CustomPattern(name="Password", pattern=r"password[=:]\s*['\"][^'\"]+['\"]"),
        ]
        config = SecretScanningConfig(patterns=patterns)
        assert len(config.patterns) == 3
        assert config.patterns[0].name == "API Key"
        assert config.patterns[1].name == "Secret Token"
        assert config.patterns[2].name == "Password"

    def test_secret_scanning_with_alert_settings(self):
        """Secret scanning with alert settings can be created."""
        from wetwire_github.secret_scanning import (
            AlertSettings,
            SecretScanningConfig,
        )

        config = SecretScanningConfig(
            alert_settings=AlertSettings(
                push_protection=True,
                alert_notifications=True,
            )
        )
        assert config.alert_settings is not None
        assert config.alert_settings.push_protection is True
        assert config.alert_settings.alert_notifications is True

    def test_secret_scanning_defaults(self):
        """Secret scanning has proper defaults."""
        from wetwire_github.secret_scanning import SecretScanningConfig

        config = SecretScanningConfig()
        assert config.enabled is True
        assert config.push_protection is False
        assert config.patterns == []
        assert config.alert_settings is None

    def test_secret_scanning_combined(self):
        """Secret scanning with all settings can be created."""
        from wetwire_github.secret_scanning import (
            AlertSettings,
            CustomPattern,
            SecretScanningConfig,
        )

        config = SecretScanningConfig(
            enabled=True,
            push_protection=True,
            patterns=[
                CustomPattern(
                    name="API Key",
                    pattern=r"api_key_[a-zA-Z0-9]{32}",
                    secret_type="api_key",
                )
            ],
            alert_settings=AlertSettings(
                push_protection=True,
                alert_notifications=True,
            ),
        )
        assert config.enabled is True
        assert config.push_protection is True
        assert len(config.patterns) == 1
        assert config.alert_settings.push_protection is True


class TestSecretScanningSerialization:
    """Tests for Secret Scanning serialization."""

    def test_serialize_basic_config(self):
        """Basic secret scanning config serializes to valid dict."""
        from wetwire_github.secret_scanning import SecretScanningConfig
        from wetwire_github.serialize import to_dict

        config = SecretScanningConfig(enabled=True)

        result = to_dict(config)
        assert result["enabled"] is True

    def test_serialize_with_push_protection(self):
        """Secret scanning with push protection serializes correctly."""
        from wetwire_github.secret_scanning import SecretScanningConfig
        from wetwire_github.serialize import to_dict

        config = SecretScanningConfig(enabled=True, push_protection=True)

        result = to_dict(config)
        assert result["enabled"] is True
        assert result["push-protection"] is True

    def test_serialize_with_single_pattern(self):
        """Secret scanning with custom pattern serializes correctly."""
        from wetwire_github.secret_scanning import (
            CustomPattern,
            SecretScanningConfig,
        )
        from wetwire_github.serialize import to_dict

        config = SecretScanningConfig(
            patterns=[
                CustomPattern(
                    name="API Key",
                    pattern=r"api_key_[a-zA-Z0-9]{32}",
                    secret_type="api_key",
                )
            ]
        )

        result = to_dict(config)
        assert len(result["patterns"]) == 1
        assert result["patterns"][0]["name"] == "API Key"
        assert result["patterns"][0]["pattern"] == r"api_key_[a-zA-Z0-9]{32}"
        assert result["patterns"][0]["secret-type"] == "api_key"

    def test_serialize_with_multiple_patterns(self):
        """Secret scanning with multiple patterns serializes correctly."""
        from wetwire_github.secret_scanning import (
            CustomPattern,
            SecretScanningConfig,
        )
        from wetwire_github.serialize import to_dict

        config = SecretScanningConfig(
            patterns=[
                CustomPattern(name="API Key", pattern=r"api_key_[a-zA-Z0-9]{32}"),
                CustomPattern(name="Secret Token", pattern=r"secret_[a-zA-Z0-9]{40}"),
            ]
        )

        result = to_dict(config)
        assert len(result["patterns"]) == 2
        assert result["patterns"][0]["name"] == "API Key"
        assert result["patterns"][1]["name"] == "Secret Token"

    def test_serialize_with_alert_settings(self):
        """Secret scanning with alert settings serializes correctly."""
        from wetwire_github.secret_scanning import (
            AlertSettings,
            SecretScanningConfig,
        )
        from wetwire_github.serialize import to_dict

        config = SecretScanningConfig(
            alert_settings=AlertSettings(
                push_protection=True,
                alert_notifications=False,
            )
        )

        result = to_dict(config)
        assert result["alert-settings"]["push-protection"] is True
        assert result["alert-settings"]["alert-notifications"] is False

    def test_serialize_omits_none_values(self):
        """Serialization omits None values."""
        from wetwire_github.secret_scanning import SecretScanningConfig
        from wetwire_github.serialize import to_dict

        config = SecretScanningConfig()

        result = to_dict(config)
        assert "alert-settings" not in result

    def test_serialize_omits_empty_lists(self):
        """Serialization omits empty lists."""
        from wetwire_github.secret_scanning import SecretScanningConfig
        from wetwire_github.serialize import to_dict

        config = SecretScanningConfig(patterns=[])

        result = to_dict(config)
        assert "patterns" not in result

    def test_serialize_preserves_false_values(self):
        """Serialization preserves False values."""
        from wetwire_github.secret_scanning import SecretScanningConfig
        from wetwire_github.serialize import to_dict

        config = SecretScanningConfig(enabled=False, push_protection=False)

        result = to_dict(config)
        assert result["enabled"] is False
        assert result["push-protection"] is False

    def test_serialize_full_example(self):
        """Full example serializes correctly."""
        from wetwire_github.secret_scanning import (
            AlertSettings,
            CustomPattern,
            SecretScanningConfig,
        )
        from wetwire_github.serialize import to_dict

        config = SecretScanningConfig(
            enabled=True,
            push_protection=True,
            patterns=[
                CustomPattern(
                    name="API Key",
                    pattern=r"api_key_[a-zA-Z0-9]{32}",
                    secret_type="api_key",
                ),
                CustomPattern(
                    name="Secret Token",
                    pattern=r"secret_[a-zA-Z0-9]{40}",
                ),
            ],
            alert_settings=AlertSettings(
                push_protection=True,
                alert_notifications=True,
            ),
        )

        result = to_dict(config)
        assert result["enabled"] is True
        assert result["push-protection"] is True
        assert len(result["patterns"]) == 2
        assert result["patterns"][0]["name"] == "API Key"
        assert result["patterns"][1]["name"] == "Secret Token"
        assert result["alert-settings"]["push-protection"] is True
        assert result["alert-settings"]["alert-notifications"] is True
