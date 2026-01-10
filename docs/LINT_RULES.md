# Lint Rules Reference

wetwire-github includes a linter with 28 rules (WAG001-WAG022, WAG050-WAG053) that enforce type-safe patterns, catch common mistakes, and detect security issues in GitHub workflow declarations.

## Quick Reference

| Rule | Description | Auto-Fix |
|------|-------------|:--------:|
| [WAG001](#wag001-use-typed-action-wrappers) | Use typed action wrappers | Yes |
| [WAG002](#wag002-use-condition-builders) | Use condition builders | Yes |
| [WAG003](#wag003-use-secrets-context) | Use Secrets.get() helper | Yes |
| [WAG004](#wag004-use-matrix-builder) | Use Strategy/Matrix classes | No |
| [WAG005](#wag005-extract-inline-env-variables) | Extract repeated env variables | No |
| [WAG006](#wag006-duplicate-workflow-names) | Detect duplicate workflow names | No |
| [WAG007](#wag007-file-too-large) | Split large files | No |
| [WAG008](#wag008-hardcoded-expressions) | Avoid hardcoded expressions | No |
| [WAG009](#wag009-validate-event-types) | Validate webhook event types | No |
| [WAG010](#wag010-document-secrets) | Document secrets usage | No |
| [WAG011](#wag011-complex-conditions) | Flag complex conditions | No |
| [WAG012](#wag012-suggest-reusable-workflows) | Suggest reusable workflows | No |
| [WAG013](#wag013-extract-inline-env-variables) | Extract inline env variables | Yes |
| [WAG014](#wag014-extract-inline-matrix-config) | Extract inline matrix config | Yes |
| [WAG015](#wag015-extract-inline-outputs) | Extract inline outputs | Yes |
| [WAG016](#wag016-suggest-reusable-workflow-extraction) | Suggest reusable workflow extraction | No |
| [WAG017](#wag017-hardcoded-secrets-in-run) | Detect hardcoded secrets in run commands | No |
| [WAG018](#wag018-unpinned-actions) | Detect unpinned actions | Yes |
| [WAG019](#wag019-unused-permissions) | Detect unused permissions | Yes |
| [WAG020](#wag020-overly-permissive-secrets) | Warn about secrets in run commands | No |
| [WAG021](#wag021-missing-oidc-configuration) | Suggest OIDC for cloud auth | No |
| [WAG022](#wag022-implicit-environment-exposure) | Detect unescaped user input | No |
| [WAG050](#wag050-unused-job-outputs) | Flag unused job outputs | Yes |
| [WAG051](#wag051-circular-job-dependencies) | Detect circular job dependencies | No |
| [WAG052](#wag052-orphan-secrets) | Flag orphan secrets | Yes |
| [WAG053](#wag053-step-output-references) | Validate step output references | No |

---

## Type Safety Rules (WAG001-004)

### WAG001: Use Typed Action Wrappers

Use typed action wrapper functions instead of raw `uses` strings for known actions.

```python
# Bad
from wetwire_github.workflow import Step

steps = [
    Step(uses="actions/checkout@v4"),
    Step(uses="actions/setup-python@v5", with_={"python-version": "3.11"}),
]
```

```python
# Good
from wetwire_github.actions import checkout, setup_python

steps = [
    checkout(fetch_depth=0),
    setup_python(python_version="3.11"),
]
```

**Why:** Typed action wrappers provide IDE autocomplete, type checking for inputs, and catch typos at import time instead of runtime.

**Known actions with wrappers:**
- `actions/checkout`
- `actions/setup-python`
- `actions/setup-node`
- `actions/setup-go`
- `actions/setup-java`
- `actions/cache`
- `actions/upload-artifact`
- `actions/download-artifact`

**Auto-fix:** No

---

### WAG002: Use Condition Builders

Use condition builder functions instead of hardcoded `${{ always() }}` strings.

```python
# Bad
from wetwire_github.workflow import Step

cleanup_step = Step(
    name="Cleanup",
    run="rm -rf temp/",
    if_="${{ always() }}",
)
```

```python
# Good
from wetwire_github.workflow import Step
from wetwire_github.workflow.expressions import always

cleanup_step = Step(
    name="Cleanup",
    run="rm -rf temp/",
    if_=always(),
)
```

**Why:** Condition builders are type-safe, provide IDE support, and prevent typos in condition function names.

**Available condition builders:**
- `always()` - Run regardless of previous step outcomes
- `failure()` - Run only if a previous step failed
- `success()` - Run only if all previous steps succeeded
- `cancelled()` - Run only if the workflow was cancelled

**Auto-fix:** No

---

### WAG003: Use Secrets Context

Use `Secrets.get()` helper instead of hardcoded `${{ secrets.* }}` strings.

```python
# Bad
from wetwire_github.workflow import Step

deploy_step = Step(
    name="Deploy",
    run="deploy.sh",
    env={
        "API_KEY": "${{ secrets.API_KEY }}",
        "DEPLOY_TOKEN": "${{ secrets.DEPLOY_TOKEN }}",
    },
)
```

```python
# Good
from wetwire_github.workflow import Step
from wetwire_github.workflow.expressions import Secrets

deploy_step = Step(
    name="Deploy",
    run="deploy.sh",
    env={
        "API_KEY": Secrets.get("API_KEY"),
        "DEPLOY_TOKEN": Secrets.get("DEPLOY_TOKEN"),
    },
)
```

**Why:** The `Secrets.get()` helper provides type safety, prevents typos in secret names, and makes secrets usage explicit and searchable.

**Auto-fix:** Yes - Automatically replaces `${{ secrets.NAME }}` with `Secrets.get("NAME")`

---

### WAG004: Use Matrix Builder

Use `Strategy` and `Matrix` classes instead of raw dictionaries.

```python
# Bad
from wetwire_github.workflow import Job

test_job = Job(
    runs_on="ubuntu-latest",
    strategy={
        "matrix": {
            "python-version": ["3.10", "3.11", "3.12"],
            "os": ["ubuntu-latest", "macos-latest"],
        }
    },
    steps=[...],
)
```

```python
# Good
from wetwire_github.workflow import Job
from wetwire_github.workflow.strategy import Strategy, Matrix

test_job = Job(
    runs_on="ubuntu-latest",
    strategy=Strategy(
        matrix=Matrix(
            values={
                "python-version": ["3.10", "3.11", "3.12"],
                "os": ["ubuntu-latest", "macos-latest"],
            }
        )
    ),
    steps=[...],
)
```

**Why:** The `Strategy` and `Matrix` classes provide type validation, better IDE support, and ensure correct structure for matrix configurations.

**Auto-fix:** No

---

## Expression Rules (WAG008)

### WAG008: Hardcoded Expressions

Avoid hardcoded `${{ }}` expression strings; use Expression objects instead.

```python
# Bad
from wetwire_github.workflow import Step

step = Step(
    name="Conditional step",
    run="echo ${{ github.ref }}",
    if_="${{ github.event_name == 'push' }}",
)
```

```python
# Good
from wetwire_github.workflow import Step
from wetwire_github.workflow.expressions import GitHub

step = Step(
    name="Conditional step",
    run=f"echo {GitHub.ref}",
    if_=GitHub.event_name == "push",
)
```

**Why:** Expression objects are type-safe, provide IDE autocomplete for available context properties, and catch errors at development time.

**Available expression contexts:**
- `GitHub.*` - GitHub context (ref, sha, event_name, etc.)
- `Secrets.get()` - Secrets context
- `Matrix.get()` - Matrix context values
- `Env.get()` - Environment variables

**Auto-fix:** No

---

## Code Organization Rules (WAG005-007)

### WAG005: Extract Inline Env Variables

Extract environment variables that are repeated across multiple steps to job or workflow level.

```python
# Bad
from wetwire_github.workflow import Job, Step

build_job = Job(
    runs_on="ubuntu-latest",
    steps=[
        Step(
            name="Build",
            run="make build",
            env={"NODE_ENV": "production", "CI": "true"},
        ),
        Step(
            name="Test",
            run="make test",
            env={"NODE_ENV": "production", "CI": "true"},  # Duplicated!
        ),
        Step(
            name="Package",
            run="make package",
            env={"NODE_ENV": "production"},  # Duplicated!
        ),
    ],
)
```

```python
# Good
from wetwire_github.workflow import Job, Step

build_job = Job(
    runs_on="ubuntu-latest",
    env={
        "NODE_ENV": "production",
        "CI": "true",
    },
    steps=[
        Step(name="Build", run="make build"),
        Step(name="Test", run="make test"),
        Step(name="Package", run="make package"),
    ],
)
```

**Why:** Extracting repeated environment variables reduces duplication, makes configuration easier to maintain, and ensures consistency across steps.

**Auto-fix:** No

---

### WAG006: Duplicate Workflow Names

Detect duplicate workflow names within the same file.

```python
# Bad
from wetwire_github.workflow import Workflow

ci_workflow = Workflow(
    name="CI",
    on={"push": {}},
    jobs={...},
)

# Later in the same file...
another_ci = Workflow(
    name="CI",  # Duplicate name!
    on={"pull_request": {}},
    jobs={...},
)
```

```python
# Good
from wetwire_github.workflow import Workflow

ci_workflow = Workflow(
    name="CI",
    on={"push": {}},
    jobs={...},
)

pr_workflow = Workflow(
    name="PR Checks",  # Unique name
    on={"pull_request": {}},
    jobs={...},
)
```

**Why:** Duplicate workflow names cause confusion in GitHub Actions UI and can lead to unexpected behavior when referencing workflows.

**Auto-fix:** No

---

### WAG007: File Too Large

Warn when a file contains more than 10 jobs, suggesting to split into multiple files.

```
# Bad: workflows.py with 15+ jobs

# Good: Split by purpose
ci.py           # CI/CD jobs (build, test, lint)
deploy.py       # Deployment jobs
release.py      # Release automation jobs
maintenance.py  # Scheduled maintenance jobs
```

**Why:** Large files are harder to maintain, review, and understand. Splitting by purpose improves organization and enables better code reuse.

**Threshold:** Default is 10 jobs per file (configurable)

**Suggested categories:**
- `ci.py` - Build, test, lint jobs
- `deploy.py` - Deployment and environment jobs
- `release.py` - Release and publishing jobs
- `security.py` - Security scanning and audit jobs
- `maintenance.py` - Scheduled cleanup and maintenance

**Auto-fix:** No

---

## Validation Rules (WAG009-010)

### WAG009: Validate Event Types

Validate that trigger event types are valid GitHub Actions events.

```python
# Bad
from wetwire_github.workflow import Workflow

workflow = Workflow(
    name="CI",
    on={"invalid_event": {}},  # Not a valid event!
    jobs={...},
)
```

```python
# Good
from wetwire_github.workflow import Workflow

workflow = Workflow(
    name="CI",
    on={
        "push": {"branches": ["main"]},
        "pull_request": {},
        "workflow_dispatch": {},
    },
    jobs={...},
)
```

**Why:** Invalid event types will cause workflow failures. Catching them early saves debugging time.

**Valid event types include:** `push`, `pull_request`, `workflow_dispatch`, `schedule`, `release`, `issues`, `workflow_call`, and [many more](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows).

**Auto-fix:** No

---

### WAG010: Document Secrets

Detect secrets used in code to help document required secrets.

```python
# Triggers a warning to document these secrets
from wetwire_github.workflow import Step
from wetwire_github.workflow.expressions import Secrets

step = Step(
    env={
        "API_KEY": Secrets.get("API_KEY"),
        "DEPLOY_TOKEN": Secrets.get("DEPLOY_TOKEN"),
    },
    run="deploy.sh",
)
```

**Why:** Secrets should be documented in your README so other contributors know what repository secrets are required.

**Suggestion:** Add a "Required Secrets" section to your documentation listing all secrets with descriptions.

**Auto-fix:** No

---

## Complexity Rules (WAG011-012)

### WAG011: Complex Conditions

Flag overly complex conditional logic in job/step conditions.

```python
# Bad - Too many operators
from wetwire_github.workflow import Step

step = Step(
    if_="cond1 && cond2 && cond3 && cond4 && cond5",
    run="complex-operation.sh",
)
```

```python
# Good - Extract to named variable
from wetwire_github.workflow import Step

is_production_deploy = (
    (GitHub.ref == "refs/heads/main") &
    (GitHub.event_name == "push") &
    success()
)

step = Step(
    if_=is_production_deploy,
    run="complex-operation.sh",
)
```

**Why:** Complex conditions are hard to read and maintain. Named variables with descriptive names make intent clear.

**Threshold:** Default is 3 operators (configurable)

**Auto-fix:** No

---

### WAG012: Suggest Reusable Workflows

Detect duplicated job patterns that could be extracted into reusable workflows.

```python
# Bad - Similar jobs duplicated
from wetwire_github.workflow import Job, Step

test_py311 = Job(
    runs_on="ubuntu-latest",
    steps=[Step(uses="actions/checkout@v4"), Step(run="pytest")],
)

test_py312 = Job(
    runs_on="ubuntu-latest",
    steps=[Step(uses="actions/checkout@v4"), Step(run="pytest")],
)
```

```python
# Good - Use reusable workflow or matrix
from wetwire_github.workflow import Job, Step
from wetwire_github.workflow.strategy import Strategy, Matrix

test_job = Job(
    runs_on="ubuntu-latest",
    strategy=Strategy(
        matrix=Matrix(values={"python": ["3.11", "3.12"]})
    ),
    steps=[
        Step(uses="actions/checkout@v4"),
        Step(run="pytest"),
    ],
)
```

**Why:** Duplicated patterns increase maintenance burden and risk of inconsistencies. Reusable workflows or matrix strategies reduce duplication.

**Auto-fix:** No

---

## Extraction Rules (WAG013-015)

### WAG013: Extract Inline Env Variables

Extract large inline environment variable dictionaries to named variables for better readability.

```python
# Bad - Too many inline env variables
from wetwire_github.workflow import Step

step = Step(
    run="make build",
    env={
        "CI": "true",
        "NODE_ENV": "production",
        "DEBUG": "false",
        "VERBOSE": "1",
        "LOG_LEVEL": "info",
    },
)
```

```python
# Good - Extract to named variable
from wetwire_github.workflow import Step

step_env = {
    "CI": "true",
    "NODE_ENV": "production",
    "DEBUG": "false",
    "VERBOSE": "1",
    "LOG_LEVEL": "info",
}

step = Step(
    run="make build",
    env=step_env,
)
```

**Why:** Large inline dictionaries make steps harder to read and maintain. Extracting environment variables to named variables improves readability, enables reuse, and makes it easier to modify configurations.

**Threshold:** Default is 3 inline env variables (configurable)

**Auto-fix:** Yes - Automatically extracts inline env dicts to a variable named `{step_var}_env`

---

### WAG014: Extract Inline Matrix Config

Extract complex inline matrix configurations to named variables.

```python
# Bad - Complex inline matrix
from wetwire_github.workflow import Job, Step
from wetwire_github.workflow.strategy import Strategy, Matrix

test_job = Job(
    runs_on="ubuntu-latest",
    strategy=Strategy(
        matrix=Matrix(
            values={
                "python": ["3.9", "3.10", "3.11", "3.12"],
                "os": ["ubuntu-latest", "macos-latest", "windows-latest"],
                "node": ["16", "18", "20"],
            }
        )
    ),
    steps=[Step(run="pytest")],
)
```

```python
# Good - Extract matrix to named variable
from wetwire_github.workflow import Job, Step
from wetwire_github.workflow.strategy import Strategy, Matrix

test_job_matrix = Matrix(
    values={
        "python": ["3.9", "3.10", "3.11", "3.12"],
        "os": ["ubuntu-latest", "macos-latest", "windows-latest"],
        "node": ["16", "18", "20"],
    }
)

test_job = Job(
    runs_on="ubuntu-latest",
    strategy=Strategy(matrix=test_job_matrix),
    steps=[Step(run="pytest")],
)
```

**Why:** Complex matrix configurations with many keys or values become difficult to read when inlined. Extracting them to named variables improves code organization and makes the matrix strategy easier to understand and modify.

**Threshold:** Default is >2 keys or >3 values per key (configurable)

**Auto-fix:** Yes - Automatically extracts complex matrix configs to a variable named `{job_var}_matrix`

---

### WAG015: Extract Inline Outputs

Extract large inline outputs dictionaries in Job definitions to named variables.

```python
# Bad - Too many inline outputs
from wetwire_github.workflow import Job, Step

build_job = Job(
    runs_on="ubuntu-latest",
    outputs={
        "version": "${{ steps.get_version.outputs.version }}",
        "tag": "${{ steps.get_tag.outputs.tag }}",
        "sha": "${{ steps.get_sha.outputs.sha }}",
        "artifact_url": "${{ steps.upload.outputs.artifact_url }}",
    },
    steps=[Step(run="echo test")],
)
```

```python
# Good - Extract to named variable
from wetwire_github.workflow import Job, Step

build_job_outputs = {
    "version": "${{ steps.get_version.outputs.version }}",
    "tag": "${{ steps.get_tag.outputs.tag }}",
    "sha": "${{ steps.get_sha.outputs.sha }}",
    "artifact_url": "${{ steps.upload.outputs.artifact_url }}",
}

build_job = Job(
    runs_on="ubuntu-latest",
    outputs=build_job_outputs,
    steps=[Step(run="echo test")],
)
```

**Why:** Large inline outputs dictionaries clutter job definitions and make them harder to scan. Extracting outputs to named variables improves readability and makes the job definition more concise.

**Threshold:** Default is 2 inline outputs (configurable)

**Auto-fix:** Yes - Automatically extracts inline outputs to a variable named `{job_var}_outputs`

---

### WAG016: Suggest Reusable Workflow Extraction

Detect duplicated inline job patterns across workflows that could be extracted into reusable workflows.

```python
# Bad - Duplicated inline jobs across workflows
from wetwire_github.workflow import Workflow, Job, Step
from wetwire_github.actions import checkout, setup_python

ci_workflow = Workflow(
    name="CI",
    on={"push": {"branches": ["main"]}},
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            steps=[
                checkout(),
                setup_python(python_version="3.11"),
                Step(run="make build"),
            ],
        ),
    },
)

pr_workflow = Workflow(
    name="PR",
    on={"pull_request": {}},
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            steps=[
                checkout(),
                setup_python(python_version="3.11"),
                Step(run="make build"),
            ],
        ),
    },
)
```

```python
# Good - Extract common job and reference it
from wetwire_github.workflow import Workflow, Job, Step
from wetwire_github.actions import checkout, setup_python

# Define the job once
build_job = Job(
    runs_on="ubuntu-latest",
    steps=[
        checkout(),
        setup_python(python_version="3.11"),
        Step(run="make build"),
    ],
)

ci_workflow = Workflow(
    name="CI",
    on={"push": {"branches": ["main"]}},
    jobs={"build": build_job},
)

pr_workflow = Workflow(
    name="PR",
    on={"pull_request": {}},
    jobs={"build": build_job},
)
```

**Alternative - Use a reusable workflow:**

```python
# build.py - Reusable workflow
from wetwire_github.workflow import Workflow, Job, Step
from wetwire_github.actions import checkout, setup_python

build_workflow = Workflow(
    name="Build",
    on={"workflow_call": {}},
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            steps=[
                checkout(),
                setup_python(python_version="3.11"),
                Step(run="make build"),
            ],
        ),
    },
)

# ci.py - Call the reusable workflow
ci_workflow = Workflow(
    name="CI",
    on={"push": {"branches": ["main"]}},
    jobs={
        "build": Job(uses="./.github/workflows/build.yml"),
    },
)
```

**Why:** Duplicated inline job definitions across multiple workflows create maintenance burden and risk of inconsistencies. Extracting to shared job variables or reusable workflows reduces duplication, ensures consistency, and makes updates easier.

**Auto-fix:** No

---

## Security Rules (WAG017-022)

### WAG017: Hardcoded Secrets in Run

Detect hardcoded secrets, API keys, passwords, tokens, and other sensitive data in `run` commands.

```python
# Bad - Hardcoded API key in run command
from wetwire_github.workflow import Step

step = Step(
    name="Deploy",
    run="curl -H 'Authorization: Bearer sk_live_abc123xyz789' https://api.example.com/deploy",
)
```

```python
# Good - Use secrets via environment variable
from wetwire_github.workflow import Step
from wetwire_github.workflow.expressions import Secrets

step = Step(
    name="Deploy",
    run="curl -H \"Authorization: Bearer $API_KEY\" https://api.example.com/deploy",
    env={"API_KEY": Secrets.get("API_KEY")},
)
```

**Why:** Hardcoded secrets in code can be exposed through version control, logs, or error messages. Always use GitHub Secrets and pass them via environment variables.

**Detected patterns:**
- API keys (16+ character strings)
- AWS credentials (AKIA prefix, secret access keys)
- Stripe keys (sk_live, sk_test, pk_live, pk_test)
- GitHub tokens (ghp_, ghs_, gho_, ghu_ prefixes)
- Password assignments in commands
- Private key markers (BEGIN PRIVATE KEY)

**Auto-fix:** No (requires moving secrets to GitHub Secrets)

---

### WAG018: Unpinned Actions

Detect actions that are not pinned to a specific version, SHA, or that are pinned to a branch.

```python
# Bad - Unpinned action
from wetwire_github.workflow import Step

step = Step(uses="actions/checkout")  # No version!
```

```python
# Bad - Pinned to branch
from wetwire_github.workflow import Step

step = Step(uses="actions/checkout@main")  # Branch can change!
```

```python
# Good - Pinned to version
from wetwire_github.actions import checkout

step = checkout(fetch_depth=0)  # Uses actions/checkout@v4
```

```python
# Better - Pinned to SHA
from wetwire_github.workflow import Step

step = Step(uses="actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11")  # Full SHA
```

**Why:** Unpinned or branch-pinned actions can change without warning, potentially introducing security vulnerabilities or breaking changes. Pinning to versions or SHAs ensures reproducible builds.

**Auto-fix:** Yes - Adds default version tags for known actions (e.g., @v4 for actions/checkout)

---

### WAG019: Unused Permissions

Detect permissions that are declared but not needed by any action in the job.

```python
# Bad - Unnecessary write permission
from wetwire_github.workflow import Job, Step

job = Job(
    runs_on="ubuntu-latest",
    permissions={
        "contents": "write",  # Not needed for checkout
        "packages": "write",  # Not used at all
    },
    steps=[Step(uses="actions/checkout@v4")],
)
```

```python
# Good - Minimal required permissions
from wetwire_github.workflow import Job, Step

job = Job(
    runs_on="ubuntu-latest",
    permissions={
        "contents": "read",
    },
    steps=[Step(uses="actions/checkout@v4")],
)
```

**Why:** Following the principle of least privilege reduces the blast radius of potential security incidents. Only grant permissions that are actually required.

**Auto-fix:** Yes - Removes unused permission declarations from Job configurations. Cannot auto-fix broad permissions like "write-all" that require manual review.

---

### WAG020: Overly Permissive Secrets

Warn about secrets interpolated directly into shell commands where they may be exposed in logs.

```python
# Bad - Secret directly in command
from wetwire_github.workflow import Step

step = Step(
    name="Deploy",
    run="deploy.sh --token=${{ secrets.DEPLOY_TOKEN }}",
)
```

```python
# Good - Secret passed via environment variable
from wetwire_github.workflow import Step
from wetwire_github.workflow.expressions import Secrets

step = Step(
    name="Deploy",
    run="deploy.sh --token=$TOKEN",
    env={"TOKEN": Secrets.get("DEPLOY_TOKEN")},
)
```

**Why:** Secrets directly interpolated in run commands may be logged if the command fails or if debug logging is enabled. Environment variables are masked by GitHub Actions.

**Auto-fix:** No

---

### WAG021: Missing OIDC Configuration

Suggest using OpenID Connect (OIDC) instead of long-lived credentials for cloud provider authentication.

```python
# Bad - Using static AWS credentials
from wetwire_github.workflow import Step

step = Step(
    uses="aws-actions/configure-aws-credentials@v4",
    with_={
        "aws-access-key-id": "${{ secrets.AWS_ACCESS_KEY_ID }}",
        "aws-secret-access-key": "${{ secrets.AWS_SECRET_ACCESS_KEY }}",
        "aws-region": "us-east-1",
    },
)
```

```python
# Good - Using OIDC with role assumption
from wetwire_github.workflow import Step

step = Step(
    uses="aws-actions/configure-aws-credentials@v4",
    with_={
        "role-to-assume": "arn:aws:iam::123456789012:role/GitHubActions",
        "aws-region": "us-east-1",
    },
)
```

**Why:** OIDC provides short-lived, automatically rotated credentials that are more secure than long-lived secrets. Supported by AWS, GCP, and Azure.

**Supported cloud providers:**
- AWS: Use `role-to-assume` instead of `aws-access-key-id`/`aws-secret-access-key`
- GCP: Use `workload_identity_provider` instead of `credentials_json`
- Azure: Use federated credentials instead of `creds` with service principal secret

**Auto-fix:** No

---

### WAG022: Implicit Environment Exposure

Detect user-controlled input (issue titles, PR bodies, etc.) used in shell commands without proper escaping.

```python
# Bad - User input directly in command
from wetwire_github.workflow import Step

step = Step(
    name="Comment",
    run="echo ${{ github.event.issue.title }}",  # Command injection risk!
)
```

```python
# Bad - Unquoted environment variable
from wetwire_github.workflow import Step

step = Step(
    name="Comment",
    run="echo $TITLE",  # Should be quoted
    env={"TITLE": "${{ github.event.issue.title }}"},
)
```

```python
# Good - Properly quoted environment variable
from wetwire_github.workflow import Step

step = Step(
    name="Comment",
    run='echo "$TITLE"',  # Properly quoted
    env={"TITLE": "${{ github.event.issue.title }}"},
)
```

**Why:** User-controlled input like issue titles, PR bodies, and commit messages can contain shell metacharacters that could execute arbitrary commands. Always use environment variables and quote them properly.

**User-controlled contexts:**
- `github.event.issue.title`, `github.event.issue.body`
- `github.event.pull_request.title`, `github.event.pull_request.body`
- `github.event.comment.body`, `github.event.review.body`
- `github.event.head_commit.message`
- `github.head_ref`
- `github.event.discussion.title`, `github.event.discussion.body`

**Auto-fix:** No

---

## Running the Linter

```bash
# Lint a file or directory
wetwire-github lint myapp/

# Lint with auto-fix (applies fixes for WAG003, WAG013-WAG015, WAG018)
wetwire-github lint myapp/ --fix

# Lint specific files
wetwire-github lint ci/workflows.py ci/jobs.py
```

## Configuring Rules

Rules can be configured programmatically:

```python
from wetwire_github.linter import Linter
from wetwire_github.linter.rules import (
    WAG001TypedActionWrappers,
    WAG007FileTooLarge,
)

# Use specific rules only
linter = Linter(rules=[
    WAG001TypedActionWrappers(),
    WAG007FileTooLarge(max_jobs=20),  # Custom threshold
])

result = linter.check(source_code, "workflows.py")
```

## Reference Tracking Rules (WAG050-053)

### WAG050: Unused Job Outputs

Flag job outputs that are never referenced by any downstream job.

```python
# Bad - 'unused_output' is never consumed
from wetwire_github.workflow import Workflow, Job, Step

build_job = Job(
    runs_on="ubuntu-latest",
    outputs={
        "version": "${{ steps.get_version.outputs.version }}",
        "unused_output": "${{ steps.other.outputs.value }}",  # Never used!
    },
    steps=[Step(run="echo test")],
)

deploy_job = Job(
    runs_on="ubuntu-latest",
    needs=["build"],
    steps=[
        Step(run="echo ${{ needs.build.outputs.version }}"),  # Only uses 'version'
    ],
)

workflow = Workflow(
    name="CI",
    on={"push": {}},
    jobs={"build": build_job, "deploy": deploy_job},
)
```

```python
# Good - All outputs are consumed
from wetwire_github.workflow import Workflow, Job, Step

build_job = Job(
    runs_on="ubuntu-latest",
    outputs={
        "version": "${{ steps.get_version.outputs.version }}",
    },
    steps=[Step(run="echo test")],
)

deploy_job = Job(
    runs_on="ubuntu-latest",
    needs=["build"],
    steps=[
        Step(run="echo ${{ needs.build.outputs.version }}"),
    ],
)

workflow = Workflow(
    name="CI",
    on={"push": {}},
    jobs={"build": build_job, "deploy": deploy_job},
)
```

**Why:** Unused outputs add noise to workflow definitions and may indicate incomplete job wiring or leftover code from refactoring.

**Auto-fix:** Yes - Removes unreferenced output definitions from Job declarations.

---

### WAG051: Circular Job Dependencies

Detect and warn about circular dependencies in job `needs` declarations.

```python
# Bad - Circular dependency: job_a -> job_b -> job_a
from wetwire_github.workflow import Workflow, Job, Step

job_a = Job(
    runs_on="ubuntu-latest",
    needs=["job_b"],  # Depends on job_b
    steps=[Step(run="echo A")],
)

job_b = Job(
    runs_on="ubuntu-latest",
    needs=["job_a"],  # Depends on job_a - CIRCULAR!
    steps=[Step(run="echo B")],
)

workflow = Workflow(
    name="CI",
    on={"push": {}},
    jobs={"job_a": job_a, "job_b": job_b},
)
```

```python
# Good - Linear dependency chain
from wetwire_github.workflow import Workflow, Job, Step

build_job = Job(
    runs_on="ubuntu-latest",
    steps=[Step(run="make build")],
)

test_job = Job(
    runs_on="ubuntu-latest",
    needs=["build"],
    steps=[Step(run="make test")],
)

deploy_job = Job(
    runs_on="ubuntu-latest",
    needs=["test"],
    steps=[Step(run="make deploy")],
)

workflow = Workflow(
    name="CI",
    on={"push": {}},
    jobs={"build": build_job, "test": test_job, "deploy": deploy_job},
)
```

**Why:** Circular dependencies prevent workflow execution. GitHub Actions will reject workflows with cycles in job dependencies.

**Auto-fix:** No

---

### WAG052: Orphan Secrets

Flag secrets that are referenced at workflow or job level but never actually used in any step.

```python
# Bad - UNUSED_SECRET is defined but never used
from wetwire_github.workflow import Workflow, Job, Step
from wetwire_github.workflow.expressions import Secrets

deploy_job = Job(
    runs_on="ubuntu-latest",
    env={
        "DEPLOY_TOKEN": Secrets.get("DEPLOY_TOKEN"),
        "UNUSED_SECRET": Secrets.get("UNUSED_SECRET"),  # Never used in steps!
    },
    steps=[
        Step(run="echo $DEPLOY_TOKEN"),  # Only uses DEPLOY_TOKEN
    ],
)

workflow = Workflow(
    name="Deploy",
    on={"push": {}},
    jobs={"deploy": deploy_job},
)
```

```python
# Good - All secrets are used
from wetwire_github.workflow import Workflow, Job, Step
from wetwire_github.workflow.expressions import Secrets

deploy_job = Job(
    runs_on="ubuntu-latest",
    steps=[
        Step(
            run="deploy.sh",
            env={"TOKEN": Secrets.get("DEPLOY_TOKEN")},
        ),
    ],
)

workflow = Workflow(
    name="Deploy",
    on={"push": {}},
    jobs={"deploy": deploy_job},
)
```

**Why:** Orphan secrets indicate incomplete workflow logic or leftover code. They also unnecessarily expose secrets that aren't needed.

**Auto-fix:** Yes - Removes unused secret declarations from workflow/job env dictionaries.

---

### WAG053: Step Output References

Validate that `steps.id.outputs.name` references point to valid step IDs that are defined before the reference.

```python
# Bad - References non-existent step ID
from wetwire_github.workflow import Job, Step

build_job = Job(
    runs_on="ubuntu-latest",
    outputs={
        "version": "${{ steps.nonexistent_step.outputs.version }}",  # Invalid!
    },
    steps=[
        Step(id="get_version", run="echo version=1.0.0"),
    ],
)
```

```python
# Bad - Forward reference to step defined later
from wetwire_github.workflow import Job, Step

build_job = Job(
    runs_on="ubuntu-latest",
    steps=[
        Step(id="first", run="echo ${{ steps.second.outputs.value }}"),  # Invalid!
        Step(id="second", run="echo 'second'"),
    ],
)
```

```python
# Good - Valid reference to previously defined step
from wetwire_github.workflow import Job, Step

build_job = Job(
    runs_on="ubuntu-latest",
    outputs={
        "version": "${{ steps.get_version.outputs.version }}",
    },
    steps=[
        Step(id="get_version", run="echo version=1.0.0"),
    ],
)
```

**Why:** Invalid step references cause runtime errors in GitHub Actions. Forward references are also invalid because a step's outputs aren't available until after it completes.

**Auto-fix:** No

---

## See Also

- [CLI Reference](CLI.md) - Full CLI documentation
- [Quick Start](QUICK_START.md) - Getting started guide
- [Expression Contexts](EXPRESSIONS.md) - Using typed expression builders
