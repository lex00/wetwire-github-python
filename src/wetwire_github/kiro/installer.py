"""Kiro CLI configuration installer.

This module handles auto-installation of Kiro CLI configurations:
- Agent config (~/.kiro/agents/wetwire-github-runner.json)
- MCP config (.kiro/mcp.json in project directory)
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

# Embedded agent configuration
# Note: mcpServers will be populated dynamically with the correct path
AGENT_CONFIG: dict[str, Any] = {
    "name": "wetwire-github-runner",
    "description": "GitHub Actions workflow generator using wetwire-github Python syntax",
    "model": "claude-sonnet-4",
    "tools": ["*"],
    "mcpServers": {},  # Populated in install_agent_config
    "prompt": """You are a GitHub Actions workflow design assistant using wetwire-github Python syntax.

When starting a new conversation, greet the user and ask what GitHub Actions workflow they'd like to build. Be helpful and guide them through the design process.

## MANDATORY LINT-FIX LOOP (NEVER SKIP)

Every time you write or edit code, you MUST follow this exact loop:

```
┌─────────────────────────────────────────────────────┐
│                  WRITE/EDIT CODE                    │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│              RUN wetwire_lint                       │
└─────────────────────┬───────────────────────────────┘
                      │
              ┌───────┴───────┐
              │  Has errors?  │
              └───────┬───────┘
                      │
         ┌────────────┼────────────┐
         │ YES                     │ NO
         ▼                         ▼
┌─────────────────┐    ┌─────────────────────────────┐
│   FIX errors    │    │    RUN wetwire_build        │
└────────┬────────┘    └─────────────────────────────┘
         │
         │ (go back to lint)
         ▼
┌─────────────────────────────────────────────────────┐
│              RUN wetwire_lint AGAIN                 │
└─────────────────────┬───────────────────────────────┘
         │
         └──────► (repeat until no errors)
```

CRITICAL RULES:
1. NEVER run wetwire_build until wetwire_lint passes with zero errors
2. After EVERY fix, you MUST re-run wetwire_lint
3. The loop is: EDIT → LINT → FIX → LINT → FIX → LINT → ... → BUILD
4. You are NOT DONE fixing until lint returns zero errors

## wetwire-github Python Syntax Principles

1. WORKFLOW DECLARATION - Workflows are Python dataclasses:
   ```python
   from wetwire_github.workflow import Workflow, Job, Step, Triggers

   ci = Workflow(
       name="CI",
       on=Triggers(push=PushTrigger(branches=["main"])),
       jobs={"build": build_job},
   )
   ```

2. JOB DECLARATION - Jobs define runner and steps:
   ```python
   from wetwire_github.workflow import Job, Step

   build_job = Job(
       runs_on="ubuntu-latest",
       steps=[
           Step(uses="actions/checkout@v4"),
           Step(run="make build"),
       ],
   )
   ```

3. TYPED ACTION WRAPPERS - Use pre-generated wrappers:
   ```python
   from wetwire_github.actions import checkout, setup_python, cache

   steps = [
       checkout(fetch_depth=0),
       setup_python(python_version="3.11"),
       cache(path="~/.cache/pip", key="pip-cache"),
   ]
   ```

4. EXPRESSION CONTEXTS - Use typed builders:
   ```python
   from wetwire_github.workflow.expressions import Secrets, Matrix, GitHub

   env = {
       "TOKEN": Secrets.get("DEPLOY_TOKEN"),
       "REF": GitHub.ref,
   }
   ```

## Key Lint Rules (WAG001-WAG008)
- WAG001: Use typed action wrappers instead of raw strings
- WAG002: Use condition builders instead of raw expressions
- WAG003: Use secrets context for secrets access
- WAG004: Use matrix builder for matrix configurations
- WAG005: Extract inline environment variables
- WAG006: Detect duplicate workflow names
- WAG007: Flag oversized files (>N jobs)
- WAG008: Avoid hardcoded expressions

## Design Workflow

EXAMPLE - Creating a CI workflow:

1. Create a Python file with the workflow:
   ```python
   from wetwire_github.workflow import Workflow, Job, Step
   from wetwire_github.actions import checkout, setup_python

   build = Job(
       runs_on="ubuntu-latest",
       steps=[
           checkout(),
           setup_python(python_version="3.11"),
           Step(run="pip install -e ."),
           Step(run="pytest"),
       ],
   )

   ci = Workflow(
       name="CI",
       on={"push": {}, "pull_request": {}},
       jobs={"build": build},
   )
   ```

2. Run wetwire_lint to check for issues

3. If lint has errors, fix them and re-run lint

4. Once lint passes, run wetwire_build to generate YAML

IMPORTANT:
- Always use typed action wrappers (checkout(), setup_python()) instead of raw strings
- Use expression builders for dynamic values
- Follow the lint-fix loop until zero errors""",
}


def get_agent_config_path() -> Path:
    """Get the path to the agent config file."""
    return Path.home() / ".kiro" / "agents" / "wetwire-github-runner.json"


def get_mcp_config_path(project_dir: Path | None = None) -> Path:
    """Get the path to the MCP config file."""
    if project_dir is None:
        project_dir = Path.cwd()
    return project_dir / ".kiro" / "mcp.json"


def check_kiro_installed() -> bool:
    """Check if Kiro CLI is installed and available."""
    return shutil.which("kiro-cli") is not None


def _get_mcp_server_path() -> str | None:
    """Find the absolute path to wetwire-github-mcp command.

    Returns:
        Absolute path to the command, or None if not found.
    """
    # First check if it's in PATH
    mcp_path = shutil.which("wetwire-github-mcp")
    if mcp_path:
        return mcp_path

    # Check common locations where uv/pip might install scripts
    try:
        # Try to find it via the current Python environment
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import shutil; print(shutil.which('wetwire-github-mcp') or '')",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return None


def install_agent_config(force: bool = False) -> bool:
    """Install the wetwire-github-runner agent config.

    Args:
        force: Overwrite existing config if True.

    Returns:
        True if config was installed, False if skipped.
    """
    config_path = get_agent_config_path()

    if config_path.exists() and not force:
        return False

    # Create a copy of the config to populate mcpServers
    config = AGENT_CONFIG.copy()

    # Find the MCP server path and add to agent config
    mcp_server_path = _get_mcp_server_path()
    if mcp_server_path:
        config["mcpServers"] = {
            "wetwire-github-mcp": {
                "command": mcp_server_path,
                "args": [],
            }
        }
    else:
        # Fallback to uv run
        config["mcpServers"] = {
            "wetwire-github-mcp": {
                "command": "uv",
                "args": ["run", "wetwire-github-mcp"],
            }
        }

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2))
    return True


def install_mcp_config(project_dir: Path | None = None, force: bool = False) -> bool:
    """Install the MCP server config in project directory.

    Args:
        project_dir: Project directory. Defaults to current directory.
        force: Overwrite existing config if True.

    Returns:
        True if config was installed, False if skipped.
    """
    config_path = get_mcp_config_path(project_dir)

    # Load existing config or create new one
    if config_path.exists():
        if not force:
            # Check if wetwire-github-mcp is already configured
            existing = json.loads(config_path.read_text())
            if "wetwire-github-mcp" in existing.get("mcpServers", {}):
                return False
            # Merge with existing
            mcp_config = existing
        else:
            mcp_config = {"mcpServers": {}}
    else:
        mcp_config = {"mcpServers": {}}

    # Try to find absolute path to wetwire-github-mcp
    mcp_server_path = _get_mcp_server_path()

    if mcp_server_path:
        # Use absolute path to the installed command
        mcp_config["mcpServers"]["wetwire-github-mcp"] = {
            "command": mcp_server_path,
        }
    else:
        # Fall back to uv run (works if wetwire-github is installed in project)
        mcp_config["mcpServers"]["wetwire-github-mcp"] = {
            "command": "uv",
            "args": ["run", "wetwire-github-mcp"],
        }

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(mcp_config, indent=2))
    return True


def install_kiro_configs(
    project_dir: Path | None = None, force: bool = False, verbose: bool = False
) -> dict[str, bool]:
    """Install all Kiro configurations.

    Args:
        project_dir: Project directory for MCP config. Defaults to cwd.
        force: Overwrite existing configs if True.
        verbose: Print status messages.

    Returns:
        Dict with 'agent' and 'mcp' keys indicating what was installed.
    """
    results = {
        "agent": install_agent_config(force=force),
        "mcp": install_mcp_config(project_dir=project_dir, force=force),
    }

    if verbose:
        if results["agent"]:
            print(f"Installed agent config: {get_agent_config_path()}", file=sys.stderr)
        if results["mcp"]:
            print(
                f"Installed MCP config: {get_mcp_config_path(project_dir)}",
                file=sys.stderr,
            )

    return results


def launch_kiro(prompt: str | None = None, project_dir: Path | None = None) -> int:
    """Launch Kiro CLI with the wetwire-github-runner agent.

    Args:
        prompt: Optional initial prompt for the conversation.
        project_dir: Project directory. Defaults to current directory.

    Returns:
        Exit code from kiro-cli.
    """
    if not check_kiro_installed():
        print(
            "Error: Kiro CLI not found. Install from https://kiro.dev/docs/cli/",
            file=sys.stderr,
        )
        return 1

    # Force reinstall configs every time to ensure latest agent prompt is used
    install_kiro_configs(project_dir=project_dir, force=True, verbose=True)

    # Build command
    cmd = ["kiro-cli", "chat", "--agent", "wetwire-github-runner", "--trust-all-tools"]
    # Always send an initial message to start the conversation
    initial_message = (
        prompt if prompt else "Hello! I'm ready to design some GitHub Actions workflows."
    )
    cmd.append(initial_message)

    # Launch Kiro
    try:
        result = subprocess.run(cmd, cwd=project_dir)
        return result.returncode
    except FileNotFoundError:
        print("Error: Failed to launch kiro-cli.", file=sys.stderr)
        return 1


def run_kiro_scenario(
    prompt: str,
    project_dir: Path | None = None,
    timeout: int = 300,
    auto_exit: bool = True,
) -> dict[str, Any]:
    """Run a Kiro CLI scenario non-interactively for testing.

    Args:
        prompt: The workflow prompt to send to Kiro.
        project_dir: Project directory. Defaults to temp directory.
        timeout: Maximum time in seconds to wait (default: 300).
        auto_exit: If True, append instruction to exit after completion.

    Returns:
        Dict with keys:
            - success: bool - Whether the scenario completed successfully
            - exit_code: int - Process exit code
            - stdout: str - Captured stdout
            - stderr: str - Captured stderr
            - workflow_valid: bool - Whether build produced valid YAML
    """
    import tempfile

    if not check_kiro_installed():
        return {
            "success": False,
            "exit_code": 1,
            "stdout": "",
            "stderr": "Kiro CLI not found",
            "workflow_valid": False,
        }

    # Use temp directory if not specified
    if project_dir is None:
        temp_dir = tempfile.mkdtemp(prefix="kiro_github_test_")
        project_dir = Path(temp_dir)
    else:
        project_dir = Path(project_dir)
        project_dir.mkdir(parents=True, exist_ok=True)

    # Ensure configs are installed
    install_kiro_configs(project_dir=project_dir, verbose=False)

    # Build the full prompt with auto-exit instruction
    full_prompt = prompt
    if auto_exit:
        full_prompt = (
            f"{prompt}\n\n"
            "After successfully creating the workflow and running lint and build, "
            "output 'SCENARIO_COMPLETE' and exit."
        )

    # Build command for non-interactive execution
    cmd = [
        "kiro-cli",
        "chat",
        "--agent",
        "wetwire-github-runner",
        "--no-interactive",
        "--trust-all-tools",
        full_prompt,
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        exit_code = result.returncode
        stdout = result.stdout
        stderr = result.stderr
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": f"Timeout after {timeout} seconds",
            "workflow_valid": False,
        }
    except FileNotFoundError:
        return {
            "success": False,
            "exit_code": 1,
            "stdout": "",
            "stderr": "Failed to launch kiro-cli",
            "workflow_valid": False,
        }

    # Check if YAML was generated
    workflow_valid = False
    github_dir = project_dir / ".github" / "workflows"
    if github_dir.exists():
        yaml_files = list(github_dir.glob("*.yml")) + list(github_dir.glob("*.yaml"))
        workflow_valid = len(yaml_files) > 0

    return {
        "success": exit_code == 0 and workflow_valid,
        "exit_code": exit_code,
        "stdout": stdout,
        "stderr": stderr,
        "workflow_valid": workflow_valid,
    }
