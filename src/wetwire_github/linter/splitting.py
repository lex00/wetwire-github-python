"""File splitting utilities for wetwire-github packages.

This module provides utilities for splitting large workflow files into
smaller, category-based files. The linter's FileTooLarge rule (WAG007)
uses these utilities to suggest file splits.

Categories:
    ci: build, test, lint, format, type-check jobs
    deploy: deployment jobs (staging, production, etc.)
    release: publish, release, package jobs
    security: security scanning, vulnerability, codeql jobs
    maintenance: cleanup, stale, cache management jobs
    main: Everything else or tightly-coupled jobs
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "JOB_CATEGORIES",
    "MAX_JOBS_PER_FILE",
    "JobInfo",
    "categorize_job",
    "suggest_workflow_splits",
]

# Default maximum number of jobs per file
MAX_JOBS_PER_FILE = 10

# =============================================================================
# Job Category Keywords
# =============================================================================

# Keywords that indicate CI-related jobs
CI_KEYWORDS = [
    "build",
    "test",
    "lint",
    "format",
    "check",
    "validate",
    "typecheck",
    "type-check",
    "type_check",
    "coverage",
    "analyze",
    "compile",
    "ci",
]

# Keywords that indicate deployment jobs
DEPLOY_KEYWORDS = [
    "deploy",
    "deployment",
    "staging",
    "production",
    "prod",
    "cdk",
    "terraform",
    "infrastructure",
    "infra",
    "provision",
]

# Keywords that indicate release/publish jobs
RELEASE_KEYWORDS = [
    "release",
    "publish",
    "upload",
    "package",
    "dist",
    "npm",
    "pypi",
    "docker",
    "registry",
    "tag",
    "version",
]

# Keywords that indicate security jobs
SECURITY_KEYWORDS = [
    "security",
    "scan",
    "codeql",
    "dependabot",
    "vulnerability",
    "snyk",
    "trivy",
    "audit",
    "sast",
    "dast",
]

# Keywords that indicate maintenance jobs
MAINTENANCE_KEYWORDS = [
    "cleanup",
    "clean",
    "stale",
    "prune",
    "expire",
    "archive",
    "schedule",
    "cron",
    "nightly",
    "weekly",
    "maintenance",
]

# Step content that indicates CI actions
CI_STEP_PATTERNS = [
    "pytest",
    "npm test",
    "yarn test",
    "go test",
    "cargo test",
    "make test",
    "ruff",
    "eslint",
    "flake8",
    "mypy",
    "pyright",
    "tsc --noEmit",
]

# Step content that indicates deploy actions
DEPLOY_STEP_PATTERNS = [
    "deploy",
    "cdk deploy",
    "terraform apply",
    "kubectl apply",
    "aws-actions/configure-aws-credentials",
    "azure/login",
    "google-github-actions/auth",
]

# Step content that indicates release actions
RELEASE_STEP_PATTERNS = [
    "npm publish",
    "twine upload",
    "cargo publish",
    "docker push",
    "gh release",
    "actions/create-release",
]

# Mapping for direct job name to category (for common patterns)
JOB_CATEGORIES: dict[str, str] = {}


@dataclass
class JobInfo:
    """Information about a job for file splitting.

    Attributes:
        name: Job ID/name
        steps: List of step commands or uses strings
        dependencies: Set of job names this job depends on (needs)
    """

    name: str
    steps: str | list[str]
    dependencies: set[str]


def categorize_job(job_name: str, steps: list[str] | None = None) -> str:
    """Get the category for a job based on its name and content.

    Args:
        job_name: The job ID/name
        steps: Optional list of step content (uses/run values)

    Returns:
        Category name (e.g., "ci", "deploy", "release", "security", "main")

    Examples:
        >>> categorize_job("build")
        'ci'
        >>> categorize_job("deploy_production")
        'deploy'
        >>> categorize_job("security_scan")
        'security'
    """
    name_lower = job_name.lower().replace("-", "_")

    # Check name-based keywords - more specific categories first
    # Security keywords first (before CI) since "vulnerability_check" should be security
    for keyword in SECURITY_KEYWORDS:
        if keyword in name_lower:
            return "security"

    for keyword in MAINTENANCE_KEYWORDS:
        if keyword in name_lower:
            return "maintenance"

    for keyword in DEPLOY_KEYWORDS:
        if keyword in name_lower:
            return "deploy"

    for keyword in RELEASE_KEYWORDS:
        if keyword in name_lower:
            return "release"

    # CI keywords last (most generic)
    for keyword in CI_KEYWORDS:
        if keyword in name_lower:
            return "ci"

    # If steps provided, check step content
    if steps:
        steps_content = " ".join(str(s).lower() for s in steps)

        for pattern in CI_STEP_PATTERNS:
            if pattern.lower() in steps_content:
                return "ci"

        for pattern in DEPLOY_STEP_PATTERNS:
            if pattern.lower() in steps_content:
                return "deploy"

        for pattern in RELEASE_STEP_PATTERNS:
            if pattern.lower() in steps_content:
                return "release"

    return "main"


def suggest_workflow_splits(
    jobs: list[JobInfo],
    max_per_file: int = MAX_JOBS_PER_FILE,
) -> dict[str, list[str]]:
    """Suggest how to split jobs into category-based files.

    This function implements the file splitting algorithm:
    1. Categorize each job by name and step content
    2. Group jobs by category
    3. If a category has > max_per_file, split into numbered files

    Args:
        jobs: List of JobInfo objects to split
        max_per_file: Maximum jobs per file (default 10)

    Returns:
        Dict mapping filename (without .py) to list of job names
        E.g., {"ci": ["build", "test"], "deploy": ["deploy_prod"]}

    Examples:
        >>> jobs = [
        ...     JobInfo("build", [], set()),
        ...     JobInfo("deploy", [], set()),
        ... ]
        >>> splits = suggest_workflow_splits(jobs)
        >>> splits
        {'ci': ['build'], 'deploy': ['deploy']}
    """
    # Categorize all jobs
    categories: dict[str, list[str]] = {}

    for job in jobs:
        steps = job.steps if isinstance(job.steps, list) else []
        category = categorize_job(job.name, steps)

        if category not in categories:
            categories[category] = []
        categories[category].append(job.name)

    # Build result, splitting large categories
    result: dict[str, list[str]] = {}

    for category, names in categories.items():
        if len(names) <= max_per_file:
            result[category] = names
        else:
            # Need to split into multiple files
            chunks = _split_into_chunks(names, max_per_file)
            for i, chunk in enumerate(chunks, start=1):
                result[f"{category}{i}"] = chunk

    return result


def _split_into_chunks(items: list[str], chunk_size: int) -> list[list[str]]:
    """Split a list into chunks of at most chunk_size."""
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]


def format_split_suggestion(splits: dict[str, list[str]]) -> str:
    """Format splitting suggestion as human-readable output.

    Args:
        splits: Dict from suggest_workflow_splits()

    Returns:
        Formatted string with split suggestions
    """
    lines = ["Suggested file splits:", ""]

    for filename, jobs in sorted(splits.items()):
        lines.append(f"  {filename}.py:")
        for job in jobs:
            lines.append(f"    - {job}")
        lines.append("")

    return "\n".join(lines)
