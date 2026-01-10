"""Security scanner for GitHub Actions workflows."""

from .scanner import SecurityScanner
from .types import SecurityIssue, SecurityReport, Severity

__all__ = [
    "SecurityScanner",
    "SecurityIssue",
    "SecurityReport",
    "Severity",
]
