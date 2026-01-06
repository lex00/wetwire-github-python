# wetwire-github

Generate GitHub YAML configurations from typed Python declarations.

## Installation

```bash
pip install wetwire-github
```

## Features

### Core Types

Type-safe Python dataclasses for GitHub Actions workflows:

```python
from wetwire_github.workflow import (
    Workflow, Job, Step, Triggers,
    PushTrigger, PullRequestTrigger,
)

ci = Workflow(
    name="CI",
    on=Triggers(
        push=PushTrigger(branches=["main"]),
        pull_request=PullRequestTrigger(branches=["main"]),
    ),
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            steps=[
                Step(uses="actions/checkout@v4"),
                Step(run="make build"),
            ],
        ),
    },
)
```

### CLI Commands

```bash
# Generate YAML from Python declarations
wetwire-github build [package]

# Validate YAML files with actionlint
wetwire-github validate [files...]

# Lint Python workflow code
wetwire-github lint [package]

# Import existing YAML to Python
wetwire-github import [files...]

# List discovered workflows
wetwire-github list [package]

# Generate dependency graph
wetwire-github graph [package]

# AI-assisted design (requires wetwire-core)
wetwire-github design

# Persona-based testing (requires wetwire-core)
wetwire-github test
```

### Extended Configuration Types

#### Dependabot

```python
from wetwire_github.dependabot import (
    Dependabot, Update, Schedule, PackageEcosystem
)

config = Dependabot(
    version=2,
    updates=[
        Update(
            package_ecosystem=PackageEcosystem.NPM,
            directory="/",
            schedule=Schedule(interval="weekly"),
        ),
    ],
)
```

#### Issue Templates (Issue Forms)

```python
from wetwire_github.issue_templates import (
    IssueTemplate, Input, Textarea, Dropdown, Checkboxes, Markdown
)

template = IssueTemplate(
    name="Bug Report",
    description="Report a bug",
    labels=["bug"],
    body=[
        Markdown(value="## Bug Report"),
        Input(label="Title", id="title", required=True),
        Textarea(label="Description", id="description"),
        Dropdown(
            label="Severity",
            id="severity",
            options=["Low", "Medium", "High"],
        ),
    ],
)
```

#### Discussion Templates

```python
from wetwire_github.discussion_templates import (
    DiscussionTemplate, DiscussionCategory
)
from wetwire_github.issue_templates import Input, Textarea

template = DiscussionTemplate(
    title="Feature Request",
    labels=["enhancement"],
    body=[
        Input(label="Feature name", id="name"),
        Textarea(label="Description", id="description"),
    ],
)
```

### Typed Action Wrappers

Pre-generated typed wrappers for common GitHub Actions:

```python
from wetwire_github.actions import (
    checkout, setup_python, setup_node, cache,
    upload_artifact, download_artifact,
)

steps = [
    checkout(fetch_depth=0),
    setup_python(python_version="3.11"),
    cache(path="~/.cache/pip", key="pip-${{ hashFiles('**/requirements.txt') }}"),
]
```

### wetwire-core Integration

Integration with wetwire-core for AI-assisted workflow design:

```python
from wetwire_github.core_integration import (
    get_tool_definitions,
    handle_tool_call,
    score_workflow,
    run_persona_test,
)

# Get tool definitions for RunnerAgent
tools = get_tool_definitions()

# Score a workflow for best practices
score = score_workflow("path/to/workflow.yaml")

# Run persona-based testing
result = run_persona_test("reviewer", "path/to/workflow.yaml")
```

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run linter
uv run ruff check

# Run type checker
uv run ty check src/wetwire_github/
```

## License

MIT
