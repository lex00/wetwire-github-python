"""Cost estimation types."""

from dataclasses import dataclass, field


@dataclass
class RunnerCost:
    """Cost per minute for different runner types.

    Default values reflect GitHub Actions pricing as of 2026:
    - Linux: $0.008/minute
    - Windows: $0.016/minute
    - macOS: $0.08/minute
    """

    linux_per_minute: float = 0.008
    windows_per_minute: float = 0.016
    macos_per_minute: float = 0.08


@dataclass
class CostEstimate:
    """Estimated cost for a workflow execution.

    Attributes:
        total_cost: Total estimated cost in USD
        linux_minutes: Total minutes on Linux runners
        windows_minutes: Total minutes on Windows runners
        macos_minutes: Total minutes on macOS runners
        job_estimates: Per-job cost breakdown (job name -> cost)
    """

    total_cost: float
    linux_minutes: float = 0
    windows_minutes: float = 0
    macos_minutes: float = 0
    job_estimates: dict[str, float] = field(default_factory=dict)
