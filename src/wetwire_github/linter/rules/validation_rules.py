"""Validation-related linting rules.

Rules that validate webhook event types and secrets documentation.
"""

import ast
import re

from wetwire_github.linter.linter import LintError

from .base import BaseRule

__all__ = [
    "WAG009ValidateEventTypes",
    "WAG010MissingSecretVariables",
    "WAG049ValidateWorkflowInputs",
    "VALID_EVENT_TYPES",
]

# Valid GitHub Actions event types
VALID_EVENT_TYPES = {
    "branch_protection_rule",
    "check_run",
    "check_suite",
    "create",
    "delete",
    "deployment",
    "deployment_status",
    "discussion",
    "discussion_comment",
    "fork",
    "gollum",
    "issue_comment",
    "issues",
    "label",
    "merge_group",
    "milestone",
    "page_build",
    "project",
    "project_card",
    "project_column",
    "public",
    "pull_request",
    "pull_request_comment",
    "pull_request_review",
    "pull_request_review_comment",
    "pull_request_target",
    "push",
    "registry_package",
    "release",
    "repository_dispatch",
    "schedule",
    "status",
    "watch",
    "workflow_call",
    "workflow_dispatch",
    "workflow_run",
}


class WAG009ValidateEventTypes(BaseRule):
    """WAG009: Validate webhook event types in triggers.

    Ensures that workflow triggers use valid GitHub event types.
    """

    @property
    def id(self) -> str:
        return "WAG009"

    @property
    def description(self) -> str:
        return "Validate webhook event types in triggers"

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return errors

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and self._is_workflow_call(node):
                for keyword in node.keywords:
                    if keyword.arg == "on":
                        # Check if it's a dict literal
                        if isinstance(keyword.value, ast.Dict):
                            for key in keyword.value.keys:
                                if isinstance(key, ast.Constant) and isinstance(
                                    key.value, str
                                ):
                                    event_name = key.value
                                    if event_name not in VALID_EVENT_TYPES:
                                        errors.append(
                                            LintError(
                                                rule_id=self.id,
                                                message=f"Unknown event type '{event_name}'",
                                                file_path=file_path,
                                                line=key.lineno,
                                                column=key.col_offset,
                                                suggestion=f"Valid events: {', '.join(sorted(VALID_EVENT_TYPES)[:5])}...",
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


class WAG010MissingSecretVariables(BaseRule):
    """WAG010: Detect secrets used but not documented.

    Flags secrets referenced in expressions that aren't defined in the
    file, helping identify missing secret documentation.
    """

    # Pattern to find secrets access
    _SECRETS_PATTERN = re.compile(r"\$\{\{\s*secrets\.(\w+)\s*\}\}")
    _SECRETS_GET_PATTERN = re.compile(r'Secrets\.get\(["\'](\w+)["\']\)')

    @property
    def id(self) -> str:
        return "WAG010"

    @property
    def description(self) -> str:
        return "Detect secrets used in code to help document required secrets"

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        secrets_used: set[str] = set()

        # Find all secrets referenced
        for match in self._SECRETS_PATTERN.finditer(source):
            secrets_used.add(match.group(1))
        for match in self._SECRETS_GET_PATTERN.finditer(source):
            secrets_used.add(match.group(1))

        # Report secrets that should be documented
        if secrets_used:
            errors.append(
                LintError(
                    rule_id=self.id,
                    message=f"Secrets used: {', '.join(sorted(secrets_used))}. Ensure these are documented in your README.",
                    file_path=file_path,
                    line=1,
                    column=0,
                    suggestion="Add a 'Required Secrets' section to your documentation",
                )
            )

        return errors


class WAG049ValidateWorkflowInputs(BaseRule):
    """WAG049: Validate workflow inputs have descriptions.

    Ensures that all workflow_dispatch and workflow_call inputs have:
    - Non-empty descriptions
    - At least 2 options for choice type inputs
    """

    @property
    def id(self) -> str:
        return "WAG049"

    @property
    def description(self) -> str:
        return "Validate workflow inputs have descriptions and choice inputs have sufficient options"

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return errors

        for node in ast.walk(tree):
            # Look for WorkflowDispatchTrigger and WorkflowCallTrigger calls
            if isinstance(node, ast.Call) and self._is_trigger_call(node):
                # Find the inputs keyword argument
                for keyword in node.keywords:
                    if keyword.arg == "inputs" and isinstance(keyword.value, ast.Dict):
                        # Check each input in the dict
                        for key, value in zip(keyword.value.keys, keyword.value.values):
                            if isinstance(key, ast.Constant) and isinstance(
                                key.value, str
                            ):
                                input_name = key.value
                                # Check if value is a WorkflowInput call
                                if isinstance(value, ast.Call) and self._is_workflow_input_call(value):
                                    self._validate_input(
                                        value, input_name, file_path, errors
                                    )

        return errors

    def _is_trigger_call(self, node: ast.Call) -> bool:
        """Check if a Call node is a WorkflowDispatchTrigger or WorkflowCallTrigger call."""
        if isinstance(node.func, ast.Name):
            return node.func.id in ("WorkflowDispatchTrigger", "WorkflowCallTrigger")
        if isinstance(node.func, ast.Attribute):
            return node.func.attr in ("WorkflowDispatchTrigger", "WorkflowCallTrigger")
        return False

    def _is_workflow_input_call(self, node: ast.Call) -> bool:
        """Check if a Call node is a WorkflowInput call."""
        if isinstance(node.func, ast.Name):
            return node.func.id == "WorkflowInput"
        if isinstance(node.func, ast.Attribute):
            return node.func.attr == "WorkflowInput"
        return False

    def _validate_input(
        self, node: ast.Call, input_name: str, file_path: str, errors: list[LintError]
    ) -> None:
        """Validate a WorkflowInput node."""
        description = None
        input_type = None
        options = None

        # Extract description, type, and options from keyword arguments
        for keyword in node.keywords:
            if keyword.arg == "description":
                if isinstance(keyword.value, ast.Constant):
                    description = keyword.value.value
            elif keyword.arg == "type":
                if isinstance(keyword.value, ast.Constant):
                    input_type = keyword.value.value
            elif keyword.arg == "options":
                if isinstance(keyword.value, ast.List):
                    options = keyword.value.elts

        # Check if description is missing or empty
        if not description or (isinstance(description, str) and not description.strip()):
            errors.append(
                LintError(
                    rule_id=self.id,
                    message=f"Input '{input_name}' is missing a description",
                    file_path=file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    suggestion="Add a description parameter to WorkflowInput to document what this input is for",
                )
            )

        # Check choice type has at least 2 options
        if input_type == "choice":
            if options is None or len(options) < 2:
                errors.append(
                    LintError(
                        rule_id=self.id,
                        message=f"Input '{input_name}' has type 'choice' but fewer than 2 options",
                        file_path=file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        suggestion="Choice inputs should have at least 2 options. Consider using 'string' or 'boolean' type if only one option is needed.",
                    )
                )
