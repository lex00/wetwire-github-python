"""Report command implementation.

Generates a unified quality report by running all checks
(lint, policy, cost, security) and computing a health score.
"""

import json

from wetwire_github.cli.path_validation import PathValidationError, validate_path
from wetwire_github.cost import CostCalculator
from wetwire_github.discover import DiscoveryCache, discover_in_directory
from wetwire_github.linter import lint_directory
from wetwire_github.policy import (
    LimitJobCount,
    NoHardcodedSecrets,
    PinActions,
    Policy,
    PolicyEngine,
    RequireCheckout,
    RequireTimeouts,
)
from wetwire_github.runner import extract_workflows
from wetwire_github.security import SecurityScanner


def get_default_policies() -> list[Policy]:
    """Get the list of default built-in policies.

    Returns:
        List of Policy instances
    """
    return [
        RequireCheckout(),
        RequireTimeouts(),
        NoHardcodedSecrets(),
        PinActions(),
        LimitJobCount(max_jobs=10),
    ]


def generate_report(
    package_path: str,
    output_format: str = "text",
    no_cache: bool = False,
) -> tuple[int, str]:
    """Generate a unified quality report for workflows in a package.

    Args:
        package_path: Path to package directory containing workflow definitions
        output_format: Output format ("text" or "json")
        no_cache: If True, bypass discovery cache

    Returns:
        Tuple of (exit_code, output_string)
    """
    # Validate input path for security
    try:
        package = validate_path(package_path, must_exist=True)
    except PathValidationError as e:
        error_msg = f"Error: Invalid package path: {e}"
        if output_format == "json":
            return 1, json.dumps({"error": error_msg})
        return 1, error_msg

    if not package.exists():
        error_msg = f"Error: Path does not exist: {package_path}"
        if output_format == "json":
            return 1, json.dumps({"error": error_msg})
        return 1, error_msg

    # Initialize cache if not disabled
    cache = None if no_cache else DiscoveryCache()

    # Discover workflow files using AST
    discovered = discover_in_directory(str(package), cache=cache)
    workflow_files = {r.file_path for r in discovered if r.type == "Workflow"}

    if not workflow_files:
        msg = "No workflows found in package"
        if output_format == "json":
            return 1, json.dumps({"error": msg})
        return 1, msg

    # Extract actual workflow objects
    all_workflows = []
    for file_path in workflow_files:
        try:
            extracted = extract_workflows(file_path)
            all_workflows.extend(extracted)
        except Exception:
            # Skip problematic files
            pass

    if not all_workflows:
        msg = "No workflows could be extracted"
        if output_format == "json":
            return 1, json.dumps({"error": msg})
        return 1, msg

    # Run all checks
    lint_results = _run_lint_checks(str(package))
    policy_results = _run_policy_checks(all_workflows)
    security_results = _run_security_checks(all_workflows)
    cost_results = _run_cost_checks(all_workflows)

    # Calculate health score
    health_score = _calculate_health_score(
        lint_results, policy_results, security_results
    )

    # Build report data
    report_data = {
        "workflow_count": len(all_workflows),
        "health_score": health_score,
        "lint_issues": lint_results,
        "policy_results": policy_results,
        "security_issues": security_results,
        "cost_estimate": cost_results,
    }

    # Format output
    if output_format == "json":
        return _format_json(report_data)
    else:
        return _format_text(report_data)


def _run_lint_checks(package_path: str) -> dict:
    """Run lint checks on the package.

    Args:
        package_path: Path to package directory

    Returns:
        Dictionary with lint results
    """
    results = lint_directory(package_path)

    total_errors = sum(len(r.errors) for r in results)
    errors_by_rule: dict[str, int] = {}

    for result in results:
        for error in result.errors:
            errors_by_rule[error.rule_id] = errors_by_rule.get(error.rule_id, 0) + 1

    return {
        "total": total_errors,
        "files_checked": len(results),
        "by_rule": errors_by_rule,
    }


def _run_policy_checks(workflows: list) -> dict:
    """Run policy checks on workflows.

    Args:
        workflows: List of extracted workflows

    Returns:
        Dictionary with policy results
    """
    policies = get_default_policies()
    engine = PolicyEngine(policies=policies)

    total_passed = 0
    total_failed = 0
    failed_policies: dict[str, int] = {}

    for extracted in workflows:
        workflow = extracted.workflow
        results = engine.evaluate(workflow)

        for result in results:
            if result.passed:
                total_passed += 1
            else:
                total_failed += 1
                failed_policies[result.policy_name] = (
                    failed_policies.get(result.policy_name, 0) + 1
                )

    return {
        "passed_count": total_passed,
        "failed_count": total_failed,
        "total_failures": total_failed,
        "failed_policies": failed_policies,
    }


def _run_security_checks(workflows: list) -> dict:
    """Run security checks on workflows.

    Args:
        workflows: List of extracted workflows

    Returns:
        Dictionary with security results by severity
    """
    scanner = SecurityScanner()

    critical = 0
    high = 0
    medium = 0
    low = 0
    total = 0

    for extracted in workflows:
        workflow = extracted.workflow
        report = scanner.scan(workflow)

        critical += report.critical_count
        high += report.high_count
        medium += report.medium_count
        low += report.low_count
        total += report.total_count

    return {
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low,
        "total": total,
    }


def _run_cost_checks(workflows: list) -> dict:
    """Run cost estimation on workflows.

    Args:
        workflows: List of extracted workflows

    Returns:
        Dictionary with cost estimates
    """
    calculator = CostCalculator()

    total_cost = 0.0
    total_linux_minutes = 0.0
    total_windows_minutes = 0.0
    total_macos_minutes = 0.0

    for extracted in workflows:
        workflow = extracted.workflow
        estimate = calculator.estimate(workflow)

        total_cost += estimate.total_cost
        total_linux_minutes += estimate.linux_minutes
        total_windows_minutes += estimate.windows_minutes
        total_macos_minutes += estimate.macos_minutes

    return {
        "total_cost": round(total_cost, 4),
        "linux_minutes": total_linux_minutes,
        "windows_minutes": total_windows_minutes,
        "macos_minutes": total_macos_minutes,
    }


def _calculate_health_score(
    lint_results: dict,
    policy_results: dict,
    security_results: dict,
) -> int:
    """Calculate a health score from 0-100 based on issues found.

    The score starts at 100 and is reduced based on:
    - Lint issues: -1 per issue (max -20)
    - Policy failures: -5 per failure (max -30)
    - Security issues:
      - Critical: -15 each (max -30)
      - High: -10 each (max -20)
      - Medium: -3 each (max -10)
      - Low: -1 each (max -5)

    Args:
        lint_results: Lint check results
        policy_results: Policy check results
        security_results: Security check results

    Returns:
        Health score from 0-100
    """
    score = 100

    # Deduct for lint issues (max -20)
    lint_deduction = min(lint_results.get("total", 0), 20)
    score -= lint_deduction

    # Deduct for policy failures (max -30)
    policy_deduction = min(policy_results.get("failed_count", 0) * 5, 30)
    score -= policy_deduction

    # Deduct for security issues
    critical_deduction = min(security_results.get("critical", 0) * 15, 30)
    high_deduction = min(security_results.get("high", 0) * 10, 20)
    medium_deduction = min(security_results.get("medium", 0) * 3, 10)
    low_deduction = min(security_results.get("low", 0), 5)

    score -= critical_deduction
    score -= high_deduction
    score -= medium_deduction
    score -= low_deduction

    # Ensure score is within 0-100
    return max(0, min(100, score))


def _format_json(report_data: dict) -> tuple[int, str]:
    """Format report as JSON.

    Args:
        report_data: Report data dictionary

    Returns:
        Tuple of (exit_code, json_string)
    """
    # Exit code is 1 if health score is below threshold (e.g., 50)
    exit_code = 0 if report_data["health_score"] >= 50 else 1
    return exit_code, json.dumps(report_data, indent=2)


def _format_text(report_data: dict) -> tuple[int, str]:
    """Format report as human-readable text.

    Args:
        report_data: Report data dictionary

    Returns:
        Tuple of (exit_code, text_string)
    """
    lines = []

    # Header
    lines.append("=" * 60)
    lines.append("Workflow Quality Report")
    lines.append("=" * 60)
    lines.append("")

    # Overview
    lines.append(f"Workflows Analyzed: {report_data['workflow_count']}")
    lines.append(f"Health Score: {report_data['health_score']}/100")
    lines.append("")

    # Lint Issues
    lint = report_data["lint_issues"]
    lines.append("-" * 60)
    lines.append("Lint Issues")
    lines.append("-" * 60)
    lines.append(f"  Total issues: {lint['total']}")
    lines.append(f"  Files checked: {lint['files_checked']}")
    if lint["by_rule"]:
        lines.append("  By rule:")
        for rule_id, count in lint["by_rule"].items():
            lines.append(f"    {rule_id}: {count}")
    lines.append("")

    # Policy Results
    policy = report_data["policy_results"]
    lines.append("-" * 60)
    lines.append("Policy Results")
    lines.append("-" * 60)
    lines.append(f"  Passed: {policy['passed_count']}")
    lines.append(f"  Failed: {policy['failed_count']}")
    if policy["failed_policies"]:
        lines.append("  Failed policies:")
        for policy_name, count in policy["failed_policies"].items():
            lines.append(f"    {policy_name}: {count}")
    lines.append("")

    # Security Issues
    security = report_data["security_issues"]
    lines.append("-" * 60)
    lines.append("Security Issues")
    lines.append("-" * 60)
    lines.append(f"  Critical: {security['critical']}")
    lines.append(f"  High: {security['high']}")
    lines.append(f"  Medium: {security['medium']}")
    lines.append(f"  Low: {security['low']}")
    lines.append(f"  Total: {security['total']}")
    lines.append("")

    # Cost Estimate
    cost = report_data["cost_estimate"]
    lines.append("-" * 60)
    lines.append("Cost Estimate (per run)")
    lines.append("-" * 60)
    lines.append(f"  Estimated cost: ${cost['total_cost']:.4f}")
    lines.append(f"  Linux minutes: {cost['linux_minutes']:.1f}")
    lines.append(f"  Windows minutes: {cost['windows_minutes']:.1f}")
    lines.append(f"  macOS minutes: {cost['macos_minutes']:.1f}")
    lines.append("")

    # Summary
    lines.append("=" * 60)
    score = report_data["health_score"]
    if score >= 90:
        lines.append("Overall: Excellent - Workflows are in great shape!")
    elif score >= 70:
        lines.append("Overall: Good - Minor improvements recommended.")
    elif score >= 50:
        lines.append("Overall: Fair - Several issues should be addressed.")
    else:
        lines.append("Overall: Poor - Significant improvements needed.")
    lines.append("=" * 60)

    # Exit code is 1 if health score is below threshold
    exit_code = 0 if score >= 50 else 1
    return exit_code, "\n".join(lines)
