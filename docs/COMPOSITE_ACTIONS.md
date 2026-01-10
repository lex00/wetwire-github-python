# Composite Actions Best Practices

This document covers best practices for creating and using composite GitHub Actions with `wetwire-github`.

## Table of Contents

- [When to Use Composite Actions vs Reusable Workflows](#when-to-use-composite-actions-vs-reusable-workflows)
- [Best Practices](#best-practices)
- [Examples](#examples)
- [Integration Patterns](#integration-patterns)

---

## When to Use Composite Actions vs Reusable Workflows

### Composite Actions

**Use composite actions when you need to:**

- Encapsulate a sequence of steps that run within a single job
- Create reusable step sequences that can be shared across repositories
- Package steps that need to run together (e.g., setup, build, test)
- Distribute actions through the GitHub Marketplace

```python
from wetwire_github.composite import CompositeAction, CompositeRuns, ActionInput
from wetwire_github.workflow import Step

# Composite action: encapsulates steps within a job
setup_action = CompositeAction(
    name="Setup Python Project",
    description="Sets up Python with dependencies",
    inputs={
        "python-version": ActionInput(
            description="Python version to use",
            required=True,
        ),
    },
    runs=CompositeRuns(
        steps=[
            Step(uses="actions/setup-python@v5", with_={"python-version": "${{ inputs.python-version }}"}),
            Step(run="pip install -r requirements.txt", shell="bash"),
        ]
    ),
)
```

**Key characteristics:**

- Run as part of a job (share the runner environment)
- Access to job context and runner filesystem
- Can define inputs and outputs
- Steps execute sequentially within the calling job
- Cannot define triggers or multiple jobs

### Reusable Workflows

**Use reusable workflows when you need to:**

- Encapsulate entire jobs with their own runners
- Define complete CI/CD pipelines that can be called by other workflows
- Include multiple jobs with dependencies
- Define workflow-level triggers and permissions

```python
from wetwire_github.workflow import Workflow, Job, Step, Triggers, WorkflowCallTrigger, WorkflowInput

# Reusable workflow: encapsulates entire jobs
reusable_ci = Workflow(
    name="Reusable CI",
    on=Triggers(
        workflow_call=WorkflowCallTrigger(
            inputs={
                "python-version": WorkflowInput(
                    description="Python version",
                    required=True,
                    type="string",
                ),
            },
        ),
    ),
    jobs={
        "build": Job(runs_on="ubuntu-latest", steps=[...]),
        "test": Job(runs_on="ubuntu-latest", needs=["build"], steps=[...]),
    },
)
```

**Key characteristics:**

- Run as complete workflows with their own runners
- Can define multiple jobs with dependencies
- Can specify permissions and environments
- More isolated execution environment
- Called using `uses: ./.github/workflows/workflow.yml`

### Decision Matrix

| Requirement | Composite Action | Reusable Workflow |
|-------------|------------------|-------------------|
| Reuse steps within a job | Yes | No |
| Define multiple jobs | No | Yes |
| Share runner filesystem | Yes | No (artifacts required) |
| Define triggers | No | Yes |
| Publish to Marketplace | Yes | No |
| Job-level permissions | No | Yes |
| Matrix strategies | No (use in caller) | Yes |

---

## Best Practices

### Input Validation Patterns

Always define clear, descriptive inputs with appropriate defaults and requirements.

```python
from wetwire_github.composite import CompositeAction, ActionInput, CompositeRuns
from wetwire_github.workflow import Step

action = CompositeAction(
    name="Deploy Application",
    description="Deploys application to specified environment",
    inputs={
        # Required input with no default - caller must provide
        "environment": ActionInput(
            description="Target deployment environment (staging, production)",
            required=True,
        ),
        # Optional input with sensible default
        "timeout": ActionInput(
            description="Deployment timeout in seconds",
            required=False,
            default="300",
        ),
        # Input with validation in step
        "log-level": ActionInput(
            description="Logging level (debug, info, warn, error)",
            required=False,
            default="info",
        ),
    },
    runs=CompositeRuns(
        steps=[
            # Validate inputs early
            Step(
                name="Validate inputs",
                run="""
                    if [[ ! "${{ inputs.environment }}" =~ ^(staging|production)$ ]]; then
                        echo "Error: environment must be 'staging' or 'production'"
                        exit 1
                    fi
                    if [[ ! "${{ inputs.log-level }}" =~ ^(debug|info|warn|error)$ ]]; then
                        echo "Error: log-level must be one of: debug, info, warn, error"
                        exit 1
                    fi
                """,
                shell="bash",
            ),
            Step(
                name="Deploy",
                run="./deploy.sh --env ${{ inputs.environment }} --timeout ${{ inputs.timeout }}",
                shell="bash",
            ),
        ]
    ),
)
```

### Output Definition Conventions

Define outputs clearly with descriptive names and reference step outputs using the step ID.

```python
from wetwire_github.composite import CompositeAction, ActionInput, ActionOutput, CompositeRuns
from wetwire_github.workflow import Step

action = CompositeAction(
    name="Build and Package",
    description="Builds the application and outputs package information",
    outputs={
        # Reference outputs from specific steps using step ID
        "version": ActionOutput(
            description="The semantic version of the built package",
            value="${{ steps.extract-version.outputs.version }}",
        ),
        "artifact-path": ActionOutput(
            description="Path to the built artifact",
            value="${{ steps.build.outputs.artifact-path }}",
        ),
        "build-time": ActionOutput(
            description="Build duration in seconds",
            value="${{ steps.build.outputs.duration }}",
        ),
    },
    runs=CompositeRuns(
        steps=[
            Step(
                id="extract-version",
                name="Extract version",
                run="""
                    VERSION=$(cat VERSION)
                    echo "version=$VERSION" >> $GITHUB_OUTPUT
                """,
                shell="bash",
            ),
            Step(
                id="build",
                name="Build package",
                run="""
                    START=$(date +%s)
                    python -m build
                    END=$(date +%s)
                    echo "artifact-path=dist/" >> $GITHUB_OUTPUT
                    echo "duration=$((END-START))" >> $GITHUB_OUTPUT
                """,
                shell="bash",
            ),
        ]
    ),
)
```

### Step Naming Conventions

Use clear, action-oriented names that describe what each step does.

```python
from wetwire_github.composite import CompositeRuns
from wetwire_github.workflow import Step

runs = CompositeRuns(
    steps=[
        # Good: Clear action-oriented names
        Step(id="checkout", name="Check out repository", uses="actions/checkout@v4"),
        Step(id="setup-python", name="Set up Python environment", uses="actions/setup-python@v5"),
        Step(id="install-deps", name="Install dependencies", run="pip install -r requirements.txt", shell="bash"),
        Step(id="run-tests", name="Run test suite", run="pytest --cov", shell="bash"),
        Step(id="upload-coverage", name="Upload coverage report", uses="codecov/codecov-action@v4"),

        # Bad: Vague or inconsistent names (avoid these)
        # Step(name="Step 1", ...),  # Non-descriptive
        # Step(name="do stuff", ...),  # Too vague
        # Step(name="Python", ...),  # Noun instead of action
    ]
)
```

**Naming guidelines:**

- Start with a verb (Set up, Install, Run, Build, Deploy, Upload)
- Be specific about what the step does
- Use consistent casing (sentence case recommended)
- Include the step ID for steps that produce outputs

### Shell and Working Directory Handling

Always specify the shell explicitly for run steps in composite actions.

```python
from wetwire_github.composite import CompositeAction, ActionInput, CompositeRuns
from wetwire_github.workflow import Step

action = CompositeAction(
    name="Cross-Platform Build",
    description="Builds on any platform with proper shell handling",
    inputs={
        "working-directory": ActionInput(
            description="Directory to run commands in",
            required=False,
            default=".",
        ),
    },
    runs=CompositeRuns(
        steps=[
            # Always specify shell for run steps
            Step(
                name="Build on Unix",
                run="./build.sh",
                shell="bash",
                working_directory="${{ inputs.working-directory }}",
            ),
            # Use pwsh for cross-platform PowerShell
            Step(
                name="Cross-platform script",
                run="Write-Host 'Building...'",
                shell="pwsh",
            ),
            # Python for complex logic
            Step(
                name="Complex processing",
                run="""
                    import json
                    import os
                    config = json.load(open('config.json'))
                    print(f"Building version {config['version']}")
                """,
                shell="python",
            ),
        ]
    ),
)
```

**Shell options:**

| Shell | Use Case |
|-------|----------|
| `bash` | Default for Unix-like systems, most common choice |
| `pwsh` | Cross-platform PowerShell (Windows, Linux, macOS) |
| `python` | Complex logic, JSON processing, calculations |
| `sh` | POSIX-compatible scripts, minimal dependencies |
| `cmd` | Windows-specific batch scripts |
| `powershell` | Windows PowerShell (legacy) |

---

## Examples

### Example 1: Simple Setup Pattern

A composite action that sets up a Python development environment with caching.

```python
"""Simple setup composite action."""

from wetwire_github.composite import (
    ActionInput,
    ActionOutput,
    CompositeAction,
    CompositeRuns,
)
from wetwire_github.workflow import Step

setup_python_project = CompositeAction(
    name="Setup Python Project",
    description="Sets up a Python project with dependencies and caching",
    inputs={
        "python-version": ActionInput(
            description="Python version to use (e.g., '3.11', '3.12')",
            required=True,
        ),
        "cache-dependency-path": ActionInput(
            description="Path to dependency file for cache key generation",
            default="requirements.txt",
        ),
        "install-command": ActionInput(
            description="Command to install dependencies",
            default="pip install -r requirements.txt",
        ),
    },
    outputs={
        "python-path": ActionOutput(
            description="Path to the Python executable",
            value="${{ steps.setup-python.outputs.python-path }}",
        ),
        "cache-hit": ActionOutput(
            description="Whether the cache was hit",
            value="${{ steps.cache-deps.outputs.cache-hit }}",
        ),
    },
    runs=CompositeRuns(
        steps=[
            Step(
                id="setup-python",
                name="Set up Python",
                uses="actions/setup-python@v5",
                with_={
                    "python-version": "${{ inputs.python-version }}",
                },
            ),
            Step(
                id="cache-deps",
                name="Cache pip dependencies",
                uses="actions/cache@v4",
                with_={
                    "path": "~/.cache/pip",
                    "key": "${{ runner.os }}-pip-${{ hashFiles(inputs.cache-dependency-path) }}",
                    "restore-keys": "${{ runner.os }}-pip-",
                },
            ),
            Step(
                name="Install dependencies",
                run="${{ inputs.install-command }}",
                shell="bash",
            ),
        ]
    ),
)

# Write to action.yml
if __name__ == "__main__":
    from wetwire_github.composite import write_action
    write_action(setup_python_project, "./actions/setup-python-project/action.yml")
```

### Example 2: Complex Action with Multiple Outputs

A composite action that builds, tests, and produces multiple artifacts with detailed outputs.

```python
"""Complex composite action with multiple outputs."""

from wetwire_github.composite import (
    ActionInput,
    ActionOutput,
    CompositeAction,
    CompositeRuns,
)
from wetwire_github.workflow import Step

build_and_test = CompositeAction(
    name="Build and Test",
    description="Builds the project, runs tests, and produces coverage reports",
    inputs={
        "python-version": ActionInput(
            description="Python version to use",
            required=True,
        ),
        "run-coverage": ActionInput(
            description="Whether to generate coverage reports",
            default="true",
        ),
        "coverage-threshold": ActionInput(
            description="Minimum coverage percentage required",
            default="80",
        ),
        "extra-pytest-args": ActionInput(
            description="Additional arguments to pass to pytest",
            default="",
        ),
    },
    outputs={
        "test-result": ActionOutput(
            description="Test result status (passed, failed)",
            value="${{ steps.run-tests.outputs.result }}",
        ),
        "coverage-percentage": ActionOutput(
            description="Code coverage percentage",
            value="${{ steps.coverage-report.outputs.percentage }}",
        ),
        "coverage-report-path": ActionOutput(
            description="Path to the HTML coverage report",
            value="${{ steps.coverage-report.outputs.report-path }}",
        ),
        "test-count": ActionOutput(
            description="Total number of tests run",
            value="${{ steps.run-tests.outputs.test-count }}",
        ),
        "build-artifact": ActionOutput(
            description="Path to built wheel file",
            value="${{ steps.build.outputs.wheel-path }}",
        ),
    },
    runs=CompositeRuns(
        steps=[
            Step(
                id="setup",
                name="Set up Python",
                uses="actions/setup-python@v5",
                with_={"python-version": "${{ inputs.python-version }}"},
            ),
            Step(
                id="install",
                name="Install dependencies",
                run="""
                    pip install --upgrade pip
                    pip install build pytest pytest-cov
                    pip install -e ".[dev]"
                """,
                shell="bash",
            ),
            Step(
                id="build",
                name="Build package",
                run="""
                    python -m build
                    WHEEL=$(ls dist/*.whl | head -1)
                    echo "wheel-path=$WHEEL" >> $GITHUB_OUTPUT
                """,
                shell="bash",
            ),
            Step(
                id="run-tests",
                name="Run tests",
                run="""
                    set +e
                    if [ "${{ inputs.run-coverage }}" = "true" ]; then
                        pytest --cov --cov-report=xml --cov-report=html ${{ inputs.extra-pytest-args }} > test_output.txt 2>&1
                    else
                        pytest ${{ inputs.extra-pytest-args }} > test_output.txt 2>&1
                    fi
                    TEST_EXIT_CODE=$?
                    set -e

                    # Extract test count
                    TEST_COUNT=$(grep -oP '\\d+ passed' test_output.txt | grep -oP '\\d+' || echo "0")
                    echo "test-count=$TEST_COUNT" >> $GITHUB_OUTPUT

                    if [ $TEST_EXIT_CODE -eq 0 ]; then
                        echo "result=passed" >> $GITHUB_OUTPUT
                    else
                        echo "result=failed" >> $GITHUB_OUTPUT
                        cat test_output.txt
                        exit $TEST_EXIT_CODE
                    fi
                """,
                shell="bash",
            ),
            Step(
                id="coverage-report",
                name="Process coverage report",
                if_="${{ inputs.run-coverage == 'true' }}",
                run="""
                    # Extract coverage percentage from XML
                    if [ -f coverage.xml ]; then
                        COVERAGE=$(python -c "
                    import xml.etree.ElementTree as ET
                    tree = ET.parse('coverage.xml')
                    root = tree.getroot()
                    rate = float(root.get('line-rate', 0))
                    print(int(rate * 100))
                    ")
                        echo "percentage=$COVERAGE" >> $GITHUB_OUTPUT
                        echo "report-path=htmlcov/index.html" >> $GITHUB_OUTPUT

                        # Check threshold
                        if [ "$COVERAGE" -lt "${{ inputs.coverage-threshold }}" ]; then
                            echo "::warning::Coverage $COVERAGE% is below threshold ${{ inputs.coverage-threshold }}%"
                        fi
                    else
                        echo "percentage=0" >> $GITHUB_OUTPUT
                        echo "report-path=" >> $GITHUB_OUTPUT
                    fi
                """,
                shell="bash",
            ),
        ]
    ),
)

if __name__ == "__main__":
    from wetwire_github.composite import write_action
    write_action(build_and_test, "./actions/build-and-test/action.yml")
```

### Example 3: Action with Conditional Logic

A composite action that handles different deployment scenarios based on inputs.

```python
"""Composite action with conditional logic."""

from wetwire_github.composite import (
    ActionInput,
    ActionOutput,
    CompositeAction,
    CompositeRuns,
)
from wetwire_github.workflow import Step

deploy_action = CompositeAction(
    name="Smart Deploy",
    description="Deploys to different environments with conditional behavior",
    inputs={
        "environment": ActionInput(
            description="Target environment (staging, production)",
            required=True,
        ),
        "dry-run": ActionInput(
            description="Perform a dry run without actual deployment",
            default="false",
        ),
        "notify-slack": ActionInput(
            description="Send Slack notification on completion",
            default="true",
        ),
        "slack-webhook-url": ActionInput(
            description="Slack webhook URL for notifications",
            required=False,
        ),
        "rollback-on-failure": ActionInput(
            description="Automatically rollback on deployment failure",
            default="true",
        ),
    },
    outputs={
        "deployment-id": ActionOutput(
            description="Unique identifier for this deployment",
            value="${{ steps.deploy.outputs.deployment-id }}",
        ),
        "deployment-url": ActionOutput(
            description="URL of the deployed application",
            value="${{ steps.deploy.outputs.url }}",
        ),
        "status": ActionOutput(
            description="Final deployment status",
            value="${{ steps.finalize.outputs.status }}",
        ),
    },
    runs=CompositeRuns(
        steps=[
            # Validation step
            Step(
                id="validate",
                name="Validate inputs",
                run="""
                    echo "Validating deployment configuration..."

                    # Validate environment
                    if [[ ! "${{ inputs.environment }}" =~ ^(staging|production)$ ]]; then
                        echo "::error::Invalid environment. Must be 'staging' or 'production'"
                        exit 1
                    fi

                    # Require Slack webhook if notifications enabled
                    if [ "${{ inputs.notify-slack }}" = "true" ] && [ -z "${{ inputs.slack-webhook-url }}" ]; then
                        echo "::warning::Slack notifications enabled but no webhook URL provided"
                    fi

                    echo "Validation passed"
                """,
                shell="bash",
            ),
            # Pre-deployment checks for production
            Step(
                id="prod-checks",
                name="Production pre-deployment checks",
                if_="${{ inputs.environment == 'production' }}",
                run="""
                    echo "Running production pre-deployment checks..."

                    # Check for required approvals, health checks, etc.
                    ./scripts/pre-deploy-checks.sh --env production

                    echo "Production checks passed"
                """,
                shell="bash",
            ),
            # Dry run step
            Step(
                id="dry-run",
                name="Dry run deployment",
                if_="${{ inputs.dry-run == 'true' }}",
                run="""
                    echo "::notice::Performing dry run deployment to ${{ inputs.environment }}"
                    ./deploy.sh --env ${{ inputs.environment }} --dry-run
                    echo "Dry run completed successfully"
                """,
                shell="bash",
            ),
            # Actual deployment
            Step(
                id="deploy",
                name="Deploy application",
                if_="${{ inputs.dry-run != 'true' }}",
                run="""
                    echo "Deploying to ${{ inputs.environment }}..."

                    DEPLOYMENT_ID=$(uuidgen)
                    echo "deployment-id=$DEPLOYMENT_ID" >> $GITHUB_OUTPUT

                    # Perform deployment
                    DEPLOY_OUTPUT=$(./deploy.sh --env ${{ inputs.environment }} --id $DEPLOYMENT_ID 2>&1)
                    DEPLOY_EXIT=$?

                    # Extract URL from output
                    URL=$(echo "$DEPLOY_OUTPUT" | grep -oP 'Deployed to: \\K.*' || echo "")
                    echo "url=$URL" >> $GITHUB_OUTPUT

                    if [ $DEPLOY_EXIT -ne 0 ]; then
                        echo "::error::Deployment failed"
                        exit 1
                    fi

                    echo "Deployment successful: $URL"
                """,
                shell="bash",
            ),
            # Rollback on failure (conditional)
            Step(
                id="rollback",
                name="Rollback deployment",
                if_="${{ failure() && inputs.rollback-on-failure == 'true' && inputs.dry-run != 'true' }}",
                run="""
                    echo "::warning::Deployment failed, initiating rollback..."
                    ./deploy.sh --rollback --env ${{ inputs.environment }}
                    echo "Rollback completed"
                """,
                shell="bash",
            ),
            # Slack notification
            Step(
                id="notify",
                name="Send Slack notification",
                if_="${{ always() && inputs.notify-slack == 'true' && inputs.slack-webhook-url != '' }}",
                run="""
                    STATUS="${{ job.status }}"
                    ENV="${{ inputs.environment }}"

                    if [ "$STATUS" = "success" ]; then
                        EMOJI=":white_check_mark:"
                        COLOR="good"
                    else
                        EMOJI=":x:"
                        COLOR="danger"
                    fi

                    curl -X POST "${{ inputs.slack-webhook-url }}" \
                        -H "Content-Type: application/json" \
                        -d "{
                            \"attachments\": [{
                                \"color\": \"$COLOR\",
                                \"text\": \"$EMOJI Deployment to $ENV: $STATUS\"
                            }]
                        }"
                """,
                shell="bash",
            ),
            # Finalize
            Step(
                id="finalize",
                name="Finalize deployment",
                if_="${{ always() }}",
                run="""
                    if [ "${{ inputs.dry-run }}" = "true" ]; then
                        echo "status=dry-run-complete" >> $GITHUB_OUTPUT
                    elif [ "${{ job.status }}" = "success" ]; then
                        echo "status=deployed" >> $GITHUB_OUTPUT
                    else
                        echo "status=failed" >> $GITHUB_OUTPUT
                    fi
                """,
                shell="bash",
            ),
        ]
    ),
)

if __name__ == "__main__":
    from wetwire_github.composite import write_action
    write_action(deploy_action, "./actions/smart-deploy/action.yml")
```

---

## Integration Patterns

### Using Composite Actions in Workflows

Reference your composite action in a workflow using the `uses` key with a local path or repository reference.

```python
from wetwire_github.workflow import Workflow, Job, Step, Triggers, PushTrigger
from wetwire_github.actions import checkout

ci_workflow = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger(branches=["main"])),
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            steps=[
                checkout(),
                # Use local composite action
                Step(
                    name="Setup project",
                    uses="./.github/actions/setup-python-project",
                    with_={
                        "python-version": "3.11",
                        "cache-dependency-path": "pyproject.toml",
                    },
                ),
                # Use action from another repository
                Step(
                    name="Build and test",
                    uses="myorg/actions/build-and-test@v1",
                    with_={
                        "python-version": "3.11",
                        "run-coverage": "true",
                        "coverage-threshold": "85",
                    },
                ),
                Step(run="echo 'Build complete'"),
            ],
        ),
    },
)
```

### Accessing Composite Action Outputs

Access outputs from composite action steps using the step ID.

```python
from wetwire_github.workflow import Workflow, Job, Step, Triggers, PushTrigger
from wetwire_github.actions import checkout, upload_artifact

workflow = Workflow(
    name="Build and Release",
    on=Triggers(push=PushTrigger(tags=["v*"])),
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            steps=[
                checkout(),
                Step(
                    id="build-test",
                    name="Build and test",
                    uses="./.github/actions/build-and-test",
                    with_={
                        "python-version": "3.11",
                        "run-coverage": "true",
                    },
                ),
                # Access outputs from the composite action
                Step(
                    name="Report results",
                    run="""
                        echo "Test result: ${{ steps.build-test.outputs.test-result }}"
                        echo "Coverage: ${{ steps.build-test.outputs.coverage-percentage }}%"
                        echo "Tests run: ${{ steps.build-test.outputs.test-count }}"
                    """,
                ),
                # Use output in another action
                upload_artifact(
                    name="coverage-report",
                    path="${{ steps.build-test.outputs.coverage-report-path }}",
                ),
            ],
        ),
    },
)
```

### Version Pinning Strategies

Follow these strategies for referencing composite actions:

**1. Pin to a specific version tag (recommended for production):**

```python
Step(uses="myorg/my-action@v1.2.3")  # Exact version
Step(uses="myorg/my-action@v1.2")    # Minor version (gets patches)
Step(uses="myorg/my-action@v1")      # Major version (gets minor + patches)
```

**2. Pin to a commit SHA (most secure):**

```python
Step(uses="myorg/my-action@a1b2c3d4e5f6...")  # Full SHA
```

**3. Use branch reference (for development only):**

```python
Step(uses="myorg/my-action@main")     # Latest on main
Step(uses="myorg/my-action@develop")  # Development branch
```

**4. Local actions (always use relative path):**

```python
Step(uses="./.github/actions/my-action")  # Local action
```

### Organizing Composite Actions

Structure your composite actions for maintainability:

```
.github/
  actions/
    setup-python-project/
      action.yml          # Generated from Python
    build-and-test/
      action.yml
    deploy/
      action.yml
  workflows/
    ci.yml               # Uses the composite actions

actions/                  # Python source for composite actions
  setup_python_project.py
  build_and_test.py
  deploy.py
  __init__.py            # Optional: exports all actions
```

### Writing Actions to Files

Use the `write_action` utility to generate action.yml files:

```python
from wetwire_github.composite import write_action
from my_actions import setup_python_project, build_and_test, deploy_action

# Write individual actions
write_action(setup_python_project, "./.github/actions/setup-python-project/")
write_action(build_and_test, "./.github/actions/build-and-test/")
write_action(deploy_action, "./.github/actions/deploy/")

# Or specify the exact file path
write_action(setup_python_project, "./.github/actions/setup-python-project/action.yml")
```

### Combining with Reusable Workflows

Use composite actions inside reusable workflows for maximum flexibility:

```python
from wetwire_github.workflow import (
    Workflow,
    Job,
    Step,
    Triggers,
    WorkflowCallTrigger,
    WorkflowInput,
)
from wetwire_github.actions import checkout

# Reusable workflow that uses composite actions internally
reusable_ci = Workflow(
    name="Reusable Python CI",
    on=Triggers(
        workflow_call=WorkflowCallTrigger(
            inputs={
                "python-version": WorkflowInput(
                    description="Python version",
                    required=True,
                    type="string",
                ),
            },
        ),
    ),
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            steps=[
                checkout(),
                # Use composite action for setup
                Step(
                    uses="./.github/actions/setup-python-project",
                    with_={"python-version": "${{ inputs.python-version }}"},
                ),
                # Use composite action for build/test
                Step(
                    id="build",
                    uses="./.github/actions/build-and-test",
                    with_={"python-version": "${{ inputs.python-version }}"},
                ),
            ],
        ),
    },
)
```

---

## See Also

- [Quick Start](QUICK_START.md) - Getting started guide
- [Examples](EXAMPLES.md) - Workflow examples
- [CLI Reference](CLI.md) - Build commands
- [Reusable Workflows](#reusable-workflows) section in Examples
