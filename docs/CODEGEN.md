# Code Generation Guide

This document explains the code generation pipeline used to create typed Python wrappers for GitHub Actions.

**Contents:**
- [Overview](#overview) - Architecture and purpose
- [Pipeline Stages](#pipeline-stages) - Fetch, parse, generate workflow
- [Adding New Actions](#adding-new-actions) - Step-by-step guide
- [Generated Code Structure](#generated-code-structure) - Understanding the output
- [Regenerating Wrappers](#regenerating-wrappers) - Updating from upstream
- [Customization](#customization) - Extending the generator

---

## Overview

The code generation system automatically creates type-safe Python wrappers for popular GitHub Actions by parsing their `action.yml` metadata files.

### Purpose

Instead of manually writing:

```python
Step(
    uses="actions/checkout@v4",
    with_={"fetch-depth": "0", "ref": "main"},
)
```

Users can write:

```python
checkout(fetch_depth="0", ref="main")
```

This provides:
- **Type safety** - Function signatures with typed parameters
- **IDE support** - Autocomplete and inline documentation
- **Validation** - Parameter names checked at Python parse time
- **Maintainability** - Wrappers stay in sync with action schemas

### Architecture

```
┌─────────────────┐
│   fetch.py      │  Download action.yml files from GitHub
│                 │
│ Input: Repo list│
│ Output: specs/  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   parse.py      │  Parse YAML into ActionSchema dataclasses
│                 │
│ Input: specs/   │
│ Output: Schema  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  generate.py    │  Generate Python wrapper functions
│                 │
│ Input: Schema   │
│ Output: .py     │
└─────────────────┘
```

### Directory Structure

```
wetwire-github-python/
├── codegen/                    # Code generation tools
│   ├── fetch.py                # Download action.yml files
│   ├── parse.py                # Parse YAML schemas
│   └── generate.py             # Generate Python wrappers
├── specs/                      # Downloaded schemas (gitignored)
│   ├── actions/                # action.yml files
│   │   ├── checkout.yml
│   │   ├── setup-python.yml
│   │   └── ...
│   ├── workflow-schema.json    # GitHub workflow JSON schema
│   ├── dependabot-schema.json  # Dependabot JSON schema
│   └── manifest.json           # Metadata about fetched files
└── src/wetwire_github/actions/ # Generated Python wrappers
    ├── __init__.py             # Exports all wrappers
    ├── checkout.py             # Generated checkout() function
    ├── setup_python.py         # Generated setup_python() function
    └── ...
```

---

## Pipeline Stages

### Stage 1: Fetch Schemas

**File:** `codegen/fetch.py`

Downloads `action.yml` files from GitHub repositories and JSON schemas from SchemaStore.

```bash
# Run the fetcher
uv run python -m codegen.fetch
```

**What it does:**

1. Downloads GitHub workflow JSON schema from SchemaStore
2. Downloads Dependabot JSON schema from SchemaStore
3. Downloads Issue Forms JSON schema from SchemaStore
4. Fetches `action.yml` files from configured GitHub repositories
5. Saves all files to `specs/` directory
6. Creates a `manifest.json` with fetch metadata

**Output:**

```
wetwire-github schema fetcher
========================================

Fetching workflow schema...
  ✓ workflow-schema.json
Fetching dependabot schema...
  ✓ dependabot-schema.json
Fetching issue-forms schema...
  ✓ issue-forms-schema.json
Fetching action.yml files...
  ✓ checkout.yml
  ✓ setup-python.yml
  ✓ setup-node.yml
  ...

Summary:
  Schemas: 3/3
  Actions: 8/8
```

**Configuration:**

Action repositories are configured in `fetch.py`:

```python
ACTION_REPOS = {
    "checkout": "actions/checkout",
    "setup-python": "actions/setup-python",
    "setup-node": "actions/setup-node",
    # Add more actions here
}
```

**Network Requirements:**

- Requires internet connection
- Uses retry logic with exponential backoff
- Adds User-Agent header: `wetwire-github/0.1.0`

---

### Stage 2: Parse Schemas

**File:** `codegen/parse.py`

Parses downloaded YAML and JSON files into Python dataclasses.

```bash
# Run the parser
uv run python -m codegen.parse
```

**What it does:**

1. Reads `action.yml` files from `specs/actions/`
2. Parses YAML into `ActionSchema` dataclasses
3. Extracts inputs, outputs, and metadata
4. (Optional) Parses workflow JSON schema

**Key Data Structures:**

```python
@dataclass
class ActionInput:
    """Parsed input from action.yml."""
    name: str
    description: str
    required: bool
    default: str | None

@dataclass
class ActionOutput:
    """Parsed output from action.yml."""
    name: str
    description: str

@dataclass
class ActionSchema:
    """Parsed action.yml schema."""
    name: str
    description: str
    author: str | None
    inputs: list[ActionInput]
    outputs: list[ActionOutput]
    branding: dict[str, str] | None
```

**Example Parsing:**

Given `action.yml`:

```yaml
name: 'Checkout'
description: 'Checkout a Git repository'
inputs:
  repository:
    description: 'Repository name with owner'
    default: ${{ github.repository }}
  fetch-depth:
    description: 'Number of commits to fetch'
    default: 1
```

Produces `ActionSchema`:

```python
ActionSchema(
    name="Checkout",
    description="Checkout a Git repository",
    inputs=[
        ActionInput(
            name="repository",
            description="Repository name with owner",
            required=False,
            default="${{ github.repository }}",
        ),
        ActionInput(
            name="fetch-depth",
            description="Number of commits to fetch",
            required=False,
            default="1",
        ),
    ],
    outputs=[],
)
```

---

### Stage 3: Generate Python Code

**File:** `codegen/generate.py`

Generates Python wrapper functions from parsed schemas.

```bash
# Run the generator
uv run python -m codegen.generate
```

**What it does:**

1. Reads parsed schemas from `specs/actions/`
2. Generates Python function for each action
3. Converts input names to Python identifiers (kebab-case → snake_case)
4. Builds function signatures with typed parameters
5. Generates docstrings from descriptions
6. Creates `with_` dictionary mapping Python names back to YAML names
7. Writes generated code to `src/wetwire_github/actions/`
8. Updates `__init__.py` with exports
9. Formats code with `ruff` if available

**Name Conversion:**

```python
def snake_case(name: str) -> str:
    """Convert kebab-case, camelCase, or UPPERCASE to snake_case."""
    # fetch-depth → fetch_depth
    # fetchDepth → fetch_depth
    # GITHUB_TOKEN → github_token
```

**Keyword Handling:**

Reserved Python keywords get a trailing underscore:

```python
def to_python_identifier(name: str) -> str:
    """Convert to valid Python identifier."""
    result = snake_case(name)

    # Handle reserved keywords
    if result in keyword.kwlist:
        result = f"{result}_"  # 'if' → 'if_'

    return result
```

**Generated Code Structure:**

Each action gets a standalone module with a single function:

```python
# src/wetwire_github/actions/checkout.py

"""Generated wrapper for Checkout."""

from wetwire_github.workflow import Step

def checkout(
    repository: str | None = None,
    ref: str | None = None,
    fetch_depth: str | None = None,
    # ... more parameters
) -> Step:
    """Checkout a Git repository at a particular version

    Args:
        repository: Repository name with owner. For example, actions/checkout
        ref: The branch, tag or SHA to checkout
        fetch_depth: Number of commits to fetch. 0 indicates all history

    Returns:
        Step configured to use this action
    """
    with_dict = {
        "repository": repository,
        "ref": ref,
        "fetch-depth": fetch_depth,  # Note: converted back to kebab-case
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="actions/checkout@v4",
        with_=with_dict if with_dict else None,
    )
```

**Package Initialization:**

The generator creates `__init__.py` with explicit imports:

```python
# src/wetwire_github/actions/__init__.py

"""Generated GitHub Action wrappers."""

from .cache import cache
from .checkout import checkout
from .download_artifact import download_artifact
from .setup_go import setup_go
from .setup_java import setup_java
from .setup_node import setup_node
from .setup_python import setup_python
from .upload_artifact import upload_artifact

__all__ = [
    'cache',
    'checkout',
    'download_artifact',
    'setup_go',
    'setup_java',
    'setup_node',
    'setup_python',
    'upload_artifact',
]
```

---

## Adding New Actions

Follow these steps to add a new action wrapper:

### Step 1: Add Action to Registry

Edit `codegen/fetch.py` and add your action to `ACTION_REPOS`:

```python
ACTION_REPOS = {
    "checkout": "actions/checkout",
    "setup-python": "actions/setup-python",
    # ... existing actions

    # Add your new action
    "codecov": "codecov/codecov-action",  # key: nickname, value: owner/repo
}
```

**Naming Guidelines:**

- Use lowercase, hyphenated names for the key
- Key will be converted to snake_case for the function name
- `setup-python` → `setup_python()`
- `codecov` → `codecov()`

### Step 2: Fetch the Schema

Run the fetch script to download the new action's `action.yml`:

```bash
uv run python -m codegen.fetch
```

This will download `specs/actions/codecov.yml`.

### Step 3: Generate the Wrapper

Run the generator to create the Python wrapper:

```bash
uv run python -m codegen.generate
```

This creates `src/wetwire_github/actions/codecov.py` and updates `__init__.py`.

### Step 4: Verify Generated Code

Check the generated wrapper:

```bash
cat src/wetwire_github/actions/codecov.py
```

Ensure:
- Function signature looks correct
- Docstring is present and readable
- Parameter names are valid Python identifiers
- The `uses` field references the correct action version

### Step 5: Test the Wrapper

Create a test file to verify the wrapper works:

```python
# test_new_action.py
from wetwire_github.actions import codecov
from wetwire_github.workflow import Workflow, Job

step = codecov(token="secret", file="coverage.xml")
print(step.uses)  # Should print: codecov/codecov-action@v4
print(step.with_)  # Should print: {'token': 'secret', 'file': 'coverage.xml'}
```

### Step 6: Update Tests

Add tests for the new wrapper in `tests/test_actions.py`:

```python
def test_codecov_wrapper():
    step = codecov(token="test-token", file="coverage.xml")
    assert step.uses == "codecov/codecov-action@v4"
    assert step.with_["token"] == "test-token"
    assert step.with_["file"] == "coverage.xml"
```

### Optional: Customize Version

By default, all actions use `@v4`. To use a different version, edit `codegen/generate.py`:

```python
# In main() function, find this line:
action_refs[name] = (repo, "v4")  # Default to v4

# Change to version-specific mapping:
version_map = {
    "checkout": "v4",
    "setup-python": "v5",
    "codecov": "v3",  # Specify custom version
}
action_refs[name] = (repo, version_map.get(name, "v4"))
```

---

## Generated Code Structure

### Function Signature

Generated functions follow this pattern:

```python
def <action_name>(
    <required_param1>: str,              # Required inputs (positional)
    <required_param2>: str,
    <optional_param1>: str | None = None,  # Optional inputs (keyword)
    <optional_param2>: str | None = None,
) -> Step:
    """<action description>

    Args:
        <param1>: <param1 description>
        <param2>: <param2 description>

    Returns:
        Step configured to use this action
    """
```

**Rules:**

1. Required inputs come first (positional parameters)
2. Optional inputs come second (keyword parameters with `None` default)
3. All parameters are typed as `str | None` for simplicity
4. Function always returns `Step`

### Parameter Mapping

The `with_dict` maps Python parameter names back to YAML input names:

```python
with_dict = {
    "fetch-depth": fetch_depth,      # Python name → YAML name
    "ssh-key": ssh_key,              # snake_case → kebab-case
    "set-safe-directory": set_safe_directory,
}
```

### None Filtering

The generator filters out `None` values to avoid cluttering the YAML:

```python
with_dict = {k: v for k, v in with_dict.items() if v is not None}
```

This allows:

```python
checkout(fetch_depth="0")  # Only fetch_depth is set
# Produces: with_={'fetch-depth': '0'}
```

### Module Organization

Each action gets its own module:

```
src/wetwire_github/actions/
├── __init__.py           # Exports all wrappers
├── checkout.py           # def checkout()
├── setup_python.py       # def setup_python()
└── cache.py              # def cache()
```

This structure:
- Keeps code organized
- Makes imports clean: `from wetwire_github.actions import checkout`
- Allows lazy loading
- Simplifies version control diffs

---

## Regenerating Wrappers

You may need to regenerate wrappers when:
- Action schemas are updated upstream
- New inputs are added to an action
- You want to update action versions (e.g., `@v4` → `@v5`)

### Full Regeneration

Run all three stages:

```bash
# 1. Fetch latest schemas
uv run python -m codegen.fetch

# 2. Parse schemas (optional verification)
uv run python -m codegen.parse

# 3. Generate wrappers
uv run python -m codegen.generate
```

### Selective Regeneration

To regenerate a single action:

```bash
# 1. Fetch only one action
# (Currently requires editing fetch.py to limit ACTION_REPOS)

# 2. Generate
uv run python -m codegen.generate
```

### Updating Versions

To update action versions (e.g., use `@v5` instead of `@v4`):

**Option 1: Global Update**

Edit `codegen/generate.py` in the `main()` function:

```python
# Change this line:
action_refs[name] = (repo, "v4")

# To:
action_refs[name] = (repo, "v5")
```

**Option 2: Per-Action Versions**

Create a version mapping:

```python
VERSION_MAP = {
    "checkout": "v4",
    "setup-python": "v5",
    "setup-node": "v4",
}

# In main():
version = VERSION_MAP.get(name, "v4")  # Default to v4
action_refs[name] = (repo, version)
```

**Option 3: Detect Latest Version**

For automatic version detection, you'd need to:
1. Query GitHub API for latest release
2. Parse version tags
3. Select appropriate version

This is not currently implemented but could be added to `fetch.py`.

### Verifying Changes

After regeneration:

1. **Check git diff** to see what changed:
   ```bash
   git diff src/wetwire_github/actions/
   ```

2. **Run tests** to ensure nothing broke:
   ```bash
   uv run pytest tests/test_actions.py -v
   ```

3. **Test in practice** with a sample workflow:
   ```bash
   # Build a test workflow
   uv run wetwire-github build ci/
   ```

---

## Customization

### Custom Templates

The default template generates simple wrappers. To customize:

**Edit `codegen/generate.py`:**

```python
def generate_action_function(
    schema: ActionSchema,
    owner_repo: str,
    version: str,
) -> str:
    """Customize this function to change generated code."""

    # Add custom logic here
    # For example: special handling for certain actions

    if owner_repo == "actions/checkout":
        # Custom checkout wrapper with extra features
        pass
```

### Adding Type Hints

Currently all parameters are `str | None`. To add specific types:

```python
# In generate_action_function(), when building params:
for inp in required_inputs:
    # Determine type based on input name or description
    param_type = "str"
    if inp["name"] in ["fetch-depth", "timeout"]:
        param_type = "int"
    elif inp["name"] in ["persist-credentials", "clean"]:
        param_type = "bool"

    params.append(f'{inp["python_name"]}: {param_type},')
```

### Custom Naming

Override the naming convention:

```python
def _derive_function_name(action_name: str, action_ref: str) -> str:
    """Customize function naming."""

    # Custom mappings
    custom_names = {
        "actions/checkout": "git_checkout",
        "codecov/codecov-action": "upload_coverage",
    }

    if action_ref in custom_names:
        return custom_names[action_ref]

    # Fall back to default behavior
    return to_python_identifier(action_name)
```

### Pre/Post Processing

Add hooks for processing:

```python
def post_process_code(code: str, action_name: str) -> str:
    """Post-process generated code."""

    # Add custom imports
    if "setup-python" in action_name:
        code = code.replace(
            "from wetwire_github.workflow import Step",
            "from wetwire_github.workflow import Step\nfrom typing import Literal"
        )

    return code

# In main():
func_code = generate_action_function(schema, owner_repo, version)
func_code = post_process_code(func_code, name)
```

### Schema Extensions

To parse additional metadata from `action.yml`:

**Edit `codegen/parse.py`:**

```python
@dataclass
class ActionSchema:
    name: str
    description: str
    inputs: list[ActionInput]
    outputs: list[ActionOutput]

    # Add custom fields
    branding: dict[str, str] | None = None
    runs: dict[str, Any] | None = None  # Capture 'runs' section

# In parse_action_yml():
return ActionSchema(
    # ... existing fields
    runs=data.get("runs"),  # Extract runs section
)
```

### Local/Composite Actions

To support local composite actions (`./.github/actions/my-action`):

```python
# The generator already handles local paths in _derive_function_name()
# For local actions, use empty version string:

ACTION_REPOS = {
    "my-action": "./.github/actions/my-action",
}

# In generate.py main():
version = "" if repo.startswith("./") else "v4"
action_refs[name] = (repo, version)
```

---

## Troubleshooting

### Common Issues

**Issue: Fetch fails with 404**

```
✗ checkout: HTTP Error 404: Not Found
```

**Solution:** Action repository may have moved or action.yml is in a different location.

1. Check if repo exists: `https://github.com/actions/checkout`
2. Verify action.yml location (might be `action.yaml` instead)
3. Update fetch.py if needed

---

**Issue: Generated function has invalid Python syntax**

```python
def setup-python(...):  # SyntaxError
```

**Solution:** The name conversion failed. This shouldn't happen with the current implementation, but if it does:

1. Check `to_python_identifier()` in generate.py
2. Add special case mapping for problematic names
3. Manually fix generated file and add to custom mappings

---

**Issue: Parameter names clash with Python keywords**

```python
def my_action(if: str):  # SyntaxError: invalid syntax
```

**Solution:** Already handled by adding trailing underscore:

```python
if name in keyword.kwlist:
    name = f"{name}_"  # 'if' → 'if_'
```

If this doesn't work, add to special cases in `to_python_identifier()`.

---

**Issue: Generated docstring is malformed**

```python
"""Description with "quotes" breaks syntax"""
```

**Solution:** The generator doesn't currently escape quotes. You can:

1. Post-process docstrings to escape quotes
2. Use raw strings for docstrings
3. Manually fix problematic cases

---

**Issue: ruff formatting fails**

```
! ruff not available for formatting
```

**Solution:** Install ruff:

```bash
uv add --dev ruff
```

Or format manually after generation:

```bash
uv run ruff format src/wetwire_github/actions/
```

---

## See Also

- [CLI Reference](CLI.md) - Using the generated wrappers
- [Developers Guide](DEVELOPERS.md) - Contributing to wetwire-github
- [Internals](INTERNALS.md) - Architecture and design patterns
- [GitHub Actions Documentation](https://docs.github.com/en/actions) - Official action.yml specification
