"""Workflow composition builder for fluent workflow construction."""

from dataclasses import dataclass, field
from typing import Any

from .job import Job
from .triggers import Triggers
from .types import Permissions
from .workflow import Workflow


@dataclass
class ComposedWorkflow:
    """
    Fluent builder for constructing GitHub Actions workflows.

    Provides a composable API for building workflows with:
    - Named workflow configuration
    - Trigger management
    - Job dependencies and ordering
    - Environment variables
    - Permissions

    Example:
        workflow = (
            ComposedWorkflow()
            .name("CI/CD")
            .add_trigger("push", PushTrigger(branches=["main"]))
            .add_job("build", build_job)
            .add_job("test", test_job, needs=["build"])
            .add_env({"NODE_ENV": "production"})
            .add_permissions({"contents": "read"})
            .build()
        )
    """

    _name: str = field(default="")
    _triggers: dict[str, Any] = field(default_factory=dict)
    _jobs: dict[str, Job] = field(default_factory=dict)
    _job_dependencies: dict[str, list[str]] = field(default_factory=dict)
    _env: dict[str, str] = field(default_factory=dict)
    _permissions: Permissions | None = field(default=None)

    def name(self, n: str) -> "ComposedWorkflow":
        """
        Set the workflow name.

        Args:
            n: The workflow name

        Returns:
            Self for method chaining
        """
        self._name = n
        return self

    def add_trigger(self, trigger_type: str, config: Any) -> "ComposedWorkflow":
        """
        Add a trigger to the workflow.

        Args:
            trigger_type: The trigger type (e.g., "push", "pull_request")
            config: The trigger configuration object

        Returns:
            Self for method chaining

        Raises:
            ValueError: If the trigger type is not recognized
        """
        # Valid trigger types from the Triggers dataclass
        valid_triggers = {
            "push",
            "pull_request",
            "pull_request_target",
            "schedule",
            "workflow_dispatch",
            "workflow_call",
            "workflow_run",
            "repository_dispatch",
            "release",
            "issues",
            "issue_comment",
            "label",
            "milestone",
            "project",
            "project_card",
            "project_column",
            "discussion",
            "discussion_comment",
            "create",
            "delete",
            "deployment",
            "deployment_status",
            "fork",
            "gollum",
            "page_build",
            "public",
            "pull_request_review",
            "pull_request_review_comment",
            "check_run",
            "check_suite",
            "status",
            "watch",
            "member",
            "membership",
            "org_block",
            "organization",
            "team",
            "team_add",
            "merge_group",
            "branch_protection_rule",
        }

        if trigger_type not in valid_triggers:
            raise ValueError(
                f"Unknown trigger type: {trigger_type}. "
                f"Valid types: {', '.join(sorted(valid_triggers))}"
            )

        self._triggers[trigger_type] = config
        return self

    def add_job(
        self, job_id: str, job: Job, needs: list[str] | None = None
    ) -> "ComposedWorkflow":
        """
        Add a job to the workflow.

        Args:
            job_id: The unique identifier for the job
            job: The Job object
            needs: Optional list of job IDs this job depends on

        Returns:
            Self for method chaining
        """
        self._jobs[job_id] = job
        if needs:
            self._job_dependencies[job_id] = needs
        return self

    def add_env(self, env: dict[str, str]) -> "ComposedWorkflow":
        """
        Add environment variables to the workflow.

        Multiple calls to this method will merge the environment variables,
        with later values overriding earlier ones.

        Args:
            env: Dictionary of environment variables

        Returns:
            Self for method chaining
        """
        self._env.update(env)
        return self

    def add_permissions(
        self, permissions: dict[str, str] | Permissions | str
    ) -> "ComposedWorkflow":
        """
        Add permissions to the workflow.

        Args:
            permissions: Can be:
                - A dictionary mapping permission names to values
                - A Permissions object
                - A string "read-all" or "write-all"

        Returns:
            Self for method chaining
        """
        if isinstance(permissions, str):
            if permissions == "read-all":
                self._permissions = Permissions(read_all=True)
            elif permissions == "write-all":
                self._permissions = Permissions(write_all=True)
            else:
                raise ValueError(
                    f"Invalid permission string: {permissions}. "
                    "Use 'read-all' or 'write-all'"
                )
        elif isinstance(permissions, dict):
            # Cast to proper type for type checker
            perms_dict: dict[str, str] = {str(k): str(v) for k, v in permissions.items()}
            self._permissions = Permissions(**perms_dict)  # type: ignore[arg-type]
        elif isinstance(permissions, Permissions):
            self._permissions = permissions
        else:
            raise ValueError(
                f"Invalid permissions type: {type(permissions)}. "
                "Use dict, Permissions object, or 'read-all'/'write-all' string"
            )
        return self

    def build(self) -> Workflow:
        """
        Build and return the final Workflow object.

        Returns:
            The constructed Workflow

        Raises:
            ValueError: If there are validation errors (missing dependencies,
                       circular dependencies)
        """
        # Validate dependencies
        self._validate_dependencies()

        # Apply dependencies to jobs
        for job_id, needs_list in self._job_dependencies.items():
            if job_id in self._jobs:
                self._jobs[job_id].needs = needs_list

        # Build triggers
        trigger_kwargs = {}
        for trigger_type, config in self._triggers.items():
            trigger_kwargs[trigger_type] = config

        triggers = Triggers(**trigger_kwargs) if trigger_kwargs else Triggers()

        # Build workflow
        return Workflow(
            name=self._name,
            on=triggers,
            env=self._env if self._env else None,
            permissions=self._permissions,
            jobs=self._jobs,
        )

    def _validate_dependencies(self) -> None:
        """
        Validate job dependencies.

        Raises:
            ValueError: If dependencies are invalid (missing jobs, circular deps, self-deps)
        """
        # Check for self-dependencies
        for job_id, needs_list in self._job_dependencies.items():
            if job_id in needs_list:
                raise ValueError(f"Job '{job_id}' cannot depend on itself")

        # Check that all dependencies exist
        for job_id, needs_list in self._job_dependencies.items():
            for needed_job in needs_list:
                if needed_job not in self._jobs:
                    raise ValueError(
                        f"Job '{job_id}' depends on non-existent job '{needed_job}'"
                    )

        # Check for circular dependencies using DFS
        self._check_circular_dependencies()

    def _check_circular_dependencies(self) -> None:
        """
        Check for circular dependencies in the job graph.

        Uses depth-first search to detect cycles.

        Raises:
            ValueError: If a circular dependency is detected
        """
        # Track visited nodes and recursion stack
        visited = set()
        rec_stack = set()

        def has_cycle(job_id: str) -> bool:
            """DFS helper to detect cycles."""
            visited.add(job_id)
            rec_stack.add(job_id)

            # Check all dependencies
            if job_id in self._job_dependencies:
                for dep in self._job_dependencies[job_id]:
                    if dep not in visited:
                        if has_cycle(dep):
                            return True
                    elif dep in rec_stack:
                        return True

            rec_stack.remove(job_id)
            return False

        # Check all jobs
        for job_id in self._jobs:
            if job_id not in visited:
                if has_cycle(job_id):
                    raise ValueError(
                        f"Circular dependency detected in workflow jobs involving '{job_id}'"
                    )
