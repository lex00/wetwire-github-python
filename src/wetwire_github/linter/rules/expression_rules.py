"""Expression-related linting rules.

Rules that check for proper use of expression builders and typed helpers.
"""

import ast
import re

from wetwire_github.linter.linter import LintError

from .base import BaseRule

__all__ = [
    "WAG002UseConditionBuilders",
    "WAG003UseSecretsContext",
    "WAG008HardcodedExpressions",
]


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
