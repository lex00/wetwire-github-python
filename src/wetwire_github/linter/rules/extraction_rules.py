"""Extraction-related linting rules.

Rules for detecting inline structures that should be extracted to named variables.
"""

import ast
import re

from wetwire_github.linter.linter import LintError

from .base import BaseRule

__all__ = [
    "WAG013InlineEnvVariables",
    "WAG014InlineMatrixConfig",
    "WAG015InlineOutputs",
]


class WAG013InlineEnvVariables(BaseRule):
    """WAG013: Extract inline environment variables.

    Detects when Step() has a large inline env dict and suggests
    extracting to a named variable for readability.
    """

    def __init__(self, max_inline: int = 3) -> None:
        self.max_inline = max_inline

    @property
    def id(self) -> str:
        return "WAG013"

    @property
    def description(self) -> str:
        return f"Extract inline env dicts with >{self.max_inline} variables"

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return errors

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and self._is_step_call(node):
                for keyword in node.keywords:
                    if keyword.arg == "env" and isinstance(keyword.value, ast.Dict):
                        num_keys = len(keyword.value.keys)
                        if num_keys > self.max_inline:
                            errors.append(
                                LintError(
                                    rule_id=self.id,
                                    message=f"Step has {num_keys} inline env variables; extract to a named variable",
                                    file_path=file_path,
                                    line=keyword.value.lineno,
                                    column=keyword.value.col_offset,
                                    suggestion="Create: step_env = {...}; Step(..., env=step_env)",
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
        """Fix inline env by extracting to a variable.

        Returns:
            Tuple of (fixed_source, fixed_count, remaining_errors)
        """
        fixed_count = 0
        fixed_source = source

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return source, 0, self.check(source, file_path)

        # Find assignments with Step calls that have inline env
        replacements: list[tuple[int, int, str, str]] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                if self._is_step_call(node.value):
                    # Get the variable name
                    var_name = ""
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            var_name = target.id
                            break

                    for keyword in node.value.keywords:
                        if keyword.arg == "env" and isinstance(keyword.value, ast.Dict):
                            num_keys = len(keyword.value.keys)
                            if num_keys > self.max_inline:
                                # Extract the dict source
                                env_start = keyword.value.lineno
                                env_col = keyword.value.col_offset
                                env_end = keyword.value.end_lineno or env_start
                                env_end_col = keyword.value.end_col_offset or env_col

                                env_var_name = f"{var_name}_env" if var_name else "step_env"
                                replacements.append(
                                    (env_start, env_col, env_end, env_end_col, env_var_name, node.lineno)  # type: ignore[misc]
                                )

        if not replacements:
            return source, 0, self.check(source, file_path)

        # Apply replacements (simple approach: regex-based)
        lines = source.splitlines(keepends=True)

        for start_line, start_col, end_line, end_col, var_name, assign_line in reversed(replacements):  # type: ignore[assignment]
            # Extract the inline dict
            if start_line == end_line:
                dict_str = lines[start_line - 1][start_col:end_col]
            else:
                dict_str = lines[start_line - 1][start_col:]
                for i in range(start_line, end_line - 1):
                    dict_str += lines[i]
                dict_str += lines[end_line - 1][:end_col]

            # Create the extracted variable declaration
            indent = len(lines[assign_line - 1]) - len(lines[assign_line - 1].lstrip())
            new_var_line = " " * indent + f"{var_name} = {dict_str.strip()}\n"

            # Replace inline dict with variable reference
            if start_line == end_line:
                lines[start_line - 1] = (
                    lines[start_line - 1][:start_col] + var_name + lines[start_line - 1][end_col:]
                )
            else:
                # Multi-line dict
                lines[start_line - 1] = lines[start_line - 1][:start_col] + var_name + "\n"
                # Remove intermediate lines
                for i in range(end_line - 2, start_line - 1, -1):
                    del lines[i]
                # Adjust last line
                if end_line > start_line:
                    remaining_idx = start_line  # After deletions
                    if remaining_idx < len(lines):
                        lines[remaining_idx] = lines[remaining_idx][end_col:]

            # Insert the new variable before the assignment
            insert_line = assign_line - 1
            lines.insert(insert_line, new_var_line)
            fixed_count += 1

        fixed_source = "".join(lines)
        remaining_errors = self.check(fixed_source, file_path)

        return fixed_source, fixed_count, remaining_errors


class WAG014InlineMatrixConfig(BaseRule):
    """WAG014: Extract inline matrix configuration.

    Detects complex inline Matrix definitions and suggests extraction.
    """

    def __init__(self, max_keys: int = 2, max_values_per_key: int = 3) -> None:
        self.max_keys = max_keys
        self.max_values_per_key = max_values_per_key

    @property
    def id(self) -> str:
        return "WAG014"

    @property
    def description(self) -> str:
        return f"Extract complex inline matrix (>{self.max_keys} keys or >{self.max_values_per_key} values)"

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return errors

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and self._is_job_call(node):
                for keyword in node.keywords:
                    if keyword.arg == "strategy" and isinstance(keyword.value, ast.Call):
                        if self._is_strategy_call(keyword.value):
                            matrix_error = self._check_strategy_for_matrix(
                                keyword.value, file_path
                            )
                            if matrix_error:
                                errors.append(matrix_error)

        return errors

    def _check_strategy_for_matrix(
        self, strategy_node: ast.Call, file_path: str
    ) -> LintError | None:
        """Check Strategy call for complex inline Matrix."""
        for kw in strategy_node.keywords:
            if kw.arg == "matrix" and isinstance(kw.value, ast.Call):
                if self._is_matrix_call(kw.value):
                    # Check values parameter
                    for matrix_kw in kw.value.keywords:
                        if matrix_kw.arg == "values" and isinstance(
                            matrix_kw.value, ast.Dict
                        ):
                            is_complex = self._is_complex_matrix(matrix_kw.value)
                            if is_complex:
                                return LintError(
                                    rule_id=self.id,
                                    message="Complex inline matrix configuration; extract to a named variable",
                                    file_path=file_path,
                                    line=kw.value.lineno,
                                    column=kw.value.col_offset,
                                    suggestion="Create: job_matrix = Matrix(...); Strategy(matrix=job_matrix)",
                                )
        return None

    def _is_complex_matrix(self, dict_node: ast.Dict) -> bool:
        """Check if a matrix values dict is complex."""
        num_keys = len(dict_node.keys)
        if num_keys > self.max_keys:
            return True

        for value in dict_node.values:
            if isinstance(value, ast.List):
                if len(value.elts) > self.max_values_per_key:
                    return True

        return False

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

    def _is_matrix_call(self, node: ast.Call) -> bool:
        """Check if a Call node is a Matrix() call."""
        if isinstance(node.func, ast.Name):
            return node.func.id == "Matrix"
        if isinstance(node.func, ast.Attribute):
            return node.func.attr == "Matrix"
        return False

    def fix(self, source: str, file_path: str) -> tuple[str, int, list[LintError]]:
        """Fix inline matrix by extracting to a variable.

        Returns:
            Tuple of (fixed_source, fixed_count, remaining_errors)
        """
        fixed_count = 0
        fixed_source = source

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return source, 0, self.check(source, file_path)

        # Find Job assignments with inline complex matrix
        replacements: list[tuple[ast.Call, str, int]] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                if self._is_job_call(node.value):
                    var_name = ""
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            var_name = target.id
                            break

                    for keyword in node.value.keywords:
                        if keyword.arg == "strategy" and isinstance(
                            keyword.value, ast.Call
                        ):
                            if self._is_strategy_call(keyword.value):
                                for strat_kw in keyword.value.keywords:
                                    if strat_kw.arg == "matrix" and isinstance(
                                        strat_kw.value, ast.Call
                                    ):
                                        if self._is_matrix_call(strat_kw.value):
                                            for matrix_kw in strat_kw.value.keywords:
                                                if matrix_kw.arg == "values" and isinstance(
                                                    matrix_kw.value, ast.Dict
                                                ):
                                                    if self._is_complex_matrix(
                                                        matrix_kw.value
                                                    ):
                                                        replacements.append(
                                                            (
                                                                strat_kw.value,
                                                                var_name,
                                                                node.lineno,
                                                            )
                                                        )

        if not replacements:
            return source, 0, self.check(source, file_path)

        # Apply replacements using regex
        for matrix_node, var_name, assign_line in reversed(replacements):
            matrix_var = f"{var_name}_matrix" if var_name else "job_matrix"

            # Find the Matrix(...) in source and extract it
            lines = fixed_source.splitlines(keepends=True)
            start_line = matrix_node.lineno
            start_col = matrix_node.col_offset
            end_line = matrix_node.end_lineno or start_line
            end_col = matrix_node.end_col_offset or start_col

            # Extract matrix source
            if start_line == end_line:
                matrix_str = lines[start_line - 1][start_col:end_col]
            else:
                matrix_str = lines[start_line - 1][start_col:]
                for i in range(start_line, end_line - 1):
                    matrix_str += lines[i]
                matrix_str += lines[end_line - 1][:end_col]

            # Create new variable line
            indent = len(lines[assign_line - 1]) - len(lines[assign_line - 1].lstrip())
            new_var_line = " " * indent + f"{matrix_var} = {matrix_str.strip()}\n"

            # Replace inline matrix with variable reference
            pattern = re.escape(matrix_str.strip())
            fixed_source = re.sub(pattern, matrix_var, fixed_source, count=1)

            # Insert the new variable before the assignment
            lines = fixed_source.splitlines(keepends=True)
            lines.insert(assign_line - 1, new_var_line)
            fixed_source = "".join(lines)
            fixed_count += 1

        remaining_errors = self.check(fixed_source, file_path)

        return fixed_source, fixed_count, remaining_errors


class WAG015InlineOutputs(BaseRule):
    """WAG015: Extract inline outputs.

    Detects large inline outputs dicts in Job() and suggests extraction.
    """

    def __init__(self, max_inline: int = 2) -> None:
        self.max_inline = max_inline

    @property
    def id(self) -> str:
        return "WAG015"

    @property
    def description(self) -> str:
        return f"Extract inline outputs dicts with >{self.max_inline} entries"

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return errors

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and self._is_job_call(node):
                for keyword in node.keywords:
                    if keyword.arg == "outputs" and isinstance(keyword.value, ast.Dict):
                        num_outputs = len(keyword.value.keys)
                        if num_outputs > self.max_inline:
                            errors.append(
                                LintError(
                                    rule_id=self.id,
                                    message=f"Job has {num_outputs} inline outputs; extract to a named variable",
                                    file_path=file_path,
                                    line=keyword.value.lineno,
                                    column=keyword.value.col_offset,
                                    suggestion="Create: job_outputs = {...}; Job(..., outputs=job_outputs)",
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

    def fix(self, source: str, file_path: str) -> tuple[str, int, list[LintError]]:
        """Fix inline outputs by extracting to a variable.

        Returns:
            Tuple of (fixed_source, fixed_count, remaining_errors)
        """
        fixed_count = 0
        fixed_source = source

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return source, 0, self.check(source, file_path)

        # Find Job assignments with inline outputs
        replacements: list[tuple[int, int, int, int, str, int]] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                if self._is_job_call(node.value):
                    var_name = ""
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            var_name = target.id
                            break

                    for keyword in node.value.keywords:
                        if keyword.arg == "outputs" and isinstance(
                            keyword.value, ast.Dict
                        ):
                            num_outputs = len(keyword.value.keys)
                            if num_outputs > self.max_inline:
                                outputs_start = keyword.value.lineno
                                outputs_col = keyword.value.col_offset
                                outputs_end = keyword.value.end_lineno or outputs_start
                                outputs_end_col = (
                                    keyword.value.end_col_offset or outputs_col
                                )

                                outputs_var = (
                                    f"{var_name}_outputs" if var_name else "job_outputs"
                                )
                                replacements.append(
                                    (
                                        outputs_start,
                                        outputs_col,
                                        outputs_end,
                                        outputs_end_col,
                                        outputs_var,
                                        node.lineno,
                                    )
                                )

        if not replacements:
            return source, 0, self.check(source, file_path)

        # Apply replacements
        lines = fixed_source.splitlines(keepends=True)

        for (
            start_line,
            start_col,
            end_line,
            end_col,
            var_name,
            assign_line,
        ) in reversed(replacements):
            # Extract the inline dict
            if start_line == end_line:
                dict_str = lines[start_line - 1][start_col:end_col]
            else:
                dict_str = lines[start_line - 1][start_col:]
                for i in range(start_line, end_line - 1):
                    dict_str += lines[i]
                dict_str += lines[end_line - 1][:end_col]

            # Create the extracted variable declaration
            indent = len(lines[assign_line - 1]) - len(lines[assign_line - 1].lstrip())
            new_var_line = " " * indent + f"{var_name} = {dict_str.strip()}\n"

            # Replace inline dict with variable reference
            if start_line == end_line:
                lines[start_line - 1] = (
                    lines[start_line - 1][:start_col]
                    + var_name
                    + lines[start_line - 1][end_col:]
                )
            else:
                # Multi-line dict - use regex on full source for safety
                fixed_source = "".join(lines)
                pattern = re.escape(dict_str.strip())
                fixed_source = re.sub(pattern, var_name, fixed_source, count=1)
                lines = fixed_source.splitlines(keepends=True)

            # Insert the new variable before the assignment
            insert_line = assign_line - 1
            lines.insert(insert_line, new_var_line)
            fixed_count += 1
            fixed_source = "".join(lines)
            lines = fixed_source.splitlines(keepends=True)

        remaining_errors = self.check(fixed_source, file_path)

        return fixed_source, fixed_count, remaining_errors
