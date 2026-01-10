# Import Workflow Guide

This guide explains how to use the `wetwire-github import` command to convert existing GitHub Actions YAML workflows to typed Python declarations.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Command Options](#command-options)
- [Conversion Process](#conversion-process)
- [Supported YAML Features](#supported-yaml-features)
- [Examples](#examples)
- [Edge Cases and Limitations](#edge-cases-and-limitations)
- [Round-Trip Testing](#round-trip-testing)
- [Project Scaffolding](#project-scaffolding)
- [Advanced Usage](#advanced-usage)

---

## Overview

The import command converts existing GitHub Actions workflow YAML files into typed Python code using wetwire-github's declarative API. This is useful for:

- **Migrating existing workflows** to wetwire-github
- **Learning the API** by seeing how YAML maps to Python
- **Bootstrapping new projects** from templates or examples
- **Refactoring complex workflows** into maintainable Python code

The importer parses YAML into an intermediate representation (IR), then generates clean, idiomatic Python code that follows wetwire-github best practices.

---

## Quick Start

Convert a single workflow file:

```bash
# Import existing workflow
wetwire-github import .github/workflows/ci.yml

# Generated files:
#   ci/
#   ├── pyproject.toml
#   ├── .gitignore
#   └── ci.py
```

Import multiple workflows:

```bash
# Import all workflows
wetwire-github import .github/workflows/*.yml

# Generated files (one per workflow):
#   ci/
#   ├── pyproject.toml
#   ├── .gitignore
#   ├── ci.py
#   ├── release.py
#   └── deploy.py
```

---

## Command Options

```bash
wetwire-github import [OPTIONS] FILES...
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--output PATH` | `-o` | Output directory for generated Python code (default: `ci/`) |
| `--single-file` | | Generate all workflows in a single `workflows.py` file |
| `--no-scaffold` | | Skip project scaffolding (pyproject.toml, .gitignore) |
| `--type TYPE` | `-t` | Config type: `workflow`, `dependabot`, or `issue-template` |

### Examples

```bash
# Import to specific directory
wetwire-github import .github/workflows/ci.yml -o my-workflows/

# Import all workflows into single file
wetwire-github import .github/workflows/*.yml --single-file

# Import without scaffolding (code only)
wetwire-github import .github/workflows/ci.yml --no-scaffold

# Import Dependabot configuration
wetwire-github import .github/dependabot.yml --type dependabot
```

---

## Conversion Process

The import command follows these steps:

1. **Parse YAML** - Load and validate workflow YAML using PyYAML
2. **Create IR** - Convert to intermediate representation (IRWorkflow, IRJob, IRStep)
3. **Analyze Structure** - Detect triggers, jobs, steps, and dependencies
4. **Generate Imports** - Determine needed classes (Workflow, Job, Step, Triggers)
5. **Generate Code** - Create Python declarations with proper formatting
6. **Write Files** - Save to output directory with scaffolding

### Intermediate Representation (IR)

The importer uses three main IR classes:

- **IRWorkflow** - Top-level workflow with name, triggers, jobs
- **IRJob** - Job definition with runs-on, steps, needs, env
- **IRStep** - Individual step with run/uses, with, env, if

These IR classes preserve all information from the YAML while normalizing the structure for code generation.

---

## Supported YAML Features

### Workflows

- ✅ Workflow name
- ✅ Trigger configuration (on)
- ✅ Environment variables (env)
- ✅ Permissions
- ✅ Concurrency
- ✅ Defaults

### Jobs

- ✅ Job name and ID
- ✅ Runner specification (runs-on)
- ✅ Job dependencies (needs)
- ✅ Conditional execution (if)
- ✅ Environment variables (env)
- ✅ Strategy and matrix
- ✅ Container configuration
- ✅ Service containers
- ✅ Job outputs
- ✅ Timeout settings
- ✅ Continue on error

### Steps

- ✅ Step name and ID
- ✅ Action references (uses)
- ✅ Shell commands (run)
- ✅ Action inputs (with)
- ✅ Environment variables (env)
- ✅ Conditional execution (if)
- ✅ Shell specification
- ✅ Working directory
- ✅ Timeout settings
- ✅ Continue on error

### Triggers

- ✅ push (branches, tags, paths)
- ✅ pull_request (branches, types)
- ✅ pull_request_target
- ✅ workflow_dispatch
- ✅ workflow_call
- ✅ workflow_run
- ✅ schedule (cron)
- ✅ release
- ✅ issues
- ✅ issue_comment
- ✅ create
- ✅ delete

---

## Examples

### Example 1: Basic CI Workflow

**Input YAML (.github/workflows/ci.yml):**
```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: pytest
```

**Command:**
```bash
wetwire-github import .github/workflows/ci.yml -o ci/
```

**Generated Python (ci/ci.py):**
```python
from wetwire_github.workflow import (
    Job,
    PullRequestTrigger,
    PushTrigger,
    Step,
    Triggers,
    Workflow,
)

ci = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger(branches=["main"]), pull_request=PullRequestTrigger(branches=["main"])),
    jobs={
        "test": Job(runs_on="ubuntu-latest", steps=[
            Step(uses="actions/checkout@v4"),
            Step(name="Run tests", run="pytest"),
        ]),
    },
)
```

### Example 2: Matrix Build

**Input YAML:**
```yaml
name: Test Matrix
on: push

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
        os: [ubuntu-latest, macos-latest]
      fail-fast: false
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - run: pytest
```

**Generated Python:**
```python
from wetwire_github.workflow import (
    Job,
    PushTrigger,
    Step,
    Triggers,
    Workflow,
)

test_matrix = Workflow(
    name="Test Matrix",
    on=Triggers(push=PushTrigger()),
    jobs={
        "test": Job(
            runs_on="ubuntu-latest",
            strategy={
                "matrix": {
                    "python-version": ["3.10", "3.11", "3.12"],
                    "os": ["ubuntu-latest", "macos-latest"]
                },
                "fail-fast": False
            },
            steps=[
                Step(uses="actions/checkout@v4"),
                Step(uses="actions/setup-python@v4", with_={"python_version": "${{ matrix.python-version }}"}),
                Step(run="pytest"),
            ]
        ),
    },
)
```

### Example 3: Multi-Job Pipeline

**Input YAML:**
```yaml
name: CI/CD
on: push

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make build

  test:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - run: make test

  deploy:
    runs-on: ubuntu-latest
    needs: [build, test]
    if: github.ref == 'refs/heads/main'
    steps:
      - run: make deploy
```

**Generated Python:**
```python
from wetwire_github.workflow import (
    Job,
    PushTrigger,
    Step,
    Triggers,
    Workflow,
)

ci_cd = Workflow(
    name="CI/CD",
    on=Triggers(push=PushTrigger()),
    jobs={
        "build": Job(runs_on="ubuntu-latest", steps=[
            Step(uses="actions/checkout@v4"),
            Step(run="make build"),
        ]),
        "test": Job(runs_on="ubuntu-latest", needs=["build"], steps=[
            Step(run="make test"),
        ]),
        "deploy": Job(
            runs_on="ubuntu-latest",
            needs=["build", "test"],
            if_="github.ref == 'refs/heads/main'",
            steps=[
                Step(run="make deploy"),
            ]
        ),
    },
)
```

### Example 4: Environment Variables and Secrets

**Input YAML:**
```yaml
name: Deploy
on:
  push:
    tags: ["v*.*.*"]

env:
  NODE_ENV: production

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy
        run: ./deploy.sh
        env:
          API_KEY: ${{ secrets.API_KEY }}
          AWS_REGION: us-east-1
```

**Generated Python:**
```python
from wetwire_github.workflow import (
    Job,
    PushTrigger,
    Step,
    Triggers,
    Workflow,
)

deploy = Workflow(
    name="Deploy",
    on=Triggers(push=PushTrigger(tags=["v*.*.*"])),
    env={"NODE_ENV": "production"},
    jobs={
        "deploy": Job(runs_on="ubuntu-latest", steps=[
            Step(uses="actions/checkout@v4"),
            Step(
                name="Deploy",
                run="./deploy.sh",
                env={
                    "API_KEY": "${{ secrets.API_KEY }}",
                    "AWS_REGION": "us-east-1"
                }
            ),
        ]),
    },
)
```

### Example 5: Multiple Workflows in Single File

**Command:**
```bash
wetwire-github import .github/workflows/ci.yml .github/workflows/release.yml --single-file -o ci/
```

**Generated Python (ci/workflows.py):**
```python
from wetwire_github.workflow import (
    Job,
    PushTrigger,
    ReleaseTrigger,
    Step,
    Triggers,
    Workflow,
)

ci = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger(branches=["main"])),
    jobs={
        "test": Job(runs_on="ubuntu-latest", steps=[
            Step(run="pytest"),
        ]),
    },
)

release = Workflow(
    name="Release",
    on=Triggers(release=ReleaseTrigger()),
    jobs={
        "publish": Job(runs_on="ubuntu-latest", steps=[
            Step(run="make publish"),
        ]),
    },
)
```

---

## Edge Cases and Limitations

### Reserved Python Keywords

The importer automatically handles Python reserved keywords by appending underscores:

- `with` → `with_`
- `if` → `if_`

**YAML:**
```yaml
steps:
  - uses: actions/checkout@v4
    with:
      fetch-depth: 0
    if: github.event_name == 'push'
```

**Python:**
```python
Step(
    uses="actions/checkout@v4",
    with_={"fetch_depth": 0},
    if_="github.event_name == 'push'"
)
```

### Kebab-Case to Snake-Case

The importer converts kebab-case keys to snake_case:

- `fetch-depth` → `fetch_depth`
- `python-version` → `python_version`
- `working-directory` → `working_directory`

### Multiline Strings

Multiline run commands are preserved using triple-quoted strings:

**YAML:**
```yaml
steps:
  - run: |
      echo "Building..."
      make build
      echo "Done"
```

**Python:**
```python
Step(run="""echo "Building..."
make build
echo "Done"
""")
```

### String Escaping

Special characters in strings are properly escaped:

- Quotes: `"` → `\"`
- Backslashes: `\` → `\\`
- Newlines: `\n` → `\\n`

### Unsupported Features

The following features are parsed but may not generate optimal Python code:

- **Complex matrix configurations** - Include/exclude patterns are preserved as dicts
- **Reusable workflows** - `uses` in jobs is preserved but not yet converted to typed calls
- **Composite actions** - Local action definitions are not imported
- **Advanced expressions** - GitHub expression syntax is preserved as strings

To improve generated code for these features, use the `lint` command after import:

```bash
wetwire-github import .github/workflows/ci.yml
wetwire-github lint ci/ --fix
```

### YAML 1.1 Quirks

The importer handles YAML 1.1 quirks:

- `on: true` - The keyword `on` may be parsed as boolean `True` in YAML 1.1
- Solution: The importer checks both `data.get("on")` and `data.get(True)`

---

## Round-Trip Testing

After importing, you can verify the conversion by building and comparing:

### Step 1: Import Existing Workflow

```bash
# Import existing workflow
wetwire-github import .github/workflows/ci.yml -o ci/
```

### Step 2: Build Python to YAML

```bash
# Generate YAML from Python
wetwire-github build ci/ -o .github/workflows-new/
```

### Step 3: Compare

```bash
# Compare original and regenerated YAML
diff .github/workflows/ci.yml .github/workflows-new/ci.yml
```

### Expected Differences

The regenerated YAML may differ from the original in these ways:

1. **Formatting** - Different indentation, quote styles, line breaks
2. **Key ordering** - Dict keys may be in different order
3. **Normalization** - Shorthand syntax expanded (e.g., `on: push` → `on:\n  push: {}`)
4. **Comments** - YAML comments are not preserved

These differences are **semantic equivalents** - the workflows will behave identically.

### Functional Testing

The most reliable verification is functional testing:

```bash
# Import workflow
wetwire-github import .github/workflows/ci.yml -o ci/

# Build new YAML
wetwire-github build ci/

# Validate with actionlint
wetwire-github validate .github/workflows/ci.yml

# Run in GitHub Actions
git commit -am "Migrate to wetwire-github"
git push
# Observe workflow runs in GitHub Actions UI
```

---

## Project Scaffolding

By default, the import command creates a complete project structure:

```
ci/
├── pyproject.toml     # Project configuration
├── .gitignore         # Python gitignore
└── ci.py              # Generated workflow code
```

### pyproject.toml

Generated project configuration:

```toml
[project]
name = "my-workflows"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "wetwire-github>=0.1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

You can customize this after generation:

- Change project name
- Add additional dependencies
- Configure development tools
- Set up uv or other package managers

### .gitignore

Generated gitignore for Python projects:

```
__pycache__/
*.py[cod]
.venv/
.env
```

### Skip Scaffolding

If you're importing into an existing project:

```bash
wetwire-github import .github/workflows/ci.yml --no-scaffold
```

This generates only Python code without project files.

---

## Advanced Usage

### Import to Existing Package

Import workflows into an existing Python package:

```bash
# Your existing project structure
my-project/
├── pyproject.toml
├── src/
└── ci/
    ├── __init__.py
    └── jobs.py

# Import workflows into ci/ package
wetwire-github import .github/workflows/*.yml -o ci/ --no-scaffold
```

### Incremental Refactoring

Import, then refactor to use best practices:

```bash
# Step 1: Import
wetwire-github import .github/workflows/ci.yml -o ci/

# Step 2: Lint to find improvements
wetwire-github lint ci/

# Step 3: Apply auto-fixes
wetwire-github lint ci/ --fix

# Step 4: Manual refactoring
# - Extract reusable jobs to ci/jobs.py
# - Extract common steps to ci/steps.py
# - Use typed action wrappers
# - Use expression helpers
```

Example refactoring:

**Generated code:**
```python
Step(uses="actions/checkout@v4")
Step(uses="actions/setup-python@v4", with_={"python_version": "3.11"})
```

**Refactored with action wrappers:**
```python
from wetwire_github.actions import checkout, setup_python

checkout()
setup_python(python_version="3.11")
```

### Batch Import with Script

Import many workflows programmatically:

```python
from pathlib import Path
from wetwire_github.cli.import_cmd import import_workflows

# Find all workflow files
workflow_dir = Path(".github/workflows")
yaml_files = [str(f) for f in workflow_dir.glob("*.yml")]

# Import all workflows
exit_code, messages = import_workflows(
    file_paths=yaml_files,
    output_dir="ci",
    single_file=False,
    no_scaffold=False,
)

for msg in messages:
    print(msg)
```

### Import from Remote Repositories

Import workflows from GitHub repositories:

```bash
# Download workflow
curl -o ci.yml https://raw.githubusercontent.com/user/repo/main/.github/workflows/ci.yml

# Import
wetwire-github import ci.yml -o ci/

# Clean up
rm ci.yml
```

### Import Dependabot Configuration

Import Dependabot configuration:

```bash
wetwire-github import .github/dependabot.yml --type dependabot -o ci/
```

Note: Dependabot import support is experimental. Check generated code carefully.

### Import Issue Templates

Import GitHub issue templates:

```bash
wetwire-github import .github/ISSUE_TEMPLATE/*.yml --type issue-template -o ci/
```

---

## Best Practices

### 1. Review Generated Code

Always review generated code before committing:

```bash
wetwire-github import .github/workflows/ci.yml -o ci/
cat ci/ci.py  # Review generated code
```

### 2. Run Linter

Check for potential improvements:

```bash
wetwire-github import .github/workflows/ci.yml -o ci/
wetwire-github lint ci/
```

### 3. Test Before Replacing

Build and validate before replacing original workflows:

```bash
# Import
wetwire-github import .github/workflows/ci.yml -o ci/

# Build to temp directory
wetwire-github build ci/ -o .github/workflows-test/

# Validate
wetwire-github validate .github/workflows-test/ci.yml

# Test in PR before merging
```

### 4. Preserve Original YAML

Keep original YAML files as reference:

```bash
# Backup originals
cp -r .github/workflows .github/workflows.backup

# Import
wetwire-github import .github/workflows/*.yml -o ci/

# Keep backups until confident
```

### 5. Incremental Migration

Migrate workflows one at a time:

```bash
# Migrate CI first
wetwire-github import .github/workflows/ci.yml -o ci/
wetwire-github build ci/
# Test, iterate, commit

# Then migrate release
wetwire-github import .github/workflows/release.yml -o ci/
wetwire-github build ci/
# Test, iterate, commit
```

---

## Troubleshooting

### Import Fails with Parse Error

**Problem:** YAML syntax error

**Solution:**
```bash
# Validate YAML first
yamllint .github/workflows/ci.yml

# Or use actionlint
actionlint .github/workflows/ci.yml
```

### Generated Code Has Syntax Errors

**Problem:** Invalid Python generated

**Solution:**
```bash
# Check Python syntax
python -m py_compile ci/ci.py

# Report issue if reproducible
```

### Generated Code Doesn't Match Original Behavior

**Problem:** Semantic difference in conversion

**Solution:**
1. Build YAML from Python: `wetwire-github build ci/`
2. Compare with diff: `diff .github/workflows/ci.yml .github/workflows/ci.yml`
3. Test both in GitHub Actions
4. Report issue if confirmed

### Import Creates Too Many Files

**Problem:** Want single file instead of multiple

**Solution:**
```bash
# Use --single-file flag
wetwire-github import .github/workflows/*.yml --single-file -o ci/
```

### Import Clutters Directory

**Problem:** Don't want scaffolding files

**Solution:**
```bash
# Use --no-scaffold flag
wetwire-github import .github/workflows/ci.yml --no-scaffold -o ci/
```

---

## See Also

- [CLI Reference](CLI.md) - Full command documentation
- [Examples](EXAMPLES.md) - Workflow examples
- [Quick Start](QUICK_START.md) - Getting started guide
- [Lint Rules](LINT_RULES.md) - Code quality rules to apply after import
- [Wetwire Specification](https://github.com/lex00/wetwire/blob/main/docs/WETWIRE_SPEC.md) - Core patterns
