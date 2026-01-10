"""Workflow cost estimation module.

Provides tools for estimating GitHub Actions workflow execution costs
based on runner types, job timeouts, and matrix configurations.

Example:
    >>> from wetwire_github.cost import CostCalculator, RunnerCost
    >>> from wetwire_github.workflow import Workflow, Job
    >>>
    >>> workflow = Workflow(
    ...     name="CI",
    ...     jobs={"build": Job(runs_on="ubuntu-latest", timeout_minutes=10)}
    ... )
    >>> calculator = CostCalculator()
    >>> estimate = calculator.estimate(workflow)
    >>> print(f"Estimated cost: ${estimate.total_cost:.2f}")
"""

from .calculator import CostCalculator
from .types import CostEstimate, RunnerCost

__all__ = [
    "CostCalculator",
    "CostEstimate",
    "RunnerCost",
]
