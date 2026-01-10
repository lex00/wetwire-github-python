# MCP Server Documentation

This document covers the Model Context Protocol (MCP) server integration for wetwire-github, enabling AI agents like Claude Code and Kiro CLI to interact with wetwire-github commands programmatically.

## Overview

### What is MCP?

The [Model Context Protocol (MCP)](https://github.com/anthropics/mcp) is an open protocol developed by Anthropic that enables AI models to securely interact with external tools and data sources. MCP provides a standardized way for AI agents to:

- Discover available tools
- Execute tool calls with typed parameters
- Receive structured results

### Why MCP for wetwire-github?

The MCP server enables AI-assisted workflow development by exposing wetwire-github's CLI commands as tools that AI agents can invoke. This allows:

- **Automated workflow generation**: AI can generate Python workflow declarations
- **Iterative refinement**: AI can lint, fix, and validate generated code
- **Import existing workflows**: AI can convert YAML to Python automatically
- **Visualization**: AI can generate dependency graphs

---

## Installation

### Basic Installation

```bash
# Install wetwire-github with MCP support
pip install wetwire-github[mcp]

# Or with uv
uv pip install wetwire-github[mcp]
```

### Verifying Installation

```bash
# Check if MCP is available
python -c "from wetwire_github.mcp_server import MCP_AVAILABLE; print(f'MCP available: {MCP_AVAILABLE}')"
```

### Enterprise Installation

For enterprise environments with strict dependency management:

```bash
# Install with locked dependencies
pip install wetwire-github[mcp] --require-hashes -c constraints.txt

# Or in an isolated virtual environment
python -m venv wetwire-env
source wetwire-env/bin/activate
pip install wetwire-github[mcp]
```

---

## Starting the Server

### Command Line

```bash
# Start the MCP server
wetwire-github mcp-server

# Or via Python module
python -m wetwire_github.mcp_server
```

### With Debug Logging

```bash
# Enable verbose debug logging
WETWIRE_MCP_DEBUG=1 wetwire-github mcp-server

# Or
WETWIRE_MCP_DEBUG=true wetwire-github mcp-server
```

Debug logging outputs to stderr and includes:
- Tool call invocations with arguments
- Success/failure status for each operation
- Exception stack traces for debugging

---

## Available Tools

The MCP server exposes the following tools:

### wetwire_init

Create a new wetwire-github project with example workflow.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | No | Project name |
| `output` | string | No | Output directory (default: current directory) |

**Example:**
```json
{
  "name": "wetwire_init",
  "arguments": {
    "name": "my-ci",
    "output": "./projects"
  }
}
```

### wetwire_build

Generate GitHub Actions YAML from Python workflow declarations.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `package` | string | No | Python package path to discover workflows from |
| `output` | string | No | Output directory (default: `.github/workflows/`) |
| `format` | string | No | Output format: `yaml` or `json` (default: yaml) |

**Example:**
```json
{
  "name": "wetwire_build",
  "arguments": {
    "package": "ci/",
    "output": ".github/workflows/"
  }
}
```

### wetwire_lint

Run code quality rules (WAG001-WAG015) on Python workflow code.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `package` | string | No | Python package path to lint |
| `fix` | boolean | No | Automatically fix fixable issues |
| `format` | string | No | Output format: `text` or `json` (default: text) |

**Example:**
```json
{
  "name": "wetwire_lint",
  "arguments": {
    "package": "ci/",
    "fix": true
  }
}
```

### wetwire_validate

Validate generated YAML files using actionlint.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `files` | array[string] | No | YAML files to validate |
| `format` | string | No | Output format: `text` or `json` (default: text) |

**Example:**
```json
{
  "name": "wetwire_validate",
  "arguments": {
    "files": [".github/workflows/ci.yml"]
  }
}
```

### wetwire_import

Convert existing GitHub Actions YAML to typed Python code.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `files` | array[string] | No | YAML files to import |
| `output` | string | No | Output directory for generated Python code |
| `single_file` | boolean | No | Generate all code in a single file |

**Example:**
```json
{
  "name": "wetwire_import",
  "arguments": {
    "files": [".github/workflows/ci.yml"],
    "output": "ci/"
  }
}
```

### wetwire_list

List discovered workflows and jobs from Python packages.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `package` | string | No | Python package path to discover from |
| `format` | string | No | Output format: `table` or `json` (default: table) |

**Example:**
```json
{
  "name": "wetwire_list",
  "arguments": {
    "package": "ci/",
    "format": "json"
  }
}
```

### wetwire_graph

Generate DAG visualization of workflow job dependencies.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `package` | string | No | Python package path to analyze |
| `format` | string | No | Output format: `dot` or `mermaid` (default: mermaid) |
| `output` | string | No | Output file path |

**Example:**
```json
{
  "name": "wetwire_graph",
  "arguments": {
    "package": "ci/",
    "format": "mermaid"
  }
}
```

---

## Integration with AI Tools

### Claude Code Configuration

Add the following to your Claude Code MCP configuration:

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

For systems using uv:

```json
{
  "mcpServers": {
    "wetwire-github": {
      "command": "uv",
      "args": ["run", "wetwire-github", "mcp-server"]
    }
  }
}
```

### Kiro CLI Configuration

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

### Cursor Configuration

Add to `.cursor/mcp.json`:

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

---

## Debugging Guide

### Enable Verbose Logging

```bash
# Set environment variable before starting server
export WETWIRE_MCP_DEBUG=1
wetwire-github mcp-server
```

### Log Output Location

Logs are written to stderr, which is captured by the MCP client. Common log messages:

```
2025-01-10 12:00:00 - wetwire_github.mcp - INFO - Starting MCP server...
2025-01-10 12:00:00 - wetwire_github.mcp - INFO - MCP server created successfully
2025-01-10 12:00:00 - wetwire_github.mcp - INFO - MCP server running on stdio transport
2025-01-10 12:00:01 - wetwire_github.mcp - DEBUG - Tool call received: name=wetwire_build, arguments={'package': 'ci/'}
2025-01-10 12:00:01 - wetwire_github.mcp - INFO - Executing wetwire_build: package=ci/, output=.github/workflows/, format=yaml
2025-01-10 12:00:01 - wetwire_github.mcp - INFO - wetwire_build completed successfully
```

### Testing the Server Manually

You can test the MCP server using the MCP inspector:

```bash
# Install MCP inspector
npm install -g @anthropics/mcp-inspector

# Run inspector with wetwire-github server
mcp-inspector wetwire-github mcp-server
```

### Common Issues

#### "MCP package is required for server functionality"

This error occurs when the `mcp` package is not installed:

```
MCP (Model Context Protocol) package is required for server functionality.

Install with pip:
    pip install wetwire-github[mcp]

Or with uv:
    uv pip install wetwire-github[mcp]
```

**Solution:** Install the MCP dependency as shown above.

#### Tool Calls Failing Silently

Enable debug logging to see detailed error information:

```bash
WETWIRE_MCP_DEBUG=1 wetwire-github mcp-server
```

#### Server Not Responding

Check that:
1. The server process is running
2. The MCP client configuration is correct
3. The command path is accessible

---

## Troubleshooting

### Missing Dependencies

If you see import errors for `mcp`:

```bash
# Reinstall with MCP support
pip uninstall wetwire-github
pip install wetwire-github[mcp]
```

### Permission Issues

Ensure the wetwire-github command is in your PATH:

```bash
# Check if command is available
which wetwire-github

# If not found, ensure the installation location is in PATH
export PATH="$HOME/.local/bin:$PATH"
```

### Python Version Compatibility

The MCP server requires Python 3.10 or later:

```bash
python --version
# Python 3.10.0 or higher required
```

### Virtual Environment Issues

If using a virtual environment, ensure it's activated:

```bash
# Activate the environment
source /path/to/venv/bin/activate

# Verify wetwire-github is installed
pip show wetwire-github
```

For Claude Code or Kiro CLI, you may need to specify the full path to the Python executable:

```json
{
  "mcpServers": {
    "wetwire-github": {
      "command": "/path/to/venv/bin/wetwire-github",
      "args": ["mcp-server"]
    }
  }
}
```

---

## Security Considerations

### File System Access

The MCP server has access to the file system based on the working directory. Consider:

- Running the server from a project-specific directory
- Using appropriate file system permissions
- Not exposing the server to untrusted networks

### Environment Variables

Sensitive information should be handled via environment variables, not passed through MCP tool arguments.

### Enterprise Deployments

For enterprise environments:

1. **Audit logging**: Enable `WETWIRE_MCP_DEBUG=1` for tool invocation auditing
2. **Network isolation**: Run the MCP server on localhost only
3. **Access control**: Use OS-level permissions to restrict who can start the server

---

## API Reference

### Python API

```python
from wetwire_github.mcp_server import (
    MCP_AVAILABLE,
    create_server,
    run_server,
    main,
    # Tool handlers
    handle_init,
    handle_build,
    handle_lint,
    handle_validate,
    handle_import,
    handle_list,
    handle_graph,
    # Result type
    ToolResult,
)

# Check if MCP is available
if MCP_AVAILABLE:
    # Create server instance
    server = create_server()

    # Or run the server directly
    import asyncio
    asyncio.run(run_server())
```

### Direct Handler Usage

You can use the tool handlers directly without running the MCP server:

```python
from wetwire_github.mcp_server import handle_build, handle_lint

# Build workflows
result = handle_build(package="ci/", output=".github/workflows/")
print(f"Success: {result.success}")
print(f"Message: {result.message}")

# Lint code
result = handle_lint(package="ci/", fix=True)
print(f"Success: {result.success}")
print(f"Message: {result.message}")
```

---

## See Also

- [CLI Reference](CLI.md) - Full CLI documentation
- [Quick Start](QUICK_START.md) - Getting started guide
- [Lint Rules](LINT_RULES.md) - WAG001-WAG015 rule documentation
- [MCP Specification](https://github.com/anthropics/mcp) - Model Context Protocol
