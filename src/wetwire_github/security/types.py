"""Security scanner types."""

from dataclasses import dataclass, field
from enum import Enum


class Severity(Enum):
    """Severity levels for security issues."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class SecurityIssue:
    """A detected security issue in a workflow."""

    title: str
    description: str
    severity: Severity
    recommendation: str
    location: str = ""


@dataclass
class SecurityReport:
    """Summary report of security issues found in a workflow."""

    issues: list[SecurityIssue] = field(default_factory=list)

    @property
    def critical_count(self) -> int:
        """Count of critical severity issues."""
        return sum(1 for issue in self.issues if issue.severity == Severity.CRITICAL)

    @property
    def high_count(self) -> int:
        """Count of high severity issues."""
        return sum(1 for issue in self.issues if issue.severity == Severity.HIGH)

    @property
    def medium_count(self) -> int:
        """Count of medium severity issues."""
        return sum(1 for issue in self.issues if issue.severity == Severity.MEDIUM)

    @property
    def low_count(self) -> int:
        """Count of low severity issues."""
        return sum(1 for issue in self.issues if issue.severity == Severity.LOW)

    @property
    def total_count(self) -> int:
        """Total count of all issues."""
        return len(self.issues)
