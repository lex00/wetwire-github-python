"""MCP (Model Context Protocol) server for wetwire-github.

Provides AI agent integration via the Model Context Protocol,
enabling tools like Kiro CLI to interact with wetwire-github commands.

Usage:
    wetwire-github mcp-server

Or via Python:
    python -m wetwire_github.mcp_server
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

# Optional MCP dependency - gracefully handle if not installed
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent, Tool

    MCP_AVAILABLE = True
except ImportError:
    Server = None  # type: ignore[misc, assignment]
    stdio_server = None  # type: ignore[misc, assignment]
    TextContent = None  # type: ignore[misc, assignment]
    Tool = None  # type: ignore[misc, assignment]
    MCP_AVAILABLE = False

if TYPE_CHECKING:
    from mcp.server import Server as ServerType


@dataclass
class ToolResult:
    """Result from a tool handler."""

    success: bool
    message: str


def get_tool_definitions() -> list:
    """Get list of MCP tool definitions.

    Returns:
        List of Tool objects defining available commands.
    """
    if not MCP_AVAILABLE:
        return []

    return [
        Tool(
            name="wetwire_init",
            description="Create a new wetwire-github project with example workflow. "
            "Scaffolds project structure with pyproject.toml and sample code.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Project name",
                    },
                    "output": {
                        "type": "string",
                        "description": "Output directory (default: current directory)",
                    },
                },
            },
        ),
        Tool(
            name="wetwire_build",
            description="Generate GitHub Actions YAML from Python workflow declarations. "
            "Discovers Workflow objects and serializes to .github/workflows/.",
            inputSchema={
                "type": "object",
                "properties": {
                    "package": {
                        "type": "string",
                        "description": "Python package path to discover workflows from",
                    },
                    "output": {
                        "type": "string",
                        "description": "Output directory (default: .github/workflows/)",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["yaml", "json"],
                        "description": "Output format (default: yaml)",
                    },
                },
            },
        ),
        Tool(
            name="wetwire_lint",
            description="Run code quality rules (WAG001-WAG008) on Python workflow code. "
            "Checks for typed action wrappers, expression builders, secrets access.",
            inputSchema={
                "type": "object",
                "properties": {
                    "package": {
                        "type": "string",
                        "description": "Python package path to lint",
                    },
                    "fix": {
                        "type": "boolean",
                        "description": "Automatically fix fixable issues",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["text", "json"],
                        "description": "Output format (default: text)",
                    },
                },
            },
        ),
        Tool(
            name="wetwire_validate",
            description="Validate generated YAML files using actionlint. "
            "Checks for GitHub Actions workflow syntax errors.",
            inputSchema={
                "type": "object",
                "properties": {
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "YAML files to validate",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["text", "json"],
                        "description": "Output format (default: text)",
                    },
                },
            },
        ),
        Tool(
            name="wetwire_import",
            description="Convert existing GitHub Actions YAML to typed Python code. "
            "Imports workflow files and generates typed declarations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "YAML files to import",
                    },
                    "output": {
                        "type": "string",
                        "description": "Output directory for generated Python code",
                    },
                    "single_file": {
                        "type": "boolean",
                        "description": "Generate all code in a single file",
                    },
                },
            },
        ),
        Tool(
            name="wetwire_list",
            description="List discovered workflows and jobs from Python packages. "
            "Shows all Workflow objects found in the specified package.",
            inputSchema={
                "type": "object",
                "properties": {
                    "package": {
                        "type": "string",
                        "description": "Python package path to discover from",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["table", "json"],
                        "description": "Output format (default: table)",
                    },
                },
            },
        ),
        Tool(
            name="wetwire_graph",
            description="Generate DAG visualization of workflow job dependencies. "
            "Creates mermaid or graphviz diagrams showing job relationships.",
            inputSchema={
                "type": "object",
                "properties": {
                    "package": {
                        "type": "string",
                        "description": "Python package path to analyze",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["dot", "mermaid"],
                        "description": "Output format (default: mermaid)",
                    },
                    "output": {
                        "type": "string",
                        "description": "Output file path",
                    },
                },
            },
        ),
    ]


def handle_init(name: str | None = None, output: str = ".") -> ToolResult:
    """Handle wetwire_init tool call.

    Args:
        name: Project name.
        output: Output directory.

    Returns:
        ToolResult with success status and message.
    """
    from wetwire_github.cli.init_cmd import init_project

    exit_code, messages = init_project(name=name, output_dir=output)

    return ToolResult(
        success=exit_code == 0,
        message="\n".join(messages) if messages else "Project initialized",
    )


def handle_build(
    package: str | None = None,
    output: str = ".github/workflows/",
    format: str = "yaml",
) -> ToolResult:
    """Handle wetwire_build tool call.

    Args:
        package: Python package path to discover workflows from.
        output: Output directory for generated files.
        format: Output format (yaml or json).

    Returns:
        ToolResult with success status and message.
    """
    from wetwire_github.cli.build import build_workflows

    exit_code, messages = build_workflows(
        package_path=package or ".",
        output_dir=output,
        output_format=format,
    )

    return ToolResult(
        success=exit_code == 0,
        message="\n".join(messages) if messages else "Build complete",
    )


def handle_lint(
    package: str | None = None,
    fix: bool = False,
    format: str = "text",
) -> ToolResult:
    """Handle wetwire_lint tool call.

    Args:
        package: Python package path to lint.
        fix: Whether to auto-fix issues.
        format: Output format (text or json).

    Returns:
        ToolResult with success status and message.
    """
    from wetwire_github.cli.lint_cmd import lint_package

    exit_code, output = lint_package(
        package_path=package or ".",
        output_format=format,
        fix=fix,
    )

    return ToolResult(
        success=exit_code == 0,
        message=output or "Lint complete",
    )


def handle_validate(
    files: list[str] | None = None,
    format: str = "text",
) -> ToolResult:
    """Handle wetwire_validate tool call.

    Args:
        files: YAML files to validate.
        format: Output format (text or json).

    Returns:
        ToolResult with success status and message.
    """
    from wetwire_github.cli.validate import validate_files

    exit_code, output = validate_files(
        file_paths=files or [],
        output_format=format,
    )

    return ToolResult(
        success=exit_code == 0,
        message=output or "Validation complete",
    )


def handle_import(
    files: list[str] | None = None,
    output: str | None = None,
    single_file: bool = False,
) -> ToolResult:
    """Handle wetwire_import tool call.

    Args:
        files: YAML files to import.
        output: Output directory for generated code.
        single_file: Whether to generate a single file.

    Returns:
        ToolResult with success status and message.
    """
    from wetwire_github.cli.import_cmd import import_workflows

    exit_code, messages = import_workflows(
        file_paths=files or [],
        output_dir=output or ".",
        single_file=single_file,
        no_scaffold=False,
    )

    return ToolResult(
        success=exit_code == 0,
        message="\n".join(messages) if messages else "Import complete",
    )


def handle_list(
    package: str | None = None,
    format: str = "table",
) -> ToolResult:
    """Handle wetwire_list tool call.

    Args:
        package: Python package path to discover from.
        format: Output format (table or json).

    Returns:
        ToolResult with success status and message.
    """
    from wetwire_github.cli.list_cmd import list_resources

    exit_code, output = list_resources(
        package_path=package or ".",
        output_format=format,
    )

    return ToolResult(
        success=exit_code == 0,
        message=output or "No workflows found",
    )


def handle_graph(
    package: str | None = None,
    format: str = "mermaid",
    output: str | None = None,
) -> ToolResult:
    """Handle wetwire_graph tool call.

    Args:
        package: Python package path to analyze.
        format: Output format (dot or mermaid).
        output: Output file path.

    Returns:
        ToolResult with success status and message.
    """
    from wetwire_github.cli.graph_cmd import graph_workflows

    exit_code, graph_output = graph_workflows(
        package_path=package or ".",
        output_format=format,
        output_file=output,
    )

    return ToolResult(
        success=exit_code == 0,
        message=graph_output or "Graph generated",
    )


def create_server() -> ServerType:
    """Create and configure the MCP server.

    Returns:
        Configured MCP server instance.

    Raises:
        ImportError: If mcp package is not installed.
    """
    if not MCP_AVAILABLE or Server is None:
        raise ImportError(
            "MCP package is required for server functionality. "
            "Install with: pip install mcp"
        )

    server = Server("wetwire-github-mcp")

    @server.list_tools()
    async def list_tools() -> list:
        """List available tools."""
        return get_tool_definitions()

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list:
        """Handle tool calls."""
        # TextContent is guaranteed to be available since we checked MCP_AVAILABLE
        assert TextContent is not None

        handlers = {
            "wetwire_init": handle_init,
            "wetwire_build": handle_build,
            "wetwire_lint": handle_lint,
            "wetwire_validate": handle_validate,
            "wetwire_import": handle_import,
            "wetwire_list": handle_list,
            "wetwire_graph": handle_graph,
        }

        if name not in handlers:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        try:
            result = handlers[name](**arguments)
            status = "Success" if result.success else "Failed"
            return [TextContent(type="text", text=f"[{status}] {result.message}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {e!s}")]

    return server


async def run_server() -> None:
    """Run the MCP server with stdio transport.

    This is the main entry point for the MCP server.
    """
    if not MCP_AVAILABLE or stdio_server is None:
        raise ImportError(
            "MCP package is required for server functionality. "
            "Install with: pip install mcp"
        )

    server = create_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_server())
