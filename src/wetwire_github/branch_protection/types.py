"""Branch Protection Rules configuration types.

Dataclasses for GitHub Branch Protection Rules configuration.
Based on the GitHub Branch Protection Rules API.
"""

from dataclasses import dataclass, field


@dataclass
class StatusCheck:
    """Required status checks configuration.

    Attributes:
        strict: Require branches to be up to date before merging
        contexts: List of required status check names
    """

    strict: bool = False
    contexts: list[str] = field(default_factory=list)


@dataclass
class RequiredReviewers:
    """Pull request review requirements configuration.

    Attributes:
        required_count: Number of required reviewers
        dismiss_stale_reviews: Dismiss reviews when new commits are pushed
        require_code_owner_reviews: Require review from code owners
        require_last_push_approval: Require approval from last pusher
        dismissal_restrictions: Users/teams who can dismiss reviews
        bypass_pull_request_allowances: Users/teams who can bypass PR requirements
    """

    required_count: int = 1
    dismiss_stale_reviews: bool | None = None
    require_code_owner_reviews: bool | None = None
    require_last_push_approval: bool | None = None
    dismissal_restrictions: list[str] = field(default_factory=list)
    bypass_pull_request_allowances: list[str] = field(default_factory=list)


@dataclass
class PushRestrictions:
    """Push access restrictions configuration.

    Attributes:
        users: List of users who can push
        teams: List of teams who can push
        apps: List of apps who can push
    """

    users: list[str] = field(default_factory=list)
    teams: list[str] = field(default_factory=list)
    apps: list[str] = field(default_factory=list)


@dataclass
class BranchProtectionRule:
    """Branch protection rule configuration.

    Attributes:
        pattern: Branch name pattern to protect
        require_status_checks: Required status checks configuration
        require_pull_request_reviews: Pull request review requirements
        restrictions: Push access restrictions
        enforce_admins: Enforce rules for administrators
        require_linear_history: Require linear commit history
        allow_force_pushes: Allow force pushes
        allow_deletions: Allow branch deletions
        required_conversation_resolution: Require conversation resolution
        lock_branch: Lock the branch (read-only)
        allow_fork_syncing: Allow fork syncing
    """

    pattern: str
    require_status_checks: StatusCheck | None = None
    require_pull_request_reviews: RequiredReviewers | None = None
    restrictions: PushRestrictions | None = None
    enforce_admins: bool | None = None
    require_linear_history: bool | None = None
    allow_force_pushes: bool | None = None
    allow_deletions: bool | None = None
    required_conversation_resolution: bool | None = None
    lock_branch: bool | None = None
    allow_fork_syncing: bool | None = None
