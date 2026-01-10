"""Action-related linting rules.

Rules that check for proper use of typed action wrappers.
"""

import ast
import re

from wetwire_github.linter.linter import LintError

from .base import BaseRule

__all__ = ["WAG001TypedActionWrappers", "KNOWN_ACTIONS"]

# Known action wrappers we provide
KNOWN_ACTIONS = {
    "actions/attest-build-provenance",
    "actions/cache",
    "actions/checkout",
    "actions/configure-pages",
    "actions/create-github-app-token",
    "actions/dependency-review-action",
    "actions/deploy-pages",
    "actions/download-artifact",
    "actions/first-interaction",
    "actions/github-script",
    "actions/labeler",
    "actions/setup-dotnet",
    "actions/setup-go",
    "actions/setup-java",
    "actions/setup-node",
    "actions/setup-python",
    "actions/stale",
    "actions/upload-artifact",
    "actions/upload-pages-artifact",
    "actions/upload-release-asset",
    "aws-actions/configure-aws-credentials",
    "codecov/codecov-action",
    "docker/build-push-action",
    "docker/login-action",
    "docker/metadata-action",
    "docker/setup-buildx-action",
    "peaceiris/actions-gh-pages",
    "peter-evans/create-pull-request",
    "ruby/setup-ruby",
    "softprops/action-gh-release",
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
            "actions/attest-build-provenance": "attest_build_provenance",
            "actions/cache": "cache",
            "actions/checkout": "checkout",
            "actions/configure-pages": "configure_pages",
            "actions/create-github-app-token": "create_github_app_token",
            "actions/dependency-review-action": "dependency_review",
            "actions/deploy-pages": "deploy_pages",
            "actions/download-artifact": "download_artifact",
            "actions/first-interaction": "first_interaction",
            "actions/github-script": "github_script",
            "actions/labeler": "labeler",
            "actions/setup-dotnet": "setup_dotnet",
            "actions/setup-go": "setup_go",
            "actions/setup-java": "setup_java",
            "actions/setup-node": "setup_node",
            "actions/setup-python": "setup_python",
            "actions/stale": "stale",
            "actions/upload-artifact": "upload_artifact",
            "actions/upload-pages-artifact": "upload_pages_artifact",
            "actions/upload-release-asset": "upload_release_asset",
            "aws-actions/configure-aws-credentials": "configure_aws_credentials",
            "codecov/codecov-action": "codecov",
            "docker/build-push-action": "docker_build_push",
            "docker/login-action": "docker_login",
            "docker/metadata-action": "docker_metadata",
            "docker/setup-buildx-action": "setup_buildx",
            "peaceiris/actions-gh-pages": "gh_pages",
            "peter-evans/create-pull-request": "create_pull_request",
            "ruby/setup-ruby": "setup_ruby",
            "softprops/action-gh-release": "gh_release",
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
