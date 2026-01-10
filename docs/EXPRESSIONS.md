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

### Event Context

Access GitHub event payload properties based on the webhook event that triggered the workflow.

```python
from wetwire_github.workflow.expressions import Event

# Access pull request properties
pr_title = Event.pull_request("title")
pr_author = Event.pull_request("user.login")
pr_draft = Event.pull_request("draft")

# Access issue properties
issue_title = Event.issue("title")
issue_labels = Event.issue("labels")

# Access release properties
release_tag = Event.release("tag_name")
release_name = Event.release("name")

# Access discussion properties
discussion_title = Event.discussion("title")
discussion_body = Event.discussion("body")

# Access push event properties
push_ref = Event.push("ref")
push_before = Event.push("before")
push_after = Event.push("after")

# Access workflow_run properties
workflow_conclusion = Event.workflow_run("conclusion")
workflow_name = Event.workflow_run("name")

# Access event sender properties
sender_login = Event.sender("login")
sender_type = Event.sender("type")

# Access event repository properties
repo_full_name = Event.repository("full_name")
repo_default_branch = Event.repository("default_branch")
```

**Convenience Properties:**

For common event payload fields, use the shorthand properties:

```python
from wetwire_github.workflow.expressions import Event

# Pull request shortcuts
Event.pr_title          # github.event.pull_request.title
Event.pr_body           # github.event.pull_request.body
Event.pr_number         # github.event.pull_request.number

# Issue shortcuts
Event.issue_title       # github.event.issue.title
Event.issue_body        # github.event.issue.body
Event.issue_number      # github.event.issue.number

# Release shortcuts
Event.release_tag_name  # github.event.release.tag_name
Event.release_body      # github.event.release.body

# Commit shortcuts
Event.head_commit_message  # github.event.head_commit.message
Event.head_commit_id       # github.event.head_commit.id

# Sender/Repository shortcuts
Event.sender_login      # github.event.sender.login
Event.repo_full_name    # github.event.repository.full_name
Event.repo_name         # github.event.repository.name
```

**Example:**

```python
from wetwire_github.workflow import Job, Step
from wetwire_github.workflow.expressions import Event, contains
from wetwire_github.actions import checkout

pr_labeler_job = Job(
    runs_on="ubuntu-latest",
    steps=[
        checkout(),
        Step(
            name="Label bug reports",
            run="gh pr edit ${{ github.event.pull_request.number }} --add-label bug",
            if_=contains(Event.pr_title, "[BUG]"),
        ),
        Step(
            name="Comment on draft PR",
            run="gh pr comment ${{ github.event.pull_request.number }} --body 'Draft PR detected'",
            if_=Event.pull_request("draft"),
        ),
    ],
)
```

**When to use Event context:**
- Conditional execution based on event payload content (PR title, issue labels)
- Accessing event-specific metadata (release tag, workflow run conclusion)
- Building dynamic messages or notifications using event data
- Filtering workflows by event properties (draft PRs, specific labels)

---

### Vars Context

Access configuration variables defined at the repository, organization, or environment level. Unlike secrets, variables are not encrypted and are meant for non-sensitive configuration.

```python
from wetwire_github.workflow.expressions import Vars

# Get configuration variable by name
api_url = Vars.get("API_URL")
environment = Vars.get("ENVIRONMENT")
region = Vars.get("DEPLOYMENT_REGION")
```

**Example:**

```python
from wetwire_github.workflow import Job, Step
from wetwire_github.workflow.expressions import Vars, Secrets
from wetwire_github.actions import checkout

deploy_job = Job(
    runs_on="ubuntu-latest",
    steps=[
        checkout(),
        Step(
            name="Deploy to configured environment",
            run="./deploy.sh",
            env={
                "API_URL": Vars.get("API_URL"),           # Non-sensitive config
                "REGION": Vars.get("DEPLOYMENT_REGION"),  # Non-sensitive config
                "API_KEY": Secrets.get("API_KEY"),        # Sensitive secret
            },
        ),
    ],
)
```

**When to use Vars context:**
- Non-sensitive configuration values (API URLs, feature flags, environment names)
- Values that differ between repositories or organizations
- Configuration that should be visible in workflow logs
- Settings that may need to be changed without updating workflow code

**Vars vs Secrets:**

| Context | Use For | Encrypted | Visible in Logs |
|---------|---------|-----------|----------------|
| `Vars.get()` | Non-sensitive config (URLs, regions) | No | Yes |
| `Secrets.get()` | Sensitive data (tokens, passwords) | Yes | No (masked) |

---

### Strategy Context

Access matrix strategy execution information when using matrix builds. Provides job index, total count, and strategy settings.

```python
from wetwire_github.workflow.expressions import StrategyInstance

# Available properties
StrategyInstance.fail_fast      # Whether fail-fast is enabled
StrategyInstance.job_index      # Zero-based index of current matrix job
StrategyInstance.job_total      # Total number of matrix jobs
StrategyInstance.max_parallel   # Maximum parallel jobs allowed
```

**Example:**

```python
from wetwire_github.workflow import Job, Step
from wetwire_github.workflow.strategy import Strategy, Matrix as MatrixStrategy
from wetwire_github.workflow.expressions import Matrix, StrategyInstance
from wetwire_github.actions import checkout

test_job = Job(
    runs_on="ubuntu-latest",
    strategy=Strategy(
        matrix=MatrixStrategy(
            values={
                "python": ["3.10", "3.11", "3.12"],
                "os": ["ubuntu-latest", "macos-latest"],
            }
        ),
        fail_fast=False,
        max_parallel=4,
    ),
    steps=[
        checkout(),
        Step(
            name="Show matrix info",
            run=f"""
                echo "Testing Python {Matrix.get('python')} on {Matrix.get('os')}"
                echo "Job {StrategyInstance.job_index} of {StrategyInstance.job_total}"
                echo "Max parallel: {StrategyInstance.max_parallel}"
                echo "Fail fast: {StrategyInstance.fail_fast}"
            """,
        ),
        Step(run="pytest"),
    ],
)
```

**When to use Strategy context:**
- Display progress information in matrix builds (job 1 of 10)
- Conditional behavior based on job position (first/last job)
- Debugging matrix execution strategy
- Dynamic artifact naming based on job index

**Note:** In most cases, you'll use `Matrix.get()` to access matrix values rather than `StrategyInstance`. The strategy context is primarily for metadata about the matrix execution itself.

---

### Job Context

Access information about the currently running job, including execution status and container details.

```python
from wetwire_github.workflow.expressions import Job

# Available properties
Job.status              # Current job status (success, failure, cancelled)
Job.container_id        # ID of the job's container
Job.container_network   # Network ID of the job's container

# Access service container properties
Job.services("postgres", "id")         # Service container ID
Job.services("redis", "ports.6379")    # Service container port mapping
```

**Example:**

```python
from wetwire_github.workflow import Job as JobClass, Step
from wetwire_github.workflow.expressions import Job
from wetwire_github.actions import checkout

integration_test_job = JobClass(
    runs_on="ubuntu-latest",
    container="node:16",
    services={
        "postgres": {
            "image": "postgres:14",
            "env": {
                "POSTGRES_PASSWORD": "postgres",
            },
            "options": "--health-cmd pg_isready --health-interval 10s",
        },
        "redis": {
            "image": "redis:6",
        },
    },
    steps=[
        checkout(),
        Step(
            name="Run integration tests",
            run="npm test",
            env={
                "POSTGRES_HOST": "postgres",
                "POSTGRES_PORT": "5432",
                "REDIS_HOST": "redis",
                "REDIS_PORT": "6379",
                "POSTGRES_CONTAINER_ID": Job.services("postgres", "id"),
                "JOB_CONTAINER_ID": Job.container_id,
            },
        ),
        Step(
            name="Debug on failure",
            if_=Job.status == "failure",
            run=f"""
                echo "Job status: {Job.status}"
                echo "Container ID: {Job.container_id}"
                echo "Postgres container: {Job.services('postgres', 'id')}"
                docker logs {Job.services('postgres', 'id')}
            """,
        ),
    ],
)
```

**When to use Job context:**
- Conditional execution based on job status
- Debugging container-based jobs
- Accessing service container IDs for logging or debugging
- Service discovery in containerized workflows
- Network troubleshooting in multi-container jobs

**Common service properties:**
- `Job.services("name", "id")` - Container ID
- `Job.services("name", "network")` - Network ID
- `Job.services("name", "ports.PORT")` - Port mapping (e.g., `ports.5432`)

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

## Expression Functions

GitHub Actions provides built-in functions for string manipulation, formatting, and data processing. wetwire-github wraps these in typed Python functions.

### contains()

Check if a string contains a substring.

```python
from wetwire_github.workflow.expressions import contains, Event, GitHub

# Check if PR title contains a keyword
has_bug = contains(Event.pr_title, "bug")

# Check if branch name contains a pattern
is_feature = contains(GitHub.ref, "feature/")
```

**Example:**
```python
from wetwire_github.workflow import Step
from wetwire_github.workflow.expressions import contains, Event

# Label PRs based on title
label_step = Step(
    name="Add bug label",
    run="gh pr edit ${{ github.event.pull_request.number }} --add-label bug",
    if_=contains(Event.pr_title, "bug"),
)
```

**Output:**
```yaml
- name: Add bug label
  run: gh pr edit ${{ github.event.pull_request.number }} --add-label bug
  if: ${{ contains(github.event.pull_request.title, 'bug') }}
```

---

### startsWith()

Check if a string starts with a prefix.

```python
from wetwire_github.workflow.expressions import startsWith, Event, GitHub

# Check if PR title starts with prefix
is_feat = startsWith(Event.pr_title, "feat:")
is_fix = startsWith(Event.pr_title, "fix:")

# Check if branch starts with pattern
is_release = startsWith(GitHub.ref_name, "release/")
```

**Example:**
```python
from wetwire_github.workflow import Step
from wetwire_github.workflow.expressions import startsWith, GitHub

# Deploy only release branches
deploy_step = Step(
    name="Deploy release",
    run="./deploy.sh",
    if_=startsWith(GitHub.ref_name, "release/"),
)
```

**Output:**
```yaml
- name: Deploy release
  run: ./deploy.sh
  if: ${{ startsWith(github.ref_name, 'release/') }}
```

---

### endsWith()

Check if a string ends with a suffix.

```python
from wetwire_github.workflow.expressions import endsWith, Event, GitHub

# Check if file path ends with extension
is_markdown = endsWith(Event.pr_title, ".md")
is_python = endsWith("setup.py", ".py")

# Check if tag ends with pattern
is_rc = endsWith(GitHub.ref_name, "-rc")
```

**Example:**
```python
from wetwire_github.workflow import Job
from wetwire_github.workflow.expressions import endsWith, GitHub

# Run docs job only for markdown changes
docs_job = Job(
    runs_on="ubuntu-latest",
    if_=endsWith(GitHub.head_ref, "-docs"),
    steps=[...],
)
```

**Output:**
```yaml
docs:
  runs-on: ubuntu-latest
  if: ${{ endsWith(github.head_ref, '-docs') }}
```

---

### format()

Format a string with placeholders using `{0}`, `{1}`, etc.

```python
from wetwire_github.workflow.expressions import format, GitHub, Runner, hashFiles

# Simple formatting
cache_key = format("cache-{0}-{1}", Runner.os, "v1")

# With expression arguments
versioned_cache = format("deps-{0}-{1}", GitHub.ref_name, hashFiles("**/requirements.txt"))
```

**Example:**
```python
from wetwire_github.workflow import Step
from wetwire_github.workflow.expressions import format, GitHub, Runner
from wetwire_github.actions import cache

# Dynamic cache key
cache_step = cache(
    path="~/.cache/pip",
    key=format("pip-{0}-{1}-{2}", Runner.os, GitHub.ref_name, hashFiles("requirements.txt")),
)
```

**Output:**
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ format('pip-{0}-{1}-{2}', runner.os, github.ref_name, hashFiles('requirements.txt')) }}
```

---

### hashFiles()

Generate a hash of files matching a glob pattern. Commonly used for cache keys.

```python
from wetwire_github.workflow.expressions import hashFiles

# Single file
lock_hash = hashFiles("requirements.txt")

# Glob pattern
all_reqs = hashFiles("**/requirements*.txt")

# Multiple patterns (comma-separated)
all_deps = hashFiles("package-lock.json, yarn.lock")
```

**Example:**
```python
from wetwire_github.workflow.expressions import hashFiles, format, Runner
from wetwire_github.actions import cache

# Cache with file hash key
cache_step = cache(
    path="~/.npm",
    key=format("npm-{0}-{1}", Runner.os, hashFiles("package-lock.json")),
    restore_keys=["npm-" + str(Runner.os) + "-"],
)
```

**Output:**
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ format('npm-{0}-{1}', runner.os, hashFiles('package-lock.json')) }}
    restore-keys: npm-${{ runner.os }}-
```

---

### join()

Join an array into a string with a separator.

```python
from wetwire_github.workflow.expressions import join, Matrix

# Join with default separator (comma)
versions = join(Matrix.get("versions"))

# Join with custom separator
paths = join(Matrix.get("paths"), ":")
```

**Example:**
```python
from wetwire_github.workflow import Job, Step
from wetwire_github.workflow.strategy import Strategy, Matrix as MatrixStrategy
from wetwire_github.workflow.expressions import join, Matrix

test_job = Job(
    runs_on="ubuntu-latest",
    strategy=Strategy(
        matrix=MatrixStrategy(
            values={"versions": [["3.10", "3.11", "3.12"]]}
        )
    ),
    steps=[
        Step(
            name="Display versions",
            run="echo 'Testing: $VERSIONS'",
            env={"VERSIONS": join(Matrix.get("versions"), ", ")},
        ),
    ],
)
```

**Output:**
```yaml
- name: Display versions
  run: echo 'Testing: $VERSIONS'
  env:
    VERSIONS: ${{ join(matrix.versions, ', ') }}
```

---

### toJson()

Convert a value to JSON string format.

```python
from wetwire_github.workflow.expressions import toJson, Matrix, Expression

# Convert matrix to JSON
matrix_json = toJson(Expression("matrix"))

# Convert context to JSON
github_json = toJson(Expression("github"))
```

**Example:**
```python
from wetwire_github.workflow import Step
from wetwire_github.workflow.expressions import toJson, Expression

debug_step = Step(
    name="Debug matrix",
    run="echo '$MATRIX_JSON'",
    env={"MATRIX_JSON": toJson(Expression("matrix"))},
)
```

**Output:**
```yaml
- name: Debug matrix
  run: echo '$MATRIX_JSON'
  env:
    MATRIX_JSON: ${{ toJSON(matrix) }}
```

---

### fromJson()

Parse a JSON string into an object.

```python
from wetwire_github.workflow.expressions import fromJson, Env, Inputs

# Parse JSON from environment variable
config = fromJson(Env.get("CONFIG_JSON"))

# Parse JSON from input
matrix_config = fromJson(Inputs.get("matrix_json"))
```

**Example:**
```python
from wetwire_github.workflow import Job, Step
from wetwire_github.workflow.strategy import Strategy
from wetwire_github.workflow.expressions import fromJson, Inputs

# Dynamic matrix from JSON input
test_job = Job(
    runs_on="ubuntu-latest",
    strategy=Strategy(
        matrix=fromJson(Inputs.get("matrix_json"))
    ),
    steps=[...],
)
```

**Output:**
```yaml
test:
  runs-on: ubuntu-latest
  strategy:
    matrix: ${{ fromJSON(inputs.matrix_json) }}
```

---

### lower()

Convert a string to lowercase.

```python
from wetwire_github.workflow.expressions import lower, GitHub, Env

# Lowercase literal string
name = lower("HELLO")

# Lowercase expression
ref_lower = lower(GitHub.ref_name)
env_lower = lower(Env.get("ENVIRONMENT"))
```

**Example:**
```python
from wetwire_github.workflow import Step
from wetwire_github.workflow.expressions import lower, GitHub

normalize_step = Step(
    name="Normalize branch name",
    run="echo $BRANCH",
    env={"BRANCH": lower(GitHub.ref_name)},
)
```

**Output:**
```yaml
- name: Normalize branch name
  run: echo $BRANCH
  env:
    BRANCH: ${{ lower(github.ref_name) }}
```

---

### upper()

Convert a string to uppercase.

```python
from wetwire_github.workflow.expressions import upper, GitHub, Env

# Uppercase literal string
name = upper("hello")

# Uppercase expression
ref_upper = upper(GitHub.ref_name)
env_upper = upper(Env.get("environment"))
```

**Example:**
```python
from wetwire_github.workflow import Step
from wetwire_github.workflow.expressions import upper, Inputs

deploy_step = Step(
    name="Deploy to environment",
    run="./deploy.sh",
    env={"ENV": upper(Inputs.get("environment"))},
)
```

**Output:**
```yaml
- name: Deploy to environment
  run: ./deploy.sh
  env:
    ENV: ${{ upper(inputs.environment) }}
```

---

### trim()

Remove leading and trailing whitespace from a string.

```python
from wetwire_github.workflow.expressions import trim, Env, Inputs

# Trim literal string
cleaned = trim("  hello  ")

# Trim expression
clean_input = trim(Inputs.get("value"))
clean_env = trim(Env.get("CONFIG"))
```

**Example:**
```python
from wetwire_github.workflow import Step
from wetwire_github.workflow.expressions import trim, Inputs

deploy_step = Step(
    name="Deploy with cleaned input",
    run="./deploy.sh $VERSION",
    env={"VERSION": trim(Inputs.get("version"))},
)
```

**Output:**
```yaml
- name: Deploy with cleaned input
  run: ./deploy.sh $VERSION
  env:
    VERSION: ${{ trim(inputs.version) }}
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
