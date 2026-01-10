# Quick Start

Get started with `wetwire-github` in 5 minutes.

## Installation

```bash
uv add wetwire-github
```

Or with pip:

```bash
pip install wetwire-github
```

---

## Your First Workflow

Create a package for your CI/CD configuration:

```
ci/
├── __init__.py
└── workflows.py
```

**ci/workflows.py:**
```python
from wetwire_github.workflow import Workflow, Job, Step, Triggers, PushTrigger
from wetwire_github.actions import checkout

build_job = Job(
    runs_on="ubuntu-latest",
    steps=[
        checkout(),
        Step(run="echo 'Hello, World!'"),
    ],
)

ci = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger(branches=["main"])),
    jobs={"build": build_job},
)
```

**Generate YAML:**
```bash
wetwire-github build ci/
# Creates .github/workflows/ci.yml
```

That's it. Workflows are discovered from Python declarations and serialized to GitHub Actions YAML.

---

## Using Typed Action Wrappers

Instead of raw `uses` strings, use pre-generated typed wrappers:

```python
from wetwire_github.workflow import Workflow, Job, Step, Triggers, PushTrigger
from wetwire_github.actions import checkout, setup_python, cache

build_job = Job(
    runs_on="ubuntu-latest",
    steps=[
        checkout(fetch_depth=0),
        setup_python(python_version="3.11"),
        cache(
            path="~/.cache/pip",
            key="pip-${{ hashFiles('**/requirements.txt') }}",
        ),
        Step(run="pip install -r requirements.txt"),
        Step(run="pytest"),
    ],
)
```

Available action wrappers:
- `checkout()` - actions/checkout
- `setup_python()` - actions/setup-python
- `setup_node()` - actions/setup-node
- `setup_go()` - actions/setup-go
- `setup_java()` - actions/setup-java
- `cache()` - actions/cache
- `upload_artifact()` - actions/upload-artifact
- `download_artifact()` - actions/download-artifact

---

## Expression Helpers

Use typed expression builders for GitHub contexts:

```python
from wetwire_github.workflow.expressions import Secrets, GitHub, Matrix

# Access secrets
env = {
    "TOKEN": Secrets.get("DEPLOY_TOKEN"),
    "NPM_TOKEN": Secrets.get("NPM_TOKEN"),
}

# Access GitHub context
if_condition = GitHub.ref == "refs/heads/main"

# Access matrix values
python_version = Matrix.get("python")
```

---

## Matrix Builds

Create matrix builds for testing across multiple configurations:

```python
from wetwire_github.workflow import Job, Step, Strategy, Matrix

test_job = Job(
    runs_on="ubuntu-latest",
    strategy=Strategy(
        matrix=Matrix(
            python=["3.10", "3.11", "3.12"],
            os=["ubuntu-latest", "macos-latest"],
        ),
    ),
    steps=[
        checkout(),
        setup_python(python_version="${{ matrix.python }}"),
        Step(run="pytest"),
    ],
)
```

---

## Multi-Job Workflows

Define job dependencies with `needs`:

```python
from wetwire_github.workflow import Workflow, Job, Step, Triggers, PushTrigger
from wetwire_github.actions import checkout

build_job = Job(
    runs_on="ubuntu-latest",
    steps=[
        checkout(),
        Step(run="make build"),
    ],
)

test_job = Job(
    runs_on="ubuntu-latest",
    needs=["build"],
    steps=[
        checkout(),
        Step(run="make test"),
    ],
)

deploy_job = Job(
    runs_on="ubuntu-latest",
    needs=["test"],
    if_condition="${{ github.ref == 'refs/heads/main' }}",
    steps=[
        checkout(),
        Step(run="make deploy"),
    ],
)

ci = Workflow(
    name="CI/CD",
    on=Triggers(push=PushTrigger(branches=["main"])),
    jobs={
        "build": build_job,
        "test": test_job,
        "deploy": deploy_job,
    },
)
```

---

## Using the CLI

```bash
# Generate YAML from Python declarations
wetwire-github build ci/

# List discovered workflows
wetwire-github list ci/

# Lint workflow declarations
wetwire-github lint ci/

# Auto-fix lintable issues
wetwire-github lint ci/ --fix

# Validate generated YAML (requires actionlint)
wetwire-github validate .github/workflows/

# Visualize job dependencies
wetwire-github graph ci/
```

---

## Importing Existing Workflows

Convert existing YAML workflows to typed Python:

```bash
# Import a single workflow
wetwire-github import .github/workflows/ci.yml -o ci/

# Import all workflows
wetwire-github import .github/workflows/*.yml -o ci/
```

This generates typed Python code that you can then modify and regenerate.

---

## Multi-File Organization

Split workflows across files:

```
ci/
├── __init__.py
├── workflows.py     # Main workflow definitions
├── jobs.py          # Reusable job definitions
└── steps.py         # Common step sequences
```

**ci/jobs.py:**
```python
from wetwire_github.workflow import Job, Step
from wetwire_github.actions import checkout, setup_python

def python_test_job(python_version: str = "3.11") -> Job:
    """Create a Python test job."""
    return Job(
        runs_on="ubuntu-latest",
        steps=[
            checkout(),
            setup_python(python_version=python_version),
            Step(run="pip install -e '.[dev]'"),
            Step(run="pytest"),
        ],
    )
```

**ci/workflows.py:**
```python
from wetwire_github.workflow import Workflow, Triggers, PushTrigger, PullRequestTrigger
from .jobs import python_test_job

ci = Workflow(
    name="CI",
    on=Triggers(
        push=PushTrigger(branches=["main"]),
        pull_request=PullRequestTrigger(branches=["main"]),
    ),
    jobs={"test": python_test_job("3.11")},
)
```

---

## Dependabot Configuration

Define Dependabot configuration with typed dataclasses:

```python
from wetwire_github.dependabot import Dependabot, Update, Schedule, PackageEcosystem

dependabot = Dependabot(
    version=2,
    updates=[
        Update(
            package_ecosystem=PackageEcosystem.PIP,
            directory="/",
            schedule=Schedule(interval="weekly"),
        ),
        Update(
            package_ecosystem=PackageEcosystem.GITHUB_ACTIONS,
            directory="/",
            schedule=Schedule(interval="weekly"),
        ),
    ],
)
```

```bash
wetwire-github build ci/ --type dependabot
# Creates .github/dependabot.yml
```

---

## Issue Templates

Create GitHub Issue Forms with typed elements:

```python
from wetwire_github.issue_templates import (
    IssueTemplate, Input, Textarea, Dropdown
)

bug_report = IssueTemplate(
    name="Bug Report",
    description="Report a bug",
    body=[
        Input(
            id="version",
            label="Version",
            description="What version are you using?",
            required=True,
        ),
        Textarea(
            id="description",
            label="Bug Description",
            description="Describe the bug",
            required=True,
        ),
        Dropdown(
            id="severity",
            label="Severity",
            options=["Low", "Medium", "High", "Critical"],
            required=True,
        ),
    ],
)
```

```bash
wetwire-github build ci/ --type issue-template
# Creates .github/ISSUE_TEMPLATE/bug_report.yml
```

---

## Scaffold a New Project

Create a new project with example workflow:

```bash
wetwire-github init my-ci
```

This creates:
```
my-ci/
├── __init__.py
├── workflows.py
└── pyproject.toml
```

---

## AI-Assisted Design

Create workflows interactively with AI:

```bash
# Start design session (uses Anthropic API by default)
wetwire-github design

# Use Kiro CLI for enterprise environments
wetwire-github design --provider kiro

# Example prompt:
# "Create a CI workflow that runs tests on Python 3.11 and 3.12,
#  deploys to production on main branch"
```

Requires `wetwire-core` and `ANTHROPIC_API_KEY` for the default provider.
For Kiro CLI integration, see the [Kiro CLI Guide](GITHUB-KIRO-CLI.md).

---

## MCP Server (AI Agent Integration)

Enable AI tools like Claude Code to interact with wetwire-github:

```bash
# Install with MCP support
pip install wetwire-github[mcp]

# Start the MCP server
wetwire-github mcp-server
```

Configure your AI tool to use the MCP server. For Claude Code, add to your MCP configuration:

```json
{
  "mcpServers": {
    "wetwire-github": {
      "command": "wetwire-github",
      "args": ["mcp-server"]
    }
  }
}
```

See [MCP Server Documentation](MCP_SERVER.md) for full configuration options.

---

## Next Steps

- See the full [CLI Reference](CLI.md)
- Learn about [Lint Rules](LINT_RULES.md)
- Explore [Examples](EXAMPLES.md)
- Create [Composite Actions](COMPOSITE_ACTIONS.md)
- Set up [MCP Server](MCP_SERVER.md) for AI agent integration
- Set up [Kiro CLI Integration](GITHUB-KIRO-CLI.md) for enterprise AI-assisted design
- Read the [Wetwire Specification](https://github.com/lex00/wetwire/blob/main/docs/WETWIRE_SPEC.md)
