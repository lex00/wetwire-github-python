# wetwire-github

Generate GitHub YAML configurations from typed Python declarations.

## Installation

```bash
pip install wetwire-github
```

## Quick Start

```python
# __init__.py - Set up the namespace
from wetwire_github.loader import setup_all
setup_all(__file__, __name__, globals())
```

```python
# workflows.py - Define workflows using injected types
from . import *

# Flat declarations - define steps, jobs, then workflow
build_steps = [
    checkout(),
    setup_python(python_version="3.11"),
    Step(run="make build"),
]

build_job = Job(
    runs_on="ubuntu-latest",
    steps=build_steps,
)

ci_triggers = Triggers(
    push=PushTrigger(branches=["main"]),
)

ci = Workflow(
    name="CI",
    on=ci_triggers,
    jobs={"build": build_job},
)
```

```bash
wetwire-github build mypackage
```

## Features

### Flat, Declarative Patterns

wetwire encourages flat declarations - define small pieces and compose:

```python
# workflows.py
from . import *

# Define steps separately
checkout_step = checkout(fetch_depth=0)
python_step = setup_python(python_version="3.11")
cache_step = cache(path="~/.cache/pip", key="pip-deps")
test_step = Step(run="pytest")

# Compose into jobs
test_job = Job(
    runs_on="ubuntu-latest",
    steps=[checkout_step, python_step, cache_step, test_step],
)

# Define triggers
ci_triggers = Triggers(
    push=PushTrigger(branches=["main"]),
    pull_request=PullRequestTrigger(branches=["main"]),
)

# Compose workflow
ci = Workflow(
    name="CI",
    on=ci_triggers,
    jobs={"test": test_job},
)
```

### CLI Commands

```bash
# Create a new project
wetwire-github init [name]

# Generate YAML from Python declarations
wetwire-github build [package]

# Validate YAML files with actionlint
wetwire-github validate [files...]

# Lint Python workflow code (--fix for auto-fix)
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
# dependabot.py
from . import *

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
# issue_templates.py
from . import *

bug_report = IssueTemplate(
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

### Typed Action Wrappers

Pre-generated typed wrappers for common GitHub Actions are injected into the namespace:

```python
# workflows.py
from . import *

steps = [
    checkout(fetch_depth=0),
    setup_python(python_version="3.11"),
    cache(path="~/.cache/pip", key="pip-${{ hashFiles('**/requirements.txt') }}"),
]
```

Available wrappers: `checkout`, `setup_python`, `setup_node`, `setup_go`, `setup_java`, `setup_dotnet`, `setup_ruby`, `cache`, `upload_artifact`, `download_artifact`, `github_script`, `docker_login`, `docker_build_push`, and more.

### GitHub Context Pseudo-Parameters

Type-safe constants for GitHub context values:

```python
# workflows.py
from . import *

deploy_step = Step(
    run="./deploy.sh",
    env={
        "REF": GITHUB_REF,
        "SHA": GITHUB_SHA,
        "ACTOR": GITHUB_ACTOR,
    },
)
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
