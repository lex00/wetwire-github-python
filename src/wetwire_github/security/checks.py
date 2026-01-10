"""Individual security check functions."""

import re

from wetwire_github.workflow import Workflow

from .types import SecurityIssue, Severity


def check_hardcoded_secrets(workflow: Workflow) -> list[SecurityIssue]:
    """Check for hardcoded secrets in workflow."""
    issues = []

    # Patterns for common secret formats
    secret_patterns = [
        (r"(?i)(api[_-]?key|apikey)\s*[=:]\s*['\"]?([a-zA-Z0-9_-]{8,})", "API key"),
        (r"(?i)-p\s*['\"]([^\s'\"]{8,})['\"]", "password"),  # -p'password' or -p"password"
        (r"(?i)(password|passwd|pwd)\s*[=:]\s*['\"]?([^\s'\"]{8,})", "password"),
        (r"(?i)(token)\s*[=:]\s*['\"]?(secret[a-zA-Z0-9_-]{3,}|[a-zA-Z0-9_-]{20,})", "token"),
        (r"sk_test_[a-zA-Z0-9]{3,}", "Stripe test key"),
        (r"sk_live_[a-zA-Z0-9]{3,}", "Stripe live key"),
        (r"ghp_[a-zA-Z0-9]{20,}", "GitHub personal access token"),
        (r"ghs_[a-zA-Z0-9]{20,}", "GitHub OAuth token"),
    ]

    for job_name, job in workflow.jobs.items():
        for step_idx, step in enumerate(job.steps):
            # Check run commands
            if step.run:
                for pattern, secret_type in secret_patterns:
                    if re.search(pattern, step.run):
                        issues.append(
                            SecurityIssue(
                                title="Hardcoded Secret Detected",
                                description=f"Possible {secret_type} found in run command",
                                severity=Severity.CRITICAL,
                                recommendation="Use GitHub Secrets to store sensitive values. Access them via ${{ secrets.SECRET_NAME }}",
                                location=f"job: {job_name}, step: {step_idx + 1}",
                            )
                        )
                        break  # Only report once per step

            # Check environment variables
            if step.env:
                for env_key, env_value in step.env.items():
                    if isinstance(env_value, str):
                        for pattern, secret_type in secret_patterns:
                            if re.search(pattern, env_value):
                                issues.append(
                                    SecurityIssue(
                                        title="Hardcoded Secret Detected",
                                        description=f"Possible {secret_type} found in environment variable '{env_key}'",
                                        severity=Severity.CRITICAL,
                                        recommendation="Use GitHub Secrets to store sensitive values. Access them via ${{ secrets.SECRET_NAME }}",
                                        location=f"job: {job_name}, step: {step_idx + 1}",
                                    )
                                )
                                break  # Only report once per env var

    return issues


def check_script_injection(workflow: Workflow) -> list[SecurityIssue]:
    """Check for potential script injection vulnerabilities."""
    issues = []

    # Dangerous GitHub event contexts that can be controlled by users
    dangerous_contexts = [
        "github.event.issue.title",
        "github.event.issue.body",
        "github.event.pull_request.title",
        "github.event.pull_request.body",
        "github.event.pull_request.head.ref",
        "github.event.pull_request.head.label",
        "github.event.comment.body",
        "github.event.discussion.title",
        "github.event.discussion.body",
        "github.event.review.body",
        "github.event.commits",
        "github.event.head_commit.message",
    ]

    for job_name, job in workflow.jobs.items():
        for step_idx, step in enumerate(job.steps):
            if step.run:
                for dangerous_context in dangerous_contexts:
                    # Check for direct usage in run commands
                    if dangerous_context in step.run:
                        issues.append(
                            SecurityIssue(
                                title="Script Injection Risk",
                                description=f"Unsafe use of '{dangerous_context}' in run command. User-controlled input may allow script injection.",
                                severity=Severity.HIGH,
                                recommendation="Use environment variables to pass user input safely, or sanitize the input before use.",
                                location=f"job: {job_name}, step: {step_idx + 1}",
                            )
                        )
                        break  # Only report once per step

    return issues


def check_unpinned_actions(workflow: Workflow) -> list[SecurityIssue]:
    """Check for actions without proper version pinning."""
    issues = []

    for job_name, job in workflow.jobs.items():
        for step_idx, step in enumerate(job.steps):
            if step.uses:
                # Parse the action reference
                action_ref = step.uses

                # Skip local actions (paths starting with ./)
                if action_ref.startswith("./"):
                    continue

                # Check if action has a version/ref
                if "@" not in action_ref:
                    issues.append(
                        SecurityIssue(
                            title="Unpinned Action",
                            description=f"Action '{action_ref}' is not pinned to a specific version or SHA",
                            severity=Severity.MEDIUM,
                            recommendation="Pin actions to a full-length commit SHA for maximum security, or use a version tag (e.g., @v4)",
                            location=f"job: {job_name}, step: {step_idx + 1}",
                        )
                    )
                else:
                    # Check if pinned to a branch instead of SHA or version
                    parts = action_ref.split("@", 1)
                    if len(parts) == 2:
                        ref = parts[1]
                        # Check if it's a full commit SHA (40 hex characters)
                        is_sha = len(ref) == 40 and all(c in "0123456789abcdef" for c in ref.lower())
                        # Check if it's a version tag (starts with v or contains dots)
                        is_version = ref.startswith("v") or "." in ref

                        # If it's neither SHA nor version, it's likely a branch
                        if not is_sha and not is_version:
                            issues.append(
                                SecurityIssue(
                                    title="Unpinned Action",
                                    description=f"Action '{action_ref}' appears to be pinned to a branch '{ref}', which can change",
                                    severity=Severity.MEDIUM,
                                    recommendation="Pin actions to a full-length commit SHA for maximum security, or use a version tag (e.g., @v4)",
                                    location=f"job: {job_name}, step: {step_idx + 1}",
                                )
                            )

    return issues


def check_excessive_permissions(workflow: Workflow) -> list[SecurityIssue]:
    """Check for overly permissive permissions."""
    issues = []

    # Check workflow-level permissions
    if workflow.permissions and workflow.permissions.write_all:
        issues.append(
            SecurityIssue(
                title="Excessive Permissions",
                description="Workflow has write-all permissions enabled",
                severity=Severity.HIGH,
                recommendation="Use minimal required permissions. Specify only the permissions needed (e.g., contents: read, issues: write)",
                location="workflow-level permissions",
            )
        )

    # Check job-level permissions
    for job_name, job in workflow.jobs.items():
        if job.permissions and job.permissions.write_all:
            issues.append(
                SecurityIssue(
                    title="Excessive Permissions",
                    description=f"Job '{job_name}' has write-all permissions enabled",
                    severity=Severity.HIGH,
                    recommendation="Use minimal required permissions. Specify only the permissions needed (e.g., contents: read, issues: write)",
                    location=f"job: {job_name}",
                )
            )

    return issues


def check_missing_permissions(workflow: Workflow) -> list[SecurityIssue]:
    """Check for workflows without explicit permissions block."""
    issues = []

    # Check if workflow has any permissions defined
    if workflow.permissions is None:
        issues.append(
            SecurityIssue(
                title="Missing Permissions Block",
                description="Workflow does not have an explicit permissions block",
                severity=Severity.LOW,
                recommendation="Add a permissions block to explicitly control what the workflow can access. Use 'read-all: true' for read-only access or specify individual permissions.",
                location="workflow",
            )
        )

    return issues
