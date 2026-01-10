# Troubleshooting

This guide helps you diagnose and fix common issues with wetwire-github.

## Quick Fixes

Before diving into specific errors, try these common solutions:

```bash
# Reinstall the package
pip install --force-reinstall wetwire-github

# Clear the discovery cache
rm -rf .wetwire-cache

# Check your Python version (requires 3.10+)
python --version
```

---

## Workflow Loading Errors

### Module Not Found

**Error message:**
```
ModuleNotFoundError: No module named 'ci'
```
or
```
ImportError: Cannot load module from /path/to/workflows.py
```

**Causes:**
- The package path is not in your Python path
- Missing `__init__.py` file in your workflow package
- Incorrect package structure

**Solutions:**

1. Ensure your workflow package has an `__init__.py` file:
   ```
   ci/
   ├── __init__.py    # Required
   └── workflows.py
   ```

2. Run commands from the project root:
   ```bash
   # From project root
   wetwire-github build ci/

   # Not from inside the package
   cd ci && wetwire-github build .  # May fail
   ```

3. If using a custom package location, add it to your Python path:
   ```bash
   PYTHONPATH=. wetwire-github build ci/
   ```

**Prevention:**
- Use `wetwire-github init my-ci` to create a properly structured package
- Always include `__init__.py` in your workflow packages

---

### Syntax Errors

**Error message:**
```
SyntaxError: invalid syntax
```
or the command produces no output with no error message.

**Causes:**
- Python syntax error in your workflow file
- Incompatible Python version
- Malformed dataclass instantiation

**Solutions:**

1. Validate your Python syntax:
   ```bash
   python -m py_compile ci/workflows.py
   ```

2. Check for common syntax issues:
   ```python
   # Wrong: trailing comma before closing parenthesis in some contexts
   jobs={"build": build_job,}  # Some linters may flag this

   # Wrong: missing comma between arguments
   Job(
       runs_on="ubuntu-latest"
       steps=[...]  # Missing comma after runs_on
   )

   # Correct:
   Job(
       runs_on="ubuntu-latest",
       steps=[...],
   )
   ```

3. Ensure you're using Python 3.10 or later:
   ```bash
   python --version
   # Must be 3.10 or higher
   ```

**Prevention:**
- Use a Python IDE with syntax highlighting
- Run `wetwire-github lint ci/` before building

---

### Import Errors

**Error message:**
```
ImportError: cannot import name 'Workflow' from 'wetwire_github'
```
or
```
AttributeError: module 'wetwire_github.workflow' has no attribute 'Workflow'
```

**Causes:**
- Outdated wetwire-github version
- Incorrect import path
- Circular imports in your workflow files

**Solutions:**

1. Use the correct import path:
   ```python
   # Correct imports
   from wetwire_github.workflow import Workflow, Job, Step, Triggers
   from wetwire_github.actions import checkout, setup_python

   # Wrong (old pattern)
   from wetwire_github import Workflow  # Does not work
   ```

2. Update wetwire-github:
   ```bash
   pip install --upgrade wetwire-github
   ```

3. Check for circular imports by simplifying your file structure:
   ```python
   # Avoid cross-imports between workflow files
   # jobs.py
   from wetwire_github.workflow import Job

   # workflows.py - import from jobs is OK
   from .jobs import build_job
   ```

**Prevention:**
- Follow the import patterns in the [Quick Start](QUICK_START.md) guide
- Keep workflow definitions simple and avoid complex circular dependencies

---

## Actionlint Integration Issues

### Actionlint Not Installed

**Error message:**
```
Warning: actionlint is not installed. Install it for full validation.
```

**Causes:**
- Actionlint is not installed on your system
- Actionlint is not in your PATH

**Solutions:**

1. Install actionlint:
   ```bash
   # macOS
   brew install actionlint

   # Linux (Go required)
   go install github.com/rhysd/actionlint/cmd/actionlint@latest

   # Or download from releases
   # https://github.com/rhysd/actionlint/releases
   ```

2. Verify installation:
   ```bash
   actionlint --version
   ```

3. If installed but not found, add to PATH:
   ```bash
   # For Go installations
   export PATH="$PATH:$(go env GOPATH)/bin"
   ```

**Prevention:**
- Add actionlint installation to your CI/CD pipeline
- Document actionlint as a development dependency

---

### Invalid YAML Generated

**Error message:**
```
.github/workflows/ci.yml:12:9: property "pyton-version" is not defined in object type
```

**Causes:**
- Typo in parameter names
- Using parameters not supported by the action version
- Invalid YAML structure from workflow definition

**Solutions:**

1. Check parameter names match action documentation:
   ```python
   # Wrong
   setup_python(pyton_version="3.11")  # Typo

   # Correct
   setup_python(python_version="3.11")
   ```

2. Use typed action wrappers instead of raw `uses` strings:
   ```python
   # Better: typed wrapper catches typos at definition time
   from wetwire_github.actions import setup_python
   step = setup_python(python_version="3.11")

   # Risky: raw string doesn't validate parameters
   step = Step(
       uses="actions/setup-python@v5",
       with_={"pyton-version": "3.11"}  # Typo won't be caught
   )
   ```

3. Validate after building:
   ```bash
   wetwire-github build ci/ && wetwire-github validate .github/workflows/
   ```

**Prevention:**
- Use typed action wrappers from `wetwire_github.actions`
- Run `wetwire-github lint ci/` to catch common issues
- Always validate generated YAML before committing

---

## Cache-Related Problems

### Stale Cache

**Symptoms:**
- Changes to workflow files are not reflected in build output
- Build produces outdated YAML
- List command shows old workflow definitions

**Causes:**
- Discovery cache contains outdated data
- File modification time not updated correctly

**Solutions:**

1. Clear the cache:
   ```bash
   rm -rf .wetwire-cache
   ```

2. Rebuild:
   ```bash
   wetwire-github build ci/
   ```

**Prevention:**
- Add `.wetwire-cache` to your `.gitignore`
- Clear cache when switching branches with significant workflow changes

---

### Cache Corruption

**Symptoms:**
- Unexpected errors when loading workflows
- JSON parse errors in cache files
- Workflows not discovered despite being present

**Causes:**
- Interrupted write operation
- Disk space issues
- Manual editing of cache files

**Solutions:**

1. Delete the entire cache directory:
   ```bash
   rm -rf .wetwire-cache
   ```

2. If errors persist, check disk space:
   ```bash
   df -h .
   ```

3. Ensure write permissions:
   ```bash
   ls -la .wetwire-cache
   ```

**Prevention:**
- Don't edit cache files manually
- Add `.wetwire-cache` to `.gitignore`
- Ensure adequate disk space

---

## MCP Server Issues

### Server Not Starting

**Error message:**
```
MCP (Model Context Protocol) package is required for server functionality.

Install with pip:
    pip install wetwire-github[mcp]
```

**Causes:**
- MCP package not installed
- Missing optional dependency

**Solutions:**

1. Install with MCP support:
   ```bash
   pip install wetwire-github[mcp]

   # Or with uv
   uv pip install wetwire-github[mcp]
   ```

2. Verify installation:
   ```bash
   python -c "from mcp.server import Server; print('MCP OK')"
   ```

**Prevention:**
- Install with MCP extras from the start if you need AI integration

---

### Tool Not Found

**Error message:**
```
Error: Tool 'wetwire_build' not found
```

**Causes:**
- MCP server not running
- Tool name mismatch
- Client misconfiguration

**Solutions:**

1. Verify the MCP server is running:
   ```bash
   wetwire-github mcp-server
   ```

2. Check available tools in your MCP client configuration:
   ```json
   {
     "mcpServers": {
       "wetwire-github": {
         "command": "wetwire-github",
         "args": ["mcp-server"]
       }
     }
   }
   ```

3. Available tool names are:
   - `wetwire_init`
   - `wetwire_build`
   - `wetwire_lint`
   - `wetwire_validate`
   - `wetwire_import`
   - `wetwire_list`
   - `wetwire_graph`

**Prevention:**
- Use the exact tool names as documented
- See [MCP Server Documentation](MCP_SERVER.md) for full configuration

---

### MCP Debug Mode

For troubleshooting MCP server issues, enable debug logging:

```bash
WETWIRE_MCP_DEBUG=1 wetwire-github mcp-server
```

This outputs detailed logs to stderr, including:
- Tool invocations
- Parameter parsing
- Error details

---

## Path and Permission Errors

### File Not Found

**Error message:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'ci/workflows.py'
```

**Causes:**
- Incorrect path to workflow package
- Typo in file or directory name
- Working directory mismatch

**Solutions:**

1. Verify the path exists:
   ```bash
   ls -la ci/
   ```

2. Use absolute paths if needed:
   ```bash
   wetwire-github build /path/to/project/ci/
   ```

3. Check current working directory:
   ```bash
   pwd
   ls -la
   ```

**Prevention:**
- Use tab completion for paths
- Run commands from project root

---

### Permission Denied

**Error message:**
```
PermissionError: [Errno 13] Permission denied: '.github/workflows/ci.yml'
```

**Causes:**
- Insufficient write permissions
- File locked by another process
- Read-only filesystem

**Solutions:**

1. Check file permissions:
   ```bash
   ls -la .github/workflows/
   ```

2. Fix permissions:
   ```bash
   chmod 644 .github/workflows/*.yml
   ```

3. Check if file is open in another program

**Prevention:**
- Ensure proper permissions on output directories
- Don't run as root unless necessary

---

## Provider Configuration Issues

### Anthropic Provider

**Error message:**
```
Error: ANTHROPIC_API_KEY environment variable not set
```

**Causes:**
- Missing API key
- API key not exported to environment

**Solutions:**

1. Set the API key:
   ```bash
   export ANTHROPIC_API_KEY="your-api-key"
   ```

2. Or use a `.env` file (requires python-dotenv):
   ```
   ANTHROPIC_API_KEY=your-api-key
   ```

3. Verify the key is set:
   ```bash
   echo $ANTHROPIC_API_KEY
   ```

**Prevention:**
- Store API keys securely
- Use environment variable management tools

---

### Kiro Provider

**Error message:**
```
Error: Kiro CLI not found. Install from https://kiro.dev/docs/cli/
```

**Causes:**
- Kiro CLI not installed
- Kiro CLI not in PATH

**Solutions:**

1. Install Kiro CLI following the official guide:
   ```bash
   # Visit https://kiro.dev/docs/cli/ for installation instructions
   ```

2. Verify installation:
   ```bash
   kiro-cli --version
   ```

3. If installed but not found:
   ```bash
   which kiro-cli
   # Add the directory to your PATH if needed
   ```

**Prevention:**
- Follow the [Kiro CLI Guide](GITHUB-KIRO-CLI.md) for setup

---

### Kiro Configuration Issues

**Error message:**
```
Failed to launch kiro-cli
```
or
```
Timeout after 300 seconds
```

**Causes:**
- Missing or invalid Kiro configuration
- Agent configuration not installed
- Network issues

**Solutions:**

1. Reinstall Kiro configurations:
   ```bash
   wetwire-github kiro --install
   ```

2. Verify agent configuration exists:
   ```bash
   ls ~/.kiro/agents/wetwire-github-runner.json
   ```

3. Check project-level configuration:
   ```bash
   ls .kiro/mcp.json
   ```

**Prevention:**
- Run `wetwire-github kiro --install` after updates
- Ensure network connectivity for AI providers

---

## Build and Lint Errors

### No Workflows Discovered

**Symptoms:**
- `wetwire-github list ci/` shows no workflows
- Build produces no output files

**Causes:**
- Workflow variables not at module level
- Missing imports
- Workflow inside functions or classes

**Solutions:**

1. Ensure workflows are at module level:
   ```python
   # Correct: module-level variable
   ci = Workflow(...)

   # Wrong: inside function
   def create_workflow():
       return Workflow(...)
   ```

2. Verify imports are correct:
   ```python
   from wetwire_github.workflow import Workflow, Job, Step, Triggers
   ```

3. Check file is valid Python:
   ```bash
   python -c "import ci.workflows"
   ```

**Prevention:**
- Follow examples in [Quick Start](QUICK_START.md)
- Use `wetwire-github list ci/` to verify discovery

---

### Lint Rule Violations

**Error message:**
```
ci/workflows.py:23:12: WAG001 Use typed action wrapper instead of raw 'uses' string
```

**Causes:**
- Code doesn't follow wetwire-github best practices
- Using deprecated patterns

**Solutions:**

1. Auto-fix supported rules:
   ```bash
   wetwire-github lint ci/ --fix
   ```

2. Manually fix remaining issues following the lint rule documentation.
   See [Lint Rules](LINT_RULES.md) for details on each rule.

**Prevention:**
- Run lint as part of your CI pipeline
- Use typed action wrappers from the start

---

## Getting More Help

If you're still stuck:

1. **Check the documentation:**
   - [Quick Start](QUICK_START.md)
   - [CLI Reference](CLI.md)
   - [FAQ](FAQ.md)

2. **Enable verbose output:**
   ```bash
   # For MCP server
   WETWIRE_MCP_DEBUG=1 wetwire-github mcp-server
   ```

3. **Check the issue tracker:**
   Search existing issues or file a new one with:
   - Python version (`python --version`)
   - wetwire-github version (`wetwire-github --version`)
   - Full error message
   - Minimal reproduction steps

---

## Common Error Quick Reference

| Error | Quick Fix |
|-------|-----------|
| `ModuleNotFoundError` | Add `__init__.py`, check path |
| `SyntaxError` | Run `python -m py_compile file.py` |
| `actionlint not installed` | `brew install actionlint` |
| `MCP package required` | `pip install wetwire-github[mcp]` |
| `ANTHROPIC_API_KEY not set` | `export ANTHROPIC_API_KEY=...` |
| `Kiro CLI not found` | Install from https://kiro.dev/docs/cli/ |
| `No workflows discovered` | Check module-level definitions |
| `Stale cache` | `rm -rf .wetwire-cache` |
| `Permission denied` | Check file permissions |
