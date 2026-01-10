"""Core types for workflow policy engine."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from wetwire_github.workflow import Workflow


@dataclass
class PolicyResult:
    """Result of policy evaluation."""

    policy_name: str
    """Name of the policy that was evaluated."""

    passed: bool
    """Whether the workflow passed the policy check."""

    message: str = ""
    """Optional message with details about the result."""


class Policy(ABC):
    """Base class for workflow policies.

    A policy defines a rule that workflows must comply with.
    Subclasses implement the evaluate method to check compliance.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the policy name."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a description of what the policy checks."""
        ...

    @abstractmethod
    def evaluate(self, workflow: Workflow) -> PolicyResult:
        """Evaluate a workflow against this policy.

        Args:
            workflow: The workflow to evaluate

        Returns:
            PolicyResult with pass/fail status and optional message
        """
        ...
