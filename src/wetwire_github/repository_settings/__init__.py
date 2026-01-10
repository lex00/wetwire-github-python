"""Repository Settings configuration types.

Type-safe declarations for GitHub Repository Settings configuration.
"""

from wetwire_github.repository_settings.types import (
    FeatureSettings,
    MergeSettings,
    PageSettings,
    RepositorySettings,
    SecuritySettings,
)

__all__ = [
    "RepositorySettings",
    "SecuritySettings",
    "MergeSettings",
    "FeatureSettings",
    "PageSettings",
]
