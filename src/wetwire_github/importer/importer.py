"""YAML workflow parser implementation.

Parses GitHub workflow YAML files into an intermediate representation.
"""

from dataclasses import dataclass, field
from typing import Any

import yaml


@dataclass
class IRStep:
    """Intermediate representation of a workflow step."""

    id: str | None = None
    name: str | None = None
    uses: str | None = None
    run: str | None = None
    with_: dict[str, Any] | None = None
    env: dict[str, Any] | None = None
    if_: str | None = None
    shell: str | None = None
    working_directory: str | None = None
    continue_on_error: bool | None = None
    timeout_minutes: int | None = None


@dataclass
class IRJob:
    """Intermediate representation of a workflow job."""

    id: str
    name: str | None = None
    runs_on: str | None = None
    steps: list[IRStep] = field(default_factory=list)
    needs: list[str] | None = None
    env: dict[str, Any] | None = None
    if_: str | None = None
    strategy: dict[str, Any] | None = None
    container: dict[str, Any] | None = None
    services: dict[str, Any] | None = None
    outputs: dict[str, str] | None = None
    timeout_minutes: int | None = None
    continue_on_error: bool | None = None


@dataclass
class IRWorkflow:
    """Intermediate representation of a workflow."""

    name: str | None = None
    on: dict[str, Any] = field(default_factory=dict)
    jobs: dict[str, IRJob] = field(default_factory=dict)
    env: dict[str, Any] | None = None
    permissions: dict[str, str] | str | None = None
    concurrency: dict[str, Any] | str | None = None
    defaults: dict[str, Any] | None = None


def _parse_step(data: dict[str, Any]) -> IRStep:
    """Parse a step from YAML data.

    Args:
        data: Step data dict

    Returns:
        Parsed IRStep
    """
    return IRStep(
        id=data.get("id"),
        name=data.get("name"),
        uses=data.get("uses"),
        run=data.get("run"),
        with_=data.get("with"),
        env=data.get("env"),
        if_=data.get("if"),
        shell=data.get("shell"),
        working_directory=data.get("working-directory"),
        continue_on_error=data.get("continue-on-error"),
        timeout_minutes=data.get("timeout-minutes"),
    )


def _parse_job(job_id: str, data: dict[str, Any]) -> IRJob:
    """Parse a job from YAML data.

    Args:
        job_id: The job identifier
        data: Job data dict

    Returns:
        Parsed IRJob
    """
    # Parse needs - can be string or list
    needs = data.get("needs")
    if isinstance(needs, str):
        needs = [needs]

    # Parse steps
    steps = []
    for step_data in data.get("steps", []):
        steps.append(_parse_step(step_data))

    return IRJob(
        id=job_id,
        name=data.get("name"),
        runs_on=data.get("runs-on"),
        steps=steps,
        needs=needs,
        env=data.get("env"),
        if_=data.get("if"),
        strategy=data.get("strategy"),
        container=data.get("container"),
        services=data.get("services"),
        outputs=data.get("outputs"),
        timeout_minutes=data.get("timeout-minutes"),
        continue_on_error=data.get("continue-on-error"),
    )


def _parse_on(data: Any) -> dict[str, Any]:
    """Parse the 'on' trigger configuration.

    Args:
        data: On trigger data (can be string, list, or dict)

    Returns:
        Normalized dict format
    """
    if isinstance(data, str):
        return {data: {}}
    if isinstance(data, list):
        return {event: {} for event in data}
    if isinstance(data, dict):
        return data
    return {}


def parse_workflow_yaml(content: str) -> IRWorkflow:
    """Parse a workflow YAML string into an IR.

    Args:
        content: YAML content string

    Returns:
        Parsed IRWorkflow
    """
    data = yaml.safe_load(content)

    if not isinstance(data, dict):
        return IRWorkflow()

    # Parse jobs
    jobs = {}
    for job_id, job_data in data.get("jobs", {}).items():
        jobs[job_id] = _parse_job(job_id, job_data)

    # Handle YAML 1.1 quirk where 'on' is interpreted as boolean True
    on_value = data.get("on") or data.get(True, {})

    return IRWorkflow(
        name=data.get("name"),
        on=_parse_on(on_value),
        jobs=jobs,
        env=data.get("env"),
        permissions=data.get("permissions"),
        concurrency=data.get("concurrency"),
        defaults=data.get("defaults"),
    )


def parse_workflow_file(file_path: str) -> IRWorkflow | None:
    """Parse a workflow YAML file into an IR.

    Args:
        file_path: Path to the YAML file

    Returns:
        Parsed IRWorkflow, or None if file not found
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            return parse_workflow_yaml(f.read())
    except FileNotFoundError:
        return None


def build_reference_graph(
    workflow: IRWorkflow,
    include_actions: bool = False,
) -> dict[str, list[str]]:
    """Build a reference graph from a workflow.

    Args:
        workflow: Parsed workflow IR
        include_actions: Whether to include action references

    Returns:
        Dict mapping job/resource name to list of dependencies
    """
    graph: dict[str, list[str]] = {}

    # Track job dependencies
    for job_id, job in workflow.jobs.items():
        graph[job_id] = list(job.needs) if job.needs else []

    # Track action references
    if include_actions:
        actions = set()
        for job in workflow.jobs.values():
            for step in job.steps:
                if step.uses:
                    actions.add(step.uses)
        graph["actions"] = sorted(actions)

    return graph
