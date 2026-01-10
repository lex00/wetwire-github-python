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

    def fix(self, source: str, file_path: str) -> tuple[str, int, list[LintError]]:
        """Fix raw action strings by replacing with typed wrappers.

        Returns:
            Tuple of (fixed_source, fixed_count, remaining_errors)
        """
        fixed_count = 0
        fixed_source = source

        # Map of action names to wrapper function names
        action_wrappers = {
            "actions/checkout": "checkout",
            "actions/setup-python": "setup_python",
            "actions/setup-node": "setup_node",
            "actions/setup-go": "setup_go",
            "actions/setup-java": "setup_java",
            "actions/cache": "cache",
            "actions/upload-artifact": "upload_artifact",
            "actions/download-artifact": "download_artifact",
        }

        # Pattern to find Step(uses="actions/...@v...")
        for action_name, wrapper_name in action_wrappers.items():
            # Match Step(uses="action@version") or Step(uses='action@version')
            pattern = re.compile(
                rf'Step\s*\(\s*uses\s*=\s*["\']({re.escape(action_name)}@[^"\']+)["\']\s*\)',
                re.MULTILINE,
            )

            def make_replacement(match: re.Match[str]) -> str:
                nonlocal fixed_count
                fixed_count += 1
                return f"{wrapper_name}()"

            fixed_source = pattern.sub(make_replacement, fixed_source)

        # Check if there are remaining issues
        remaining_errors = self.check(fixed_source, file_path)

        return fixed_source, fixed_count, remaining_errors


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
        return (
            "Detect hardcoded GitHub expression strings; use Expression objects instead"
        )

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


class WAG002UseConditionBuilders(BaseRule):
    """WAG002: Use condition builders instead of raw expressions.

    Detects hardcoded condition function calls like ${{ always() }} and
    suggests using the typed condition builders from expressions module.
    """

    # Pattern to find condition function calls
    _CONDITION_PATTERN = re.compile(
        r"\$\{\{\s*(always|failure|success|cancelled)\(\)\s*\}\}"
    )

    @property
    def id(self) -> str:
        return "WAG002"

    @property
    def description(self) -> str:
        return (
            "Use condition builders (always(), failure(), etc.) instead of raw strings"
        )

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return errors

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check Step and Job calls for if_ parameter
                if self._is_step_or_job_call(node):
                    for keyword in node.keywords:
                        if keyword.arg == "if_" and isinstance(
                            keyword.value, ast.Constant
                        ):
                            value = keyword.value.value
                            if isinstance(value, str):
                                match = self._CONDITION_PATTERN.search(value)
                                if match:
                                    func_name = match.group(1)
                                    errors.append(
                                        LintError(
                                            rule_id=self.id,
                                            message=f"Use {func_name}() helper instead of hardcoded '${{{{ {func_name}() }}}}'",
                                            file_path=file_path,
                                            line=node.lineno,
                                            column=node.col_offset,
                                            suggestion=f"Import {func_name} from wetwire_github.workflow.expressions",
                                        )
                                    )

        return errors

    def _is_step_or_job_call(self, node: ast.Call) -> bool:
        """Check if a Call node is a Step() or Job() call."""
        if isinstance(node.func, ast.Name):
            return node.func.id in ("Step", "Job")
        if isinstance(node.func, ast.Attribute):
            return node.func.attr in ("Step", "Job")
        return False

    def fix(self, source: str, file_path: str) -> tuple[str, int, list[LintError]]:
        """Fix hardcoded condition expressions by replacing with builders.

        Returns:
            Tuple of (fixed_source, fixed_count, remaining_errors)
        """
        fixed_count = 0
        fixed_source = source

        # Replace each condition function
        for func_name in ["always", "failure", "success", "cancelled"]:
            # Pattern to match if_="${{ func() }}" or if_='${{ func() }}'
            pattern = re.compile(
                rf'if_\s*=\s*["\'][^"\']*\$\{{\{{\s*{func_name}\(\)\s*\}}\}}[^"\']*["\']',
                re.MULTILINE,
            )

            def make_replacement(match: re.Match[str]) -> str:
                nonlocal fixed_count
                fixed_count += 1
                return f"if_={func_name}()"

            fixed_source = pattern.sub(make_replacement, fixed_source)

        # Check if there are remaining issues
        remaining_errors = self.check(fixed_source, file_path)

        return fixed_source, fixed_count, remaining_errors


class WAG003UseSecretsContext(BaseRule):
    """WAG003: Use secrets context for secrets access.

    Detects hardcoded secrets access like ${{ secrets.TOKEN }} and
    suggests using Secrets.get() helper. Supports auto-fix.
    """

    # Pattern to find secrets access
    _SECRETS_PATTERN = re.compile(r"\$\{\{\s*secrets\.(\w+)\s*\}\}")

    @property
    def id(self) -> str:
        return "WAG003"

    @property
    def description(self) -> str:
        return "Use Secrets.get() helper instead of hardcoded secrets access"

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return errors

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                match = self._SECRETS_PATTERN.search(node.value)
                if match:
                    secret_name = match.group(1)
                    errors.append(
                        LintError(
                            rule_id=self.id,
                            message=f"Use Secrets.get('{secret_name}') instead of hardcoded '${{{{ secrets.{secret_name} }}}}'",
                            file_path=file_path,
                            line=node.lineno,
                            column=node.col_offset,
                            suggestion=f'Replace with: Secrets.get("{secret_name}")',
                        )
                    )

        return errors

    def fix(self, source: str, file_path: str) -> tuple[str, int, list[LintError]]:
        """Fix hardcoded secrets access by replacing with Secrets.get().

        Returns:
            Tuple of (fixed_source, fixed_count, remaining_errors)
        """
        fixed_count = 0
        fixed_source = source

        # Find all matches and replace them
        def replace_secret(match: re.Match[str]) -> str:
            nonlocal fixed_count
            fixed_count += 1
            secret_name = match.group(1)
            return f'Secrets.get("{secret_name}")'

        fixed_source = self._SECRETS_PATTERN.sub(replace_secret, fixed_source)

        # Check if there are any remaining issues (shouldn't be after fix)
        remaining_errors = self.check(fixed_source, file_path)

        return fixed_source, fixed_count, remaining_errors


class WAG004UseMatrixBuilder(BaseRule):
    """WAG004: Use Matrix builder for matrix configurations.

    Detects raw dict usage for strategy/matrix and suggests using
    the Strategy and Matrix classes.
    """

    @property
    def id(self) -> str:
        return "WAG004"

    @property
    def description(self) -> str:
        return "Use Strategy(matrix=Matrix(...)) instead of raw dicts"

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return errors

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and self._is_job_call(node):
                for keyword in node.keywords:
                    if keyword.arg == "strategy":
                        # Check if strategy is a dict literal
                        if isinstance(keyword.value, ast.Dict):
                            errors.append(
                                LintError(
                                    rule_id=self.id,
                                    message="Use Strategy class instead of raw dict for strategy",
                                    file_path=file_path,
                                    line=keyword.value.lineno,
                                    column=keyword.value.col_offset,
                                    suggestion="Use: Strategy(matrix=Matrix(values={...}))",
                                )
                            )
                        # Check if Strategy call has dict for matrix
                        elif isinstance(keyword.value, ast.Call):
                            if self._is_strategy_call(keyword.value):
                                for strat_kw in keyword.value.keywords:
                                    if strat_kw.arg == "matrix" and isinstance(
                                        strat_kw.value, ast.Dict
                                    ):
                                        errors.append(
                                            LintError(
                                                rule_id=self.id,
                                                message="Use Matrix class instead of raw dict for matrix",
                                                file_path=file_path,
                                                line=strat_kw.value.lineno,
                                                column=strat_kw.value.col_offset,
                                                suggestion="Use: Matrix(values={...})",
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

    def _is_strategy_call(self, node: ast.Call) -> bool:
        """Check if a Call node is a Strategy() call."""
        if isinstance(node.func, ast.Name):
            return node.func.id == "Strategy"
        if isinstance(node.func, ast.Attribute):
            return node.func.attr == "Strategy"
        return False


class WAG005ExtractInlineEnvVariables(BaseRule):
    """WAG005: Extract inline environment variables.

    Detects when the same environment variable is defined in multiple
    steps within a job and suggests extracting to job-level env.
    """

    @property
    def id(self) -> str:
        return "WAG005"

    @property
    def description(self) -> str:
        return "Extract repeated env variables to job or workflow level"

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return errors

        # Find all Step calls and collect their env keys
        env_occurrences: dict[str, list[int]] = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and self._is_step_call(node):
                for keyword in node.keywords:
                    if keyword.arg == "env" and isinstance(keyword.value, ast.Dict):
                        for key in keyword.value.keys:
                            if isinstance(key, ast.Constant) and isinstance(
                                key.value, str
                            ):
                                key_name = key.value
                                if key_name not in env_occurrences:
                                    env_occurrences[key_name] = []
                                env_occurrences[key_name].append(node.lineno)

        # Report keys that appear in multiple steps
        for key_name, lines in env_occurrences.items():
            if len(lines) >= 2:
                errors.append(
                    LintError(
                        rule_id=self.id,
                        message=f"Env variable '{key_name}' defined in {len(lines)} steps; consider extracting to job-level env",
                        file_path=file_path,
                        line=lines[0],
                        column=0,
                        suggestion="Move to Job(env={...}) or Workflow(env={...})",
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


def get_default_rules() -> list[BaseRule]:
    """Return the default set of linting rules."""
    return [
        WAG001TypedActionWrappers(),
        WAG002UseConditionBuilders(),
        WAG003UseSecretsContext(),
        WAG004UseMatrixBuilder(),
        WAG005ExtractInlineEnvVariables(),
        WAG006DuplicateWorkflowNames(),
        WAG007FileTooLarge(),
        WAG008HardcodedExpressions(),
    ]
