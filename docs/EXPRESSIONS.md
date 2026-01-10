# Expression Contexts

Type-safe expression builders for GitHub Actions contexts, conditions, and operators.

## Overview

wetwire-github provides typed expression builders that replace raw `${{ }}` strings with Python objects. This gives you:

- **IDE autocomplete** for context properties
- **Type safety** through static analysis
- **Compile-time errors** instead of runtime failures
- **Searchability** - grep for `Secrets.get()` instead of regex patterns

Instead of this:
```python
Step(
    run="deploy.sh",
    if_="${{ github.ref == 'refs/heads/main' && success() }}",
    env={"TOKEN": "${{ secrets.DEPLOY_TOKEN }}"},
)
```

You write this:
```python
from wetwire_github.workflow.expressions import GitHub, Secrets, success

Step(
    run="deploy.sh",
    if_=GitHub.ref == "refs/heads/main" & success(),
    env={"TOKEN": Secrets.get("DEPLOY_TOKEN")},
)
```

---

## Expression Contexts

### GitHub Context

Access GitHub Actions context properties.

```python
from wetwire_github.workflow.expressions import GitHub

# Available properties
GitHub.ref              # The branch or tag ref (e.g., refs/heads/main)
GitHub.sha              # The commit SHA
GitHub.actor            # Username that triggered the workflow
GitHub.event_name       # Event that triggered the workflow (push, pull_request, etc.)
GitHub.repository       # Repository name (owner/repo)
GitHub.run_id           # Unique ID for the workflow run
GitHub.run_number       # Sequential run number
GitHub.workflow         # Workflow name
GitHub.job              # Current job ID
GitHub.head_ref         # PR head branch
GitHub.base_ref         # PR base branch
GitHub.event_path       # Path to event payload file
GitHub.workspace        # Default working directory path
GitHub.action           # Name of currently running action
GitHub.token            # GitHub token for authentication
GitHub.server_url       # GitHub server URL (e.g., https://github.com)
GitHub.api_url          # GitHub API URL
GitHub.graphql_url      # GitHub GraphQL URL
GitHub.ref_name         # Short ref name (without refs/heads/)
GitHub.ref_type         # Type of ref (branch or tag)
GitHub.triggering_actor # User who triggered the workflow
```

**Example:**
```python
from wetwire_github.workflow import Step
from wetwire_github.workflow.expressions import GitHub

step = Step(
    name="Print context",
    run="echo 'Running on $REF for $REPO'",
    env={
        "REF": GitHub.ref,
        "REPO": GitHub.repository,
        "SHA": GitHub.sha,
    },
)
```

---

### Secrets Context

Access repository and organization secrets.

```python
from wetwire_github.workflow.expressions import Secrets

# Get a secret by name
token = Secrets.get("GITHUB_TOKEN")
api_key = Secrets.get("API_KEY")
```

**Example:**
```python
from wetwire_github.workflow import Step
from wetwire_github.workflow.expressions import Secrets

deploy_step = Step(
    name="Deploy to production",
    run="./deploy.sh",
    env={
        "API_KEY": Secrets.get("PROD_API_KEY"),
        "DEPLOY_TOKEN": Secrets.get("DEPLOY_TOKEN"),
    },
)
```

**Why use `Secrets.get()` instead of raw strings?**
- Searchable: `grep "Secrets.get"` finds all secret usage
- Lint-friendly: WAG003 rule detects and auto-fixes raw secret strings
- Type-safe: Prevents typos in secret names

---

### Matrix Context

Access matrix strategy values.

```python
from wetwire_github.workflow.expressions import Matrix

# Get matrix values
python_version = Matrix.get("python")
os_name = Matrix.get("os")
node_version = Matrix.get("node")
```

**Example:**
```python
from wetwire_github.workflow import Job, Step
from wetwire_github.workflow.strategy import Strategy, Matrix as MatrixStrategy
from wetwire_github.workflow.expressions import Matrix
from wetwire_github.actions import checkout, setup_python

test_job = Job(
    runs_on=Matrix.get("os"),  # Use matrix value for runner
    strategy=Strategy(
        matrix=MatrixStrategy(
            values={
                "python": ["3.10", "3.11", "3.12"],
                "os": ["ubuntu-latest", "macos-latest"],
            }
        )
    ),
    steps=[
        checkout(),
        setup_python(python_version=Matrix.get("python")),
        Step(run="pytest"),
    ],
)
```

---

### Env Context

Access environment variables set at workflow, job, or step level.

```python
from wetwire_github.workflow.expressions import Env

# Get environment variable
node_env = Env.get("NODE_ENV")
api_url = Env.get("API_URL")
```

**Example:**
```python
from wetwire_github.workflow import Job, Step
from wetwire_github.workflow.expressions import Env

build_job = Job(
    runs_on="ubuntu-latest",
    env={
        "NODE_ENV": "production",
        "BUILD_NUMBER": "1.0.0",
    },
    steps=[
        Step(
            name="Build with environment",
            run=f"echo Building {Env.get('NODE_ENV')} v{Env.get('BUILD_NUMBER')}",
        ),
    ],
)
```

---

### Runner Context

Access information about the runner executing the job.

```python
from wetwire_github.workflow.expressions import Runner

# Available properties
Runner.os           # Operating system (Linux, Windows, macOS)
Runner.arch         # Architecture (X64, ARM, ARM64)
Runner.name         # Runner name
Runner.temp         # Path to temporary directory
Runner.tool_cache   # Path to tool cache directory
Runner.debug        # Whether debug logging is enabled
```

**Example:**
```python
from wetwire_github.workflow import Step
from wetwire_github.workflow.expressions import Runner

step = Step(
    name="OS-specific command",
    run="echo 'Running on' $OS",
    env={"OS": Runner.os},
)
```

---

### Inputs Context

Access workflow inputs from `workflow_dispatch` or `workflow_call` triggers.

```python
from wetwire_github.workflow.expressions import Inputs

# Get workflow input
environment = Inputs.get("environment")
version = Inputs.get("version")
```

**Example:**
```python
from wetwire_github.workflow import Workflow, Job, Step, Triggers, WorkflowDispatchTrigger
from wetwire_github.workflow.expressions import Inputs

deploy_workflow = Workflow(
    name="Deploy",
    on=Triggers(
        workflow_dispatch=WorkflowDispatchTrigger(
            inputs={
                "environment": {"type": "string", "required": True},
                "version": {"type": "string", "required": True},
            }
        )
    ),
    jobs={
        "deploy": Job(
            runs_on="ubuntu-latest",
            steps=[
                Step(
                    name="Deploy to environment",
                    run=f"deploy.sh {Inputs.get('environment')} {Inputs.get('version')}",
                ),
            ],
        )
    },
)
```

---

### Needs Context

Access outputs and results from dependent jobs.

```python
from wetwire_github.workflow.expressions import Needs

# Get job output
version = Needs.output("build", "version")
artifact_name = Needs.output("build", "artifact-name")

# Get job result (success, failure, cancelled, skipped)
build_result = Needs.result("build")
```

**Example:**
```python
from wetwire_github.workflow import Job, Step
from wetwire_github.workflow.expressions import Needs
from wetwire_github.actions import checkout

build_job = Job(
    runs_on="ubuntu-latest",
    outputs={"version": "${{ steps.get_version.outputs.version }}"},
    steps=[
        checkout(),
        Step(
            id="get_version",
            run="echo version=1.2.3 >> $GITHUB_OUTPUT",
        ),
    ],
)

deploy_job = Job(
    runs_on="ubuntu-latest",
    needs=["build"],
    steps=[
        Step(
            name="Deploy version",
            run=f"deploy.sh {Needs.output('build', 'version')}",
        ),
    ],
)
```

---

### Steps Context

Access outputs and status from previous steps within the same job.

```python
from wetwire_github.workflow.expressions import Steps

# Get step output
artifact_path = Steps.output("build", "artifact-path")

# Get step outcome (success, failure, cancelled, skipped)
build_outcome = Steps.outcome("build")

# Get step conclusion (success, failure, cancelled, skipped, neutral)
build_conclusion = Steps.conclusion("build")
```

**Example:**
```python
from wetwire_github.workflow import Job, Step
from wetwire_github.workflow.expressions import Steps

job = Job(
    runs_on="ubuntu-latest",
    steps=[
        Step(
            id="build",
            run="make build",
        ),
        Step(
            id="get-artifact",
            run="echo artifact=$(ls dist/) >> $GITHUB_OUTPUT",
        ),
        Step(
            name="Upload artifact",
            run=f"upload {Steps.output('get-artifact', 'artifact')}",
        ),
    ],
)
```

---

## Condition Builders

Condition functions control when jobs or steps execute.

### always()

Run regardless of previous step outcomes.

```python
from wetwire_github.workflow.expressions import always

cleanup_step = Step(
    name="Cleanup",
    run="rm -rf temp/",
    if_=always(),
)
```

---

### failure()

Run only if a previous step failed.

```python
from wetwire_github.workflow.expressions import failure

notify_step = Step(
    name="Notify on failure",
    run="./notify-failure.sh",
    if_=failure(),
)
```

---

### success()

Run only if all previous steps succeeded.

```python
from wetwire_github.workflow.expressions import success

deploy_step = Step(
    name="Deploy",
    run="./deploy.sh",
    if_=success(),
)
```

---

### cancelled()

Run only if the workflow was cancelled.

```python
from wetwire_github.workflow.expressions import cancelled

cleanup_step = Step(
    name="Cleanup on cancel",
    run="./cleanup.sh",
    if_=cancelled(),
)
```

---

### branch() and tag()

Helper functions for common branch/tag checks.

```python
from wetwire_github.workflow.expressions import branch, tag

# Check if running on main branch
on_main = branch("main")

# Check if running on a version tag
on_version_tag = tag("v1.0.0")
```

**Example:**
```python
from wetwire_github.workflow import Step
from wetwire_github.workflow.expressions import branch

deploy_step = Step(
    name="Deploy to production",
    run="./deploy.sh",
    if_=branch("main"),
)
```

---

## Expression Composition

Combine expressions using Python operators and methods.

### Comparison Operators

Expression objects support comparison operators:

```python
from wetwire_github.workflow.expressions import GitHub

# Equality
is_main_branch = GitHub.ref == "refs/heads/main"
is_push_event = GitHub.event_name == "push"

# Inequality (using Python string comparison)
not_draft = GitHub.event_name != "pull_request_draft"
```

**Important:** Since `Expression` inherits from `str`, the `==` and `!=` operators return Python `str` objects that serialize correctly to GitHub Actions expressions.

---

### Logical Operators

Combine conditions using `&` (AND), `|` (OR), or methods.

```python
from wetwire_github.workflow.expressions import GitHub, success

# Using & operator for AND
deploy_condition = (GitHub.ref == "refs/heads/main") & success()

# Using | for OR (note: use sparingly, prefer explicit conditions)
deploy_to_staging_or_prod = (
    (GitHub.ref == "refs/heads/main") |
    (GitHub.ref == "refs/heads/staging")
)
```

**Alternative: Using methods**
```python
from wetwire_github.workflow.expressions import Expression

# Using .and_() method
condition = Expression("github.ref == 'refs/heads/main'").and_(
    Expression("success()")
)

# Using .or_() method
condition = Expression("github.ref == 'refs/heads/main'").or_(
    Expression("github.ref == 'refs/heads/staging'")
)

# Using .not_() method
not_draft = Expression("github.event.pull_request.draft").not_()
```

---

### Combining Multiple Conditions

```python
from wetwire_github.workflow.expressions import GitHub, success, failure

# Complex condition: Deploy on main branch if successful
deploy_condition = (GitHub.ref == "refs/heads/main") & success()

# Even more complex: Run cleanup on failure or cancellation
cleanup_condition = failure() | cancelled()

# Multiple ANDs
production_deploy = (
    (GitHub.ref == "refs/heads/main") &
    (GitHub.event_name == "push") &
    success()
)
```

**Best practice:** Extract complex conditions to named variables:
```python
from wetwire_github.workflow.expressions import GitHub, success

is_production_deploy = (
    (GitHub.ref == "refs/heads/main") &
    (GitHub.event_name == "push") &
    success()
)

deploy_step = Step(
    name="Deploy to production",
    run="./deploy.sh",
    if_=is_production_deploy,
)
```

---

## Practical Examples

### Example 1: Conditional Deployment

Deploy to production only on main branch pushes.

```python
from wetwire_github.workflow import Job, Step
from wetwire_github.workflow.expressions import GitHub, Secrets, success
from wetwire_github.actions import checkout

deploy_job = Job(
    runs_on="ubuntu-latest",
    needs=["test"],
    if_=(GitHub.ref == "refs/heads/main") & success(),
    steps=[
        checkout(),
        Step(
            name="Deploy",
            run="./deploy.sh",
            env={
                "DEPLOY_TOKEN": Secrets.get("DEPLOY_TOKEN"),
                "API_KEY": Secrets.get("PROD_API_KEY"),
            },
        ),
    ],
)
```

---

### Example 2: Matrix Build with Dynamic Values

```python
from wetwire_github.workflow import Job, Step
from wetwire_github.workflow.strategy import Strategy, Matrix as MatrixStrategy
from wetwire_github.workflow.expressions import Matrix
from wetwire_github.actions import checkout, setup_python

test_job = Job(
    runs_on=Matrix.get("os"),
    strategy=Strategy(
        matrix=MatrixStrategy(
            values={
                "python": ["3.10", "3.11", "3.12"],
                "os": ["ubuntu-latest", "windows-latest", "macos-latest"],
            }
        )
    ),
    steps=[
        checkout(),
        setup_python(python_version=Matrix.get("python")),
        Step(
            name="Run tests",
            run="pytest",
            env={
                "PYTHON_VERSION": Matrix.get("python"),
                "OS": Matrix.get("os"),
            },
        ),
    ],
)
```

---

### Example 3: Reusable Workflow with Inputs

```python
from wetwire_github.workflow import Workflow, Job, Step, Triggers, WorkflowCallTrigger
from wetwire_github.workflow.expressions import Inputs, Secrets
from wetwire_github.actions import checkout

deploy_workflow = Workflow(
    name="Deploy Reusable",
    on=Triggers(
        workflow_call=WorkflowCallTrigger(
            inputs={
                "environment": {
                    "type": "string",
                    "required": True,
                    "description": "Target environment",
                },
                "version": {
                    "type": "string",
                    "required": True,
                    "description": "Version to deploy",
                },
            },
            secrets={
                "deploy_token": {"required": True},
            },
        )
    ),
    jobs={
        "deploy": Job(
            runs_on="ubuntu-latest",
            environment=Inputs.get("environment"),
            steps=[
                checkout(),
                Step(
                    name="Deploy version",
                    run=f"./deploy.sh {Inputs.get('version')}",
                    env={
                        "ENVIRONMENT": Inputs.get("environment"),
                        "DEPLOY_TOKEN": Secrets.get("deploy_token"),
                    },
                ),
            ],
        )
    },
)
```

---

### Example 4: Using Job Outputs

```python
from wetwire_github.workflow import Workflow, Job, Step, Triggers, PushTrigger
from wetwire_github.workflow.expressions import GitHub, Needs
from wetwire_github.actions import checkout

build_job = Job(
    runs_on="ubuntu-latest",
    outputs={
        "version": "${{ steps.version.outputs.version }}",
        "artifact": "${{ steps.version.outputs.artifact }}",
    },
    steps=[
        checkout(),
        Step(
            id="version",
            run="""
                VERSION=$(cat VERSION)
                echo "version=$VERSION" >> $GITHUB_OUTPUT
                echo "artifact=myapp-$VERSION.tar.gz" >> $GITHUB_OUTPUT
            """,
        ),
        Step(run="make build"),
    ],
)

deploy_job = Job(
    runs_on="ubuntu-latest",
    needs=["build"],
    steps=[
        checkout(),
        Step(
            name="Download and deploy",
            run=f"""
                echo "Deploying version: {Needs.output('build', 'version')}"
                echo "Artifact: {Needs.output('build', 'artifact')}"
                ./deploy.sh {Needs.output('build', 'artifact')}
            """,
        ),
    ],
)

ci = Workflow(
    name="Build and Deploy",
    on=Triggers(push=PushTrigger(branches=["main"])),
    jobs={"build": build_job, "deploy": deploy_job},
)
```

---

### Example 5: Cleanup with always()

```python
from wetwire_github.workflow import Job, Step
from wetwire_github.workflow.expressions import always
from wetwire_github.actions import checkout

test_job = Job(
    runs_on="ubuntu-latest",
    steps=[
        checkout(),
        Step(
            name="Setup test database",
            run="docker-compose up -d",
        ),
        Step(
            name="Run tests",
            run="pytest",
        ),
        Step(
            name="Cleanup",
            run="docker-compose down",
            if_=always(),  # Always cleanup, even if tests fail
        ),
    ],
)
```

---

## Pseudo-Parameters (Alternative Pattern)

For simple use cases, wetwire-github also provides pre-formatted constants:

```python
from wetwire_github.pseudo import GITHUB_REF, GITHUB_SHA, GITHUB_REPOSITORY

step = Step(
    run="echo $REF",
    env={
        "REF": GITHUB_REF,           # ${{ github.ref }}
        "SHA": GITHUB_SHA,           # ${{ github.sha }}
        "REPO": GITHUB_REPOSITORY,   # ${{ github.repository }}
    },
)
```

**When to use pseudo-parameters vs expression contexts?**

| Pattern | Use Case |
|---------|----------|
| `GitHub.ref` | Conditions, comparisons, type-safe expressions |
| `GITHUB_REF` | Simple environment variable assignments |

**Available pseudo-parameters:**
- `GITHUB_REF`, `GITHUB_REF_NAME`, `GITHUB_SHA`
- `GITHUB_REPOSITORY`, `GITHUB_REPOSITORY_OWNER`, `GITHUB_ACTOR`
- `GITHUB_WORKFLOW`, `GITHUB_RUN_ID`, `GITHUB_RUN_NUMBER`, `GITHUB_JOB`
- `GITHUB_HEAD_REF`, `GITHUB_BASE_REF`
- `GITHUB_EVENT_NAME`, `GITHUB_EVENT_PATH`
- `GITHUB_WORKSPACE`, `GITHUB_ACTION`, `GITHUB_ACTION_PATH`

See [pseudo.py](../src/wetwire_github/pseudo.py) for full list.

---

## Converting to Strings

Expression objects automatically serialize to `${{ }}` format when converted to strings:

```python
from wetwire_github.workflow.expressions import GitHub, Secrets

print(str(GitHub.ref))
# Output: ${{ github.ref }}

print(str(Secrets.get("TOKEN")))
# Output: ${{ secrets.TOKEN }}

print(str(GitHub.ref == "refs/heads/main"))
# Output: ${{ github.ref == 'refs/heads/main' }}
```

In most cases, you don't need to call `str()` explicitly as the serializer handles it automatically.

---

## Common Patterns

### Pattern 1: Environment-Specific Secrets

```python
from wetwire_github.workflow.expressions import Inputs, Secrets

# Different secrets per environment
api_key = Secrets.get(f"{Inputs.get('environment')}_API_KEY")
```

### Pattern 2: PR vs Push Detection

```python
from wetwire_github.workflow.expressions import GitHub

is_pr = GitHub.event_name == "pull_request"
is_push = GitHub.event_name == "push"
```

### Pattern 3: Branch-Specific Deployment

```python
from wetwire_github.workflow.expressions import branch

deploy_to_prod = branch("main")
deploy_to_staging = branch("staging")
```

### Pattern 4: Conditional on Job Success

```python
from wetwire_github.workflow.expressions import Needs

previous_job_succeeded = Needs.result("build") == "success"
```

---

## See Also

- [Lint Rules](LINT_RULES.md) - Rules for expression usage (WAG002, WAG003, WAG008)
- [Quick Start](QUICK_START.md) - Getting started with expressions
- [GitHub Actions Expression Syntax](https://docs.github.com/en/actions/learn-github-actions/expressions) - Official GitHub documentation
- [GitHub Actions Contexts](https://docs.github.com/en/actions/learn-github-actions/contexts) - Available context properties
