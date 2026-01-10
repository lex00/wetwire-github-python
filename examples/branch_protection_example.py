"""Example: Configuring branch protection rules with wetwire-github.

This example demonstrates how to define comprehensive branch protection rules
for different branch patterns in a production repository.
"""

from wetwire_github.branch_protection import (
    BranchProtectionRule,
    PushRestrictions,
    RequiredReviewers,
    StatusCheck,
)
from wetwire_github.serialize import to_yaml

# Example 1: Strict main branch protection for production
# This configuration enforces code review, status checks, and restricts pushes
main_branch_protection = BranchProtectionRule(
    pattern="main",
    require_status_checks=StatusCheck(
        strict=True,  # Require branch to be up-to-date before merging
        contexts=[
            "ci/build",
            "ci/test",
            "ci/lint",
            "security/dependency-scan",
            "security/codeql",
        ],
    ),
    require_pull_request_reviews=RequiredReviewers(
        required_count=2,  # Require 2 approvals
        dismiss_stale_reviews=True,  # Dismiss approvals on new commits
        require_code_owner_reviews=True,  # CODEOWNERS must approve
        require_last_push_approval=True,  # Last pusher cannot approve
        dismissal_restrictions=["security-team"],  # Only security can dismiss
    ),
    restrictions=PushRestrictions(
        teams=["core-maintainers"],
        apps=["github-actions", "dependabot"],
    ),
    enforce_admins=True,  # Rules apply to admins too
    require_linear_history=True,  # No merge commits
    allow_force_pushes=False,  # Prevent history rewriting
    allow_deletions=False,  # Prevent branch deletion
    required_conversation_resolution=True,  # All comments must be resolved
)


# Example 2: Release branch protection
# Less strict than main, but still requires review and tests
release_branch_protection = BranchProtectionRule(
    pattern="release/*",
    require_status_checks=StatusCheck(
        strict=True,
        contexts=["ci/build", "ci/test"],
    ),
    require_pull_request_reviews=RequiredReviewers(
        required_count=1,
        dismiss_stale_reviews=True,
    ),
    enforce_admins=False,  # Allow admin overrides for hotfixes
    allow_force_pushes=False,
    allow_deletions=False,
)


# Example 3: Development branch with minimal protection
# Allows more flexibility while still requiring basic CI
develop_branch_protection = BranchProtectionRule(
    pattern="develop",
    require_status_checks=StatusCheck(
        strict=False,  # Don't require up-to-date branch
        contexts=["ci/build", "ci/test"],
    ),
    require_pull_request_reviews=RequiredReviewers(
        required_count=1,
    ),
    allow_force_pushes=False,
    allow_deletions=False,
)


# Example 4: Feature branch protection
# Basic protection for all feature branches
feature_branch_protection = BranchProtectionRule(
    pattern="feature/*",
    require_status_checks=StatusCheck(
        strict=False,
        contexts=["ci/test"],
    ),
    allow_force_pushes=True,  # Allow rebasing feature branches
    allow_deletions=True,  # Allow cleanup after merge
)


# Example 5: Hotfix branch with expedited review
# Critical fixes with single reviewer but strict checks
hotfix_branch_protection = BranchProtectionRule(
    pattern="hotfix/*",
    require_status_checks=StatusCheck(
        strict=True,
        contexts=["ci/build", "ci/test", "security/scan"],
    ),
    require_pull_request_reviews=RequiredReviewers(
        required_count=1,
        require_code_owner_reviews=True,
        bypass_pull_request_allowances=["incident-responders"],
    ),
    allow_force_pushes=False,
    allow_deletions=True,
)


# Example 6: Locked archive branch
# Read-only branch for historical versions
archive_branch_protection = BranchProtectionRule(
    pattern="archive/*",
    lock_branch=True,  # Make completely read-only
    allow_fork_syncing=False,
)


# Print example configurations
if __name__ == "__main__":
    print("=== Main Branch Protection ===")
    print(to_yaml(main_branch_protection))
    print()

    print("=== Release Branch Protection ===")
    print(to_yaml(release_branch_protection))
    print()

    print("=== Feature Branch Protection ===")
    print(to_yaml(feature_branch_protection))
