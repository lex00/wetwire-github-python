"""Policy engine for evaluating workflows against policies."""

from wetwire_github.workflow import Workflow

from .types import Policy, PolicyResult


class PolicyEngine:
    """Engine for evaluating workflows against a set of policies.

    Example:
        >>> from wetwire_github.policy import PolicyEngine, RequireCheckout
        >>> engine = PolicyEngine(policies=[RequireCheckout()])
        >>> results = engine.evaluate(workflow)
        >>> for result in results:
        ...     if not result.passed:
        ...         print(f"{result.policy_name}: {result.message}")
    """

    def __init__(self, policies: list[Policy]):
        """Initialize the policy engine.

        Args:
            policies: List of policies to evaluate
        """
        self.policies = policies

    def evaluate(self, workflow: Workflow) -> list[PolicyResult]:
        """Evaluate a workflow against all policies.

        Args:
            workflow: The workflow to evaluate

        Returns:
            List of policy results, one for each policy
        """
        return [policy.evaluate(workflow) for policy in self.policies]

    def fix_all(self, workflow: Workflow) -> Workflow:
        """Apply all fixable policies to make workflow compliant.

        Iterates through all policies and applies their fix methods.
        Policies without auto-fix capability will return the workflow unchanged.

        Args:
            workflow: The workflow to fix

        Returns:
            A new Workflow with all fixable policies applied
        """
        result = workflow
        for policy in self.policies:
            result = policy.fix(result)
        return result
