"""Security scanner for GitHub Actions workflows."""

from wetwire_github.workflow import Workflow

from .checks import (
    check_excessive_permissions,
    check_hardcoded_secrets,
    check_missing_permissions,
    check_script_injection,
    check_unpinned_actions,
)
from .types import SecurityReport


class SecurityScanner:
    """Scanner for detecting security issues in workflows."""

    def scan(self, workflow: Workflow) -> SecurityReport:
        """
        Scan a workflow for security issues.

        Args:
            workflow: The workflow to scan

        Returns:
            SecurityReport containing all detected issues
        """
        issues = []

        # Run all security checks
        issues.extend(check_hardcoded_secrets(workflow))
        issues.extend(check_script_injection(workflow))
        issues.extend(check_unpinned_actions(workflow))
        issues.extend(check_excessive_permissions(workflow))
        issues.extend(check_missing_permissions(workflow))

        return SecurityReport(issues=issues)
