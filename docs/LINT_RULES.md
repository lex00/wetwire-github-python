# Lint Rules Reference

wetwire-github includes a linter with 12 rules (WAG001-WAG012) that enforce type-safe patterns and catch common mistakes in GitHub workflow declarations.

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

## Running the Linter

```bash
# Lint a file or directory
wetwire-github lint myapp/

# Lint with auto-fix (applies fixes for WAG003)
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

## See Also

- [CLI Reference](CLI.md) - Full CLI documentation
- [Quick Start](QUICK_START.md) - Getting started guide
- [Expression Contexts](EXPRESSIONS.md) - Using typed expression builders
