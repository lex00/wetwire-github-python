"""Pattern-related linting rules.

Rules that detect patterns and suggest improvements.
"""

import ast

from wetwire_github.linter.linter import LintError

from .base import BaseRule

__all__ = [
    "WAG011ComplexConditions",
    "WAG012SuggestReusableWorkflows",
]


class WAG011ComplexConditions(BaseRule):
    """WAG011: Flag overly complex conditional logic.

    Detects if_ conditions with many operators and suggests extracting
    to named variables for readability.
    """

    def __init__(self, max_operators: int = 3) -> None:
        self.max_operators = max_operators

    @property
    def id(self) -> str:
        return "WAG011"

    @property
    def description(self) -> str:
        return f"Flag conditions with more than {self.max_operators} operators"

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return errors

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if self._is_step_or_job_call(node):
                    for keyword in node.keywords:
                        if keyword.arg == "if_":
                            complexity = self._count_complexity(keyword.value)
                            if complexity > self.max_operators:
                                errors.append(
                                    LintError(
                                        rule_id=self.id,
                                        message=f"Complex condition (complexity: {complexity}); extract to a named variable",
                                        file_path=file_path,
                                        line=node.lineno,
                                        column=node.col_offset,
                                        suggestion="Create: is_deploy_ready = condition1 & condition2 & condition3",
                                    )
                                )

        return errors

    def _count_complexity(self, node: ast.expr) -> int:
        """Count the complexity of an expression."""
        if isinstance(node, ast.BoolOp):
            # and/or operators
            return len(node.values) - 1 + sum(
                self._count_complexity(v) for v in node.values
            )
        if isinstance(node, ast.Compare):
            # ==, !=, <, >, etc.
            return len(node.ops)
        if isinstance(node, ast.BinOp):
            # &, |, etc.
            return (
                1
                + self._count_complexity(node.left)
                + self._count_complexity(node.right)
            )
        if isinstance(node, ast.UnaryOp):
            # not, ~
            return 1 + self._count_complexity(node.operand)
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            # Count && and || in string expressions
            value = node.value
            return value.count("&&") + value.count("||") + value.count(" and ") + value.count(" or ")
        return 0

    def _is_step_or_job_call(self, node: ast.Call) -> bool:
        """Check if a Call node is a Step() or Job() call."""
        if isinstance(node.func, ast.Name):
            return node.func.id in ("Step", "Job")
        if isinstance(node.func, ast.Attribute):
            return node.func.attr in ("Step", "Job")
        return False


class WAG012SuggestReusableWorkflows(BaseRule):
    """WAG012: Detect duplicated job patterns across workflows.

    Identifies jobs with similar structure that could be extracted
    into reusable workflows.
    """

    @property
    def id(self) -> str:
        return "WAG012"

    @property
    def description(self) -> str:
        return "Suggest reusable workflows for duplicated job patterns"

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return errors

        # Collect job signatures (runs_on + first action)
        job_signatures: dict[str, list[tuple[str, int]]] = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                if self._is_job_call(node.value):
                    signature = self._get_job_signature(node.value)
                    if signature:
                        job_name = ""
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                job_name = target.id
                                break
                        if signature not in job_signatures:
                            job_signatures[signature] = []
                        job_signatures[signature].append((job_name, node.lineno))

        # Report duplicated patterns
        for signature, jobs in job_signatures.items():
            if len(jobs) >= 2:
                job_names = [name for name, _ in jobs]
                errors.append(
                    LintError(
                        rule_id=self.id,
                        message=f"Jobs have similar patterns: {', '.join(job_names)}. Consider a reusable workflow.",
                        file_path=file_path,
                        line=jobs[0][1],
                        column=0,
                        suggestion="Create a reusable workflow with workflow_call trigger",
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

    def _get_job_signature(self, node: ast.Call) -> str | None:
        """Extract a signature from a Job call."""
        runs_on = None
        first_action = None

        for keyword in node.keywords:
            if keyword.arg == "runs_on" and isinstance(keyword.value, ast.Constant):
                runs_on = keyword.value.value
            if keyword.arg == "steps" and isinstance(keyword.value, ast.List):
                # Get first step's uses or run
                if keyword.value.elts:
                    first_step = keyword.value.elts[0]
                    if isinstance(first_step, ast.Call):
                        for step_kw in first_step.keywords:
                            if step_kw.arg == "uses" and isinstance(
                                step_kw.value, ast.Constant
                            ):
                                first_action = step_kw.value.value
                                break

        if runs_on and first_action:
            return f"{runs_on}:{first_action}"
        return None
