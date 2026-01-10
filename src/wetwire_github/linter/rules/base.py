"""Base classes for linting rules.

Provides the core infrastructure for defining lint rules.
"""

from abc import ABC, abstractmethod

from wetwire_github.linter.linter import LintError

__all__ = ["BaseRule", "LintError"]


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
