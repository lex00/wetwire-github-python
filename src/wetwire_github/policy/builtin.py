"""Built-in policy implementations for workflow validation."""

import re

from wetwire_github.workflow import Workflow

from .types import Policy, PolicyResult


class RequireCheckout(Policy):
    """Policy requiring all jobs to use actions/checkout.

    This ensures that jobs have access to the repository code.
    """

    @property
    def name(self) -> str:
        """Return the policy name."""
        return "RequireCheckout"

    @property
    def description(self) -> str:
        """Return a description of what the policy checks."""
        return "All jobs must use actions/checkout action"

    def evaluate(self, workflow: Workflow) -> PolicyResult:
        """Evaluate workflow for checkout action usage.

        Args:
            workflow: The workflow to evaluate

        Returns:
            PolicyResult indicating pass/fail
        """
        if not workflow.jobs:
            return PolicyResult(
                policy_name=self.name,
                passed=True,
                message="No jobs in workflow",
            )

        missing_checkout = []
        for job_id, job in workflow.jobs.items():
            has_checkout = any(
                step.uses and "checkout" in step.uses for step in job.steps
            )
            if not has_checkout:
                missing_checkout.append(job_id)

        if missing_checkout:
            return PolicyResult(
                policy_name=self.name,
                passed=False,
                message=f"Jobs missing checkout action: {', '.join(missing_checkout)}",
            )

        return PolicyResult(
            policy_name=self.name,
            passed=True,
            message="All jobs use checkout action",
        )


class RequireTimeouts(Policy):
    """Policy requiring all jobs to have timeout_minutes set.

    This prevents jobs from running indefinitely.
    """

    @property
    def name(self) -> str:
        """Return the policy name."""
        return "RequireTimeouts"

    @property
    def description(self) -> str:
        """Return a description of what the policy checks."""
        return "All jobs should have timeout_minutes set"

    def evaluate(self, workflow: Workflow) -> PolicyResult:
        """Evaluate workflow for timeout configuration.

        Args:
            workflow: The workflow to evaluate

        Returns:
            PolicyResult indicating pass/fail
        """
        if not workflow.jobs:
            return PolicyResult(
                policy_name=self.name,
                passed=True,
                message="No jobs in workflow",
            )

        missing_timeout = []
        for job_id, job in workflow.jobs.items():
            if job.timeout_minutes is None:
                missing_timeout.append(job_id)

        if missing_timeout:
            return PolicyResult(
                policy_name=self.name,
                passed=False,
                message=f"Jobs missing timeout_minutes: {', '.join(missing_timeout)}",
            )

        return PolicyResult(
            policy_name=self.name,
            passed=True,
            message="All jobs have timeout_minutes set",
        )


class NoHardcodedSecrets(Policy):
    """Policy preventing hardcoded secrets in run commands.

    This checks for common secret patterns like TOKEN, PASSWORD, API_KEY.
    """

    # Patterns to detect potential hardcoded secrets
    SECRET_PATTERNS = [
        r"\bTOKEN\b",
        r"\bPASSWORD\b",
        r"\bAPI_KEY\b",
        r"\bSECRET\b",
        r"\bKEY\b",
        r"password\d*",
    ]

    @property
    def name(self) -> str:
        """Return the policy name."""
        return "NoHardcodedSecrets"

    @property
    def description(self) -> str:
        """Return a description of what the policy checks."""
        return "No secrets should be hardcoded in run commands"

    def evaluate(self, workflow: Workflow) -> PolicyResult:
        """Evaluate workflow for hardcoded secrets.

        Args:
            workflow: The workflow to evaluate

        Returns:
            PolicyResult indicating pass/fail
        """
        issues = []

        for job_id, job in workflow.jobs.items():
            for i, step in enumerate(job.steps):
                if step.run:
                    for pattern in self.SECRET_PATTERNS:
                        if re.search(pattern, step.run, re.IGNORECASE):
                            issues.append(
                                f"Job '{job_id}', step {i}: potential secret pattern '{pattern}'"
                            )
                            break

        if issues:
            return PolicyResult(
                policy_name=self.name,
                passed=False,
                message=f"Found potential hardcoded secrets: {'; '.join(issues)}",
            )

        return PolicyResult(
            policy_name=self.name,
            passed=True,
            message="No hardcoded secrets detected",
        )


class RequireApproval(Policy):
    """Policy for detecting jobs that should use environment with reviewers.

    This is detection only - it identifies jobs that use environments,
    but doesn't enforce reviewer configuration.
    """

    @property
    def name(self) -> str:
        """Return the policy name."""
        return "RequireApproval"

    @property
    def description(self) -> str:
        """Return a description of what the policy checks."""
        return "Jobs should use environment with reviewers (detection only)"

    def evaluate(self, workflow: Workflow) -> PolicyResult:
        """Evaluate workflow for environment usage.

        Args:
            workflow: The workflow to evaluate

        Returns:
            PolicyResult with info about environment usage
        """
        jobs_with_env = []
        jobs_without_env = []

        for job_id, job in workflow.jobs.items():
            if job.environment:
                jobs_with_env.append(job_id)
            else:
                jobs_without_env.append(job_id)

        if jobs_without_env:
            return PolicyResult(
                policy_name=self.name,
                passed=False,
                message=f"Jobs without environment: {', '.join(jobs_without_env)}",
            )

        if jobs_with_env:
            return PolicyResult(
                policy_name=self.name,
                passed=True,
                message=f"All jobs use environment: {', '.join(jobs_with_env)}",
            )

        return PolicyResult(
            policy_name=self.name,
            passed=True,
            message="No jobs in workflow",
        )


class PinActions(Policy):
    """Policy requiring actions to be pinned to SHA or version.

    Actions should not use branch names or be unpinned.
    """

    # Pattern to match SHA (40 hex characters)
    SHA_PATTERN = re.compile(r"@[0-9a-f]{40}$")
    # Pattern to match version (e.g., @v1, @v1.2.3)
    VERSION_PATTERN = re.compile(r"@v\d+(\.\d+)*$")

    @property
    def name(self) -> str:
        """Return the policy name."""
        return "PinActions"

    @property
    def description(self) -> str:
        """Return a description of what the policy checks."""
        return "Actions should be pinned to SHA or version"

    def evaluate(self, workflow: Workflow) -> PolicyResult:
        """Evaluate workflow for action pinning.

        Args:
            workflow: The workflow to evaluate

        Returns:
            PolicyResult indicating pass/fail
        """
        unpinned = []

        for job_id, job in workflow.jobs.items():
            for i, step in enumerate(job.steps):
                if step.uses:
                    # Check if action is pinned to SHA or version
                    if "@" not in step.uses:
                        unpinned.append(f"Job '{job_id}', step {i}: {step.uses}")
                    elif self.SHA_PATTERN.search(
                        step.uses
                    ) or self.VERSION_PATTERN.search(step.uses):
                        # Properly pinned
                        continue
                    else:
                        # Pinned to something else (likely a branch)
                        unpinned.append(f"Job '{job_id}', step {i}: {step.uses}")

        if unpinned:
            return PolicyResult(
                policy_name=self.name,
                passed=False,
                message=f"Actions not properly pinned: {'; '.join(unpinned)}",
            )

        return PolicyResult(
            policy_name=self.name,
            passed=True,
            message="All actions properly pinned",
        )


class LimitJobCount(Policy):
    """Policy limiting the number of jobs in a workflow.

    This helps keep workflows manageable and reduces complexity.
    """

    def __init__(self, max_jobs: int = 10):
        """Initialize the policy with a job limit.

        Args:
            max_jobs: Maximum number of jobs allowed (default: 10)
        """
        self.max_jobs = max_jobs

    @property
    def name(self) -> str:
        """Return the policy name."""
        return "LimitJobCount"

    @property
    def description(self) -> str:
        """Return a description of what the policy checks."""
        return f"Workflow should not exceed {self.max_jobs} jobs"

    def evaluate(self, workflow: Workflow) -> PolicyResult:
        """Evaluate workflow for job count.

        Args:
            workflow: The workflow to evaluate

        Returns:
            PolicyResult indicating pass/fail
        """
        job_count = len(workflow.jobs)

        if job_count > self.max_jobs:
            return PolicyResult(
                policy_name=self.name,
                passed=False,
                message=f"Workflow has {job_count} jobs, exceeds limit of {self.max_jobs}",
            )

        return PolicyResult(
            policy_name=self.name,
            passed=True,
            message=f"Workflow has {job_count} jobs (limit: {self.max_jobs})",
        )
