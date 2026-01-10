"""Example: Configuring repository settings with wetwire-github.

This example demonstrates how to define complete repository settings
for different types of projects (open source, internal, documentation).
"""

from wetwire_github.repository_settings import (
    FeatureSettings,
    MergeSettings,
    PageSettings,
    RepositorySettings,
    SecuritySettings,
)
from wetwire_github.serialize import to_yaml

# Example 1: Open source project settings
# Public repository with full community features and security scanning
open_source_settings = RepositorySettings(
    name="awesome-library",
    description="A well-documented open source library with active community",
    homepage="https://awesome-library.dev",
    private=False,
    security=SecuritySettings(
        enable_vulnerability_alerts=True,
        enable_automated_security_fixes=True,
        enable_secret_scanning=True,
        enable_secret_scanning_push_protection=True,
        enable_dependabot_alerts=True,
    ),
    merge=MergeSettings(
        allow_squash_merge=True,  # Clean commit history
        allow_merge_commit=False,  # Avoid merge commits
        allow_rebase_merge=True,  # Allow for linear history
        delete_branch_on_merge=True,  # Auto cleanup
        allow_auto_merge=True,  # Streamline contributions
    ),
    features=FeatureSettings(
        has_issues=True,  # Bug reports and feature requests
        has_wiki=True,  # Community documentation
        has_discussions=True,  # Community forum
        has_projects=True,  # Project tracking
    ),
    pages=PageSettings(
        enabled=True,
        branch="main",
        path="/docs",
        cname="docs.awesome-library.dev",
        https_enforced=True,
    ),
)


# Example 2: Internal production service
# Private repository with strict security but minimal extra features
production_service_settings = RepositorySettings(
    name="payment-service",
    description="Internal payment processing microservice",
    homepage="https://internal.example.com/docs/payment-service",
    private=True,
    security=SecuritySettings(
        enable_vulnerability_alerts=True,
        enable_automated_security_fixes=True,
        enable_secret_scanning=True,
        enable_secret_scanning_push_protection=True,
        enable_dependabot_alerts=True,
    ),
    merge=MergeSettings(
        allow_squash_merge=True,  # Squash only for clean history
        allow_merge_commit=False,
        allow_rebase_merge=False,
        delete_branch_on_merge=True,
        allow_auto_merge=False,  # Require manual merge for control
    ),
    features=FeatureSettings(
        has_issues=True,  # Internal issue tracking
        has_wiki=False,  # Use internal docs system
        has_discussions=False,  # Use Slack/Teams
        has_projects=False,  # Use Jira/Linear
    ),
)


# Example 3: Documentation repository
# Public docs site with minimal features needed
documentation_settings = RepositorySettings(
    name="company-docs",
    description="Public documentation for our products",
    homepage="https://docs.example.com",
    private=False,
    security=SecuritySettings(
        enable_vulnerability_alerts=True,
        enable_automated_security_fixes=True,
        enable_secret_scanning=True,  # Even docs can leak secrets
        enable_secret_scanning_push_protection=True,
        enable_dependabot_alerts=True,
    ),
    merge=MergeSettings(
        allow_squash_merge=True,
        allow_merge_commit=True,  # Allow for content PRs
        allow_rebase_merge=True,
        delete_branch_on_merge=True,
        allow_auto_merge=True,  # Fast turnaround for typos
    ),
    features=FeatureSettings(
        has_issues=True,  # Feedback on docs
        has_wiki=False,  # Docs are the content
        has_discussions=True,  # Q&A forum
        has_projects=False,
    ),
    pages=PageSettings(
        enabled=True,
        branch="main",
        path="/",  # Root of repo is the docs
        cname="docs.example.com",
        https_enforced=True,
    ),
)


# Example 4: Experimental/prototype repository
# Private with minimal constraints for rapid iteration
prototype_settings = RepositorySettings(
    name="ml-experiment-2024",
    description="Machine learning prototype - experimental",
    private=True,
    security=SecuritySettings(
        enable_vulnerability_alerts=True,
        enable_automated_security_fixes=False,  # Don't interrupt experiments
        enable_secret_scanning=True,
        enable_secret_scanning_push_protection=False,  # Allow flexibility
        enable_dependabot_alerts=True,
    ),
    merge=MergeSettings(
        allow_squash_merge=True,
        allow_merge_commit=True,
        allow_rebase_merge=True,
        delete_branch_on_merge=False,  # Keep experiment branches
        allow_auto_merge=True,
    ),
    features=FeatureSettings(
        has_issues=True,
        has_wiki=True,  # Document findings
        has_discussions=False,
        has_projects=False,
    ),
)


# Example 5: Archived/legacy repository
# Read-only repository for reference only
archived_settings = RepositorySettings(
    name="legacy-api-v1",
    description="[ARCHIVED] Legacy API v1 - no longer maintained",
    homepage="https://docs.example.com/legacy-api-v1",
    private=False,
    security=SecuritySettings(
        enable_vulnerability_alerts=True,  # Still want to know about vulns
        enable_automated_security_fixes=False,  # Don't auto-fix
        enable_secret_scanning=True,
        enable_secret_scanning_push_protection=False,  # No pushes anyway
        enable_dependabot_alerts=True,
    ),
    merge=MergeSettings(
        allow_squash_merge=False,  # No merging
        allow_merge_commit=False,
        allow_rebase_merge=False,
        delete_branch_on_merge=False,
        allow_auto_merge=False,
    ),
    features=FeatureSettings(
        has_issues=False,  # Closed
        has_wiki=True,  # Keep docs readable
        has_discussions=False,  # Closed
        has_projects=False,
    ),
)


# Print example configurations
if __name__ == "__main__":
    print("=== Open Source Project Settings ===")
    print(to_yaml(open_source_settings))
    print()

    print("=== Production Service Settings ===")
    print(to_yaml(production_service_settings))
    print()

    print("=== Documentation Repository Settings ===")
    print(to_yaml(documentation_settings))
