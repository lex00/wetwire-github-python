"""Security-related linting rules.

Rules that check for security issues in workflow declarations.
"""

import ast
import re

from wetwire_github.linter.linter import LintError

from .base import BaseRule

__all__ = ["WAG017HardcodedSecretsInRun", "WAG018UnpinnedActions"]

# Patterns for common secret formats
SECRET_PATTERNS = [
    # Generic API keys
    (r"(?i)(api[_-]?key|apikey)\s*[=:]\s*['\"]?([a-zA-Z0-9_-]{16,})", "API key"),
    # Password patterns
    (r"(?i)-p\s*['\"]([^\s'\"]{8,})['\"]", "password"),
    (r"(?i)-p([^\s]{8,})(?:\s|$)", "password"),
    (r"(?i)(password|passwd|pwd)\s*[=:]\s*['\"]?([^\s'\"]{8,})", "password"),
    # AWS credentials
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    (r"(?i)aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*['\"]?([a-zA-Z0-9/+=]{40})", "AWS Secret Key"),
    # Stripe keys
    (r"sk_test_[a-zA-Z0-9]{20,}", "Stripe test key"),
    (r"sk_live_[a-zA-Z0-9]{20,}", "Stripe live key"),
    (r"pk_test_[a-zA-Z0-9]{20,}", "Stripe publishable test key"),
    (r"pk_live_[a-zA-Z0-9]{20,}", "Stripe publishable live key"),
    # GitHub tokens
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub personal access token"),
    (r"ghs_[a-zA-Z0-9]{36}", "GitHub OAuth token"),
    (r"gho_[a-zA-Z0-9]{36}", "GitHub OAuth token"),
    (r"ghu_[a-zA-Z0-9]{36}", "GitHub user token"),
    # Generic tokens
    (r"(?i)(token|auth|bearer)\s*[=:]\s*['\"]?([a-zA-Z0-9_-]{20,})", "token"),
    # Private keys
    (r"-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----", "private key"),
]

# Common actions with their default versions for auto-fix
ACTION_VERSIONS = {
    "actions/checkout": "v4",
    "actions/setup-python": "v5",
    "actions/setup-node": "v4",
    "actions/setup-go": "v5",
    "actions/setup-java": "v4",
    "actions/cache": "v4",
    "actions/upload-artifact": "v4",
    "actions/download-artifact": "v4",
    "actions/github-script": "v7",
    "actions/stale": "v9",
    "actions/labeler": "v5",
}


class WAG017HardcodedSecretsInRun(BaseRule):
    """WAG017: Detect hardcoded secrets in run commands.

    Scans run commands for patterns that look like hardcoded secrets,
    API keys, passwords, tokens, and other sensitive data.
    """

    @property
    def id(self) -> str:
        return "WAG017"

    @property
    def description(self) -> str:
        return "Detect hardcoded secrets in run commands"

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return errors

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Look for Step(..., run="...")
                if self._is_step_call(node):
                    for keyword in node.keywords:
                        if keyword.arg == "run" and isinstance(
                            keyword.value, ast.Constant
                        ):
                            run_value = keyword.value.value
                            if isinstance(run_value, str):
                                # Skip if it uses ${{ secrets.* }}
                                if "${{ secrets." in run_value:
                                    continue

                                # Check for secret patterns
                                for pattern, secret_type in SECRET_PATTERNS:
                                    if re.search(pattern, run_value):
                                        errors.append(
                                            LintError(
                                                rule_id=self.id,
                                                message=f"Possible hardcoded {secret_type} detected in run command",
                                                file_path=file_path,
                                                line=node.lineno,
                                                column=node.col_offset,
                                                suggestion="Use Secrets.get() or ${{ secrets.SECRET_NAME }} to securely access sensitive values",
                                            )
                                        )
                                        break  # Only report once per run command

        return errors

    def _is_step_call(self, node: ast.Call) -> bool:
        """Check if a Call node is a Step() call."""
        if isinstance(node.func, ast.Name):
            return node.func.id == "Step"
        if isinstance(node.func, ast.Attribute):
            return node.func.attr == "Step"
        return False

    def fix(self, source: str, file_path: str) -> tuple[str, int, list[LintError]]:
        """Cannot auto-fix hardcoded secrets - requires manual intervention.

        Returns:
            Tuple of (unchanged_source, 0, original_errors)
        """
        # Cannot auto-fix secrets - they need to be moved to GitHub Secrets
        # and the code needs manual update
        errors = self.check(source, file_path)
        return source, 0, errors


class WAG018UnpinnedActions(BaseRule):
    """WAG018: Detect unpinned actions.

    Actions should be pinned to a specific version (e.g., @v4) or commit SHA
    to prevent supply chain attacks.
    """

    @property
    def id(self) -> str:
        return "WAG018"

    @property
    def description(self) -> str:
        return "Detect unpinned actions that may pose security risks"

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
                                error = self._check_action_pin(
                                    uses_value, file_path, node.lineno, node.col_offset
                                )
                                if error:
                                    errors.append(error)

        return errors

    def _is_step_call(self, node: ast.Call) -> bool:
        """Check if a Call node is a Step() call."""
        if isinstance(node.func, ast.Name):
            return node.func.id == "Step"
        if isinstance(node.func, ast.Attribute):
            return node.func.attr == "Step"
        return False

    def _check_action_pin(
        self, action_ref: str, file_path: str, line: int, column: int
    ) -> LintError | None:
        """Check if an action reference is properly pinned."""
        # Skip local actions (paths starting with ./)
        if action_ref.startswith("./"):
            return None

        # Check if action has a version/ref
        if "@" not in action_ref:
            action_name = action_ref.split("/")[0] + "/" + action_ref.split("/")[1] if "/" in action_ref else action_ref
            suggestion = f"Pin to a version, e.g., {action_ref}@v4"
            if action_name in ACTION_VERSIONS:
                suggestion = f"Pin to a version, e.g., {action_ref}@{ACTION_VERSIONS[action_name]}"

            return LintError(
                rule_id=self.id,
                message=f"Action '{action_ref}' is unpinned (no version specified)",
                file_path=file_path,
                line=line,
                column=column,
                suggestion=suggestion,
            )

        # Check if pinned to a branch instead of SHA or version
        parts = action_ref.split("@", 1)
        if len(parts) == 2:
            ref = parts[1]
            action_name = parts[0]

            # Check if it's a full commit SHA (40 hex characters)
            is_sha = len(ref) == 40 and all(
                c in "0123456789abcdef" for c in ref.lower()
            )

            # Check if it's a version tag (starts with v or contains dots)
            is_version = ref.startswith("v") or "." in ref

            # Common branch names to flag
            branch_names = {"main", "master", "develop", "dev", "latest", "trunk"}

            # If it's neither SHA nor version, it's likely a branch
            if not is_sha and not is_version:
                suggestion = "Pin to a version tag (e.g., @v4) or full commit SHA"
                if action_name in ACTION_VERSIONS:
                    suggestion = f"Pin to @{ACTION_VERSIONS[action_name]} or a full commit SHA"

                severity_note = ""
                if ref.lower() in branch_names:
                    severity_note = f" Branch '{ref}' can change at any time."

                return LintError(
                    rule_id=self.id,
                    message=f"Action '{action_ref}' is pinned to branch '{ref}'.{severity_note}",
                    file_path=file_path,
                    line=line,
                    column=column,
                    suggestion=suggestion,
                )

        return None

    def fix(self, source: str, file_path: str) -> tuple[str, int, list[LintError]]:
        """Fix unpinned actions by adding default version tags.

        Returns:
            Tuple of (fixed_source, fixed_count, remaining_errors)
        """
        fixed_count = 0
        fixed_source = source

        # Pattern to find Step(uses="action") without version
        # Match actions without @ symbol
        for action_name, default_version in ACTION_VERSIONS.items():
            # Pattern: Step(uses="actions/checkout") -> Step(uses="actions/checkout@v4")
            # Handle both single and double quotes
            for quote in ['"', "'"]:
                pattern = re.compile(
                    rf'Step\s*\(\s*uses\s*=\s*{quote}({re.escape(action_name)}){quote}',
                    re.MULTILINE,
                )

                def make_replacement(match: re.Match[str]) -> str:
                    nonlocal fixed_count
                    fixed_count += 1
                    return f'Step(uses={quote}{match.group(1)}@{default_version}{quote}'

                fixed_source = pattern.sub(make_replacement, fixed_source)

        # Check for remaining issues (custom actions, branch pins, etc.)
        remaining_errors = self.check(fixed_source, file_path)

        return fixed_source, fixed_count, remaining_errors
