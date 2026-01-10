# Examples Reference

This document provides comprehensive examples of wetwire-github usage patterns for GitHub Actions workflows, Dependabot configuration, and issue templates.

## Table of Contents

- [Basic CI Workflow](#basic-ci-workflow)
- [Matrix Build Workflow](#matrix-build-workflow)
- [Multi-Job CI/CD Pipeline](#multi-job-cicd-pipeline)
- [Release Workflow with Secrets](#release-workflow-with-secrets)
- [Using Action Wrappers](#using-action-wrappers)
- [Dependabot Configuration](#dependabot-configuration)
- [Issue Templates](#issue-templates)
- [Conditional Execution](#conditional-execution)
- [Reusable Workflows](#reusable-workflows)
- [Scheduled Workflows](#scheduled-workflows)
- [Container Jobs](#container-jobs)
- [Service Containers](#service-containers)

---

## Basic CI Workflow

A simple CI workflow that runs on push and pull requests:

```python
from wetwire_github.workflow import (
    Workflow,
    Job,
    Step,
    Triggers,
    PushTrigger,
    PullRequestTrigger,
)
from wetwire_github.actions import checkout, setup_python

# Define the build job
build_job = Job(
    runs_on="ubuntu-latest",
    steps=[
        checkout(),
        setup_python(python_version="3.11"),
        Step(run="pip install -e '.[dev]'"),
        Step(run="pytest"),
    ],
)

# Define the workflow
ci = Workflow(
    name="CI",
    on=Triggers(
        push=PushTrigger(branches=["main"]),
        pull_request=PullRequestTrigger(branches=["main"]),
    ),
    jobs={"build": build_job},
)
```

**Generated YAML:**
```yaml
name: CI
on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - run: pip install -e '.[dev]'
      - run: pytest
```

---

## Matrix Build Workflow

Test across multiple Python versions and operating systems:

```python
from wetwire_github.workflow import (
    Workflow,
    Job,
    Step,
    Triggers,
    PushTrigger,
    Strategy,
    Matrix,
)
from wetwire_github.workflow.expressions import MatrixContext
from wetwire_github.actions import checkout, setup_python

# Define matrix strategy
test_strategy = Strategy(
    matrix=Matrix(
        values={
            "python-version": ["3.10", "3.11", "3.12"],
            "os": ["ubuntu-latest", "macos-latest", "windows-latest"],
        },
    ),
    fail_fast=False,
)

# Define the test job
test_job = Job(
    runs_on=str(MatrixContext.get("os")),
    strategy=test_strategy,
    steps=[
        checkout(),
        setup_python(python_version=str(MatrixContext.get("python-version"))),
        Step(run="pip install -e '.[dev]'"),
        Step(run="pytest --cov"),
    ],
)

# Define the workflow
matrix_ci = Workflow(
    name="Matrix CI",
    on=Triggers(push=PushTrigger(branches=["main", "develop"])),
    jobs={"test": test_job},
)
```

### Matrix with Include/Exclude

Add specific combinations or exclude certain ones:

```python
from wetwire_github.workflow import Strategy, Matrix

strategy = Strategy(
    matrix=Matrix(
        values={
            "python-version": ["3.10", "3.11", "3.12"],
            "os": ["ubuntu-latest", "macos-latest"],
        },
        include=[
            # Add experimental Python 3.13 on Ubuntu only
            {"python-version": "3.13", "os": "ubuntu-latest", "experimental": True},
        ],
        exclude=[
            # Skip Python 3.10 on macOS
            {"python-version": "3.10", "os": "macos-latest"},
        ],
    ),
    fail_fast=False,
)
```

---

## Multi-Job CI/CD Pipeline

A complete CI/CD pipeline with build, test, and deploy stages:

```python
from wetwire_github.workflow import (
    Workflow,
    Job,
    Step,
    Triggers,
    PushTrigger,
    Environment,
    Permissions,
)
from wetwire_github.workflow.expressions import Secrets, GitHub, Needs
from wetwire_github.actions import checkout, setup_python, upload_artifact, download_artifact

# Build job - compiles and packages the application
build_job = Job(
    name="Build",
    runs_on="ubuntu-latest",
    steps=[
        checkout(),
        setup_python(python_version="3.11"),
        Step(run="pip install build"),
        Step(run="python -m build"),
        upload_artifact(name="dist", path="dist/"),
    ],
    outputs={"version": "${{ steps.version.outputs.version }}"},
)

# Test job - runs test suite after build completes
test_job = Job(
    name="Test",
    runs_on="ubuntu-latest",
    needs=["build"],
    steps=[
        checkout(),
        setup_python(python_version="3.11"),
        download_artifact(name="dist"),
        Step(run="pip install dist/*.whl"),
        Step(run="pytest tests/ -v"),
    ],
)

# Lint job - runs in parallel with test
lint_job = Job(
    name="Lint",
    runs_on="ubuntu-latest",
    needs=["build"],
    steps=[
        checkout(),
        setup_python(python_version="3.11"),
        Step(run="pip install ruff"),
        Step(run="ruff check ."),
        Step(run="ruff format --check ."),
    ],
)

# Deploy job - deploys to production after all checks pass
deploy_job = Job(
    name="Deploy",
    runs_on="ubuntu-latest",
    needs=["test", "lint"],
    if_=str(GitHub.ref == "refs/heads/main"),
    environment=Environment(name="production", url="https://myapp.example.com"),
    permissions=Permissions(contents="read", id_token="write"),
    steps=[
        checkout(),
        download_artifact(name="dist"),
        Step(
            name="Publish to PyPI",
            run="twine upload dist/*",
            env={
                "TWINE_USERNAME": "__token__",
                "TWINE_PASSWORD": str(Secrets.get("PYPI_TOKEN")),
            },
        ),
    ],
)

# Define the complete workflow
cicd = Workflow(
    name="CI/CD Pipeline",
    on=Triggers(push=PushTrigger(branches=["main", "develop"])),
    jobs={
        "build": build_job,
        "test": test_job,
        "lint": lint_job,
        "deploy": deploy_job,
    },
)
```

---

## Release Workflow with Secrets

Publish releases when tags are pushed:

```python
from wetwire_github.workflow import (
    Workflow,
    Job,
    Step,
    Triggers,
    PushTrigger,
    Permissions,
)
from wetwire_github.workflow.expressions import Secrets, GitHub
from wetwire_github.actions import checkout, setup_python

release_job = Job(
    name="Release",
    runs_on="ubuntu-latest",
    permissions=Permissions(contents="write"),
    steps=[
        checkout(fetch_depth="0"),
        setup_python(python_version="3.11"),
        Step(run="pip install build twine"),
        Step(run="python -m build"),
        Step(
            name="Create GitHub Release",
            run="gh release create ${{ github.ref_name }} dist/* --generate-notes",
            env={"GH_TOKEN": str(Secrets.get("GITHUB_TOKEN"))},
        ),
        Step(
            name="Publish to PyPI",
            run="twine upload dist/*",
            env={
                "TWINE_USERNAME": "__token__",
                "TWINE_PASSWORD": str(Secrets.get("PYPI_TOKEN")),
            },
        ),
    ],
)

release = Workflow(
    name="Release",
    on=Triggers(push=PushTrigger(tags=["v*.*.*"])),
    jobs={"release": release_job},
)
```

### Using Multiple Secrets

```python
from wetwire_github.workflow import Step
from wetwire_github.workflow.expressions import Secrets

deploy_step = Step(
    name="Deploy to AWS",
    run="aws s3 sync ./dist s3://my-bucket/",
    env={
        "AWS_ACCESS_KEY_ID": str(Secrets.get("AWS_ACCESS_KEY_ID")),
        "AWS_SECRET_ACCESS_KEY": str(Secrets.get("AWS_SECRET_ACCESS_KEY")),
        "AWS_REGION": "us-east-1",
    },
)
```

---

## Using Action Wrappers

wetwire-github provides typed wrappers for common GitHub Actions:

```python
from wetwire_github.workflow import Job, Step
from wetwire_github.actions import (
    checkout,
    setup_python,
    setup_node,
    setup_go,
    setup_java,
    cache,
    upload_artifact,
    download_artifact,
)

# Checkout with options
checkout(
    fetch_depth="0",           # Full history for versioning
    submodules="recursive",    # Include submodules
    token="${{ secrets.PAT }}", # Custom token for private repos
)

# Python setup with caching
setup_python(
    python_version="3.11",
    cache="pip",               # Enable pip caching
    cache_dependency_path="requirements.txt",
)

# Node.js setup
setup_node(
    node_version="20",
    cache="npm",
)

# Go setup
setup_go(
    go_version="1.21",
)

# Java setup
setup_java(
    java_version="17",
    distribution="temurin",
)

# Custom cache
cache(
    path="~/.cache/pip",
    key="pip-${{ runner.os }}-${{ hashFiles('requirements.txt') }}",
    restore_keys="pip-${{ runner.os }}-",
)

# Upload build artifacts
upload_artifact(
    name="coverage-report",
    path="htmlcov/",
    retention_days="30",
)

# Download artifacts from previous job
download_artifact(
    name="coverage-report",
    path="./reports/",
)
```

### Complete Example with Wrappers

```python
from wetwire_github.workflow import Workflow, Job, Step, Triggers, PushTrigger
from wetwire_github.actions import checkout, setup_python, cache, upload_artifact

build_job = Job(
    runs_on="ubuntu-latest",
    steps=[
        checkout(fetch_depth="0"),
        setup_python(python_version="3.11", cache="pip"),
        cache(
            path=".venv",
            key="venv-${{ runner.os }}-${{ hashFiles('pyproject.toml') }}",
        ),
        Step(name="Install dependencies", run="pip install -e '.[dev]'"),
        Step(name="Run tests", run="pytest --cov --cov-report=html"),
        upload_artifact(name="coverage", path="htmlcov/"),
    ],
)

ci = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger(branches=["main"])),
    jobs={"build": build_job},
)
```

---

## Dependabot Configuration

Configure Dependabot to keep dependencies updated:

```python
from wetwire_github.dependabot import (
    Dependabot,
    Update,
    Schedule,
    PackageEcosystem,
    Group,
)

# Basic configuration
dependabot = Dependabot(
    version=2,
    updates=[
        # Python dependencies
        Update(
            package_ecosystem=PackageEcosystem.PIP,
            directory="/",
            schedule=Schedule(interval="weekly", day="monday", time="09:00"),
            labels=["dependencies", "python"],
            reviewers=["myorg/python-team"],
            open_pull_requests_limit=10,
        ),
        # GitHub Actions
        Update(
            package_ecosystem=PackageEcosystem.GITHUB_ACTIONS,
            directory="/",
            schedule=Schedule(interval="weekly"),
            labels=["dependencies", "github-actions"],
        ),
        # npm for frontend
        Update(
            package_ecosystem=PackageEcosystem.NPM,
            directory="/frontend",
            schedule=Schedule(interval="daily"),
        ),
    ],
)
```

### Grouping Dependencies

```python
from wetwire_github.dependabot import Dependabot, Update, Schedule, PackageEcosystem, Group

dependabot = Dependabot(
    version=2,
    updates=[
        Update(
            package_ecosystem=PackageEcosystem.PIP,
            directory="/",
            schedule=Schedule(interval="weekly"),
            groups={
                "dev-dependencies": Group(
                    patterns=["pytest*", "ruff", "mypy", "black"],
                    dependency_type="development",
                ),
                "aws-sdk": Group(
                    patterns=["boto3", "botocore", "aiobotocore"],
                ),
            },
        ),
    ],
)
```

### Ignoring Dependencies

```python
from wetwire_github.dependabot import Update, Schedule, PackageEcosystem

update = Update(
    package_ecosystem=PackageEcosystem.PIP,
    directory="/",
    schedule=Schedule(interval="weekly"),
    ignore=[
        {"dependency-name": "django", "versions": [">=5.0"]},
        {"dependency-name": "numpy", "update-types": ["version-update:semver-major"]},
    ],
)
```

---

## Issue Templates

Create GitHub Issue Forms with typed elements:

### Bug Report Template

```python
from wetwire_github.issue_templates import (
    IssueTemplate,
    Input,
    Textarea,
    Dropdown,
    Checkboxes,
    CheckboxOption,
    Markdown,
)

bug_report = IssueTemplate(
    name="Bug Report",
    description="Report a bug to help us improve",
    title="[Bug]: ",
    labels=["bug", "triage"],
    assignees=["maintainer1"],
    body=[
        Markdown(value="Thanks for taking the time to fill out this bug report!"),
        Input(
            id="version",
            label="Version",
            description="What version of the software are you running?",
            placeholder="e.g., 1.2.3",
            required=True,
        ),
        Dropdown(
            id="os",
            label="Operating System",
            description="What OS are you using?",
            options=["Linux", "macOS", "Windows", "Other"],
            required=True,
        ),
        Textarea(
            id="description",
            label="Bug Description",
            description="A clear and concise description of the bug",
            placeholder="Describe what happened...",
            required=True,
        ),
        Textarea(
            id="steps",
            label="Steps to Reproduce",
            description="Steps to reproduce the behavior",
            placeholder="1. Go to...\n2. Click on...\n3. See error",
            required=True,
        ),
        Textarea(
            id="expected",
            label="Expected Behavior",
            description="What did you expect to happen?",
            required=True,
        ),
        Textarea(
            id="logs",
            label="Relevant Logs",
            description="Please copy and paste any relevant log output",
            render="shell",
            required=False,
        ),
        Checkboxes(
            id="terms",
            label="Code of Conduct",
            description="Please confirm the following:",
            options=[
                CheckboxOption(
                    label="I have searched for existing issues",
                    required=True,
                ),
                CheckboxOption(
                    label="I agree to follow the Code of Conduct",
                    required=True,
                ),
            ],
        ),
    ],
)
```

### Feature Request Template

```python
from wetwire_github.issue_templates import (
    IssueTemplate,
    Input,
    Textarea,
    Dropdown,
    Markdown,
)

feature_request = IssueTemplate(
    name="Feature Request",
    description="Suggest a new feature or enhancement",
    title="[Feature]: ",
    labels=["enhancement"],
    body=[
        Markdown(value="## Feature Request\n\nPlease describe the feature you'd like."),
        Input(
            id="summary",
            label="Feature Summary",
            description="A brief summary of the feature",
            required=True,
        ),
        Dropdown(
            id="priority",
            label="Priority",
            options=["Low", "Medium", "High", "Critical"],
            default=1,  # Medium
            required=True,
        ),
        Textarea(
            id="motivation",
            label="Motivation",
            description="Why do you want this feature? What problem does it solve?",
            required=True,
        ),
        Textarea(
            id="proposal",
            label="Proposed Solution",
            description="Describe how you'd like this feature to work",
            required=True,
        ),
        Textarea(
            id="alternatives",
            label="Alternatives Considered",
            description="What alternatives have you considered?",
            required=False,
        ),
    ],
)
```

---

## Conditional Execution

Use expression helpers for conditional job and step execution:

```python
from wetwire_github.workflow import Workflow, Job, Step, Triggers, PushTrigger
from wetwire_github.workflow.expressions import (
    GitHub,
    Secrets,
    Needs,
    always,
    failure,
    success,
    cancelled,
    branch,
    tag,
)
from wetwire_github.actions import checkout

# Branch-based conditions
deploy_job = Job(
    runs_on="ubuntu-latest",
    if_=str(branch("main")),  # Only run on main branch
    steps=[
        checkout(),
        Step(run="make deploy"),
    ],
)

# Tag-based conditions
release_job = Job(
    runs_on="ubuntu-latest",
    if_=str(tag("v*")),  # Only run on version tags
    steps=[
        checkout(),
        Step(run="make release"),
    ],
)

# Combining conditions
staging_job = Job(
    runs_on="ubuntu-latest",
    if_=str(branch("develop").or_(branch("staging"))),
    steps=[
        checkout(),
        Step(run="make deploy-staging"),
    ],
)

# Always run cleanup (even on failure)
cleanup_job = Job(
    runs_on="ubuntu-latest",
    needs=["build", "test"],
    if_=str(always()),
    steps=[
        Step(run="make cleanup"),
    ],
)

# Run only on failure
notify_failure_job = Job(
    runs_on="ubuntu-latest",
    needs=["build", "test"],
    if_=str(failure()),
    steps=[
        Step(
            name="Notify Slack",
            run="curl -X POST $SLACK_WEBHOOK -d '{\"text\":\"Build failed!\"}'",
            env={"SLACK_WEBHOOK": str(Secrets.get("SLACK_WEBHOOK"))},
        ),
    ],
)
```

### Step-Level Conditions

```python
from wetwire_github.workflow import Job, Step
from wetwire_github.workflow.expressions import GitHub, success, failure

job = Job(
    runs_on="ubuntu-latest",
    steps=[
        Step(name="Build", run="make build"),
        Step(name="Test", run="make test"),
        Step(
            name="Upload coverage",
            run="codecov",
            if_=str(success()),  # Only if tests passed
        ),
        Step(
            name="Debug logs",
            run="cat build.log",
            if_=str(failure()),  # Only if something failed
        ),
    ],
)
```

### Complex Conditions

```python
from wetwire_github.workflow.expressions import GitHub, Secrets, Expression

# Check for specific event
is_pr = Expression("github.event_name == 'pull_request'")
is_push = Expression("github.event_name == 'push'")

# Check actor
is_bot = Expression("github.actor == 'dependabot[bot]'")
is_admin = Expression("contains(github.event.sender.type, 'Bot') == false")

# Combine multiple conditions
deploy_condition = branch("main").and_(Expression("github.event_name == 'push'"))
```

---

## Reusable Workflows

### Workflow Call Trigger

Create a reusable workflow that can be called by other workflows:

```python
from wetwire_github.workflow import (
    Workflow,
    Job,
    Step,
    Triggers,
    WorkflowCallTrigger,
    WorkflowInput,
    WorkflowOutput,
    WorkflowSecret,
)
from wetwire_github.workflow.expressions import Inputs, Secrets
from wetwire_github.actions import checkout, setup_python

# Reusable workflow with inputs and outputs
reusable_build = Workflow(
    name="Reusable Build",
    on=Triggers(
        workflow_call=WorkflowCallTrigger(
            inputs={
                "python-version": WorkflowInput(
                    description="Python version to use",
                    required=True,
                    type="string",
                    default="3.11",
                ),
                "run-tests": WorkflowInput(
                    description="Whether to run tests",
                    required=False,
                    type="boolean",
                    default="true",
                ),
            },
            outputs={
                "artifact-name": WorkflowOutput(
                    description="Name of the uploaded artifact",
                    value="${{ jobs.build.outputs.artifact-name }}",
                ),
            },
            secrets={
                "pypi-token": WorkflowSecret(
                    description="PyPI API token",
                    required=True,
                ),
            },
        ),
    ),
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            outputs={"artifact-name": "dist-${{ github.sha }}"},
            steps=[
                checkout(),
                setup_python(python_version=str(Inputs.get("python-version"))),
                Step(run="pip install build && python -m build"),
                Step(
                    name="Run tests",
                    run="pytest",
                    if_=str(Inputs.get("run-tests")),
                ),
            ],
        ),
    },
)
```

### Calling a Reusable Workflow

```python
from wetwire_github.workflow import Workflow, Job, Step, Triggers, PushTrigger
from wetwire_github.workflow.expressions import Secrets

caller_workflow = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger(branches=["main"])),
    jobs={
        "build": Job(
            uses="./.github/workflows/reusable-build.yml",
            with_={
                "python-version": "3.12",
                "run-tests": True,
            },
            secrets={
                "pypi-token": str(Secrets.get("PYPI_TOKEN")),
            },
        ),
    },
)
```

---

## Scheduled Workflows

Run workflows on a schedule using cron expressions:

```python
from wetwire_github.workflow import (
    Workflow,
    Job,
    Step,
    Triggers,
    ScheduleTrigger,
)
from wetwire_github.actions import checkout

# Daily security scan
security_job = Job(
    runs_on="ubuntu-latest",
    steps=[
        checkout(),
        Step(run="pip install safety"),
        Step(run="safety check"),
    ],
)

scheduled = Workflow(
    name="Scheduled Security Scan",
    on=Triggers(
        schedule=[
            ScheduleTrigger(cron="0 6 * * *"),  # Every day at 6 AM UTC
        ],
    ),
    jobs={"security": security_job},
)

# Multiple schedules
multi_schedule = Workflow(
    name="Multiple Schedules",
    on=Triggers(
        schedule=[
            ScheduleTrigger(cron="0 */6 * * *"),  # Every 6 hours
            ScheduleTrigger(cron="0 0 * * 0"),    # Weekly on Sunday
        ],
    ),
    jobs={"job": Job(runs_on="ubuntu-latest", steps=[Step(run="echo 'Running'")])},
)
```

---

## Container Jobs

Run jobs in Docker containers:

```python
from wetwire_github.workflow import (
    Workflow,
    Job,
    Step,
    Triggers,
    PushTrigger,
    Container,
)
from wetwire_github.workflow.expressions import Secrets

container_job = Job(
    runs_on="ubuntu-latest",
    container=Container(
        image="python:3.11-slim",
        env={"PYTHONUNBUFFERED": "1"},
        volumes=["/tmp/data:/data"],
        options="--cpus 2 --memory 4g",
    ),
    steps=[
        Step(run="python --version"),
        Step(run="pip install pytest && pytest"),
    ],
)

# Container with credentials
private_container_job = Job(
    runs_on="ubuntu-latest",
    container=Container(
        image="ghcr.io/myorg/myimage:latest",
        credentials={
            "username": "${{ github.actor }}",
            "password": str(Secrets.get("GITHUB_TOKEN")),
        },
    ),
    steps=[
        Step(run="run-my-tool"),
    ],
)

container_workflow = Workflow(
    name="Container Jobs",
    on=Triggers(push=PushTrigger(branches=["main"])),
    jobs={
        "container": container_job,
        "private": private_container_job,
    },
)
```

---

## Service Containers

Use service containers for databases and other services:

```python
from wetwire_github.workflow import (
    Workflow,
    Job,
    Step,
    Triggers,
    PushTrigger,
    Service,
)
from wetwire_github.workflow.expressions import Secrets
from wetwire_github.actions import checkout, setup_python

# Job with PostgreSQL service
test_with_db = Job(
    runs_on="ubuntu-latest",
    services={
        "postgres": Service(
            image="postgres:15",
            env={
                "POSTGRES_USER": "testuser",
                "POSTGRES_PASSWORD": "testpass",
                "POSTGRES_DB": "testdb",
            },
            ports=["5432:5432"],
            options="--health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5",
        ),
        "redis": Service(
            image="redis:7",
            ports=["6379:6379"],
        ),
    },
    steps=[
        checkout(),
        setup_python(python_version="3.11"),
        Step(run="pip install -e '.[test]'"),
        Step(
            run="pytest",
            env={
                "DATABASE_URL": "postgresql://testuser:testpass@postgres:5432/testdb",
                "REDIS_URL": "redis://redis:6379",
            },
        ),
    ],
)

services_workflow = Workflow(
    name="Integration Tests",
    on=Triggers(push=PushTrigger(branches=["main"])),
    jobs={"test": test_with_db},
)
```

---

## Project Structure

Organize your workflow definitions across multiple files:

```
ci/
├── __init__.py
├── workflows.py       # Main workflow definitions
├── jobs.py            # Reusable job definitions
├── steps.py           # Common step sequences
└── dependabot.py      # Dependabot configuration
```

### ci/steps.py

```python
"""Common step sequences for reuse across jobs."""

from wetwire_github.workflow import Step
from wetwire_github.actions import checkout, setup_python, cache


def python_setup_steps(python_version: str = "3.11") -> list[Step]:
    """Standard Python setup steps with caching."""
    return [
        checkout(),
        setup_python(python_version=python_version, cache="pip"),
        cache(
            path=".venv",
            key="venv-${{ runner.os }}-${{ hashFiles('pyproject.toml') }}",
        ),
    ]


def install_and_test_steps() -> list[Step]:
    """Install dependencies and run tests."""
    return [
        Step(name="Install dependencies", run="pip install -e '.[dev]'"),
        Step(name="Run linter", run="ruff check ."),
        Step(name="Run tests", run="pytest --cov"),
    ]
```

### ci/jobs.py

```python
"""Reusable job definitions."""

from wetwire_github.workflow import Job, Step, Strategy, Matrix
from .steps import python_setup_steps, install_and_test_steps


def python_test_job(python_version: str = "3.11") -> Job:
    """Create a standard Python test job."""
    return Job(
        runs_on="ubuntu-latest",
        steps=python_setup_steps(python_version) + install_and_test_steps(),
    )


def matrix_test_job() -> Job:
    """Create a matrix test job across Python versions."""
    return Job(
        runs_on="ubuntu-latest",
        strategy=Strategy(
            matrix=Matrix(
                values={"python-version": ["3.10", "3.11", "3.12"]},
            ),
            fail_fast=False,
        ),
        steps=python_setup_steps("${{ matrix.python-version }}") + install_and_test_steps(),
    )
```

### ci/workflows.py

```python
"""Main workflow definitions."""

from wetwire_github.workflow import Workflow, Triggers, PushTrigger, PullRequestTrigger
from .jobs import python_test_job, matrix_test_job

ci = Workflow(
    name="CI",
    on=Triggers(
        push=PushTrigger(branches=["main"]),
        pull_request=PullRequestTrigger(branches=["main"]),
    ),
    jobs={"test": python_test_job()},
)

ci_matrix = Workflow(
    name="CI Matrix",
    on=Triggers(
        push=PushTrigger(branches=["main"]),
        pull_request=PullRequestTrigger(branches=["main"]),
    ),
    jobs={"test": matrix_test_job()},
)
```

---

## Building Workflows

Generate YAML from your Python definitions:

```bash
# Build all workflows in a package
wetwire-github build ci/

# Build specific workflow types
wetwire-github build ci/ --type workflow
wetwire-github build ci/ --type dependabot
wetwire-github build ci/ --type issue-template

# List discovered workflows
wetwire-github list ci/

# Lint workflow declarations
wetwire-github lint ci/

# Auto-fix lint issues
wetwire-github lint ci/ --fix

# Validate generated YAML
wetwire-github validate .github/workflows/
```

---

## See Also

- [Quick Start](QUICK_START.md) - Getting started guide
- [Composite Actions](COMPOSITE_ACTIONS.md) - Best practices for composite actions
- [CLI Reference](CLI.md) - Full CLI documentation
- [Developers Guide](DEVELOPERS.md) - Contributing guidelines
- [FAQ](FAQ.md) - Frequently asked questions
