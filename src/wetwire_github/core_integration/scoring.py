"""Workflow quality scoring for wetwire-core integration.

Provides scoring metrics for workflow quality assessment.
"""

from pathlib import Path
from typing import Any

import yaml


def score_workflow(workflow_path: str) -> dict[str, Any]:
    """Score a workflow file for quality and best practices.

    Args:
        workflow_path: Path to YAML workflow file

    Returns:
        Score dictionary with total_score and details
    """
    path = Path(workflow_path)

    if not path.exists():
        return {
            "total_score": 0,
            "details": {"error": f"File not found: {workflow_path}"},
        }

    try:
        content = path.read_text()
        workflow = yaml.safe_load(content)
    except Exception as e:
        return {
            "total_score": 0,
            "details": {"error": f"Failed to parse YAML: {e}"},
        }

    if not isinstance(workflow, dict):
        return {
            "total_score": 0,
            "details": {"error": "Invalid workflow format"},
        }

    # Run scoring checks
    checks = [
        _check_has_name(workflow),
        _check_has_triggers(workflow),
        _check_has_jobs(workflow),
        _check_uses_checkout(workflow),
        _check_has_permissions(workflow),
        _check_uses_pinned_actions(workflow),
        _check_has_timeout(workflow),
        _check_uses_cache(workflow),
        _check_has_concurrency(workflow),
        _check_job_naming(workflow),
    ]

    # Calculate total score
    total = sum(c["score"] for c in checks)
    max_score = sum(c["max_score"] for c in checks)
    percentage = (total / max_score * 100) if max_score > 0 else 0

    return {
        "total_score": round(percentage, 1),
        "points": total,
        "max_points": max_score,
        "details": {
            "checks": checks,
            "passed": sum(1 for c in checks if c["passed"]),
            "failed": sum(1 for c in checks if not c["passed"]),
        },
    }


def _check_has_name(workflow: dict) -> dict[str, Any]:
    """Check if workflow has a name."""
    has_name = "name" in workflow and bool(workflow["name"])
    return {
        "name": "has_name",
        "description": "Workflow has a descriptive name",
        "passed": has_name,
        "score": 10 if has_name else 0,
        "max_score": 10,
    }


def _check_has_triggers(workflow: dict) -> dict[str, Any]:
    """Check if workflow has triggers defined."""
    has_triggers = "on" in workflow
    return {
        "name": "has_triggers",
        "description": "Workflow has trigger events defined",
        "passed": has_triggers,
        "score": 10 if has_triggers else 0,
        "max_score": 10,
    }


def _check_has_jobs(workflow: dict) -> dict[str, Any]:
    """Check if workflow has jobs defined."""
    has_jobs = "jobs" in workflow and bool(workflow.get("jobs"))
    return {
        "name": "has_jobs",
        "description": "Workflow has jobs defined",
        "passed": has_jobs,
        "score": 10 if has_jobs else 0,
        "max_score": 10,
    }


def _check_uses_checkout(workflow: dict) -> dict[str, Any]:
    """Check if workflow uses checkout action."""
    uses_checkout = False

    jobs = workflow.get("jobs", {})
    for job in jobs.values():
        if not isinstance(job, dict):
            continue
        steps = job.get("steps", [])
        for step in steps:
            if not isinstance(step, dict):
                continue
            uses = step.get("uses", "")
            if "actions/checkout" in uses:
                uses_checkout = True
                break

    return {
        "name": "uses_checkout",
        "description": "Workflow uses actions/checkout for repository access",
        "passed": uses_checkout,
        "score": 10 if uses_checkout else 0,
        "max_score": 10,
    }


def _check_has_permissions(workflow: dict) -> dict[str, Any]:
    """Check if workflow has explicit permissions."""
    has_permissions = "permissions" in workflow

    # Also check job-level permissions
    jobs = workflow.get("jobs", {})
    for job in jobs.values():
        if isinstance(job, dict) and "permissions" in job:
            has_permissions = True
            break

    return {
        "name": "has_permissions",
        "description": "Workflow has explicit permissions defined (security)",
        "passed": has_permissions,
        "score": 15 if has_permissions else 0,
        "max_score": 15,
    }


def _check_uses_pinned_actions(workflow: dict) -> dict[str, Any]:
    """Check if actions use pinned versions (SHA or version tag)."""
    pinned = True
    unpinned_actions = []

    jobs = workflow.get("jobs", {})
    for job in jobs.values():
        if not isinstance(job, dict):
            continue
        steps = job.get("steps", [])
        for step in steps:
            if not isinstance(step, dict):
                continue
            uses = step.get("uses", "")
            if uses and "@" not in uses:
                pinned = False
                unpinned_actions.append(uses)

    return {
        "name": "uses_pinned_actions",
        "description": "All actions use pinned versions (@vX or @sha)",
        "passed": pinned,
        "score": 15 if pinned else 0,
        "max_score": 15,
        "details": {"unpinned": unpinned_actions} if unpinned_actions else {},
    }


def _check_has_timeout(workflow: dict) -> dict[str, Any]:
    """Check if jobs have timeout defined."""
    has_timeout = False

    jobs = workflow.get("jobs", {})
    for job in jobs.values():
        if isinstance(job, dict) and "timeout-minutes" in job:
            has_timeout = True
            break

    return {
        "name": "has_timeout",
        "description": "Jobs have timeout-minutes defined",
        "passed": has_timeout,
        "score": 5 if has_timeout else 0,
        "max_score": 5,
    }


def _check_uses_cache(workflow: dict) -> dict[str, Any]:
    """Check if workflow uses caching."""
    uses_cache = False

    jobs = workflow.get("jobs", {})
    for job in jobs.values():
        if not isinstance(job, dict):
            continue
        steps = job.get("steps", [])
        for step in steps:
            if not isinstance(step, dict):
                continue
            uses = step.get("uses", "")
            if "actions/cache" in uses:
                uses_cache = True
                break
            # Check for setup-* actions with cache option
            with_opts = step.get("with", {})
            if isinstance(with_opts, dict) and "cache" in with_opts:
                uses_cache = True
                break

    return {
        "name": "uses_cache",
        "description": "Workflow uses caching for faster builds",
        "passed": uses_cache,
        "score": 10 if uses_cache else 0,
        "max_score": 10,
    }


def _check_has_concurrency(workflow: dict) -> dict[str, Any]:
    """Check if workflow has concurrency control."""
    has_concurrency = "concurrency" in workflow
    return {
        "name": "has_concurrency",
        "description": "Workflow has concurrency control to prevent duplicate runs",
        "passed": has_concurrency,
        "score": 5 if has_concurrency else 0,
        "max_score": 5,
    }


def _check_job_naming(workflow: dict) -> dict[str, Any]:
    """Check if jobs have descriptive names."""
    jobs = workflow.get("jobs", {})
    if not jobs:
        return {
            "name": "job_naming",
            "description": "Jobs have descriptive names",
            "passed": False,
            "score": 0,
            "max_score": 10,
        }

    named_jobs = sum(1 for job in jobs.values() if isinstance(job, dict) and job.get("name"))
    total_jobs = len(jobs)
    all_named = named_jobs == total_jobs

    return {
        "name": "job_naming",
        "description": "Jobs have descriptive names",
        "passed": all_named,
        "score": 10 if all_named else int(named_jobs / total_jobs * 10),
        "max_score": 10,
    }
