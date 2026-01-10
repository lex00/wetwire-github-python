# Validation Reference

wetwire-github provides validation capabilities for GitHub workflow definitions. This includes external validation using actionlint and built-in reference validation for job dependencies, step IDs, and output references.

## Quick Reference

| Function | Description |
|----------|-------------|
| [`validate_workflow()`](#validate_workflow) | Validate using actionlint |
| [`validate_yaml()`](#validate_yaml) | Validate raw YAML with actionlint |
| [`validate_job_dependencies()`](#validate_job_dependencies) | Check all job needs are defined |
| [`validate_step_ids()`](#validate_step_ids) | Ensure step IDs are unique |
| [`validate_step_outputs()`](#validate_step_outputs) | Check output references are valid |

---

## External Validation (actionlint)

### validate_workflow

Validate a Workflow object using the external actionlint tool.

```python
from wetwire_github.validation import validate_workflow
from wetwire_github.workflow import Workflow, Job, Step

workflow = Workflow(
    name="CI",
    jobs={"build": Job(runs_on="ubuntu-latest", steps=[Step(run="make build")])},
)

result = validate_workflow(workflow)

if not result.valid:
    for error in result.errors:
        print(f"Line {error.line}: {error.message}")
```

**Returns:** `ValidationResult` with:
- `valid: bool` - Whether the workflow is valid
- `errors: list[ValidationError]` - List of validation errors
- `actionlint_available: bool` - Whether actionlint is installed

---

### validate_yaml

Validate raw YAML content using actionlint.

```python
from wetwire_github.validation import validate_yaml

yaml_content = """
name: CI
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: make build
"""

result = validate_yaml(yaml_content)
print(f"Valid: {result.valid}")
```

---

### is_actionlint_available

Check if actionlint is installed and available in PATH.

```python
from wetwire_github.validation import is_actionlint_available

if is_actionlint_available():
    print("actionlint is installed")
else:
    print("Install actionlint for YAML validation")
```

---

## Reference Validation

Reference validation functions check for common structural issues in workflow definitions without requiring external tools.

### validate_job_dependencies

Check that all job dependencies (`needs`) reference jobs that exist in the workflow.

```python
from wetwire_github.validation import validate_job_dependencies
from wetwire_github.workflow import Workflow, Job, Step

# Invalid: deploy needs "test" which doesn't exist
workflow = Workflow(
    name="CI",
    jobs={
        "build": Job(runs_on="ubuntu-latest", steps=[Step(run="make build")]),
        "deploy": Job(
            runs_on="ubuntu-latest",
            needs=["build", "test"],  # "test" is undefined!
            steps=[Step(run="make deploy")],
        ),
    },
)

result = validate_job_dependencies(workflow)

if not result.valid:
    for error in result.errors:
        print(f"Job '{error.job_id}': {error.message}")
        # Output: Job 'deploy': Job 'deploy' depends on undefined job 'test'
```

**Detects:**
- References to job names that don't exist in the workflow
- Typos in job dependency names

---

### validate_step_ids

Ensure step IDs are unique within each job. Duplicate step IDs within a job will cause GitHub Actions to fail.

```python
from wetwire_github.validation import validate_step_ids
from wetwire_github.workflow import Workflow, Job, Step

# Invalid: duplicate step ID "setup" in the same job
workflow = Workflow(
    name="CI",
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            steps=[
                Step(id="setup", run="echo setup 1"),
                Step(id="setup", run="echo setup 2"),  # Duplicate!
            ],
        ),
    },
)

result = validate_step_ids(workflow)

if not result.valid:
    for error in result.errors:
        print(f"Job '{error.job_id}': {error.message}")
        # Output: Job 'build': Duplicate step ID 'setup' in job 'build'
```

**Note:** The same step ID can be used in different jobs - IDs only need to be unique within their job.

---

### validate_step_outputs

Validate that step output references (`steps.<id>.outputs.<name>`) point to valid step IDs that are defined before the reference.

```python
from wetwire_github.validation import validate_step_outputs
from wetwire_github.workflow import Workflow, Job, Step

# Invalid: reference to undefined step "version"
workflow = Workflow(
    name="CI",
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            steps=[
                Step(run="echo ${{ steps.version.outputs.value }}"),  # "version" doesn't exist!
            ],
        ),
    },
)

result = validate_step_outputs(workflow)

if not result.valid:
    for error in result.errors:
        print(f"{error.message}")
        # Output: Reference to undefined or forward step ID 'version' in job 'build'
```

**Detects:**
- References to step IDs that don't exist
- Forward references to steps defined later in the job
- Invalid references in `run`, `env`, `if_`, and `with_` fields
- Invalid references in job outputs

**Example of forward reference detection:**

```python
# Invalid: forward reference to step defined later
workflow = Workflow(
    name="CI",
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            steps=[
                Step(run="echo ${{ steps.later.outputs.value }}"),  # Forward ref!
                Step(id="later", run="echo 'value=test' >> $GITHUB_OUTPUT"),
            ],
        ),
    },
)
```

---

## Result Types

### ValidationResult

Result from actionlint validation.

```python
@dataclass
class ValidationResult:
    valid: bool                           # True if validation passed
    errors: list[ValidationError]         # List of errors found
    actionlint_available: bool = True     # False if actionlint not installed
```

### ValidationError

A single actionlint error.

```python
@dataclass
class ValidationError:
    line: int               # Line number in YAML
    column: int             # Column number in YAML
    message: str            # Error message
    severity: str = "error" # Error severity
    rule: str | None = None # Actionlint rule ID
```

### ReferenceValidationResult

Result from reference validation functions.

```python
@dataclass
class ReferenceValidationResult:
    valid: bool                     # True if validation passed
    errors: list[ReferenceError]    # List of errors found
```

### ReferenceError

A single reference validation error.

```python
@dataclass
class ReferenceError:
    message: str                    # Human-readable error message
    job_id: str | None = None       # Job where error occurred
    step_id: str | None = None      # Step ID (for duplicate ID errors)
    reference: str | None = None    # The invalid reference
```

---

## Complete Validation Example

Run all validation checks on a workflow:

```python
from wetwire_github.validation import (
    validate_workflow,
    validate_job_dependencies,
    validate_step_ids,
    validate_step_outputs,
)
from wetwire_github.workflow import Workflow, Job, Step

workflow = Workflow(
    name="CI",
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            steps=[
                Step(id="checkout", uses="actions/checkout@v4"),
                Step(id="build", run="make build"),
            ],
        ),
        "test": Job(
            runs_on="ubuntu-latest",
            needs=["build"],
            steps=[
                Step(run="make test"),
            ],
        ),
    },
)

# Run all validations
results = [
    ("actionlint", validate_workflow(workflow)),
    ("job_dependencies", validate_job_dependencies(workflow)),
    ("step_ids", validate_step_ids(workflow)),
    ("step_outputs", validate_step_outputs(workflow)),
]

all_valid = True
for name, result in results:
    if not result.valid:
        all_valid = False
        print(f"{name} validation failed:")
        for error in result.errors:
            print(f"  - {error.message}")

if all_valid:
    print("All validations passed!")
```

---

## CLI Integration

Validation is also available via the CLI:

```bash
# Validate with actionlint
wetwire-github validate ci/

# The lint command also checks for reference issues
wetwire-github lint ci/
```

See [CLI.md](CLI.md) for more CLI commands.
