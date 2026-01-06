# wetwire-github (Python)

Generate GitHub YAML configurations from typed Python declarations.

## Syntax Principles

All configurations use typed Python dataclasses. No raw dictionaries, no string templates.

### Workflows

```python
from wetwire_github.workflow import Workflow, Job, Step, Triggers

ci = Workflow(
    name="CI",
    on=Triggers(
        push=PushTrigger(branches=["main"]),
        pull_request=PullRequestTrigger(branches=["main"]),
    ),
    jobs={"build": BuildJob},
)
```

### Jobs

```python
from wetwire_github.workflow import Job, Step

build_job = Job(
    runs_on="ubuntu-latest",
    steps=[
        Step(uses="actions/checkout@v4"),
        Step(run="make build"),
    ],
)
```

### Typed Action Wrappers

Use pre-generated wrappers instead of raw `uses` strings:

```python
from wetwire_github.actions import checkout, setup_python, cache

steps = [
    checkout(fetch_depth=0),
    setup_python(python_version="3.11"),
    cache(path="~/.cache/pip", key="pip-cache"),
]
```

### Expression Contexts

Use typed expression builders for GitHub contexts:

```python
from wetwire_github.workflow.expressions import Secrets, Matrix, GitHub

env = {
    "TOKEN": Secrets.get("DEPLOY_TOKEN"),
    "REF": GitHub.ref,
}

# Conditional execution
if_condition = GitHub.ref == "refs/heads/main"
```

## Package Structure

```
wetwire_github/
├── workflow/           # Core types: Workflow, Job, Step, Triggers
├── actions/            # Typed action wrappers (checkout, setup-*, cache)
├── dependabot/         # Dependabot configuration types
├── issue_templates/    # Issue form types
├── discussion_templates/  # Discussion template types
├── linter/             # 8 lint rules (WAG001-WAG008)
├── importer/           # YAML to Python conversion
├── discover/           # AST-based discovery
└── serialize/          # Python to YAML conversion
```

## Lint Rules (WAG001-WAG008)

- **WAG001**: Use typed action wrappers instead of raw strings
- **WAG002**: Use condition builders instead of raw expressions
- **WAG003**: Use secrets context for secrets access
- **WAG004**: Use matrix builder for matrix configurations
- **WAG005**: Extract inline environment variables
- **WAG006**: Detect duplicate workflow names
- **WAG007**: Flag oversized files (>N jobs)
- **WAG008**: Avoid hardcoded expressions

## Key Principles

1. **Typed dataclasses** — Use Workflow, Job, Step classes
2. **Action wrappers** — Use typed wrappers not raw strings
3. **Expression builders** — Use Secrets.get(), Matrix.get() helpers
4. **Flat declarations** — Extract complex configs to named variables

## Build

```bash
wetwire-github build [package]
# Outputs .github/workflows/*.yml
```

## Project Structure

```
my-project/
├── ci/
│   ├── __init__.py
│   ├── workflows.py    # Workflow definitions
│   ├── jobs.py         # Reusable job definitions
│   └── steps.py        # Common step sequences
└── .github/
    └── workflows/      # Generated YAML output
```
