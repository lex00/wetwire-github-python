"""Reference graph tracking linting rules.

Rules that track references between jobs, steps, outputs, and secrets
to detect unused outputs, circular dependencies, orphan secrets, and
invalid step output references.
"""

import ast
import re

from wetwire_github.linter.linter import LintError

from .base import BaseRule

__all__ = [
    "WAG050UnusedJobOutputs",
    "WAG051CircularJobDependencies",
    "WAG052OrphanSecrets",
    "WAG053StepOutputReferences",
]


class WAG050UnusedJobOutputs(BaseRule):
    """WAG050: Detect job outputs that are never referenced by downstream jobs.

    Flags job outputs that are defined but never consumed by any other job
    via needs.jobname.outputs.outputname patterns.
    """

    # Pattern to match needs.jobname.outputs.outputname references
    _NEEDS_OUTPUT_PATTERN = re.compile(
        r"\$\{\{\s*needs\.(\w+)\.outputs\.(\w+)\s*\}\}"
    )

    @property
    def id(self) -> str:
        return "WAG050"

    @property
    def description(self) -> str:
        return "Flag job outputs that are never referenced by downstream jobs"

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return errors

        # Build a map of job variable names to their outputs
        job_outputs: dict[str, dict[str, int]] = {}  # job_var -> {output_name: line}

        # Build a map of job variable names to their job keys in workflows
        job_var_to_key: dict[str, str] = {}

        # First pass: collect job outputs and job key mappings
        for node in ast.walk(tree):
            # Look for Job assignments
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                if self._is_job_call(node.value):
                    job_var = self._get_assign_target_name(node)
                    if job_var:
                        outputs = self._extract_job_outputs(node.value)
                        if outputs:
                            job_outputs[job_var] = outputs

            # Look for Workflow definitions to get job key mappings
            if isinstance(node, ast.Call) and self._is_workflow_call(node):
                for keyword in node.keywords:
                    if keyword.arg == "jobs" and isinstance(keyword.value, ast.Dict):
                        for key, value in zip(keyword.value.keys, keyword.value.values):
                            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                                job_key = key.value
                                if isinstance(value, ast.Name):
                                    job_var_to_key[value.id] = job_key

        # Second pass: find all referenced outputs
        referenced_outputs: set[tuple[str, str]] = set()  # (job_key, output_name)

        # Search through the entire source for needs references
        for match in self._NEEDS_OUTPUT_PATTERN.finditer(source):
            job_key = match.group(1)
            output_name = match.group(2)
            referenced_outputs.add((job_key, output_name))

        # Check for unreferenced outputs
        for job_var, outputs in job_outputs.items():
            job_key = job_var_to_key.get(job_var, job_var)
            for output_name, line in outputs.items():
                if (job_key, output_name) not in referenced_outputs:
                    errors.append(
                        LintError(
                            rule_id=self.id,
                            message=f"Job output '{output_name}' in job '{job_key}' is never referenced by any downstream job",
                            file_path=file_path,
                            line=line,
                            column=0,
                            suggestion=f"Remove unused output or reference it via needs.{job_key}.outputs.{output_name}",
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

    def _is_workflow_call(self, node: ast.Call) -> bool:
        """Check if a Call node is a Workflow() call."""
        if isinstance(node.func, ast.Name):
            return node.func.id == "Workflow"
        if isinstance(node.func, ast.Attribute):
            return node.func.attr == "Workflow"
        return False

    def _get_assign_target_name(self, node: ast.Assign) -> str | None:
        """Get the variable name from an assignment."""
        if node.targets and isinstance(node.targets[0], ast.Name):
            return node.targets[0].id
        return None

    def _extract_job_outputs(self, node: ast.Call) -> dict[str, int]:
        """Extract output names and their line numbers from a Job call."""
        outputs: dict[str, int] = {}
        for keyword in node.keywords:
            if keyword.arg == "outputs" and isinstance(keyword.value, ast.Dict):
                for key in keyword.value.keys:
                    if isinstance(key, ast.Constant) and isinstance(key.value, str):
                        outputs[key.value] = key.lineno
        return outputs


class WAG051CircularJobDependencies(BaseRule):
    """WAG051: Detect circular dependencies in job needs.

    Analyzes job dependency graphs to detect cycles that would prevent
    workflow execution.
    """

    @property
    def id(self) -> str:
        return "WAG051"

    @property
    def description(self) -> str:
        return "Detect circular dependencies in job needs declarations"

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return errors

        # Build dependency graph from workflow definitions
        # job_key -> [dependency_job_keys]
        dependencies: dict[str, list[str]] = {}
        job_lines: dict[str, int] = {}

        # Map of job variable name to its key in the workflow
        job_var_to_key: dict[str, str] = {}
        # Map of job variable name to its needs list
        job_var_needs: dict[str, list[str]] = {}
        job_var_lines: dict[str, int] = {}

        # First pass: collect job definitions and their needs
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                if self._is_job_call(node.value):
                    job_var = self._get_assign_target_name(node)
                    if job_var:
                        needs = self._extract_job_needs(node.value)
                        job_var_needs[job_var] = needs
                        job_var_lines[job_var] = node.lineno

        # Second pass: find workflow definitions to get job key mappings
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and self._is_workflow_call(node):
                for keyword in node.keywords:
                    if keyword.arg == "jobs" and isinstance(keyword.value, ast.Dict):
                        for key, value in zip(keyword.value.keys, keyword.value.values):
                            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                                job_key = key.value
                                if isinstance(value, ast.Name):
                                    job_var = value.id
                                    job_var_to_key[job_var] = job_key
                                    if job_var in job_var_needs:
                                        dependencies[job_key] = job_var_needs[job_var]
                                        job_lines[job_key] = job_var_lines.get(job_var, 1)

        # Detect cycles using DFS
        cycles = self._find_cycles(dependencies)

        for cycle in cycles:
            cycle_str = " -> ".join(cycle + [cycle[0]])  # Show full cycle
            errors.append(
                LintError(
                    rule_id=self.id,
                    message=f"Circular dependency detected: {cycle_str}",
                    file_path=file_path,
                    line=job_lines.get(cycle[0], 1),
                    column=0,
                    suggestion="Remove one of the dependencies to break the cycle",
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

    def _is_workflow_call(self, node: ast.Call) -> bool:
        """Check if a Call node is a Workflow() call."""
        if isinstance(node.func, ast.Name):
            return node.func.id == "Workflow"
        if isinstance(node.func, ast.Attribute):
            return node.func.attr == "Workflow"
        return False

    def _get_assign_target_name(self, node: ast.Assign) -> str | None:
        """Get the variable name from an assignment."""
        if node.targets and isinstance(node.targets[0], ast.Name):
            return node.targets[0].id
        return None

    def _extract_job_needs(self, node: ast.Call) -> list[str]:
        """Extract the needs list from a Job call."""
        needs: list[str] = []
        for keyword in node.keywords:
            if keyword.arg == "needs":
                if isinstance(keyword.value, ast.List):
                    for elt in keyword.value.elts:
                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                            needs.append(elt.value)
                elif isinstance(keyword.value, ast.Constant) and isinstance(
                    keyword.value.value, str
                ):
                    needs.append(keyword.value.value)
        return needs

    def _find_cycles(self, graph: dict[str, list[str]]) -> list[list[str]]:
        """Find all cycles in a directed graph using DFS."""
        cycles: list[list[str]] = []
        visited: set[str] = set()
        rec_stack: set[str] = set()
        path: list[str] = []

        def dfs(node: str) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:]
                    # Only add unique cycles
                    normalized = self._normalize_cycle(cycle)
                    if normalized not in [self._normalize_cycle(c) for c in cycles]:
                        cycles.append(cycle)

            path.pop()
            rec_stack.remove(node)

        for node in graph:
            if node not in visited:
                dfs(node)

        return cycles

    def _normalize_cycle(self, cycle: list[str]) -> tuple[str, ...]:
        """Normalize a cycle for comparison (start from smallest element)."""
        if not cycle:
            return tuple()
        min_idx = cycle.index(min(cycle))
        return tuple(cycle[min_idx:] + cycle[:min_idx])


class WAG052OrphanSecrets(BaseRule):
    """WAG052: Detect secrets that are defined but not used.

    Flags secrets that are referenced in workflow/job env but never
    actually used in any step's run command or env.
    """

    # Pattern to match Secrets.get("NAME") calls
    _SECRETS_GET_PATTERN = re.compile(r'Secrets\.get\(["\'](\w+)["\']\)')
    # Pattern to match ${{ secrets.NAME }} expressions
    _SECRETS_EXPR_PATTERN = re.compile(r"\$\{\{\s*secrets\.(\w+)\s*\}\}")

    @property
    def id(self) -> str:
        return "WAG052"

    @property
    def description(self) -> str:
        return "Flag secrets that are referenced but not actually used in steps"

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return errors

        # Collect secrets defined at workflow/job level env
        workflow_job_secrets: dict[str, int] = {}  # secret_name -> line
        # Collect secrets used directly in steps
        step_secrets: set[str] = set()
        # Collect env var names that map to secrets at workflow/job level
        env_var_to_secret: dict[str, str] = {}  # ENV_VAR -> secret_name
        # Collect env vars used in step run commands
        step_env_vars_used: set[str] = set()

        # Find workflow-level and job-level env with secrets
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if self._is_workflow_call(node) or self._is_job_call(node):
                    for keyword in node.keywords:
                        if keyword.arg == "env" and isinstance(keyword.value, ast.Dict):
                            self._extract_env_secrets(
                                keyword.value,
                                workflow_job_secrets,
                                env_var_to_secret,
                            )

        # Find secrets used directly in steps
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and self._is_step_call(node):
                for keyword in node.keywords:
                    # Check step-level env
                    if keyword.arg == "env":
                        step_secrets_in_env = self._find_secrets_in_node(keyword.value)
                        step_secrets.update(step_secrets_in_env)

                    # Check run commands for env var usage
                    if keyword.arg == "run" and isinstance(keyword.value, ast.Constant):
                        run_cmd = keyword.value.value
                        if isinstance(run_cmd, str):
                            # Find $ENV_VAR or ${ENV_VAR} patterns
                            for env_var in env_var_to_secret:
                                if f"${env_var}" in run_cmd or f"${{{env_var}}}" in run_cmd:
                                    step_env_vars_used.add(env_var)

        # Find unused secrets at workflow/job level
        for secret_name, line in workflow_job_secrets.items():
            # Check if secret is used directly in steps
            if secret_name in step_secrets:
                continue

            # Check if the env var mapping to this secret is used
            used_via_env = False
            for env_var, mapped_secret in env_var_to_secret.items():
                if mapped_secret == secret_name and env_var in step_env_vars_used:
                    used_via_env = True
                    break

            if not used_via_env:
                errors.append(
                    LintError(
                        rule_id=self.id,
                        message=f"Secret '{secret_name}' is defined but not used in any step",
                        file_path=file_path,
                        line=line,
                        column=0,
                        suggestion="Remove the unused secret or use it in a step",
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

    def _is_job_call(self, node: ast.Call) -> bool:
        """Check if a Call node is a Job() call."""
        if isinstance(node.func, ast.Name):
            return node.func.id == "Job"
        if isinstance(node.func, ast.Attribute):
            return node.func.attr == "Job"
        return False

    def _is_step_call(self, node: ast.Call) -> bool:
        """Check if a Call node is a Step() call."""
        if isinstance(node.func, ast.Name):
            return node.func.id == "Step"
        if isinstance(node.func, ast.Attribute):
            return node.func.attr == "Step"
        return False

    def _extract_env_secrets(
        self,
        dict_node: ast.Dict,
        secrets_out: dict[str, int],
        env_mapping: dict[str, str],
    ) -> None:
        """Extract secrets from an env dict node."""
        for key, value in zip(dict_node.keys, dict_node.values):
            if not isinstance(key, ast.Constant) or not isinstance(key.value, str):
                continue

            env_var_name = key.value
            secret_names = self._find_secrets_in_node(value)

            for secret_name in secret_names:
                secrets_out[secret_name] = key.lineno
                env_mapping[env_var_name] = secret_name

    def _find_secrets_in_node(self, node: ast.expr) -> set[str]:
        """Find all secret names referenced in an AST node."""
        secrets: set[str] = set()

        # Check for Secrets.get() calls
        if isinstance(node, ast.Call):
            if self._is_secrets_get_call(node):
                if node.args and isinstance(node.args[0], ast.Constant):
                    secrets.add(node.args[0].value)

        # Check for string expressions with ${{ secrets.NAME }}
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            for match in self._SECRETS_EXPR_PATTERN.finditer(node.value):
                secrets.add(match.group(1))

        # Check dict values recursively
        if isinstance(node, ast.Dict):
            for value in node.values:
                secrets.update(self._find_secrets_in_node(value))

        return secrets

    def _is_secrets_get_call(self, node: ast.Call) -> bool:
        """Check if a Call node is a Secrets.get() call."""
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == "get":
                if isinstance(node.func.value, ast.Name):
                    return node.func.value.id == "Secrets"
        return False


class WAG053StepOutputReferences(BaseRule):
    """WAG053: Validate step output references.

    Ensures that steps.id.outputs.name references point to valid step IDs
    that are defined before the reference (no forward references).
    """

    # Pattern to match steps.id.outputs.name references (may be anywhere in expression)
    _STEP_OUTPUT_PATTERN = re.compile(
        r"steps\.(\w+)\.outputs\.(\w+)"
    )

    @property
    def id(self) -> str:
        return "WAG053"

    @property
    def description(self) -> str:
        return "Validate that step output references point to valid step IDs"

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return errors

        # Process each job independently (step IDs are job-scoped)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and self._is_job_call(node):
                job_errors = self._check_job_step_references(node, file_path)
                errors.extend(job_errors)

        return errors

    def _is_job_call(self, node: ast.Call) -> bool:
        """Check if a Call node is a Job() call."""
        if isinstance(node.func, ast.Name):
            return node.func.id == "Job"
        if isinstance(node.func, ast.Attribute):
            return node.func.attr == "Job"
        return False

    def _check_job_step_references(
        self, job_node: ast.Call, file_path: str
    ) -> list[LintError]:
        """Check step references within a single job."""
        errors = []

        # Collect steps in order and their IDs
        steps_list: list[tuple[ast.Call, int]] = []  # (step_node, index)
        step_ids_by_index: dict[int, str] = {}  # index -> step_id

        for keyword in job_node.keywords:
            if keyword.arg == "steps" and isinstance(keyword.value, ast.List):
                for idx, step_elt in enumerate(keyword.value.elts):
                    if isinstance(step_elt, ast.Call):
                        steps_list.append((step_elt, idx))
                        step_id = self._extract_step_id(step_elt)
                        if step_id:
                            step_ids_by_index[idx] = step_id

        # Check job outputs for step references
        for keyword in job_node.keywords:
            if keyword.arg == "outputs" and isinstance(keyword.value, ast.Dict):
                all_step_ids = set(step_ids_by_index.values())
                errors.extend(
                    self._check_node_for_invalid_step_refs(
                        keyword.value,
                        all_step_ids,
                        file_path,
                        "job outputs",
                    )
                )

        # Check each step for references to prior steps only
        for step_node, step_idx in steps_list:
            # Valid step IDs are those defined before this step
            valid_step_ids = {
                step_id
                for idx, step_id in step_ids_by_index.items()
                if idx < step_idx
            }

            errors.extend(
                self._check_step_for_invalid_refs(
                    step_node, valid_step_ids, file_path
                )
            )

        return errors

    def _extract_step_id(self, step_node: ast.Call) -> str | None:
        """Extract the id from a Step call."""
        for keyword in step_node.keywords:
            if keyword.arg == "id" and isinstance(keyword.value, ast.Constant):
                return keyword.value.value
        return None

    def _check_step_for_invalid_refs(
        self, step_node: ast.Call, valid_step_ids: set[str], file_path: str
    ) -> list[LintError]:
        """Check a step for invalid step output references."""
        errors = []

        for keyword in step_node.keywords:
            context = f"step '{keyword.arg}'"
            if keyword.arg in ("run", "env", "if_", "with_"):
                errors.extend(
                    self._check_node_for_invalid_step_refs(
                        keyword.value, valid_step_ids, file_path, context
                    )
                )

        return errors

    def _check_node_for_invalid_step_refs(
        self,
        node: ast.expr,
        valid_step_ids: set[str],
        file_path: str,
        context: str,
    ) -> list[LintError]:
        """Check an AST node for invalid step output references."""
        errors = []

        # Check string constants
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            for match in self._STEP_OUTPUT_PATTERN.finditer(node.value):
                step_id = match.group(1)
                if step_id not in valid_step_ids:
                    errors.append(
                        LintError(
                            rule_id=self.id,
                            message=f"Reference to undefined or forward step ID '{step_id}' in {context}",
                            file_path=file_path,
                            line=node.lineno,
                            column=node.col_offset,
                            suggestion=f"Ensure step with id='{step_id}' is defined before this reference",
                        )
                    )

        # Check dict values
        if isinstance(node, ast.Dict):
            for value in node.values:
                errors.extend(
                    self._check_node_for_invalid_step_refs(
                        value, valid_step_ids, file_path, context
                    )
                )

        return errors
