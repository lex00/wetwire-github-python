"""Self-hosted runner configuration types."""

from dataclasses import dataclass, field


@dataclass
class SelfHostedRunner:
    """Configuration for self-hosted GitHub Actions runners.

    Self-hosted runners allow you to run jobs on your own infrastructure
    with specific hardware, software, or security requirements.

    Example:
        runner = SelfHostedRunner(
            labels=["self-hosted", "linux", "x64", "gpu"],
            group="production-runners",
        )

        job = Job(
            runs_on=runner,
            steps=[Step(run="nvidia-smi")],
        )
    """

    labels: list[str] = field(default_factory=list)
    """Labels to match against runner capabilities."""

    group: str | None = None
    """Runner group name for organization-level or enterprise-level runner groups."""
