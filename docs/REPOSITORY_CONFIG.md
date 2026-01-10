# Repository Configuration

Type-safe configuration for GitHub repository settings, branch protection rules, and secret scanning.

## Overview

wetwire-github provides three modules for managing repository configuration as code:

| Module | Description |
|--------|-------------|
| `repository_settings` | Repository visibility, features, merge settings, security, and GitHub Pages |
| `branch_protection` | Branch protection rules with status checks, reviews, and push restrictions |
| `secret_scanning` | Secret scanning configuration with custom patterns |

These modules provide:

- **Typed dataclasses** for all configuration options
- **IDE autocomplete** for property names and types
- **Compile-time validation** instead of runtime YAML errors
- **Serialization** to GitHub API-compatible formats

---

## Repository Settings

Configure repository-level settings including visibility, features, merge behavior, security, and GitHub Pages.

### Quick Start

```python
from wetwire_github.repository_settings import (
    RepositorySettings,
    SecuritySettings,
    MergeSettings,
    FeatureSettings,
    PageSettings,
)

settings = RepositorySettings(
    name="my-project",
    description="A well-configured repository",
    private=False,
    security=SecuritySettings(
        enable_vulnerability_alerts=True,
        enable_secret_scanning=True,
    ),
    merge=MergeSettings(
        allow_squash_merge=True,
        delete_branch_on_merge=True,
    ),
    features=FeatureSettings(
        has_issues=True,
        has_discussions=True,
    ),
)
```

### RepositorySettings

The main configuration class for repository settings.

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | Required | Repository name |
| `description` | `str \| None` | `None` | Repository description |
| `homepage` | `str \| None` | `None` | Repository homepage URL |
| `private` | `bool` | `False` | Repository visibility |
| `security` | `SecuritySettings \| None` | `None` | Security settings |
| `merge` | `MergeSettings \| None` | `None` | Merge behavior settings |
| `features` | `FeatureSettings \| None` | `None` | Feature toggles |
| `pages` | `PageSettings \| None` | `None` | GitHub Pages settings |

### SecuritySettings

Configure security features for the repository.

```python
from wetwire_github.repository_settings import SecuritySettings

security = SecuritySettings(
    enable_vulnerability_alerts=True,
    enable_automated_security_fixes=True,
    enable_secret_scanning=True,
    enable_secret_scanning_push_protection=True,
    enable_dependabot_alerts=True,
)
```

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_vulnerability_alerts` | `bool` | `False` | Enable vulnerability alerts |
| `enable_automated_security_fixes` | `bool` | `False` | Enable Dependabot security updates |
| `enable_secret_scanning` | `bool` | `False` | Enable secret scanning |
| `enable_secret_scanning_push_protection` | `bool` | `False` | Block commits containing secrets |
| `enable_dependabot_alerts` | `bool` | `False` | Enable Dependabot alerts |

### MergeSettings

Configure how pull requests can be merged.

```python
from wetwire_github.repository_settings import MergeSettings

merge = MergeSettings(
    allow_squash_merge=True,
    allow_merge_commit=False,
    allow_rebase_merge=False,
    delete_branch_on_merge=True,
    allow_auto_merge=True,
)
```

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `allow_squash_merge` | `bool` | `True` | Allow squash merging |
| `allow_merge_commit` | `bool` | `True` | Allow merge commits |
| `allow_rebase_merge` | `bool` | `True` | Allow rebase merging |
| `delete_branch_on_merge` | `bool` | `False` | Auto-delete head branches |
| `allow_auto_merge` | `bool` | `False` | Allow auto-merge |

### FeatureSettings

Enable or disable repository features.

```python
from wetwire_github.repository_settings import FeatureSettings

features = FeatureSettings(
    has_issues=True,
    has_wiki=True,
    has_discussions=True,
    has_projects=True,
)
```

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `has_issues` | `bool` | `True` | Enable Issues |
| `has_wiki` | `bool` | `False` | Enable Wiki |
| `has_discussions` | `bool` | `False` | Enable Discussions |
| `has_projects` | `bool` | `False` | Enable Projects |

### PageSettings

Configure GitHub Pages.

```python
from wetwire_github.repository_settings import PageSettings

pages = PageSettings(
    enabled=True,
    branch="main",
    path="/docs",
    cname="docs.example.com",
    https_enforced=True,
)
```

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `enabled` | `bool` | `False` | Enable GitHub Pages |
| `branch` | `str \| None` | `None` | Branch to deploy from |
| `path` | `str \| None` | `None` | Path within the branch |
| `cname` | `str \| None` | `None` | Custom domain |
| `https_enforced` | `bool` | `False` | Enforce HTTPS |

---

## Branch Protection Rules

Configure branch protection rules to enforce code review requirements, status checks, and push restrictions.

### Quick Start

```python
from wetwire_github.branch_protection import (
    BranchProtectionRule,
    StatusCheck,
    RequiredReviewers,
    PushRestrictions,
)

main_branch = BranchProtectionRule(
    pattern="main",
    require_status_checks=StatusCheck(
        strict=True,
        contexts=["ci/tests", "ci/lint"],
    ),
    require_pull_request_reviews=RequiredReviewers(
        required_count=2,
        dismiss_stale_reviews=True,
        require_code_owner_reviews=True,
    ),
    enforce_admins=True,
    require_linear_history=True,
)
```

### BranchProtectionRule

The main configuration class for branch protection.

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `pattern` | `str` | Required | Branch name or pattern (e.g., `main`, `release/*`) |
| `require_status_checks` | `StatusCheck \| None` | `None` | Required status checks |
| `require_pull_request_reviews` | `RequiredReviewers \| None` | `None` | PR review requirements |
| `restrictions` | `PushRestrictions \| None` | `None` | Push access restrictions |
| `enforce_admins` | `bool \| None` | `None` | Enforce rules for admins |
| `require_linear_history` | `bool \| None` | `None` | Require linear commit history |
| `allow_force_pushes` | `bool \| None` | `None` | Allow force pushes |
| `allow_deletions` | `bool \| None` | `None` | Allow branch deletion |
| `required_conversation_resolution` | `bool \| None` | `None` | Require resolved conversations |
| `lock_branch` | `bool \| None` | `None` | Lock branch (read-only) |
| `allow_fork_syncing` | `bool \| None` | `None` | Allow fork syncing |

### StatusCheck

Configure required status checks before merging.

```python
from wetwire_github.branch_protection import StatusCheck

checks = StatusCheck(
    strict=True,  # Require branch to be up-to-date
    contexts=["ci/tests", "ci/lint", "ci/build"],
)
```

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `strict` | `bool` | `False` | Require branches to be up-to-date |
| `contexts` | `list[str]` | `[]` | Required status check names |

### RequiredReviewers

Configure pull request review requirements.

```python
from wetwire_github.branch_protection import RequiredReviewers

reviewers = RequiredReviewers(
    required_count=2,
    dismiss_stale_reviews=True,
    require_code_owner_reviews=True,
    require_last_push_approval=True,
    dismissal_restrictions=["security-team"],
    bypass_pull_request_allowances=["release-bot"],
)
```

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `required_count` | `int` | `1` | Number of required approvals |
| `dismiss_stale_reviews` | `bool \| None` | `None` | Dismiss reviews on new commits |
| `require_code_owner_reviews` | `bool \| None` | `None` | Require CODEOWNERS review |
| `require_last_push_approval` | `bool \| None` | `None` | Require approval after last push |
| `dismissal_restrictions` | `list[str]` | `[]` | Users/teams who can dismiss |
| `bypass_pull_request_allowances` | `list[str]` | `[]` | Users/teams who can bypass |

### PushRestrictions

Restrict who can push to the protected branch.

```python
from wetwire_github.branch_protection import PushRestrictions

restrictions = PushRestrictions(
    users=["admin-user"],
    teams=["core-maintainers", "security-team"],
    apps=["github-actions"],
)
```

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `users` | `list[str]` | `[]` | Users who can push |
| `teams` | `list[str]` | `[]` | Teams who can push |
| `apps` | `list[str]` | `[]` | Apps who can push |

### Branch Pattern Examples

```python
from wetwire_github.branch_protection import BranchProtectionRule

# Protect main branch
main = BranchProtectionRule(pattern="main")

# Protect all release branches
release = BranchProtectionRule(pattern="release/*")

# Protect versioned branches
versioned = BranchProtectionRule(pattern="v[0-9]*")

# Protect feature branches
feature = BranchProtectionRule(pattern="feature/*")
```

---

## Secret Scanning

Configure secret scanning with custom patterns to detect organization-specific secrets.

### Quick Start

```python
from wetwire_github.secret_scanning import (
    SecretScanningConfig,
    CustomPattern,
    AlertSettings,
)

config = SecretScanningConfig(
    enabled=True,
    push_protection=True,
    patterns=[
        CustomPattern(
            name="Internal API Key",
            pattern=r"ACME_API_[a-zA-Z0-9]{32}",
            secret_type="acme_api_key",
        ),
    ],
    alert_settings=AlertSettings(
        push_protection=True,
        alert_notifications=True,
    ),
)
```

### SecretScanningConfig

The main configuration class for secret scanning.

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `enabled` | `bool` | `True` | Enable secret scanning |
| `push_protection` | `bool` | `False` | Block pushes containing secrets |
| `patterns` | `list[CustomPattern]` | `[]` | Custom secret patterns |
| `alert_settings` | `AlertSettings \| None` | `None` | Alert configuration |

### CustomPattern

Define custom patterns to detect organization-specific secrets.

```python
from wetwire_github.secret_scanning import CustomPattern

patterns = [
    # API keys
    CustomPattern(
        name="Internal API Key",
        pattern=r"ACME_API_[a-zA-Z0-9]{32}",
        secret_type="acme_api_key",
    ),
    # Database connection strings
    CustomPattern(
        name="Database URL",
        pattern=r"postgres://[^:]+:[^@]+@[^/]+/\w+",
        secret_type="database_url",
    ),
    # JWT secrets
    CustomPattern(
        name="JWT Secret",
        pattern=r"JWT_SECRET=[A-Za-z0-9+/=]{32,}",
        secret_type="jwt_secret",
    ),
]
```

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | Required | Display name for the pattern |
| `pattern` | `str` | Required | Regular expression pattern |
| `secret_type` | `str \| None` | `None` | Type identifier for categorization |

### AlertSettings

Configure alert notifications and push protection behavior.

```python
from wetwire_github.secret_scanning import AlertSettings

alerts = AlertSettings(
    push_protection=True,
    alert_notifications=True,
)
```

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `push_protection` | `bool` | `False` | Enable push protection |
| `alert_notifications` | `bool` | `True` | Send alert notifications |

### Common Secret Patterns

Here are some common patterns for detecting secrets:

```python
from wetwire_github.secret_scanning import CustomPattern

# AWS Access Key
aws_access_key = CustomPattern(
    name="AWS Access Key",
    pattern=r"AKIA[0-9A-Z]{16}",
    secret_type="aws_access_key",
)

# AWS Secret Key
aws_secret_key = CustomPattern(
    name="AWS Secret Key",
    pattern=r"[A-Za-z0-9/+=]{40}",
    secret_type="aws_secret_key",
)

# Slack Bot Token
slack_token = CustomPattern(
    name="Slack Bot Token",
    pattern=r"xoxb-[0-9]{11}-[0-9]{11}-[a-zA-Z0-9]{24}",
    secret_type="slack_bot_token",
)

# Generic API Key pattern
generic_api_key = CustomPattern(
    name="Generic API Key",
    pattern=r"api[_-]?key[_-]?[=:]\s*['\"]?[a-zA-Z0-9]{20,}['\"]?",
    secret_type="generic_api_key",
)

# Password in config
password_in_config = CustomPattern(
    name="Password in Config",
    pattern=r"password[=:]\s*['\"][^'\"]+['\"]",
    secret_type="password",
)
```

---

## Serialization

All configuration objects can be serialized to dictionaries and YAML for use with the GitHub API.

### To Dictionary

```python
from wetwire_github.repository_settings import RepositorySettings, MergeSettings
from wetwire_github.serialize import to_dict

settings = RepositorySettings(
    name="my-repo",
    merge=MergeSettings(
        allow_squash_merge=True,
        delete_branch_on_merge=True,
    ),
)

result = to_dict(settings)
# {
#     "name": "my-repo",
#     "merge": {
#         "allow-squash-merge": True,
#         "delete-branch-on-merge": True
#     }
# }
```

### To YAML

```python
from wetwire_github.branch_protection import BranchProtectionRule, StatusCheck
from wetwire_github.serialize import to_yaml

rule = BranchProtectionRule(
    pattern="main",
    require_status_checks=StatusCheck(
        strict=True,
        contexts=["ci/tests"],
    ),
)

print(to_yaml(rule))
# pattern: main
# require-status-checks:
#   strict: true
#   contexts:
#     - ci/tests
```

---

## Complete Example

Here is a complete example showing all three modules working together to configure a production-ready repository:

```python
"""Complete repository configuration example."""

from wetwire_github.repository_settings import (
    RepositorySettings,
    SecuritySettings,
    MergeSettings,
    FeatureSettings,
    PageSettings,
)
from wetwire_github.branch_protection import (
    BranchProtectionRule,
    StatusCheck,
    RequiredReviewers,
    PushRestrictions,
)
from wetwire_github.secret_scanning import (
    SecretScanningConfig,
    CustomPattern,
    AlertSettings,
)

# Repository settings
repo_settings = RepositorySettings(
    name="production-service",
    description="Production microservice with comprehensive security",
    homepage="https://docs.example.com/production-service",
    private=True,
    security=SecuritySettings(
        enable_vulnerability_alerts=True,
        enable_automated_security_fixes=True,
        enable_secret_scanning=True,
        enable_secret_scanning_push_protection=True,
        enable_dependabot_alerts=True,
    ),
    merge=MergeSettings(
        allow_squash_merge=True,
        allow_merge_commit=False,
        allow_rebase_merge=False,
        delete_branch_on_merge=True,
        allow_auto_merge=True,
    ),
    features=FeatureSettings(
        has_issues=True,
        has_wiki=False,
        has_discussions=True,
        has_projects=True,
    ),
    pages=PageSettings(
        enabled=True,
        branch="main",
        path="/docs",
        https_enforced=True,
    ),
)

# Main branch protection
main_protection = BranchProtectionRule(
    pattern="main",
    require_status_checks=StatusCheck(
        strict=True,
        contexts=["ci/build", "ci/test", "ci/lint", "security/scan"],
    ),
    require_pull_request_reviews=RequiredReviewers(
        required_count=2,
        dismiss_stale_reviews=True,
        require_code_owner_reviews=True,
        require_last_push_approval=True,
    ),
    restrictions=PushRestrictions(
        teams=["core-maintainers"],
        apps=["github-actions"],
    ),
    enforce_admins=True,
    require_linear_history=True,
    allow_force_pushes=False,
    allow_deletions=False,
    required_conversation_resolution=True,
)

# Release branch protection (less strict)
release_protection = BranchProtectionRule(
    pattern="release/*",
    require_status_checks=StatusCheck(
        strict=True,
        contexts=["ci/build", "ci/test"],
    ),
    require_pull_request_reviews=RequiredReviewers(
        required_count=1,
        dismiss_stale_reviews=True,
    ),
    allow_force_pushes=False,
    allow_deletions=False,
)

# Secret scanning configuration
secret_scanning = SecretScanningConfig(
    enabled=True,
    push_protection=True,
    patterns=[
        CustomPattern(
            name="Internal API Key",
            pattern=r"PROD_API_[a-zA-Z0-9]{32}",
            secret_type="internal_api_key",
        ),
        CustomPattern(
            name="Service Account Token",
            pattern=r"svc_[a-zA-Z0-9]{40}",
            secret_type="service_token",
        ),
        CustomPattern(
            name="Database Connection String",
            pattern=r"postgres://[^:]+:[^@]+@prod[^/]*/\w+",
            secret_type="database_url",
        ),
    ],
    alert_settings=AlertSettings(
        push_protection=True,
        alert_notifications=True,
    ),
)
```

---

## See Also

- [Expression Contexts](EXPRESSIONS.md) - Type-safe expression builders
- [CLI Reference](CLI.md) - Command-line interface documentation
- [GitHub Repository Settings API](https://docs.github.com/en/rest/repos/repos) - Official API documentation
- [GitHub Branch Protection API](https://docs.github.com/en/rest/branches/branch-protection) - Official API documentation
- [GitHub Secret Scanning API](https://docs.github.com/en/rest/secret-scanning) - Official API documentation
