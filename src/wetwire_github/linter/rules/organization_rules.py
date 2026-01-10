"""Organization-related linting rules.

Rules that check for proper code organization and structure.
"""

import ast

from wetwire_github.linter.linter import LintError

from .base import BaseRule

__all__ = [
    "WAG004UseMatrixBuilder",
    "WAG005ExtractInlineEnvVariables",
    "WAG006DuplicateWorkflowNames",
    "WAG007FileTooLarge",
]


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

        # Extract job names for splitting suggestions
        job_names: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                if self._is_job_call(node.value):
                    # Get the variable name assigned to this Job
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            job_names.append(target.id)

        job_count = len(job_names)

        if job_count > self.max_jobs:
            # Import splitting utilities and generate suggestions
            from wetwire_github.linter.splitting import (
                JobInfo,
                suggest_workflow_splits,
            )

            # Build JobInfo list from job names
            jobs = [JobInfo(name=name, steps=[], dependencies=set()) for name in job_names]
            splits = suggest_workflow_splits(jobs, max_per_file=self.max_jobs)

            # Format suggestion message
            suggestion_parts = [
                f"File has too many jobs ({job_count}), consider splitting into:",
            ]
            for filename, names in sorted(splits.items()):
                suggestion_parts.append(f"  {filename}.py: {', '.join(names)}")

            errors.append(
                LintError(
                    rule_id=self.id,
                    message="\n".join(suggestion_parts),
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
