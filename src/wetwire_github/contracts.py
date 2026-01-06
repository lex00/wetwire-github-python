"""Protocols and result types for wetwire-github."""

from dataclasses import dataclass
from typing import Protocol


class WorkflowResource(Protocol):
    """Protocol for workflow resources."""

    def resource_type(self) -> str:
        """Return the resource type identifier."""
        ...


@dataclass
class OutputRef:
    """Reference to a step output.

    When converted to string, becomes: ${{ steps.step_id.outputs.name }}
    """

    step_id: str
    output: str

    def __str__(self) -> str:
        return f"${{{{ steps.{self.step_id}.outputs.{self.output} }}}}"


@dataclass
class DiscoveredWorkflow:
    """Workflow found by AST parsing."""

    name: str  # Variable name
    file: str  # Source file path
    line: int  # Line number
    jobs: list[str]  # Job variable names in this workflow


@dataclass
class DiscoveredJob:
    """Job found by AST parsing."""

    name: str  # Variable name
    file: str  # Source file path
    line: int  # Line number
    dependencies: list[str]  # Referenced job names (needs field)


@dataclass
class BuildResult:
    """Result of a build command."""

    success: bool
    workflows: list[str] | None = None
    files: list[str] | None = None
    errors: list[str] | None = None


@dataclass
class LintIssue:
    """A single linting issue."""

    file: str
    line: int
    column: int
    severity: str  # "error", "warning", "info"
    message: str
    rule: str  # e.g., "WAG001"
    fixable: bool


@dataclass
class LintResult:
    """Result of a lint command."""

    success: bool
    issues: list[LintIssue] | None = None


@dataclass
class ValidateResult:
    """Result of a validate command (actionlint)."""

    success: bool
    errors: list[str] | None = None
    warnings: list[str] | None = None


@dataclass
class ListWorkflow:
    """Workflow summary for list command."""

    name: str
    file: str
    line: int
    jobs: int  # Number of jobs


@dataclass
class ListResult:
    """Result of a list command."""

    workflows: list[ListWorkflow]
