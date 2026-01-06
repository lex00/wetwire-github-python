# FAQ

For general wetwire questions, see the [central FAQ](https://github.com/lex00/wetwire/blob/main/docs/FAQ.md).

## Getting Started

### How do I install wetwire-github?

```bash
pip install wetwire-github
```

### How do I generate a workflow file?

```bash
wetwire-github build my_package
# Creates .github/workflows/*.yml
```

### How do I import an existing workflow?

```bash
wetwire-github import .github/workflows/ci.yml
```

## Syntax

### How do I declare a workflow?

Use the `Workflow` dataclass with typed triggers and jobs:

```python
from wetwire_github.workflow import Workflow, Job, Step, Triggers, PushTrigger

ci = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger(branches=["main"])),
    jobs={"build": build_job},
)
```

### How do I use typed action wrappers?

Instead of raw `uses` strings, use pre-generated wrappers:

```python
from wetwire_github.actions import checkout, setup_python

steps = [
    checkout(fetch_depth=0),
    setup_python(python_version="3.11"),
]
```

### How do I access secrets?

Use the `Secrets` context:

```python
from wetwire_github.workflow.expressions import Secrets

env = {"TOKEN": Secrets.get("DEPLOY_TOKEN")}
```

### How do I create a matrix build?

Use the `Matrix` class:

```python
from wetwire_github.workflow import Strategy, Matrix

strategy = Strategy(
    matrix=Matrix(
        python=["3.10", "3.11", "3.12"],
        os=["ubuntu-latest", "macos-latest"],
    ),
)
```

## Lint Rules

### What lint rules are available?

| Rule | Description |
|------|-------------|
| WAG001 | Use typed action wrappers |
| WAG002 | Use condition builders |
| WAG003 | Use secrets context |
| WAG004 | Use matrix builder |
| WAG005 | Extract inline variables |
| WAG006 | Duplicate workflows |
| WAG007 | Oversized files |
| WAG008 | Hardcoded expressions |

### How do I run the linter?

```bash
wetwire-github lint my_package
```

## Troubleshooting

### actionlint validation fails

Ensure actionlint is installed:

```bash
# macOS
brew install actionlint

# or download from https://github.com/rhysd/actionlint
```

### Import produces unexpected output

The importer converts YAML to typed Python. Complex expressions may need manual adjustment after import.

## Resources

- [Wetwire Specification](https://github.com/lex00/wetwire/blob/main/docs/WETWIRE_SPEC.md)
- [wetwire-github-go](https://github.com/lex00/wetwire-github-go) - Go implementation
