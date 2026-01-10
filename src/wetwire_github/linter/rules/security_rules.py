"""Security-related linting rules.

Rules that check for security issues in workflow declarations.
"""

import ast
import re

from wetwire_github.linter.linter import LintError

from .base import BaseRule

__all__ = [
    "WAG017HardcodedSecretsInRun",
    "WAG018UnpinnedActions",
    "WAG019UnusedPermissions",
    "WAG020OverlyPermissiveSecrets",
    "WAG021MissingOIDCConfiguration",
    "WAG022ImplicitEnvironmentExposure",
]

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


# Mapping of common actions to their required permissions
ACTION_PERMISSION_REQUIREMENTS = {
    "actions/checkout": {"contents": "read"},
    "actions/upload-artifact": {"actions": "read"},
    "actions/download-artifact": {"actions": "read"},
    "actions/cache": {"actions": "read"},
    "actions/github-script": {"contents": "read"},
    "peter-evans/create-pull-request": {"contents": "write", "pull-requests": "write"},
    "stefanzweifel/git-auto-commit-action": {"contents": "write"},
    "peaceiris/actions-gh-pages": {"contents": "write"},
    "docker/build-push-action": {"packages": "write"},
    "docker/login-action": {"packages": "write"},
}

# User-controlled GitHub context paths that could be exploited
USER_CONTROLLED_CONTEXTS = [
    "github.event.issue.title",
    "github.event.issue.body",
    "github.event.pull_request.title",
    "github.event.pull_request.body",
    "github.event.comment.body",
    "github.event.review.body",
    "github.event.head_commit.message",
    "github.event.commits",
    "github.head_ref",
    "github.event.pages",
    "github.event.discussion.title",
    "github.event.discussion.body",
]


class WAG019UnusedPermissions(BaseRule):
    """WAG019: Detect unused permissions grants.

    Flags permissions that are declared but not needed by any step in the job.
    This helps follow the principle of least privilege.
    """

    @property
    def id(self) -> str:
        return "WAG019"

    @property
    def description(self) -> str:
        return "Detect unused permissions grants"

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return errors

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if self._is_job_call(node):
                    permissions = self._extract_permissions(node)
                    steps = self._extract_steps(node)

                    if permissions is None:
                        continue

                    # Check for overly broad permissions
                    if isinstance(permissions, str) and permissions in (
                        "write-all",
                        "read-all",
                    ):
                        errors.append(
                            LintError(
                                rule_id=self.id,
                                message=f"Overly broad '{permissions}' permission. Consider using specific permissions.",
                                file_path=file_path,
                                line=node.lineno,
                                column=node.col_offset,
                                suggestion="Use specific permissions like {'contents': 'read'} instead of broad grants",
                            )
                        )
                        continue

                    # Check for unused specific permissions
                    if isinstance(permissions, dict):
                        used_permissions = self._get_used_permissions(steps)
                        for perm, level in permissions.items():
                            if perm not in used_permissions:
                                errors.append(
                                    LintError(
                                        rule_id=self.id,
                                        message=f"Permission '{perm}: {level}' appears unused",
                                        file_path=file_path,
                                        line=node.lineno,
                                        column=node.col_offset,
                                        suggestion=f"Remove '{perm}' permission or verify it's needed",
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

    def _extract_permissions(
        self, node: ast.Call
    ) -> dict[str, str] | str | None:
        """Extract permissions from a Job call."""
        for keyword in node.keywords:
            if keyword.arg == "permissions":
                if isinstance(keyword.value, ast.Constant):
                    val = keyword.value.value
                    if isinstance(val, str):
                        return val
                    return None
                if isinstance(keyword.value, ast.Dict):
                    perms: dict[str, str] = {}
                    for key, val in zip(keyword.value.keys, keyword.value.values):
                        if isinstance(key, ast.Constant) and isinstance(
                            val, ast.Constant
                        ):
                            k = key.value
                            v = val.value
                            if isinstance(k, str) and isinstance(v, str):
                                perms[k] = v
                    return perms
        return None

    def _extract_steps(self, node: ast.Call) -> list[str]:
        """Extract action uses from steps in a Job call."""
        actions = []
        for keyword in node.keywords:
            if keyword.arg == "steps" and isinstance(keyword.value, ast.List):
                for step in keyword.value.elts:
                    if isinstance(step, ast.Call):
                        for step_kw in step.keywords:
                            if step_kw.arg == "uses" and isinstance(
                                step_kw.value, ast.Constant
                            ):
                                actions.append(step_kw.value.value)
        return actions

    def _get_used_permissions(self, actions: list[str]) -> set[str]:
        """Get the set of permissions used by the given actions."""
        used = set()
        for action in actions:
            # Strip version from action reference
            action_name = action.split("@")[0] if "@" in action else action
            if action_name in ACTION_PERMISSION_REQUIREMENTS:
                used.update(ACTION_PERMISSION_REQUIREMENTS[action_name].keys())
        return used

    def fix(self, source: str, file_path: str) -> tuple[str, int, list[LintError]]:
        """Fix unused permissions by removing them from Job declarations.

        Returns:
            Tuple of (fixed_source, fixed_count, remaining_errors)
        """
        fixed_count = 0
        fixed_source = source

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return source, 0, self.check(source, file_path)

        # Find all Job calls with unused permissions
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and self._is_job_call(node):
                permissions = self._extract_permissions(node)
                steps = self._extract_steps(node)

                if permissions is None:
                    continue

                # Can only auto-fix dict-based permissions, not "write-all" or "read-all"
                if isinstance(permissions, str):
                    continue

                # Find unused permissions
                if isinstance(permissions, dict):
                    used_permissions = self._get_used_permissions(steps)
                    unused_perms = [
                        perm for perm in permissions.keys() if perm not in used_permissions
                    ]

                    if unused_perms:
                        # Build the fixed permissions dict
                        fixed_perms = {
                            k: v for k, v in permissions.items() if k in used_permissions
                        }

                        # Find the permissions keyword argument
                        for keyword in node.keywords:
                            if keyword.arg == "permissions" and isinstance(
                                keyword.value, ast.Dict
                            ):
                                # Replace the entire permissions dict
                                if fixed_perms:
                                    # Keep used permissions
                                    new_perms_str = self._format_permissions_dict(fixed_perms)
                                else:
                                    # Remove permissions entirely if none are used
                                    new_perms_str = None

                                # Perform the replacement
                                fixed_source = self._replace_permissions_in_source(
                                    fixed_source,
                                    keyword.value,
                                    new_perms_str,
                                )
                                fixed_count += len(unused_perms)

        # Check for remaining errors
        remaining_errors = self.check(fixed_source, file_path)

        return fixed_source, fixed_count, remaining_errors

    def _format_permissions_dict(self, perms: dict[str, str]) -> str:
        """Format permissions dict as Python code."""
        items = [f'"{k}": "{v}"' for k, v in perms.items()]
        return "{" + ", ".join(items) + "}"

    def _replace_permissions_in_source(
        self, source: str, dict_node: ast.Dict, new_perms_str: str | None
    ) -> str:
        """Replace permissions dict in source code."""
        lines = source.splitlines(keepends=True)

        start_line = dict_node.lineno
        start_col = dict_node.col_offset
        end_line = dict_node.end_lineno or start_line
        end_col = dict_node.end_col_offset or start_col

        if new_perms_str is None:
            # Remove the entire permissions= keyword argument
            # This is more complex - for now, just replace with empty dict
            new_perms_str = "{}"

        # Replace the dict
        if start_line == end_line:
            # Single line replacement
            line = lines[start_line - 1]
            lines[start_line - 1] = line[:start_col] + new_perms_str + line[end_col:]
        else:
            # Multi-line dict replacement
            lines[start_line - 1] = (
                lines[start_line - 1][:start_col] + new_perms_str + "\n"
            )
            # Remove intermediate lines
            for _ in range(end_line - start_line):
                del lines[start_line]
            # Adjust the line after the dict
            if start_line < len(lines):
                lines[start_line] = lines[start_line][end_col:]

        return "".join(lines)


class WAG020OverlyPermissiveSecrets(BaseRule):
    """WAG020: Warn if secrets are used in run commands without explicit masking.

    Secrets should be passed via environment variables rather than directly
    interpolated into shell commands to avoid accidental exposure.
    """

    @property
    def id(self) -> str:
        return "WAG020"

    @property
    def description(self) -> str:
        return "Warn about secrets used directly in run commands"

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return errors

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if self._is_step_call(node):
                    run_value = None

                    for keyword in node.keywords:
                        if keyword.arg == "run" and isinstance(
                            keyword.value, ast.Constant
                        ):
                            run_value = keyword.value.value

                    if run_value and isinstance(run_value, str):
                        # Check for secrets directly in run command
                        if "${{ secrets." in run_value:
                            errors.append(
                                LintError(
                                    rule_id=self.id,
                                    message="Secret used directly in run command may be exposed in logs",
                                    file_path=file_path,
                                    line=node.lineno,
                                    column=node.col_offset,
                                    suggestion="Pass secrets via env variables: env={'TOKEN': '${{ secrets.TOKEN }}'} and use $TOKEN in the command",
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


# Cloud provider action patterns for OIDC detection
CLOUD_PROVIDER_ACTIONS: dict[str, dict[str, list[str] | str]] = {
    "aws-actions/configure-aws-credentials": {
        "static_creds": ["aws-access-key-id", "aws-secret-access-key"],
        "oidc_creds": ["role-to-assume"],
        "provider": "AWS",
        "suggestion": "Use OIDC with 'role-to-assume' instead of static AWS credentials",
    },
    "google-github-actions/auth": {
        "static_creds": ["credentials_json"],
        "oidc_creds": ["workload_identity_provider"],
        "provider": "GCP",
        "suggestion": "Use Workload Identity Federation instead of service account JSON key",
    },
    "azure/login": {
        "static_creds": ["creds"],
        "oidc_creds": ["client-id", "tenant-id", "subscription-id"],
        "provider": "Azure",
        "suggestion": "Use OIDC with federated credentials instead of service principal secret",
    },
}


class WAG021MissingOIDCConfiguration(BaseRule):
    """WAG021: Suggest OpenID Connect for cloud provider auth.

    Long-lived credentials stored as secrets are less secure than
    using OIDC-based authentication with cloud providers.
    """

    @property
    def id(self) -> str:
        return "WAG021"

    @property
    def description(self) -> str:
        return "Suggest OIDC for cloud provider authentication"

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return errors

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if self._is_step_call(node):
                    uses_value = None
                    with_dict = {}

                    for keyword in node.keywords:
                        if keyword.arg == "uses" and isinstance(
                            keyword.value, ast.Constant
                        ):
                            val = keyword.value.value
                            if isinstance(val, str):
                                uses_value = val
                        if keyword.arg in ("with_", "with") and isinstance(
                            keyword.value, ast.Dict
                        ):
                            for key, val in zip(
                                keyword.value.keys, keyword.value.values
                            ):
                                if isinstance(key, ast.Constant):
                                    k = key.value
                                    if isinstance(k, str):
                                        with_dict[k] = (
                                            val.value
                                            if isinstance(val, ast.Constant)
                                            else None
                                        )

                    if uses_value is not None:
                        # Strip version from action
                        action_name = (
                            uses_value.split("@")[0]
                            if "@" in uses_value
                            else uses_value
                        )

                        if action_name in CLOUD_PROVIDER_ACTIONS:
                            config = CLOUD_PROVIDER_ACTIONS[action_name]
                            static_creds = config["static_creds"]
                            oidc_creds = config["oidc_creds"]
                            provider = config["provider"]
                            suggestion = config["suggestion"]

                            # Check if using static credentials
                            if isinstance(static_creds, list) and isinstance(
                                oidc_creds, list
                            ):
                                uses_static = any(
                                    key in with_dict for key in static_creds
                                )
                                uses_oidc = any(
                                    key in with_dict for key in oidc_creds
                                )

                                if uses_static and not uses_oidc:
                                    suggestion_str = (
                                        suggestion
                                        if isinstance(suggestion, str)
                                        else None
                                    )
                                    errors.append(
                                        LintError(
                                            rule_id=self.id,
                                            message=f"{provider} action uses static credentials instead of OIDC",
                                            file_path=file_path,
                                            line=node.lineno,
                                            column=node.col_offset,
                                            suggestion=suggestion_str,
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


class WAG022ImplicitEnvironmentExposure(BaseRule):
    """WAG022: Warn about implicit environment exposure in shell scripts.

    User-controlled input (like issue titles, PR bodies) can contain
    malicious shell commands if not properly quoted/escaped.
    """

    @property
    def id(self) -> str:
        return "WAG022"

    @property
    def description(self) -> str:
        return "Warn about unescaped user-controlled input in shell commands"

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return errors

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if self._is_step_call(node):
                    run_value = None
                    env_vars = {}

                    for keyword in node.keywords:
                        if keyword.arg == "run" and isinstance(
                            keyword.value, ast.Constant
                        ):
                            run_value = keyword.value.value
                        if keyword.arg == "env" and isinstance(
                            keyword.value, ast.Dict
                        ):
                            for key, val in zip(
                                keyword.value.keys, keyword.value.values
                            ):
                                if isinstance(key, ast.Constant) and isinstance(
                                    val, ast.Constant
                                ):
                                    env_vars[key.value] = val.value

                    if run_value and isinstance(run_value, str):
                        # Check for direct user-controlled context injection
                        error = self._check_direct_injection(
                            run_value, file_path, node.lineno, node.col_offset
                        )
                        if error:
                            errors.append(error)
                            continue

                        # Check for unquoted env vars from user input
                        error = self._check_unquoted_env_vars(
                            run_value,
                            env_vars,
                            file_path,
                            node.lineno,
                            node.col_offset,
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

    def _check_direct_injection(
        self, run_value: str, file_path: str, line: int, column: int
    ) -> LintError | None:
        """Check for user-controlled context directly in run command."""
        for context_path in USER_CONTROLLED_CONTEXTS:
            pattern = rf"\$\{{\{{\s*{re.escape(context_path)}\s*\}}\}}"
            if re.search(pattern, run_value):
                return LintError(
                    rule_id=self.id,
                    message=f"User-controlled input '{context_path}' used directly in shell command",
                    file_path=file_path,
                    line=line,
                    column=column,
                    suggestion="Pass user input via env variable and properly quote it: \"$VAR\"",
                )
        return None

    def _check_unquoted_env_vars(
        self,
        run_value: str,
        env_vars: dict[str, str],
        file_path: str,
        line: int,
        column: int,
    ) -> LintError | None:
        """Check for unquoted env vars that contain user input."""
        for var_name, var_value in env_vars.items():
            if var_value is None:
                continue

            # Check if env var contains user-controlled input
            is_user_controlled = any(
                context in var_value for context in USER_CONTROLLED_CONTEXTS
            )

            if is_user_controlled:
                # Check if the variable is used unquoted in the run command
                # Pattern: $VAR_NAME not inside quotes
                unquoted_pattern = rf'(?<!["\'])\$(?:\{{{var_name}\}}|{var_name})(?!["\'])'
                if re.search(unquoted_pattern, run_value):
                    return LintError(
                        rule_id=self.id,
                        message=f"Environment variable ${var_name} contains user input and is not properly quoted",
                        file_path=file_path,
                        line=line,
                        column=column,
                        suggestion=f'Quote the variable: "${var_name}" instead of ${var_name}',
                    )
        return None
