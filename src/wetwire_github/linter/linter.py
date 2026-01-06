"""Linter framework for workflow Python code.

Provides the core linting infrastructure for checking workflow
declarations against best practices.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable


@dataclass
class LintError:
    """A linting error found in code."""

    rule_id: str
    message: str
    file_path: str
    line: int
    column: int
    suggestion: str | None = None


@dataclass
class LintResult:
    """Result of linting a file."""

    errors: list[LintError] = field(default_factory=list)
    file_path: str = ""

    @property
    def is_clean(self) -> bool:
        """Return True if no errors found."""
        return len(self.errors) == 0


@dataclass
class FixResult:
    """Result of applying auto-fixes to code."""

    source: str
    """The fixed source code."""
    fixed_count: int = 0
    """Number of issues fixed."""
    remaining_errors: list[LintError] = field(default_factory=list)
    """Errors that could not be auto-fixed."""
    file_path: str = ""


@runtime_checkable
class Rule(Protocol):
    """Protocol for linting rules."""

    @property
    def id(self) -> str:
        """Return the rule identifier (e.g., 'WAG001')."""
        ...

    @property
    def description(self) -> str:
        """Return a description of what the rule checks."""
        ...

    def check(self, source: str, file_path: str) -> list[LintError]:
        """Check source code and return any lint errors.

        Args:
            source: Python source code to check
            file_path: Path to the source file

        Returns:
            List of lint errors found
        """
        ...


@runtime_checkable
class FixableRule(Protocol):
    """Protocol for rules that support auto-fixing."""

    @property
    def id(self) -> str:
        """Return the rule identifier."""
        ...

    @property
    def description(self) -> str:
        """Return a description of what the rule checks."""
        ...

    def check(self, source: str, file_path: str) -> list[LintError]:
        """Check source code and return any lint errors."""
        ...

    def fix(self, source: str, file_path: str) -> tuple[str, int, list[LintError]]:
        """Apply fixes to source code.

        Args:
            source: Python source code to fix
            file_path: Path to the source file

        Returns:
            Tuple of (fixed_source, fixed_count, remaining_errors)
        """
        ...


class BaseRule(ABC):
    """Base class for lint rules."""

    @property
    @abstractmethod
    def id(self) -> str:
        """Return the rule identifier."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a description of what the rule checks."""
        ...

    @abstractmethod
    def check(self, source: str, file_path: str) -> list[LintError]:
        """Check source code and return any lint errors."""
        ...


class Linter:
    """Linter for Python workflow code."""

    rules: list[Rule]

    def __init__(self, rules: list[Rule] | None = None) -> None:
        """Initialize the linter.

        Args:
            rules: List of rules to enable. If None, uses default rules.
        """
        if rules is None:
            from .rules import get_default_rules

            self.rules = list(get_default_rules())  # type: ignore[arg-type]
        else:
            self.rules = rules

    def check(self, source: str, file_path: str = "<string>") -> LintResult:
        """Check source code against all enabled rules.

        Args:
            source: Python source code to check
            file_path: Path to the source file

        Returns:
            LintResult with all errors found
        """
        errors = []
        for rule in self.rules:
            errors.extend(rule.check(source, file_path))
        return LintResult(errors=errors, file_path=file_path)

    def fix(self, source: str, file_path: str = "<string>") -> FixResult:
        """Apply auto-fixes to source code.

        Applies fixes from all fixable rules. Non-fixable rules report
        their errors as remaining.

        Args:
            source: Python source code to fix
            file_path: Path to the source file

        Returns:
            FixResult with fixed source and remaining errors
        """
        fixed_source = source
        total_fixed = 0
        remaining_errors = []

        for rule in self.rules:
            if isinstance(rule, FixableRule):
                fixed_source, fixed_count, errors = rule.fix(fixed_source, file_path)
                total_fixed += fixed_count
                remaining_errors.extend(errors)
            else:
                # Non-fixable rules just report errors
                remaining_errors.extend(rule.check(fixed_source, file_path))

        return FixResult(
            source=fixed_source,
            fixed_count=total_fixed,
            remaining_errors=remaining_errors,
            file_path=file_path,
        )


def lint_file(file_path: str, rules: list[Rule] | None = None) -> LintResult:
    """Lint a Python file.

    Args:
        file_path: Path to the Python file
        rules: Optional list of rules to use

    Returns:
        LintResult with any errors found
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()
    except (OSError, UnicodeDecodeError):
        return LintResult(errors=[], file_path=file_path)

    linter = Linter(rules=rules)
    return linter.check(source, file_path)


def lint_directory(
    directory: str,
    rules: list[Rule] | None = None,
    recursive: bool = True,
    exclude_hidden: bool = True,
    exclude_pycache: bool = True,
) -> list[LintResult]:
    """Lint all Python files in a directory.

    Args:
        directory: Path to directory
        rules: Optional list of rules to use
        recursive: Whether to scan subdirectories
        exclude_hidden: Whether to exclude hidden directories
        exclude_pycache: Whether to exclude __pycache__ directories

    Returns:
        List of LintResults for each file
    """
    results = []
    dir_path = Path(directory)

    def should_skip_dir(name: str) -> bool:
        if exclude_pycache and name == "__pycache__":
            return True
        if exclude_hidden and name.startswith("."):
            return True
        return False

    def scan_directory(path: Path) -> None:
        try:
            entries = list(path.iterdir())
        except PermissionError:
            return

        for entry in entries:
            if entry.is_file() and entry.suffix == ".py":
                result = lint_file(str(entry), rules=rules)
                result.file_path = str(entry)
                results.append(result)
            elif entry.is_dir() and recursive:
                if not should_skip_dir(entry.name):
                    scan_directory(entry)

    scan_directory(dir_path)
    return results
