"""Linting rules for workflow declarations.

Each rule follows the WAG (Workflow Actions Guidelines) naming convention.
"""

import ast
import re
from typing import TYPE_CHECKING

from .linter import BaseRule, LintError

if TYPE_CHECKING:
    pass

# Known action wrappers we provide
KNOWN_ACTIONS = {
    "actions/checkout",
    "actions/setup-python",
    "actions/setup-node",
    "actions/setup-go",
    "actions/setup-java",
    "actions/cache",
    "actions/upload-artifact",
    "actions/download-artifact",
}


class WAG001TypedActionWrappers(BaseRule):
    """WAG001: Use typed action wrappers instead of raw strings.

    Encourages use of type-safe action wrapper functions instead of
    raw 'uses' strings for known actions.
    """

    @property
    def id(self) -> str:
        return "WAG001"

    @property
    def description(self) -> str:
        return "Use typed action wrappers instead of raw 'uses' strings"

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return errors

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Look for Step(..., uses="...")
                if self._is_step_call(node):
                    for keyword in node.keywords:
                        if keyword.arg == "uses" and isinstance(
                            keyword.value, ast.Constant
                        ):
                            uses_value = keyword.value.value
                            if isinstance(uses_value, str):
                                # Check if it's a known action
                                action_name = uses_value.split("@")[0]
                                if action_name in KNOWN_ACTIONS:
                                    errors.append(
                                        LintError(
                                            rule_id=self.id,
                                            message=f"Use typed action wrapper instead of raw string '{uses_value}'",
                                            file_path=file_path,
                                            line=node.lineno,
                                            column=node.col_offset,
                                            suggestion="Import and use the typed wrapper function",
                                        )
                                    )
        return errors

    def _is_step_call(self, node: ast.Call) -> bool:
        """Check if a Call node is a Step() call."""
        if isinstance(node.func, ast.Name):
            return node.func.id == "Step"
        if isinstance(node.func, ast.Attribute):
            return node.func.attr == "Step"
        return False


class WAG006DuplicateWorkflowNames(BaseRule):
    """WAG006: Detect duplicate workflow names in the same file."""

    @property
    def id(self) -> str:
        return "WAG006"

    @property
    def description(self) -> str:
        return "Detect duplicate workflow names in the same file"

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return errors

        # Collect workflow names
        workflow_names: dict[str, list[int]] = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and self._is_workflow_call(node):
                for keyword in node.keywords:
                    if keyword.arg == "name" and isinstance(
                        keyword.value, ast.Constant
                    ):
                        name = keyword.value.value
                        if isinstance(name, str):
                            if name not in workflow_names:
                                workflow_names[name] = []
                            workflow_names[name].append(node.lineno)

        # Report duplicates
        for name, lines in workflow_names.items():
            if len(lines) > 1:
                for line in lines[1:]:  # Skip first occurrence
                    errors.append(
                        LintError(
                            rule_id=self.id,
                            message=f"Duplicate workflow name '{name}' (first defined at line {lines[0]})",
                            file_path=file_path,
                            line=line,
                            column=0,
                        )
                    )

        return errors

    def _is_workflow_call(self, node: ast.Call) -> bool:
        """Check if a Call node is a Workflow() call."""
        if isinstance(node.func, ast.Name):
            return node.func.id == "Workflow"
        if isinstance(node.func, ast.Attribute):
            return node.func.attr == "Workflow"
        return False


class WAG007FileTooLarge(BaseRule):
    """WAG007: Warn when a file has too many jobs."""

    def __init__(self, max_jobs: int = 10) -> None:
        self.max_jobs = max_jobs

    @property
    def id(self) -> str:
        return "WAG007"

    @property
    def description(self) -> str:
        return f"Warn when a file has more than {self.max_jobs} jobs"

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return errors

        job_count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and self._is_job_call(node):
                job_count += 1

        if job_count > self.max_jobs:
            errors.append(
                LintError(
                    rule_id=self.id,
                    message=f"File has too many jobs ({job_count}), consider splitting into multiple files",
                    file_path=file_path,
                    line=1,
                    column=0,
                )
            )

        return errors

    def _is_job_call(self, node: ast.Call) -> bool:
        """Check if a Call node is a Job() call."""
        if isinstance(node.func, ast.Name):
            return node.func.id == "Job"
        if isinstance(node.func, ast.Attribute):
            return node.func.attr == "Job"
        return False


class WAG008HardcodedExpressions(BaseRule):
    """WAG008: Detect hardcoded ${{ }} expression strings."""

    # Pattern to find GitHub expression syntax
    _EXPRESSION_PATTERN = re.compile(r"\$\{\{.*?\}\}")

    @property
    def id(self) -> str:
        return "WAG008"

    @property
    def description(self) -> str:
        return "Detect hardcoded GitHub expression strings; use Expression objects instead"

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return errors

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if self._EXPRESSION_PATTERN.search(node.value):
                    errors.append(
                        LintError(
                            rule_id=self.id,
                            message=f"Hardcoded expression string '{node.value[:50]}...'; use Expression objects",
                            file_path=file_path,
                            line=node.lineno,
                            column=node.col_offset,
                            suggestion="Use wetwire_github.workflow.expressions helpers",
                        )
                    )

        return errors


def get_default_rules() -> list[BaseRule]:
    """Return the default set of linting rules."""
    return [
        WAG001TypedActionWrappers(),
        WAG006DuplicateWorkflowNames(),
        WAG007FileTooLarge(),
        WAG008HardcodedExpressions(),
    ]
