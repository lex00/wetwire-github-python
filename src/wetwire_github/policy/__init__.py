"""Workflow policy engine for organization-level rules.

This module provides a policy engine for enforcing organization-level
rules on GitHub Actions workflows. It includes built-in policies and
allows custom policy creation.

Example:
    >>> from wetwire_github.policy import (
    ...     PolicyEngine,
    ...     RequireCheckout,
    ...     RequireTimeouts,
    ...     LimitJobCount,
    ... )
    >>> from wetwire_github.workflow import Workflow
    >>>
    >>> # Define policies
    >>> policies = [
    ...     RequireCheckout(),
    ...     RequireTimeouts(),
    ...     LimitJobCount(max_jobs=5),
    ... ]
    >>>
    >>> # Evaluate workflow
    >>> engine = PolicyEngine(policies=policies)
    >>> results = engine.evaluate(workflow)
    >>>
    >>> # Check results
    >>> for result in results:
    ...     if not result.passed:
    ...         print(f"FAIL: {result.policy_name}: {result.message}")
"""

from .builtin import (
    LimitJobCount,
    NoHardcodedSecrets,
    PinActions,
    RequireApproval,
    RequireCheckout,
    RequireTimeouts,
)
from .engine import PolicyEngine
from .types import Policy, PolicyResult

__all__ = [
    # Core types
    "Policy",
    "PolicyResult",
    "PolicyEngine",
    # Built-in policies
    "RequireCheckout",
    "RequireTimeouts",
    "NoHardcodedSecrets",
    "RequireApproval",
    "PinActions",
    "LimitJobCount",
]
