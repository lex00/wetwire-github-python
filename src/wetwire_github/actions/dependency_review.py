"""Generated wrapper for actions/dependency-review-action."""

from wetwire_github.workflow import Step


def dependency_review(
    *,
    fail_on_severity: str | None = None,
    allow_licenses: list[str] | None = None,
    deny_licenses: list[str] | None = None,
    config_file: str | None = None,
) -> Step:
    """Create a step that scans dependencies for vulnerabilities.

    Args:
        fail_on_severity: Minimum severity to fail (low, moderate, high, critical)
        allow_licenses: List of allowed licenses
        deny_licenses: List of denied licenses
        config_file: Path to config file

    Returns:
        Step configured for dependency review
    """
    with_dict = {
        "fail-on-severity": fail_on_severity,
        "allow-licenses": ", ".join(allow_licenses) if allow_licenses else None,
        "deny-licenses": ", ".join(deny_licenses) if deny_licenses else None,
        "config-file": config_file,
    }
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="actions/dependency-review-action@v4",
        with_=with_dict if with_dict else None,
    )
