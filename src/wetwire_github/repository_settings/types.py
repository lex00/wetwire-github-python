"""Repository Settings configuration types.

Dataclasses for GitHub Repository Settings configuration.
Based on the GitHub Repository Settings API.
"""

from dataclasses import dataclass


@dataclass
class SecuritySettings:
    """Security settings configuration.

    Attributes:
        enable_vulnerability_alerts: Enable vulnerability alerts
        enable_automated_security_fixes: Enable automated security fixes (Dependabot security updates)
        enable_secret_scanning: Enable secret scanning
        enable_secret_scanning_push_protection: Enable secret scanning push protection
        enable_dependabot_alerts: Enable Dependabot alerts
    """

    enable_vulnerability_alerts: bool = False
    enable_automated_security_fixes: bool = False
    enable_secret_scanning: bool = False
    enable_secret_scanning_push_protection: bool = False
    enable_dependabot_alerts: bool = False


@dataclass
class MergeSettings:
    """Merge settings configuration.

    Attributes:
        allow_squash_merge: Allow squash merge
        allow_merge_commit: Allow merge commit
        allow_rebase_merge: Allow rebase merge
        delete_branch_on_merge: Delete branch on merge
        allow_auto_merge: Allow auto-merge
    """

    allow_squash_merge: bool = True
    allow_merge_commit: bool = True
    allow_rebase_merge: bool = True
    delete_branch_on_merge: bool = False
    allow_auto_merge: bool = False


@dataclass
class FeatureSettings:
    """Feature settings configuration.

    Attributes:
        has_issues: Enable issues
        has_wiki: Enable wiki
        has_discussions: Enable discussions
        has_projects: Enable projects
    """

    has_issues: bool = True
    has_wiki: bool = False
    has_discussions: bool = False
    has_projects: bool = False


@dataclass
class PageSettings:
    """GitHub Pages settings configuration.

    Attributes:
        enabled: Enable GitHub Pages
        branch: Branch to use for GitHub Pages
        path: Path to use for GitHub Pages
        cname: Custom domain for GitHub Pages
        https_enforced: Enforce HTTPS for GitHub Pages
    """

    enabled: bool = False
    branch: str | None = None
    path: str | None = None
    cname: str | None = None
    https_enforced: bool = False


@dataclass
class RepositorySettings:
    """Repository settings configuration.

    Attributes:
        name: Repository name
        description: Repository description
        homepage: Repository homepage URL
        private: Repository visibility (True for private, False for public)
        security: Security settings
        merge: Merge settings
        features: Feature settings
        pages: GitHub Pages settings
    """

    name: str
    description: str | None = None
    homepage: str | None = None
    private: bool = False
    security: SecuritySettings | None = None
    merge: MergeSettings | None = None
    features: FeatureSettings | None = None
    pages: PageSettings | None = None
