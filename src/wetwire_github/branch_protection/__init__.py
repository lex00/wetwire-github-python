"""Branch Protection Rules configuration types.

Type-safe declarations for GitHub Branch Protection Rules configuration.
"""

from wetwire_github.branch_protection.types import (
    BranchProtectionRule,
    PushRestrictions,
    RequiredReviewers,
    StatusCheck,
)

__all__ = [
    "BranchProtectionRule",
    "PushRestrictions",
    "RequiredReviewers",
    "StatusCheck",
]
