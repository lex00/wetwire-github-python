# Using wetwire-github with Kiro CLI

This guide walks you through setting up wetwire-github with Kiro CLI for AI-assisted workflow design in enterprise environments.

## Prerequisites

- Python 3.11 or later
- [uv](https://docs.astral.sh/uv/) package manager
- [Kiro CLI](https://kiro.dev/docs/cli/) installed

---

## Step 1: Install wetwire-github with MCP Support

Install wetwire-github with the `[mcp]` optional dependency:

```bash
uv add "wetwire-github[mcp]"
```

This installs:
- `wetwire-github` - GitHub Actions workflow synthesis from Python
- `mcp` - Model Context Protocol server support

Verify the installation:

```bash
uv run wetwire-github --version
```

---

## Step 2: Install Kiro CLI

If you haven't already installed Kiro CLI, follow the [official installation guide](https://kiro.dev/docs/cli/).

Verify Kiro is installed:

```bash
kiro-cli --version
```

---

## Step 3: Configure Kiro for wetwire-github

The first time you run `wetwire-github design --provider kiro`, it automatically installs the required configurations:

1. **Agent config** (`~/.kiro/agents/wetwire-github-runner.json`) - Defines the wetwire-github-runner agent with access to wetwire-github tools
2. **MCP config** (`.kiro/mcp.json` in your project) - Configures the wetwire-github-mcp server

You can also configure these manually:

### Manual Agent Configuration

Create `~/.kiro/agents/wetwire-github-runner.json`:

```json
{
  "name": "wetwire-github-runner",
  "description": "GitHub Actions workflow generator using wetwire-github Python syntax",
  "allowedTools": ["fs_read", "fs_write", "bash", "mcp:wetwire-github-mcp"],
  "context": {
    "patterns": "wetwire-github Syntax Principles...",
    "workflow": "1. Explore 2. Plan 3. Implement 4. Lint 5. Build"
  }
}
```

### Manual MCP Configuration

Create `.kiro/mcp.json` in your project directory:

```json
{
  "mcpServers": {
    "wetwire-github-mcp": {
      "command": "uv",
      "args": ["run", "wetwire-github-mcp"]
    }
  }
}
```

> **Note**: Using `uv run` ensures the MCP server command is available in your project's virtual environment.

---

## Step 4: Run Design Mode with Kiro

Start an AI-assisted design session using Kiro:

```bash
uv run wetwire-github design --provider kiro "Create a CI workflow for Python"
```

Or start an interactive session without a prompt:

```bash
uv run wetwire-github design --provider kiro
```

### Alternative: Direct Kiro Command

You can also launch Kiro directly with the wetwire-github-runner agent:

```bash
uv run wetwire-github kiro --prompt "Create a CI workflow for Python"
```

Or install configs without launching:

```bash
uv run wetwire-github kiro --install-only
```

### Options

| Option | Description |
|--------|-------------|
| `prompt` | Initial prompt describing what to build (optional) |
| `-p, --provider` | AI provider: `anthropic` (default) or `kiro` |
| `-o, --output` | Output directory (default: current directory) |

---

## Step 5: Verify Generated Code

After the design session creates your workflow code, verify it:

```bash
# Lint the generated code
uv run wetwire-github lint ./my_package

# Build the GitHub Actions YAML
uv run wetwire-github build ./my_package

# Preview the generated YAML
cat .github/workflows/*.yml
```

---

## MCP Tools Available to Kiro

The wetwire-github-mcp server exposes seven tools to the Kiro agent:

| Tool | Description |
|------|-------------|
| `wetwire_init` | Create a new wetwire-github project with example workflow |
| `wetwire_build` | Generate GitHub Actions YAML from Python workflow declarations |
| `wetwire_lint` | Run code quality rules (WAG001-WAG008) on Python workflow code |
| `wetwire_validate` | Validate generated YAML files using actionlint |
| `wetwire_import` | Convert existing GitHub Actions YAML to typed Python code |
| `wetwire_list` | List discovered workflows and jobs from Python packages |
| `wetwire_graph` | Generate DAG visualization of workflow job dependencies |

These tools enable the Kiro agent to:
1. Create new workflow packages
2. Validate code follows wetwire-github patterns
3. Generate GitHub Actions YAML
4. Import existing workflows for migration

---

## Example Workflow

Here's a complete workflow for creating a CI pipeline with test matrix:

```bash
# 1. Create a new project directory
mkdir my-ci-project && cd my-ci-project

# 2. Initialize a Python project with uv
uv init

# 3. Add wetwire-github with MCP support
uv add "wetwire-github[mcp]"

# 4. Run design mode with Kiro
uv run wetwire-github design --provider kiro "Create a CI workflow that runs tests on Python 3.11 and 3.12, deploys on main branch"

# 5. After the session, verify the generated code
uv run wetwire-github lint .
uv run wetwire-github build .

# 6. Review the generated YAML
cat .github/workflows/*.yml
```

---

## wetwire-github Code Patterns

The Kiro agent follows these wetwire-github patterns when generating code:

### Workflow Declaration
```python
from wetwire_github.workflow import Workflow, Job, Step, Triggers, PushTrigger

ci = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger(branches=["main"])),
    jobs={"build": build_job},
)
```

### Typed Action Wrappers
```python
from wetwire_github.actions import checkout, setup_python, cache

steps = [
    checkout(fetch_depth=0),
    setup_python(python_version="3.11"),
    cache(path="~/.cache/pip", key="pip-cache"),
]
```

### Expression Contexts
```python
from wetwire_github.workflow.expressions import Secrets, Matrix, GitHub

env = {
    "TOKEN": Secrets.get("DEPLOY_TOKEN"),
    "REF": GitHub.ref,
}
```

### Matrix Builds
```python
from wetwire_github.workflow import Job, Step, Strategy, Matrix

test_job = Job(
    runs_on="ubuntu-latest",
    strategy=Strategy(
        matrix=Matrix(
            python=["3.10", "3.11", "3.12"],
        ),
    ),
    steps=[
        checkout(),
        setup_python(python_version="${{ matrix.python }}"),
        Step(run="pytest"),
    ],
)
```

---

## Troubleshooting

### Kiro CLI not found

```
Error: Kiro CLI not found. Install from https://kiro.dev/docs/cli/
```

Ensure Kiro CLI is installed and in your PATH.

### MCP package not installed

```
Error: Kiro integration requires mcp package. Install with: pip install wetwire-github[mcp]
```

Reinstall with the mcp extras:

```bash
uv add "wetwire-github[mcp]"
```

### wetwire-github-mcp command not found or MCP server not loading

If Kiro reports "One or more mcp server did not load correctly", the issue is usually that the `wetwire-github-mcp` command isn't found in PATH. The auto-generated MCP config uses `uv run` to solve this:

```json
{
  "mcpServers": {
    "wetwire-github-mcp": {
      "command": "uv",
      "args": ["run", "wetwire-github-mcp"]
    }
  }
}
```

Verify the MCP server works:

```bash
uv run wetwire-github-mcp --help
```

If you have an older config using just `"command": "wetwire-github-mcp"`, update it to use `uv run` as shown above.

### Lint errors during design session

The Kiro agent follows a mandatory lint-fix loop. If you see lint errors:

1. The agent will automatically attempt to fix them
2. Re-run lint after each fix until zero errors
3. Only then will the agent run `wetwire_build`

If the agent gets stuck, you can manually fix issues:

```bash
# Check current lint status
uv run wetwire-github lint .

# Auto-fix what's possible
uv run wetwire-github lint . --fix
```

### Agent config not updating

Force reinstall of configurations:

```bash
uv run wetwire-github kiro --install-only --force
```

---

## Comparison: Kiro vs Anthropic Provider

| Feature | `--provider kiro` | `--provider anthropic` |
|---------|-------------------|------------------------|
| API | AWS Kiro CLI | Anthropic API |
| Authentication | AWS credentials | `ANTHROPIC_API_KEY` |
| Dependency | Kiro CLI + mcp | wetwire-core |
| Best for | Corporate AWS environments | Direct Anthropic access |

---

## Persona-Based Testing with Kiro

You can run persona-based tests to validate generated workflows:

```bash
# Run tests with Kiro provider
uv run wetwire-github test --provider kiro --workflow .github/workflows/ci.yml

# Run with specific scenario
uv run wetwire-github test --provider kiro --workflow ci.yml --scenario test_scenario.json
```

---

## Known Limitations

### Automated Testing

The Kiro provider's automated tests run scenarios in single-shot mode rather than simulating full multi-turn conversations. This is due to kiro-cli's architecture which requires a TTY for interactive mode.

**What this means:**
- Interactive usage (`wetwire-github design --provider kiro`) works fully with back-and-forth conversation
- Automated persona tests send an enhanced prompt with persona characteristics and let kiro complete the task autonomously
- The Anthropic provider can simulate full conversations in tests; the Kiro provider cannot

This limitation only affects automated testing. Developers using the interactive design mode get the full conversational experience.

---

## See Also

- [Quick Start](QUICK_START.md) - Basic wetwire-github usage
- [CLI Reference](CLI.md) - Full CLI documentation
- [Lint Rules](LINT_RULES.md) - Code quality rules (WAG001-WAG008)
- [Kiro CLI Docs](https://kiro.dev/docs/cli/) - Official Kiro documentation
