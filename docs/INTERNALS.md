# Internals

This document covers the internal architecture of wetwire-github for contributors and maintainers.

**Contents:**
- [Package Architecture](#package-architecture) - Module organization
- [Discovery Pipeline](#discovery-pipeline) - AST-based resource discovery
- [Serialization Process](#serialization-process) - Python to YAML conversion
- [Expression Handling](#expression-handling) - GitHub context expressions
- [Template Building](#template-building) - Topological sorting and job ordering
- [Linter Framework](#linter-framework) - WAG rules architecture
- [Extension Points](#extension-points) - How to extend the system

---

## Package Architecture

wetwire-github is organized into focused modules with clear responsibilities:

```
src/wetwire_github/
├── workflow/           # Core dataclass types
│   ├── workflow.py     # Workflow class
│   ├── job.py          # Job class
│   ├── step.py         # Step class
│   ├── triggers.py     # 30+ trigger types (push, pull_request, etc.)
│   ├── matrix.py       # Matrix and Strategy classes
│   ├── expressions.py  # Expression builders and context accessors
│   └── types.py        # Supporting types (Permissions, Container, etc.)
├── actions/            # Typed action wrapper functions
├── serialize/          # Python dataclass to YAML conversion
├── discover/           # AST-based resource discovery
├── runner/             # Module loading and value extraction
├── template/           # Topological sorting for job dependencies
├── linter/             # WAG001-WAG008 lint rules
├── validation/         # actionlint subprocess integration
├── importer/           # YAML to Python IR conversion
├── dependabot/         # Dependabot configuration types
├── issue_templates/    # GitHub Issue Forms types
├── discussion_templates/  # Discussion template types
├── core_integration/   # wetwire-core AI integration
└── cli/                # Command implementations
```

### Module Dependencies

```
CLI Commands
    │
    ├── build ──────────┬──> discover ──> runner ──> template ──> serialize
    │                   │
    ├── lint ───────────┴──> linter/rules
    │
    ├── validate ───────────> validation (actionlint)
    │
    └── import ─────────────> importer
```

---

## Discovery Pipeline

The discovery system uses Python's AST module to find `Workflow` and `Job` definitions without importing the source files.

### How It Works

```python
from wetwire_github.discover import discover_in_directory, DiscoveredResource

# Scan a package directory
resources = discover_in_directory("ci/")
# Returns: [DiscoveredResource(name="ci_workflow", type="Workflow", ...)]
```

The pipeline:
1. **Parse** - AST parses each `.py` file
2. **Visit** - `ResourceVisitor` walks the AST looking for assignments
3. **Track Imports** - Records `from wetwire_github.workflow import Workflow` aliases
4. **Match Calls** - Identifies `Workflow(...)` and `Job(...)` instantiations
5. **Extract Dependencies** - Collects variable references from call arguments

### ResourceVisitor Implementation

```python
class ResourceVisitor(ast.NodeVisitor):
    """AST visitor that discovers Workflow and Job assignments."""

    def visit_ImportFrom(self, node):
        """Track imports from wetwire_github.workflow."""
        # Records: WF -> Workflow, MyJob -> Job, etc.

    def visit_Assign(self, node):
        """Check assignments for Workflow/Job instantiations."""
        # Matches: ci = Workflow(...) or build_job = Job(...)

    def _extract_dependencies(self, call):
        """Extract variable references from call arguments."""
        # Finds: Job(steps=[checkout_step, build_step])
        #        -> dependencies: ["checkout_step", "build_step"]
```

### Dependency Graph

The discovery module can build a dependency graph:

```python
from wetwire_github.discover import build_dependency_graph

resources = discover_in_directory("ci/")
graph = build_dependency_graph(resources)
# Returns: {"ci_workflow": ["build_job", "test_job"], "build_job": [], ...}
```

This is used for:
- Detecting circular dependencies
- Ordering resources for serialization
- Validating references

---

## Serialization Process

The serializer converts Python dataclasses to GitHub Actions YAML.

### Conversion Pipeline

```python
from wetwire_github.serialize import to_dict, to_yaml

workflow = Workflow(name="CI", jobs={"build": build_job})

# Step 1: Convert to dictionary
data = to_dict(workflow)  # {"name": "CI", "jobs": {"build": {...}}}

# Step 2: Convert to YAML string
yaml_str = to_yaml(workflow)
```

### Field Name Conversion

The serializer handles several transformations:

| Python Field | YAML Field | Rule |
|-------------|------------|------|
| `working_directory` | `working-directory` | snake_case to kebab-case |
| `if_` | `if` | Reserved keyword suffix removal |
| `with_` | `with` | Reserved keyword suffix removal |
| `pull_request` | `pull_request` | Preserved (GitHub event name) |

```python
# Preserved field names (GitHub event names)
_PRESERVE_SNAKE_CASE = {
    "pull_request", "pull_request_target", "workflow_dispatch",
    "workflow_call", "workflow_run", "repository_dispatch", ...
}
```

### Empty Value Handling

The serializer omits empty values but preserves meaningful ones:

```python
def _is_empty(value):
    """Check if a value should be omitted."""
    # Omitted: None, "", [], {}
    # Preserved: False, 0, empty dataclass instances
```

### Matrix Flattening

Matrix configurations are flattened specially:

```python
# Input
Matrix(values={"python": ["3.10", "3.11"]}, include=[{"python": "3.12"}])

# Output (flattened)
{"python": ["3.10", "3.11"], "include": [{"python": "3.12"}]}
```

### Multiline String Handling

Multiline strings use YAML literal block scalar style:

```python
Step(run="echo hello\necho world")
# Produces:
#   run: |
#     echo hello
#     echo world
```

---

## Expression Handling

The expressions module provides type-safe builders for GitHub Actions expressions.

### Expression Class

```python
class Expression(str):
    """Wraps a GitHub Actions expression string."""

    def __str__(self):
        return f"${{{{ {super().__str__()} }}}}"

    def and_(self, other):
        return Expression(f"({self}) && ({other})")

    def or_(self, other):
        return Expression(f"({self}) || ({other})")

    def not_(self):
        return Expression(f"!({self})")
```

### Context Accessors

Pre-built context accessors for common patterns:

```python
# Secrets context
Secrets.get("TOKEN")  # -> ${{ secrets.TOKEN }}

# Matrix context
Matrix.get("python")  # -> ${{ matrix.python }}

# GitHub context (pre-defined properties)
GitHub.ref           # -> ${{ github.ref }}
GitHub.sha           # -> ${{ github.sha }}
GitHub.actor         # -> ${{ github.actor }}

# Needs context (job dependencies)
Needs.output("build", "artifact")  # -> ${{ needs.build.outputs.artifact }}
Needs.result("build")              # -> ${{ needs.build.result }}

# Steps context
Steps.output("test", "coverage")   # -> ${{ steps.test.outputs.coverage }}
Steps.outcome("test")              # -> ${{ steps.test.outcome }}
```

### Condition Builders

Helper functions for common conditions:

```python
from wetwire_github.workflow.expressions import always, failure, success, branch

# Status functions
Step(if_=str(always()))   # -> if: ${{ always() }}
Step(if_=str(failure()))  # -> if: ${{ failure() }}

# Branch/tag matching
Step(if_=str(branch("main")))  # -> if: ${{ github.ref == 'refs/heads/main' }}
```

### Combining Expressions

```python
# Compound conditions
condition = GitHub.ref.eq("refs/heads/main").and_(success())
# -> (github.ref == 'refs/heads/main') && (success())
```

---

## Template Building

The template module handles topological sorting of jobs based on their `needs` dependencies.

### Topological Sort (Kahn's Algorithm)

```python
from wetwire_github.template import topological_sort, CycleError

graph = {
    "deploy": ["test", "build"],  # deploy needs test and build
    "test": ["build"],            # test needs build
    "build": [],                  # build has no dependencies
}

order = topological_sort(graph)
# Returns: ["build", "test", "deploy"]
```

### Algorithm Steps

1. Build in-degree map (count of incoming edges)
2. Initialize queue with nodes having zero in-degree
3. Process queue: remove node, add to result, decrease in-degree of dependents
4. If nodes remain unprocessed, a cycle exists

### Cycle Detection

```python
from wetwire_github.template import detect_cycles

graph = {"a": ["b"], "b": ["c"], "c": ["a"]}  # Circular
cycles = detect_cycles(graph)
# Returns: [["a", "b", "c", "a"]]
```

### Job Ordering

```python
from wetwire_github.template import order_jobs

jobs = {
    "deploy": Job(needs=["test"]),
    "test": Job(needs=["build"]),
    "build": Job(),
}

ordered = order_jobs(jobs)
# Returns: [("build", Job), ("test", Job), ("deploy", Job)]
```

---

## Linter Framework

The linter checks workflow Python code against best practices (WAG = Workflow Actions Guidelines).

### Rule Architecture

```python
from wetwire_github.linter import Rule, BaseRule, LintError

class WAG001TypedActionWrappers(BaseRule):
    """WAG001: Use typed action wrappers instead of raw strings."""

    @property
    def id(self) -> str:
        return "WAG001"

    @property
    def description(self) -> str:
        return "Use typed action wrappers instead of raw 'uses' strings"

    def check(self, source: str, file_path: str) -> list[LintError]:
        # Parse AST and check for Step(uses="actions/checkout@v4")
        # Should use: checkout() wrapper instead
```

### Fixable Rules

Rules can implement auto-fix:

```python
class FixableRule(Protocol):
    def fix(self, source: str, file_path: str) -> tuple[str, int, list[LintError]]:
        """Apply fixes and return (fixed_source, fixed_count, remaining_errors)."""
```

Example: WAG003 auto-replaces `${{ secrets.TOKEN }}` with `Secrets.get("TOKEN")`.

### Rule Summary

| Rule | Description | Fixable |
|------|-------------|---------|
| WAG001 | Use typed action wrappers | No |
| WAG002 | Use condition builders | No |
| WAG003 | Use Secrets.get() for secrets | Yes |
| WAG004 | Use Matrix class for matrices | No |
| WAG005 | Extract repeated env variables | No |
| WAG006 | No duplicate workflow names | No |
| WAG007 | File has too many jobs | No |
| WAG008 | No hardcoded expressions | No |

### Linter API

```python
from wetwire_github.linter import Linter, lint_file, lint_directory

# Lint a single file
result = lint_file("ci/workflows.py")
print(result.errors)

# Lint with auto-fix
linter = Linter()
fix_result = linter.fix(source, "workflows.py")
print(f"Fixed {fix_result.fixed_count} issues")
```

---

## Extension Points

### Adding New Action Wrappers

Action wrappers are functions that return `Step` objects:

```python
# src/wetwire_github/actions/my_action.py

from wetwire_github.workflow import Step

def my_action(
    input1: str | None = None,
    input2: str | None = None,
) -> Step:
    """My custom action wrapper.

    Args:
        input1: First input parameter
        input2: Second input parameter

    Returns:
        Step configured to use this action
    """
    with_dict = {
        "input-1": input1,
        "input-2": input2,
    }
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="org/my-action@v1",
        with_=with_dict if with_dict else None,
    )
```

### Adding New Lint Rules

1. Create a class extending `BaseRule`:

```python
class WAG009MyRule(BaseRule):
    @property
    def id(self) -> str:
        return "WAG009"

    @property
    def description(self) -> str:
        return "Description of what the rule checks"

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        tree = ast.parse(source)
        # Walk AST and find issues
        return errors
```

2. Register in `get_default_rules()`:

```python
def get_default_rules() -> list[BaseRule]:
    return [
        WAG001TypedActionWrappers(),
        # ...
        WAG009MyRule(),
    ]
```

### Adding New Trigger Types

1. Define the trigger dataclass:

```python
@dataclass
class NewEventTrigger:
    """New event trigger."""
    types: list[str] | None = None
    # Add relevant fields
```

2. Add to the `Triggers` container:

```python
@dataclass
class Triggers:
    # ...
    new_event: NewEventTrigger | None = None
```

3. If the event name uses snake_case in YAML, add to `_PRESERVE_SNAKE_CASE` in serialize.py.

### Adding New Expression Contexts

```python
class CustomContext:
    """Accessor for custom context."""

    @staticmethod
    def get(name: str) -> Expression:
        """Get a value from custom context."""
        return Expression(f"custom.{name}")

# Module-level instance
Custom = CustomContext()
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `src/wetwire_github/discover/discover.py` | AST-based resource discovery |
| `src/wetwire_github/serialize/serialize.py` | Dataclass to YAML conversion |
| `src/wetwire_github/workflow/expressions.py` | Expression builders |
| `src/wetwire_github/template/template.py` | Topological sorting |
| `src/wetwire_github/linter/linter.py` | Linter framework |
| `src/wetwire_github/linter/rules.py` | WAG001-WAG008 rule implementations |
| `src/wetwire_github/runner/runner.py` | Module loading and extraction |
| `src/wetwire_github/importer/importer.py` | YAML to Python IR conversion |
| `src/wetwire_github/validation/validation.py` | actionlint integration |
| `src/wetwire_github/cli/build.py` | Build command implementation |
| `src/wetwire_github/cli/main.py` | CLI entry point and command dispatch |

---

## See Also

- [CLAUDE.md](../CLAUDE.md) - Syntax principles and usage examples
- [docs/FAQ.md](FAQ.md) - Frequently asked questions
