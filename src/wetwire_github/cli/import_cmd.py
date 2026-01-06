"""Import command implementation.

Converts existing workflow YAML files to Python code.
"""

import re
from pathlib import Path
from typing import Any

from wetwire_github.importer import IRJob, IRStep, IRWorkflow, parse_workflow_file


def import_workflows(
    file_paths: list[str],
    output_dir: str,
    single_file: bool = False,
    no_scaffold: bool = False,
) -> tuple[int, list[str]]:
    """Import workflow YAML files and convert to Python.

    Args:
        file_paths: List of YAML file paths to import
        output_dir: Directory to write generated Python code
        single_file: Whether to generate all code in a single file
        no_scaffold: Whether to skip project scaffolding

    Returns:
        Tuple of (exit_code, list of messages)
    """
    if not file_paths:
        return 1, ["No files to import"]

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    # Parse all workflows
    workflows: list[tuple[str, IRWorkflow]] = []
    for file_path in file_paths:
        workflow = parse_workflow_file(file_path)
        if workflow is None:
            return 1, [f"Error: File not found: {file_path}"]
        # Use filename stem as workflow name if not set
        name = workflow.name or Path(file_path).stem
        workflows.append((name, workflow))

    if not workflows:
        return 1, ["No workflows found"]

    # Generate scaffold if requested
    messages = []
    if not no_scaffold:
        _generate_scaffold(output, workflows)
        messages.append(f"Created project scaffold in {output}")

    # Generate Python code
    if single_file:
        # All workflows in one file
        code = _generate_combined_code(workflows)
        output_file = output / "workflows.py"
        output_file.write_text(code)
        messages.append(f"Generated: {output_file}")
    else:
        # Separate file per workflow
        for name, workflow in workflows:
            safe_name = _sanitize_name(name)
            code = _generate_workflow_code(name, workflow)
            output_file = output / f"{safe_name}.py"
            output_file.write_text(code)
            messages.append(f"Generated: {output_file}")

    return 0, messages


def _sanitize_name(name: str) -> str:
    """Convert a name to valid Python identifier."""
    result = name.lower()
    result = re.sub(r"[^a-z0-9_]", "_", result)
    result = re.sub(r"_+", "_", result)
    result = result.strip("_")
    return result or "workflow"


def _generate_scaffold(output: Path, workflows: list[tuple[str, IRWorkflow]]) -> None:
    """Generate project scaffold files."""
    # pyproject.toml
    pyproject = output / "pyproject.toml"
    if not pyproject.exists():
        pyproject.write_text('''[project]
name = "my-workflows"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "wetwire-github>=0.1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
''')

    # .gitignore
    gitignore = output / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text('''__pycache__/
*.py[cod]
.venv/
.env
''')


def _generate_combined_code(workflows: list[tuple[str, IRWorkflow]]) -> str:
    """Generate Python code for multiple workflows in one file."""
    lines = [_generate_imports(workflows)]

    for name, workflow in workflows:
        safe_name = _sanitize_name(name)
        lines.append(_generate_workflow_definition(safe_name, workflow))

    return "\n\n".join(lines) + "\n"


def _generate_workflow_code(name: str, workflow: IRWorkflow) -> str:
    """Generate Python code for a single workflow."""
    lines = [_generate_imports([(name, workflow)])]
    safe_name = _sanitize_name(name)
    lines.append(_generate_workflow_definition(safe_name, workflow))
    return "\n\n".join(lines) + "\n"


def _generate_imports(workflows: list[tuple[str, IRWorkflow]]) -> str:
    """Generate import statements."""
    imports = ["from wetwire_github.workflow import ("]
    needed = {"Workflow", "Job", "Step", "Triggers"}

    for _, workflow in workflows:
        # Detect needed trigger types
        for event in workflow.on.keys():
            trigger_name = _event_to_trigger_class(event)
            needed.add(trigger_name)

    needed_sorted = sorted(needed)
    for item in needed_sorted:
        imports.append(f"    {item},")
    imports.append(")")

    return "\n".join(imports)


def _event_to_trigger_class(event: str) -> str:
    """Convert event name to trigger class name."""
    mapping = {
        "push": "PushTrigger",
        "pull_request": "PullRequestTrigger",
        "pull_request_target": "PullRequestTargetTrigger",
        "workflow_dispatch": "WorkflowDispatchTrigger",
        "workflow_call": "WorkflowCallTrigger",
        "workflow_run": "WorkflowRunTrigger",
        "schedule": "ScheduleTrigger",
        "release": "ReleaseTrigger",
        "issues": "IssueTrigger",
        "issue_comment": "IssueCommentTrigger",
        "create": "CreateTrigger",
        "delete": "DeleteTrigger",
    }
    return mapping.get(event, "PushTrigger")


def _generate_workflow_definition(name: str, workflow: IRWorkflow) -> str:
    """Generate workflow definition code."""
    lines = [f"{name} = Workflow("]

    # name
    if workflow.name:
        lines.append(f'    name="{workflow.name}",')

    # on (triggers)
    triggers_code = _generate_triggers(workflow.on)
    lines.append(f"    on={triggers_code},")

    # jobs
    if workflow.jobs:
        lines.append("    jobs={")
        for job_id, job in workflow.jobs.items():
            job_code = _generate_job(job)
            lines.append(f'        "{job_id}": {job_code},')
        lines.append("    },")

    lines.append(")")
    return "\n".join(lines)


def _generate_triggers(on: dict[str, Any]) -> str:
    """Generate Triggers() code."""
    if not on:
        return "Triggers()"

    parts = []
    for event, config in on.items():
        trigger_class = _event_to_trigger_class(event)
        if config:
            args = _generate_trigger_args(config)
            parts.append(f"{event}={trigger_class}({args})")
        else:
            parts.append(f"{event}={trigger_class}()")

    if len(parts) == 1:
        return f"Triggers({parts[0]})"
    else:
        inner = ", ".join(parts)
        return f"Triggers({inner})"


def _generate_trigger_args(config: dict[str, Any]) -> str:
    """Generate trigger constructor arguments."""
    if not config:
        return ""

    args = []
    for key, value in config.items():
        snake_key = key.replace("-", "_")
        args.append(f"{snake_key}={repr(value)}")

    return ", ".join(args)


def _generate_job(job: IRJob) -> str:
    """Generate Job() code."""
    parts = []

    if job.runs_on:
        parts.append(f'runs_on="{job.runs_on}"')

    if job.name:
        parts.append(f'name="{job.name}"')

    if job.needs:
        parts.append(f"needs={repr(job.needs)}")

    if job.if_:
        parts.append(f'if_="{_escape_string(job.if_)}"')

    if job.env:
        parts.append(f"env={repr(job.env)}")

    if job.steps:
        steps_code = _generate_steps(job.steps)
        parts.append(f"steps={steps_code}")

    return "Job(" + ", ".join(parts) + ")"


def _generate_steps(steps: list[IRStep]) -> str:
    """Generate list of Step() calls."""
    step_strs = []
    for step in steps:
        step_strs.append(_generate_step(step))

    if len(step_strs) == 1:
        return f"[{step_strs[0]}]"
    else:
        inner = ",\n            ".join(step_strs)
        return f"[\n            {inner},\n        ]"


def _generate_step(step: IRStep) -> str:
    """Generate Step() code."""
    parts = []

    if step.name:
        parts.append(f'name="{_escape_string(step.name)}"')

    if step.uses:
        parts.append(f'uses="{step.uses}"')

    if step.run:
        if "\n" in step.run:
            # Multiline string
            parts.append(f'run="""{step.run}"""')
        else:
            parts.append(f'run="{_escape_string(step.run)}"')

    if step.with_:
        # Use with_ for reserved keyword
        with_dict = _transform_keys(step.with_)
        parts.append(f"with_={repr(with_dict)}")

    if step.env:
        parts.append(f"env={repr(step.env)}")

    if step.if_:
        parts.append(f'if_="{_escape_string(step.if_)}"')

    if step.shell:
        parts.append(f'shell="{step.shell}"')

    if step.working_directory:
        parts.append(f'working_directory="{step.working_directory}"')

    if step.id:
        parts.append(f'id="{step.id}"')

    return "Step(" + ", ".join(parts) + ")"


def _transform_keys(d: dict[str, Any]) -> dict[str, Any]:
    """Transform dict keys from kebab-case to snake_case."""
    result = {}
    for key, value in d.items():
        snake_key = key.replace("-", "_")
        result[snake_key] = value
    return result


def _escape_string(s: str) -> str:
    """Escape a string for Python code."""
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
