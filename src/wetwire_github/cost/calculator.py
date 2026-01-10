"""Cost calculator for workflow definitions."""

import itertools
from typing import Any

from wetwire_github.workflow import Job, Workflow

from .types import CostEstimate, RunnerCost


class CostCalculator:
    """Calculate estimated costs from workflow definitions."""

    def __init__(self, runner_cost: RunnerCost | None = None):
        """Initialize calculator with runner costs.

        Args:
            runner_cost: Cost per minute for different runner types.
                        Defaults to RunnerCost() with standard GitHub pricing.
        """
        self.runner_cost = runner_cost or RunnerCost()

    def estimate(self, workflow: Workflow, default_timeout: int = 30) -> CostEstimate:
        """Estimate cost for a workflow.

        Args:
            workflow: Workflow definition to estimate
            default_timeout: Default timeout in minutes if job has no timeout_minutes

        Returns:
            CostEstimate with total cost and per-job breakdown
        """
        total_linux_minutes = 0.0
        total_windows_minutes = 0.0
        total_macos_minutes = 0.0
        job_estimates: dict[str, float] = {}

        for job_name, job in workflow.jobs.items():
            # Get timeout for this job
            timeout = job.timeout_minutes if job.timeout_minutes else default_timeout

            # Determine runner type(s) and calculate costs
            if job.strategy and job.strategy.matrix:
                # Matrix job with dynamic runner
                os_breakdown = self._calculate_matrix_os_breakdown(job)
                linux_runs = os_breakdown.get("linux", 0)
                windows_runs = os_breakdown.get("windows", 0)
                macos_runs = os_breakdown.get("macos", 0)

                linux_minutes = linux_runs * timeout
                windows_minutes = windows_runs * timeout
                macos_minutes = macos_runs * timeout
            else:
                # Single job
                runner_type = self._detect_runner_type(job.runs_on)
                linux_minutes = timeout if runner_type == "linux" else 0
                windows_minutes = timeout if runner_type == "windows" else 0
                macos_minutes = timeout if runner_type == "macos" else 0

            # Calculate cost for this job
            job_cost = (
                (linux_minutes * self.runner_cost.linux_per_minute)
                + (windows_minutes * self.runner_cost.windows_per_minute)
                + (macos_minutes * self.runner_cost.macos_per_minute)
            )

            total_linux_minutes += linux_minutes
            total_windows_minutes += windows_minutes
            total_macos_minutes += macos_minutes
            job_estimates[job_name] = job_cost

        total_cost = (
            (total_linux_minutes * self.runner_cost.linux_per_minute)
            + (total_windows_minutes * self.runner_cost.windows_per_minute)
            + (total_macos_minutes * self.runner_cost.macos_per_minute)
        )

        return CostEstimate(
            total_cost=total_cost,
            linux_minutes=total_linux_minutes,
            windows_minutes=total_windows_minutes,
            macos_minutes=total_macos_minutes,
            job_estimates=job_estimates,
        )

    def _detect_runner_type(self, runs_on: str | list[str] | Any) -> str:
        """Detect runner type from runs_on value.

        Args:
            runs_on: Runner specification (string or list)

        Returns:
            "linux", "windows", or "macos"
        """
        # Handle list of labels (e.g., ["self-hosted", "linux"])
        if isinstance(runs_on, list):
            runs_on_str = " ".join(str(x) for x in runs_on).lower()
        else:
            runs_on_str = str(runs_on).lower()

        # Detect OS type
        if "windows" in runs_on_str:
            return "windows"
        elif "macos" in runs_on_str:
            return "macos"
        else:
            # Default to Linux (includes ubuntu, self-hosted without OS, etc.)
            return "linux"

    def _calculate_matrix_multiplier(self, job: Job) -> int:
        """Calculate how many times a matrix job runs.

        Args:
            job: Job with potential matrix strategy

        Returns:
            Number of matrix combinations (1 if no matrix)
        """
        if not job.strategy or not job.strategy.matrix:
            return 1

        matrix = job.strategy.matrix

        # Calculate base combinations
        if not matrix.values:
            return 1

        base_count = 1
        for dimension_values in matrix.values.values():
            base_count *= len(dimension_values)

        # Subtract excludes
        exclude_count = len(matrix.exclude) if matrix.exclude else 0

        # Add includes
        include_count = len(matrix.include) if matrix.include else 0

        return base_count - exclude_count + include_count

    def _calculate_matrix_os_breakdown(self, job: Job) -> dict[str, int]:
        """Calculate OS breakdown for a matrix job.

        Args:
            job: Job with matrix strategy

        Returns:
            Dictionary with counts for each OS type: {"linux": 2, "windows": 1, ...}
        """
        if not job.strategy or not job.strategy.matrix:
            return {}

        matrix = job.strategy.matrix

        # Check if "os" is in the matrix
        if "os" not in matrix.values:
            # If no OS in matrix, use the job's runs_on
            runner_type = self._detect_runner_type(job.runs_on)
            multiplier = self._calculate_matrix_multiplier(job)
            return {runner_type: multiplier}

        # Generate all base combinations
        os_values = matrix.values["os"]
        other_dimensions = {k: v for k, v in matrix.values.items() if k != "os"}

        # Calculate base combinations
        os_counts: dict[str, int] = {}
        if other_dimensions:
            # Multi-dimensional matrix
            other_keys = list(other_dimensions.keys())
            other_values = [other_dimensions[k] for k in other_keys]
            other_combinations = list(itertools.product(*other_values))

            for os_val in os_values:
                for other_combo in other_combinations:
                    # Check if this combination is excluded
                    combo_dict = {"os": os_val}
                    combo_dict.update(dict(zip(other_keys, other_combo)))

                    if not self._is_excluded(combo_dict, matrix.exclude):
                        runner_type = self._detect_runner_type(os_val)
                        os_counts[runner_type] = os_counts.get(runner_type, 0) + 1
        else:
            # Single dimension (just OS)
            for os_val in os_values:
                combo_dict = {"os": os_val}
                if not self._is_excluded(combo_dict, matrix.exclude):
                    runner_type = self._detect_runner_type(os_val)
                    os_counts[runner_type] = os_counts.get(runner_type, 0) + 1

        # Add includes
        if matrix.include:
            for include_combo in matrix.include:
                if "os" in include_combo:
                    runner_type = self._detect_runner_type(include_combo["os"])
                    os_counts[runner_type] = os_counts.get(runner_type, 0) + 1

        return os_counts

    def _is_excluded(
        self, combo: dict[str, Any], excludes: list[dict[str, Any]] | None
    ) -> bool:
        """Check if a combination matches any exclude pattern.

        Args:
            combo: Combination to check
            excludes: List of exclude patterns

        Returns:
            True if combination should be excluded
        """
        if not excludes:
            return False

        for exclude in excludes:
            # Check if all keys in exclude match the combo
            if all(combo.get(k) == v for k, v in exclude.items()):
                return True

        return False
