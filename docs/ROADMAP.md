# wetwire-github-python Implementation Plan & Roadmap

## Overview

Build `wetwire-github-python` following the same patterns as `wetwire-aws-python` — a synthesis library that generates GitHub YAML configurations from typed Python declarations using dataclasses.

For the wetwire pattern, see the [Wetwire Specification](https://github.com/lex00/wetwire/blob/main/docs/WETWIRE_SPEC.md).

---

## The Declarative Pattern

All declarations use dataclasses — no function calls or registration:

```python
from wetwire_github.workflow import Workflow, Job, Step, Triggers, PushTrigger
from wetwire_github.actions import checkout, setup_python

# Clean trigger declarations
ci_push = PushTrigger(branches=["main"])

# Workflow and job declarations
ci = Workflow(name="CI", on=Triggers(push=ci_push))
build = Job(name="build", runs_on="ubuntu-latest", steps=build_steps)
deploy = Job(needs=[build, test])

# Type-safe action wrappers
checkout.Checkout(fetch_depth=0).to_step()

# Expression contexts
workflow.Secrets.get("TOKEN")
workflow.Matrix.get("os")
workflow.GitHub.ref
```

**Generated package structure:** Single package per project, module-level variables, cross-file references via imports.

AST-based discovery — no registration needed.

**Key principles:**
- Variables declared as dataclass instances (no function calls)
- Cross-resource references via direct variable access
- AST-based discovery — no registration needed
- Type-safe action wrappers with `.to_step()` conversion
- Expression contexts as typed accessors (`workflow.Secrets.get(...)`)

---

## Scope

wetwire-github-python generates typed Python declarations for three GitHub YAML configuration types:

| Config Type | Output Location | Schema Source |
|-------------|-----------------|---------------|
| **GitHub Actions** | `.github/workflows/*.yml` | `json.schemastore.org/github-workflow.json` |
| **Dependabot** | `.github/dependabot.yml` | `json.schemastore.org/dependabot-2.0.json` |
| **Issue/Discussion Templates** | `.github/ISSUE_TEMPLATE/*.yml` | `json.schemastore.org/github-issue-forms.json` |

---

## Key Decisions

- **Action versions**: Hardcode major version in generated wrappers (e.g., `@v4`)
- **Validation**: Use actionlint via subprocess
- **Approach**: Full feature parity with wetwire-aws-python
- **Config types**: Support Actions, Dependabot, and Issue/Discussion Templates via `--type` flag

---

## Feature Matrix: wetwire-aws-python → wetwire-github-python

| Feature | wetwire-aws-python | wetwire-github-python |
|---------|-------------------|----------------------|
| **Schema Source** | CloudFormation spec JSON | Workflow JSON schema + action.yml files |
| **Schema URL** | AWS CF spec URL | `json.schemastore.org/github-workflow.json` |
| **Secondary Source** | — | Popular action.yml files (checkout, setup-python, etc.) |
| **Output Format** | CloudFormation JSON/YAML | GitHub Actions workflow YAML |
| **Generated Types** | AWS service dataclasses | Workflow, Job, Step, Matrix, Triggers + Action wrappers |
| **Intrinsics** | Ref, GetAtt, Sub, Join, etc. | Expression contexts (github, runner, env, secrets, matrix) |
| **Validation** | cfn-lint integration | actionlint integration |

---

## Schema Sources

### 1. Workflow Schema
- **URL**: `https://json.schemastore.org/github-workflow.json`
- **Raw**: `https://raw.githubusercontent.com/SchemaStore/schemastore/master/src/schemas/json/github-workflow.json`
- **Provides**: Triggers, jobs, steps, matrix, concurrency, permissions, environments

### 2. Action Metadata (action.yml)
- **Pattern**: `https://raw.githubusercontent.com/{owner}/{repo}/main/action.yml`
- **Popular actions to generate wrappers for**:
  - `actions/checkout`
  - `actions/setup-python`, `setup-node`, `setup-go`, `setup-java`
  - `actions/cache`
  - `actions/upload-artifact`, `download-artifact`
  - `docker/build-push-action`
  - `codecov/codecov-action`
  - `pypa/gh-action-pypi-publish`
  - (extensible list in config)

### 3. Dependabot Schema
- **URL**: `https://json.schemastore.org/dependabot-2.0.json`
- **Provides**: Package ecosystems, update schedules, registries, groups, ignore patterns

### 4. Issue Forms Schema
- **URL**: `https://json.schemastore.org/github-issue-forms.json`
- **Provides**: Form body elements (input, textarea, dropdown, checkboxes, markdown)

---

## Generated Package Structure (User Projects)

When users run `wetwire-github import` or `wetwire-github init`, the importer scaffolds a project package:

```
my-ci/                           # User's workflow package
├── pyproject.toml               # Package configuration
├── README.md                    # Generated docs
├── CLAUDE.md                    # AI assistant context
├── .gitignore
│
├── src/
│   └── my_ci/
│       ├── __init__.py
│       ├── workflows.py         # Workflow declarations
│       ├── jobs.py              # Job declarations
│       ├── steps.py             # Reusable step declarations
│       ├── triggers.py          # Trigger configurations
│       └── matrix.py            # Matrix configurations
│
└── tests/
    └── __init__.py
```

**Key patterns (same as wetwire-aws-python):**
- Single package per project
- Module-level variables for all resources
- Cross-file references work via Python imports
- Variables reference each other directly (e.g., `steps=build_steps`)

---

## Library Directory Structure

```
wetwire-github-python/
├── .github/
│   └── workflows/
│       ├── ci.yml              # Build/test on push/PR
│       └── publish.yml         # PyPI publishing
│
├── scripts/
│   ├── ci.sh                   # Local CI runner
│   └── import_samples.sh       # Round-trip testing
│
├── src/
│   └── wetwire_github/
│       ├── __init__.py
│       ├── cli/                # CLI application (typer)
│       │   ├── __init__.py
│       │   ├── main.py
│       │   ├── build.py        # Generate YAML (--type workflow|dependabot|issue-template)
│       │   ├── validate.py     # Validate via actionlint
│       │   ├── list.py         # List discovered resources
│       │   ├── lint.py         # Code quality rules
│       │   ├── import_.py      # YAML → Python conversion
│       │   └── init.py         # Project scaffolding
│       │
│       ├── discover/           # AST-based resource discovery
│       ├── importer/           # YAML to Python code conversion
│       ├── linter/             # Python code lint rules (WAG001-WAG0XX)
│       ├── template/           # YAML builder
│       ├── serialize/          # YAML serialization
│       ├── validation/         # actionlint integration
│       │
│       ├── workflow/           # Core workflow types (hand-written)
│       │   ├── __init__.py
│       │   ├── workflow.py     # Workflow dataclass
│       │   ├── job.py          # Job dataclass
│       │   ├── step.py         # Step dataclass
│       │   ├── matrix.py       # Matrix builder
│       │   ├── triggers.py     # Push, PullRequest, Schedule, etc.
│       │   ├── conditions.py   # Condition builders
│       │   └── expressions.py  # github, runner, env, secrets contexts
│       │
│       ├── dependabot/         # Dependabot types (hand-written)
│       │   ├── __init__.py
│       │   ├── dependabot.py   # Dependabot dataclass
│       │   ├── update.py       # Update dataclass
│       │   ├── schedule.py     # Schedule dataclass
│       │   ├── registries.py   # Registry types
│       │   └── groups.py       # Grouping configuration
│       │
│       ├── templates/          # Issue/Discussion template types (hand-written)
│       │   ├── __init__.py
│       │   ├── issue.py        # IssueTemplate dataclass
│       │   ├── discussion.py   # DiscussionTemplate dataclass
│       │   ├── form.py         # FormBody dataclass
│       │   └── elements.py     # Input, Textarea, Dropdown, Checkboxes, Markdown
│       │
│       ├── actions/            # GENERATED action wrappers
│       │   ├── __init__.py
│       │   ├── checkout.py     # Typed wrapper for actions/checkout
│       │   ├── setup_python.py
│       │   ├── cache.py
│       │   └── ... (top 20+ actions)
│       │
│       └── contracts.py        # Protocols and types
│
├── codegen/                    # Code generation tooling
│   ├── fetch.py                # Download schemas + action.yml
│   ├── parse.py                # Parse schemas
│   └── generate.py             # Generate Python types
│
├── examples/                   # Example configs for import testing
│   └── (fetched from real repos)
│
├── docs/
│   ├── ROADMAP.md              # This file
│   ├── FAQ.md
│   ├── QUICK_START.md
│   ├── CLI.md
│   └── IMPORT_WORKFLOW.md
│
├── specs/                      # .gitignore'd (fetched schemas)
│   ├── .gitkeep
│   ├── manifest.json
│   ├── workflow-schema.json
│   ├── dependabot-schema.json
│   ├── issue-forms-schema.json
│   └── actions/
│       ├── checkout.yml
│       └── ...
│
├── tests/
├── pyproject.toml
└── README.md
```

---

## CLI Commands

### 1. `wetwire-github build`
- Discover workflow declarations from Python packages
- Serialize to GitHub Actions YAML
- Output to `.github/workflows/` or custom path

### 2. `wetwire-github validate`
- Run actionlint on generated YAML (via subprocess)
- Report errors in structured format (text/JSON)

### 3. `wetwire-github list`
- List discovered workflows and jobs
- Show file locations and dependencies

### 4. `wetwire-github lint`
- Python code quality rules (WAG001-WAG0XX)
- Examples:
  - WAG001: Use typed action wrappers instead of raw `uses:` strings
  - WAG002: Use condition builders instead of raw expression strings
  - WAG003: Use secrets context instead of hardcoded strings
  - WAG004: Use matrix builder instead of inline dicts

### 5. `wetwire-github import`
- Convert existing workflow YAML to Python code
- Generate typed declarations
- Scaffold project structure

### 6. `wetwire-github init`
- Create new project with example workflow
- Generate pyproject.toml, package structure, workflow definitions

### 7. `wetwire-github design`
- AI-assisted infrastructure design via wetwire-core
- Interactive session with lint feedback loop

### 8. `wetwire-github test`
- Persona-based testing via wetwire-core
- Automated evaluation of code generation quality

### 9. `wetwire-github graph`
- Generate DAG visualization of workflow jobs
- Formats: `--format dot` (Graphviz), `--format mermaid` (GitHub markdown)

---

## CLI Exit Codes

Per the wetwire specification, CLI commands use consistent exit codes:

| Command | Exit 0 | Exit 1 | Exit 2 |
|---------|--------|--------|--------|
| `build` | Success | Error (parse, generation) | — |
| `lint` | No issues | Issues found | Error (parse failure) |
| `import` | Success | Error (parse, generation) | — |
| `validate` | Valid | Invalid (actionlint errors) | Error (file not found) |
| `list` | Success | Error | — |
| `init` | Success | Error (dir exists, write fail) | — |

---

## Contracts (contracts.py)

Core protocols and types (mirroring wetwire-aws-python pattern):

```python
from typing import Protocol
from dataclasses import dataclass

class WorkflowResource(Protocol):
    """Represents a GitHub workflow resource."""
    def resource_type(self) -> str: ...

@dataclass
class OutputRef:
    """Reference to a step output.

    When serialized to YAML, becomes: ${{ steps.step_id.outputs.name }}
    """
    step_id: str
    output: str

    def __str__(self) -> str:
        return f"${{{{ steps.{self.step_id}.outputs.{self.output} }}}}"

@dataclass
class DiscoveredWorkflow:
    """Workflow found by AST parsing."""
    name: str          # Variable name
    file: str          # Source file path
    line: int          # Line number
    jobs: list[str]    # Job variable names in this workflow

@dataclass
class DiscoveredJob:
    """Job found by AST parsing."""
    name: str          # Variable name
    file: str          # Source file path
    line: int          # Line number
    dependencies: list[str]  # Referenced job names (needs field)

# Result types for CLI JSON output
@dataclass
class BuildResult:
    success: bool
    workflows: list[str] | None = None
    files: list[str] | None = None
    errors: list[str] | None = None

@dataclass
class LintResult:
    success: bool
    issues: list["LintIssue"] | None = None

@dataclass
class LintIssue:
    file: str
    line: int
    column: int
    severity: str
    message: str
    rule: str
    fixable: bool

@dataclass
class ValidateResult:
    success: bool
    errors: list[str] | None = None
    warnings: list[str] | None = None

@dataclass
class ListResult:
    workflows: list["ListWorkflow"]

@dataclass
class ListWorkflow:
    name: str
    file: str
    line: int
    jobs: int
```

---

## Core Types (workflow/ package)

Types designed for declarative dataclass initialization:

```python
# workflow/workflow.py
from dataclasses import dataclass, field

@dataclass
class Workflow:
    name: str = ""
    on: "Triggers" = field(default_factory=Triggers)
    env: dict[str, any] | None = None
    defaults: "Defaults | None" = None
    concurrency: "Concurrency | None" = None
    permissions: "Permissions | None" = None
    jobs: dict[str, "Job"] = field(default_factory=dict)  # populated by discovery

# workflow/job.py
@dataclass
class Job:
    # Outputs for cross-job references (excluded from YAML)
    outputs: dict[str, OutputRef] = field(default_factory=dict, repr=False)

    name: str = ""
    runs_on: str | list[str] = "ubuntu-latest"
    needs: list[any] | None = None  # Job references
    if_: str | None = None  # 'if' is reserved
    environment: "Environment | None" = None
    concurrency: "Concurrency | None" = None
    strategy: "Strategy | None" = None
    container: "Container | None" = None
    services: dict[str, "Service"] | None = None
    steps: list["Step"] = field(default_factory=list)
    timeout_minutes: int | None = None

# workflow/step.py
@dataclass
class Step:
    id: str = ""
    name: str = ""
    if_: str | None = None
    uses: str = ""
    with_: dict[str, any] | None = None  # 'with' is reserved
    run: str = ""
    shell: str = ""
    env: dict[str, any] | None = None
    working_directory: str = ""

    def output(self, name: str) -> OutputRef:
        """Returns an OutputRef for referencing this step's outputs."""
        return OutputRef(step_id=self.id, output=name)

# workflow/triggers.py
@dataclass
class Triggers:
    push: "PushTrigger | None" = None
    pull_request: "PullRequestTrigger | None" = None
    pull_request_target: "PullRequestTargetTrigger | None" = None
    schedule: list["ScheduleTrigger"] | None = None
    workflow_dispatch: "WorkflowDispatchTrigger | None" = None
    workflow_call: "WorkflowCallTrigger | None" = None
    # ... 30+ event types

# workflow/matrix.py
@dataclass
class Strategy:
    matrix: "Matrix | None" = None
    fail_fast: bool | None = None
    max_parallel: int | None = None

@dataclass
class Matrix:
    values: dict[str, list[any]] = field(default_factory=dict)
    include: list[dict[str, any]] | None = None
    exclude: list[dict[str, any]] | None = None
```

---

## Expression Contexts (workflow/expressions.py)

```python
class Expression(str):
    """Wraps a GitHub Actions expression string."""

    def __str__(self) -> str:
        return f"${{{{ {super().__str__()} }}}}"

    def and_(self, other: "Expression") -> "Expression":
        return Expression(f"({self}) && ({other})")

    def or_(self, other: "Expression") -> "Expression":
        return Expression(f"({self}) || ({other})")

# Context accessors - used like: workflow.Secrets.get("TOKEN")
class SecretsContext:
    @staticmethod
    def get(name: str) -> Expression:
        return Expression(f"secrets.{name}")

class MatrixContext:
    @staticmethod
    def get(name: str) -> Expression:
        return Expression(f"matrix.{name}")

class GitHubContext:
    ref = Expression("github.ref")
    sha = Expression("github.sha")
    actor = Expression("github.actor")
    event_name = Expression("github.event_name")

# Condition builders
def always() -> Expression:
    return Expression("always()")

def failure() -> Expression:
    return Expression("failure()")

def success() -> Expression:
    return Expression("success()")

def cancelled() -> Expression:
    return Expression("cancelled()")

def branch(name: str) -> Expression:
    return Expression(f"github.ref == 'refs/heads/{name}'")

# Module-level instances
Secrets = SecretsContext()
Matrix = MatrixContext()
GitHub = GitHubContext()
```

---

## Generated Action Wrappers (actions/ package)

```python
# actions/checkout.py
# Code generated by wetwire-github codegen. DO NOT EDIT.
# Source: actions/checkout/action.yml

from dataclasses import dataclass
from wetwire_github.workflow import Step
from wetwire_github.contracts import OutputRef

@dataclass
class Checkout:
    """actions/checkout@v4"""

    # Inputs (from action.yml)
    repository: str = ""
    ref: str = ""
    token: str = ""
    ssh_key: str = ""
    persist_credentials: bool | None = None
    path: str = ""
    clean: bool | None = None
    fetch_depth: int = 1
    fetch_tags: bool | None = None
    submodules: str = ""
    lfs: bool | None = None

    @staticmethod
    def action() -> str:
        return "actions/checkout@v4"

    def to_step(self) -> Step:
        """Convert to a workflow.Step for use in steps list."""
        return Step(
            uses=self.action(),
            with_=self._to_with(),
        )

    def to_step_with_id(self, id: str) -> Step:
        """Convert to a workflow.Step with an ID for output references."""
        return Step(
            id=id,
            uses=self.action(),
            with_=self._to_with(),
        )

    def _to_with(self) -> dict[str, any]:
        # Convert non-default fields to with dict
        ...
```

---

## Integration with wetwire-core

Same pattern as wetwire-aws-python:

```python
# RunnerAgent tools for wetwire-github
tools = [
    "init_package",      # wetwire-github init
    "write_file",        # Write Python workflow code
    "read_file",         # Read files
    "run_lint",          # wetwire-github lint --format json
    "run_build",         # wetwire-github build --format json
    "run_validate",      # wetwire-github validate (actionlint)
    "ask_developer",     # Clarification questions
]
```

CLI must support `--format json` for agent integration.

---

## Actionlint Integration

```python
# validation/actionlint.py
import subprocess
import json
from dataclasses import dataclass

@dataclass
class ValidationIssue:
    file: str
    line: int
    column: int
    message: str
    rule_id: str

@dataclass
class ValidationResult:
    success: bool
    issues: list[ValidationIssue]

def validate_workflow(path: str) -> ValidationResult:
    """Validate workflow using actionlint."""
    result = subprocess.run(
        ["actionlint", "-format", "{{json .}}", path],
        capture_output=True,
        text=True,
    )

    issues = []
    if result.stdout:
        for line in result.stdout.strip().split("\n"):
            if line:
                data = json.loads(line)
                issues.append(ValidationIssue(
                    file=data.get("filepath", ""),
                    line=data.get("line", 0),
                    column=data.get("column", 0),
                    message=data.get("message", ""),
                    rule_id=data.get("kind", ""),
                ))

    return ValidationResult(
        success=len(issues) == 0,
        issues=issues,
    )
```

---

## Feature Matrix

| Feature | Phase | Status | Dependencies |
|---------|-------|--------|--------------|
| **Core Types** | | | |
| ├─ Workflow dataclass | 1A | [ ] | — |
| ├─ Job dataclass | 1A | [ ] | — |
| ├─ Step dataclass | 1A | [ ] | — |
| ├─ Matrix dataclass | 1A | [ ] | — |
| ├─ Triggers (all 30+ types) | 1A | [ ] | — |
| ├─ WorkflowCallTrigger (reusable workflows) | 1A | [ ] | — |
| ├─ WorkflowInput/Output/Secret types | 1A | [ ] | — |
| ├─ Expression class | 1A | [ ] | — |
| ├─ Expression contexts | 1A | [ ] | — |
| ├─ contracts.py (protocols) | 1A | [ ] | — |
| ├─ Result types (Build/Lint/Validate/List) | 1A | [ ] | — |
| └─ DiscoveredWorkflow/Job dataclasses | 1A | [ ] | — |
| **Serialization** | | | |
| ├─ Workflow → YAML | 1B | [ ] | Core Types |
| ├─ Job → YAML | 1B | [ ] | Core Types |
| ├─ Step → YAML | 1B | [ ] | Core Types |
| ├─ Matrix → YAML | 1B | [ ] | Core Types |
| ├─ Triggers → YAML | 1B | [ ] | Core Types |
| ├─ Reusable workflow (workflow_call) → YAML | 1B | [ ] | Core Types |
| ├─ Conditions → expression strings | 1B | [ ] | Core Types |
| ├─ Dataclass → dict serialization | 1B | [ ] | Core Types |
| ├─ snake_case/kebab-case conversion | 1B | [ ] | — |
| └─ None value omission | 1B | [ ] | — |
| **CLI Framework** | | | |
| ├─ main.py + typer setup | 1C | [ ] | — |
| ├─ `init` command | 1C | [ ] | — |
| ├─ `build` command (stub) | 1C | [ ] | — |
| ├─ `validate` command (stub) | 1C | [ ] | — |
| ├─ `list` command (stub) | 1C | [ ] | — |
| ├─ `lint` command (stub) | 1C | [ ] | — |
| ├─ `import` command (stub) | 1C | [ ] | — |
| ├─ `design` command (stub) | 1C | [ ] | — |
| ├─ `test` command (stub) | 1C | [ ] | — |
| ├─ `graph` command (stub) | 1C | [ ] | — |
| ├─ `version` command | 1C | [ ] | — |
| └─ Exit code semantics (0/1/2) | 1C | [ ] | — |
| **Schema Fetching** | | | |
| ├─ HTTP fetcher with retry | 1D | [ ] | — |
| ├─ Workflow schema fetch | 1D | [ ] | — |
| ├─ Action.yml fetch (checkout) | 1D | [ ] | — |
| ├─ Action.yml fetch (setup-python) | 1D | [ ] | — |
| ├─ Action.yml fetch (setup-node) | 1D | [ ] | — |
| ├─ Action.yml fetch (setup-go) | 1D | [ ] | — |
| ├─ Action.yml fetch (cache) | 1D | [ ] | — |
| ├─ Action.yml fetch (upload-artifact) | 1D | [ ] | — |
| ├─ Action.yml fetch (download-artifact) | 1D | [ ] | — |
| └─ specs/manifest.json | 1D | [ ] | — |
| **Schema Parsing** | | | |
| ├─ Workflow schema parser | 2A | [ ] | Schema Fetching |
| ├─ Action.yml parser | 2A | [ ] | Schema Fetching |
| └─ Intermediate representation | 2A | [ ] | Schema Fetching |
| **Action Codegen** | | | |
| ├─ Generator templates (Jinja2) | 2B | [ ] | Schema Parsing |
| ├─ Code formatting (black) | 2B | [ ] | — |
| ├─ actions/checkout wrapper | 2B | [ ] | Schema Parsing |
| ├─ actions/setup_python wrapper | 2B | [ ] | Schema Parsing |
| ├─ actions/setup_node wrapper | 2B | [ ] | Schema Parsing |
| ├─ actions/setup_go wrapper | 2B | [ ] | Schema Parsing |
| ├─ actions/cache wrapper | 2B | [ ] | Schema Parsing |
| ├─ actions/upload_artifact wrapper | 2B | [ ] | Schema Parsing |
| ├─ actions/download_artifact wrapper | 2B | [ ] | Schema Parsing |
| └─ Composite action wrapper support | 2B | [ ] | Schema Parsing |
| **AST Discovery** | | | |
| ├─ Package scanning (ast module) | 2C | [ ] | Core Types |
| ├─ Workflow variable detection | 2C | [ ] | Core Types |
| ├─ Job variable detection | 2C | [ ] | Core Types |
| ├─ Dependency graph building | 2C | [ ] | Core Types |
| ├─ Reference validation | 2C | [ ] | Core Types |
| ├─ Recursive directory traversal | 2C | [ ] | — |
| └─ __pycache__/hidden directory exclusion | 2C | [ ] | — |
| **Runner (Value Extraction)** | | | |
| ├─ Dynamic module import | 2G | [ ] | AST Discovery |
| ├─ pyproject.toml parsing | 2G | [ ] | — |
| ├─ Module path resolution | 2G | [ ] | — |
| └─ JSON value extraction | 2G | [ ] | — |
| **Template Builder** | | | |
| ├─ Topological sort (Kahn's algorithm) | 2H | [ ] | AST Discovery |
| ├─ Cycle detection | 2H | [ ] | AST Discovery |
| └─ Dependency ordering | 2H | [ ] | AST Discovery |
| **Build Command (full)** | | | |
| ├─ Discovery integration | 3A | [ ] | AST Discovery |
| ├─ Runner integration | 3A | [ ] | Runner |
| ├─ Template builder integration | 3A | [ ] | Template Builder |
| ├─ Multi-workflow support | 3A | [ ] | Serialization |
| ├─ Output to `.github/workflows/` | 3A | [ ] | Serialization |
| ├─ --format json/yaml | 3A | [ ] | — |
| └─ --output flag | 3A | [ ] | — |
| **Validation (actionlint)** | | | |
| ├─ actionlint subprocess integration | 2D | [ ] | — |
| ├─ ValidationResult types | 2D | [ ] | — |
| └─ `validate` command (full) | 3B | [ ] | actionlint integration |
| **Linting Rules** | | | |
| ├─ Linter framework | 2E | [ ] | — |
| ├─ Rule protocol (id, description, check) | 2E | [ ] | — |
| ├─ WAG001: typed action wrappers | 2E | [ ] | — |
| ├─ WAG002: condition builders | 2E | [ ] | — |
| ├─ WAG003: secrets context | 2E | [ ] | — |
| ├─ WAG004: matrix builder | 2E | [ ] | — |
| ├─ WAG005: inline dicts → named vars | 2E | [ ] | — |
| ├─ WAG006: duplicate workflow names | 2E | [ ] | — |
| ├─ WAG007: file too large (>N jobs) | 2E | [ ] | — |
| ├─ WAG008: hardcoded expression strings | 2E | [ ] | — |
| ├─ Recursive package scanning | 2E | [ ] | — |
| ├─ --fix flag support | 2E | [ ] | — |
| └─ `lint` command (full) | 3C | [ ] | Linter framework |
| **Import (YAML → Python)** | | | |
| ├─ YAML parser | 2F | [ ] | — |
| ├─ IR (intermediate representation) | 2F | [ ] | — |
| ├─ IRWorkflow, IRJob, IRStep dataclasses | 2F | [ ] | — |
| ├─ Reference graph tracking | 2F | [ ] | — |
| ├─ Python code generator | 3D | [ ] | YAML parser, Core Types |
| ├─ Field name transformation | 3D | [ ] | — |
| ├─ Reserved name handling (if_, with_) | 3D | [ ] | — |
| ├─ Scaffold: pyproject.toml | 3D | [ ] | — |
| ├─ Scaffold: src/package/__init__.py | 3D | [ ] | — |
| ├─ Scaffold: README.md | 3D | [ ] | — |
| ├─ Scaffold: CLAUDE.md | 3D | [ ] | — |
| ├─ Scaffold: .gitignore | 3D | [ ] | — |
| ├─ --single-file flag | 3D | [ ] | — |
| ├─ --no-scaffold flag | 3D | [ ] | — |
| ├─ Local action wrapper generation | 3D | [ ] | Action Codegen |
| └─ `import` command (full) | 3D | [ ] | Python code generator |
| **List Command** | | | |
| ├─ Table output format | 3E | [ ] | AST Discovery |
| ├─ --format json | 3E | [ ] | — |
| └─ `list` command (full) | 3E | [ ] | AST Discovery |
| **Graph Command (DAG Visualization)** | | | |
| ├─ graphviz library integration | 3H | [ ] | AST Discovery |
| ├─ DOT format output | 3H | [ ] | — |
| ├─ Mermaid format output | 3H | [ ] | — |
| ├─ Job dependency edge extraction | 3H | [ ] | AST Discovery |
| └─ `graph` command (full) | 3H | [ ] | AST Discovery |
| **Design Command (AI-assisted)** | | | |
| ├─ wetwire-core orchestrator | 3F | [ ] | All CLI commands |
| ├─ Interactive session | 3F | [ ] | — |
| ├─ --stream flag | 3F | [ ] | — |
| ├─ --max-lint-cycles flag | 3F | [ ] | — |
| └─ `design` command (full) | 3F | [ ] | wetwire-core |
| **Test Command (Persona-based)** | | | |
| ├─ Persona selection | 3G | [ ] | wetwire-core |
| ├─ Scenario configuration | 3G | [ ] | — |
| ├─ Result writing | 3G | [ ] | — |
| ├─ Session tracking | 3G | [ ] | — |
| └─ `test` command (full) | 3G | [ ] | wetwire-core |
| **Reference Example Testing** | | | |
| ├─ Fetch starter-workflows | 4A | [ ] | Schema Fetching |
| ├─ Import/rebuild cycle tests | 4A | [ ] | Import, Build |
| ├─ Round-trip validation | 4A | [ ] | Import, Build, Validate |
| └─ Success rate tracking | 4A | [ ] | — |
| **wetwire-core Integration** | | | |
| ├─ RunnerAgent tool definitions | 4B | [ ] | All CLI commands |
| ├─ Tool handlers implementation | 4B | [ ] | — |
| ├─ Stream handler support | 4B | [ ] | — |
| ├─ Session result writing | 4B | [ ] | — |
| ├─ Scoring integration | 4B | [ ] | — |
| └─ Agent testing with personas | 4B | [ ] | — |
| **Dependabot Types** | | | |
| ├─ Dependabot dataclass | 5A | [ ] | — |
| ├─ Update dataclass | 5A | [ ] | — |
| ├─ Schedule dataclass | 5A | [ ] | — |
| ├─ PackageEcosystem enum | 5A | [ ] | — |
| ├─ Registries dataclass | 5A | [ ] | — |
| ├─ Groups dataclass | 5A | [ ] | — |
| └─ contracts (Dependabot) | 5A | [ ] | — |
| **Dependabot Schema** | | | |
| ├─ Fetch dependabot-2.0.json | 5A | [ ] | — |
| ├─ Parse dependabot schema | 5A | [ ] | — |
| └─ Dependabot → YAML serialization | 5A | [ ] | — |
| **Dependabot CLI** | | | |
| ├─ `build --type dependabot` | 5A | [ ] | Dependabot Types |
| ├─ `import --type dependabot` | 5A | [ ] | Dependabot Types |
| ├─ `validate --type dependabot` | 5A | [ ] | — |
| └─ AST discovery for Dependabot | 5A | [ ] | Dependabot Types |
| **Issue Template Types** | | | |
| ├─ IssueTemplate dataclass | 5B | [ ] | — |
| ├─ FormBody dataclass | 5B | [ ] | — |
| ├─ FormElement protocol | 5B | [ ] | — |
| ├─ Input element | 5B | [ ] | — |
| ├─ Textarea element | 5B | [ ] | — |
| ├─ Dropdown element | 5B | [ ] | — |
| ├─ Checkboxes element | 5B | [ ] | — |
| ├─ Markdown element | 5B | [ ] | — |
| └─ contracts (IssueTemplate) | 5B | [ ] | — |
| **Issue Template Schema** | | | |
| ├─ Fetch github-issue-forms.json | 5B | [ ] | — |
| ├─ Parse issue forms schema | 5B | [ ] | — |
| └─ IssueTemplate → YAML serialization | 5B | [ ] | — |
| **Issue Template CLI** | | | |
| ├─ `build --type issue-template` | 5B | [ ] | IssueTemplate Types |
| ├─ `import --type issue-template` | 5B | [ ] | IssueTemplate Types |
| ├─ `validate --type issue-template` | 5B | [ ] | — |
| └─ AST discovery for IssueTemplate | 5B | [ ] | IssueTemplate Types |
| **Discussion Template Types** | | | |
| ├─ DiscussionTemplate dataclass | 5C | [ ] | FormBody (from 5B) |
| └─ Discussion category handling | 5C | [ ] | — |
| **Discussion Template CLI** | | | |
| ├─ `build --type discussion-template` | 5C | [ ] | DiscussionTemplate Types |
| └─ `import --type discussion-template` | 5C | [ ] | DiscussionTemplate Types |

---

## Phased Implementation

### Phase 1: Foundation (Parallel Streams)

All Phase 1 work streams can be developed **in parallel** with no dependencies on each other.

```
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: Foundation                                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │     1A       │  │     1B       │  │     1C       │  │     1D       │ │
│  │  Core Types  │  │ Serialization│  │     CLI      │  │Schema Fetch  │ │
│  │              │  │              │  │  Framework   │  │              │ │
│  │  workflow/   │  │  serialize/  │  │    cli/      │  │  codegen/    │ │
│  │  *.py        │  │              │  │              │  │  fetch.py    │ │
│  │              │  │              │  │              │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ │
│         │                 │                 │                 │         │
│         │                 │                 │                 │         │
│         ▼                 ▼                 ▼                 ▼         │
│    No deps           Needs 1A          No deps           No deps       │
│                      (can stub)                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Phase 2: Core Capabilities (Parallel Streams)

Phase 2 streams have dependencies on Phase 1 but are **parallel to each other**.

### Phase 3: Command Integration (Parallel Streams)

Phase 3 integrates Phase 2 capabilities into CLI commands.

### Phase 4: Polish & Integration

Reference example testing and wetwire-core integration.

### Phase 5: Extended Config Types

Dependabot, Issue Templates, Discussion Templates.

---

## Progress Tracking

### Phase 1 Progress
- [ ] 1A: Core Types (0/12)
- [ ] 1B: Serialization (0/10)
- [ ] 1C: CLI Framework (0/12)
- [ ] 1D: Schema Fetching (0/10)

### Phase 2 Progress
- [ ] 2A: Schema Parsing (0/3)
- [ ] 2B: Action Codegen (0/10)
- [ ] 2C: AST Discovery (0/7)
- [ ] 2D: Actionlint Integration (0/2)
- [ ] 2E: Linter Rules (0/12)
- [ ] 2F: YAML Parser (0/4)
- [ ] 2G: Runner/Value Extraction (0/4)
- [ ] 2H: Template Builder (0/3)

### Phase 3 Progress
- [ ] 3A: Build Command (0/7)
- [ ] 3B: Validate Command (0/1)
- [ ] 3C: Lint Command (0/1)
- [ ] 3D: Import Command (0/15)
- [ ] 3E: List Command (0/3)
- [ ] 3F: Design Command (0/5)
- [ ] 3G: Test Command (0/5)
- [ ] 3H: Graph Command (0/5)

### Phase 4 Progress
- [ ] 4A: Reference Example Testing (0/4)
- [ ] 4B: wetwire-core Integration (0/6)

### Phase 5 Progress
- [ ] 5A: Dependabot (0/13)
- [ ] 5B: Issue Templates (0/14)
- [ ] 5C: Discussion Templates (0/4)

---

## Critical Path

The minimum sequence to reach a working `build` command:

```
1A (Core Types) → 1B (Serialization) ─┐
                                      ├→ 2C (AST Discovery) → 2G (Runner) ─┐
                                      │                      2H (Template) ┼→ 3A (build)
                                      └────────────────────────────────────┘
```

The minimum sequence to reach a working `import` command:

```
1A (Core Types) ─┐
                 ├→ 3D (import)
2F (YAML Parser) ┘
```

---

## Feature Count Summary

| Phase | Streams | Features |
|-------|---------|----------|
| Phase 1 | 4 | 44 |
| Phase 2 | 8 | 45 |
| Phase 3 | 8 | 42 |
| Phase 4 | 2 | 10 |
| Phase 5 | 3 | 31 |
| **Total** | **25** | **172** |
