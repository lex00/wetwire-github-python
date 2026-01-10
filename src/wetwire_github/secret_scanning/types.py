"""Secret Scanning configuration types.

Dataclasses for GitHub Secret Scanning configuration.
Based on the GitHub Secret Scanning API.
"""

from dataclasses import dataclass, field


@dataclass
class CustomPattern:
    """Custom secret pattern configuration.

    Attributes:
        name: Display name for the custom pattern
        pattern: Regular expression pattern to match secrets
        secret_type: Optional type identifier for the secret
    """

    name: str
    pattern: str
    secret_type: str | None = None


@dataclass
class AlertSettings:
    """Secret scanning alert settings configuration.

    Attributes:
        push_protection: Enable push protection to block commits containing secrets
        alert_notifications: Enable notifications for secret scanning alerts
    """

    push_protection: bool = False
    alert_notifications: bool = True


@dataclass
class SecretScanningConfig:
    """Secret scanning configuration.

    Attributes:
        enabled: Enable secret scanning for the repository
        push_protection: Enable push protection (can also be configured via alert_settings)
        patterns: List of custom secret patterns to scan for
        alert_settings: Alert notification and protection settings
    """

    enabled: bool = True
    push_protection: bool = False
    patterns: list[CustomPattern] = field(default_factory=list)
    alert_settings: AlertSettings | None = None
