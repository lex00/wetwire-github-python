"""MCP (Model Context Protocol) server for wetwire-github.

Provides AI agent integration via the Model Context Protocol,
enabling tools like Claude Code and Kiro CLI to interact with wetwire-github commands.

Usage:
    wetwire-github mcp-server

Or via Python:
    python -m wetwire_github.mcp_server

Environment Variables:
    WETWIRE_MCP_DEBUG: Set to "1" or "true" to enable verbose debug logging

For more information, see docs/MCP_SERVER.md
"""

from __future__ import annotations

import logging
import os
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

# Configure logging based on environment
_debug_enabled = os.environ.get("WETWIRE_MCP_DEBUG", "").lower() in ("1", "true", "yes")
_log_level = logging.DEBUG if _debug_enabled else logging.WARNING

logging.basicConfig(
    level=_log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("wetwire_github.mcp")

# Optional MCP dependency - gracefully handle if not installed
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent, Tool

    MCP_AVAILABLE = True
    logger.debug("MCP package loaded successfully")
except ImportError as _import_error:
    Server = None  # type: ignore[misc, assignment]
    stdio_server = None  # type: ignore[misc, assignment]
    TextContent = None  # type: ignore[misc, assignment]
    Tool = None  # type: ignore[misc, assignment]
    MCP_AVAILABLE = False
    _MCP_IMPORT_ERROR = _import_error
    logger.debug("MCP package not available: %s", _import_error)

if TYPE_CHECKING:
    from mcp.server import Server as ServerType


def _get_mcp_install_instructions() -> str:
    """Get installation instructions for MCP package.

    Returns:
        String with installation instructions.
    """
    return """
MCP (Model Context Protocol) package is required for server functionality.

Install with pip:
    pip install wetwire-github[mcp]

Or with uv:
    uv pip install wetwire-github[mcp]

Or install mcp directly:
    pip install mcp

For more information, see:
    https://github.com/anthropics/mcp
    docs/MCP_SERVER.md
""".strip()


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
    logger.info("Executing wetwire_init: name=%s, output=%s", name, output)

    try:
        from wetwire_github.cli.init_cmd import init_project

        exit_code, messages = init_project(name=name, output_dir=output)
        success = exit_code == 0
        message = "\n".join(messages) if messages else "Project initialized"

        if success:
            logger.info("wetwire_init completed successfully")
        else:
            logger.warning("wetwire_init failed: %s", message)

        return ToolResult(success=success, message=message)
    except Exception as e:
        logger.exception("wetwire_init raised an exception")
        return ToolResult(success=False, message=f"Error initializing project: {e!s}")


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
    logger.info(
        "Executing wetwire_build: package=%s, output=%s, format=%s",
        package,
        output,
        format,
    )

    try:
        from wetwire_github.cli.build import build_workflows

        exit_code, messages = build_workflows(
            package_path=package or ".",
            output_dir=output,
            output_format=format,
        )
        success = exit_code == 0
        message = "\n".join(messages) if messages else "Build complete"

        if success:
            logger.info("wetwire_build completed successfully")
        else:
            logger.warning("wetwire_build failed: %s", message)

        return ToolResult(success=success, message=message)
    except Exception as e:
        logger.exception("wetwire_build raised an exception")
        return ToolResult(success=False, message=f"Error building workflows: {e!s}")


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
    logger.info(
        "Executing wetwire_lint: package=%s, fix=%s, format=%s",
        package,
        fix,
        format,
    )

    try:
        from wetwire_github.cli.lint_cmd import lint_package

        exit_code, output = lint_package(
            package_path=package or ".",
            output_format=format,
            fix=fix,
        )
        success = exit_code == 0
        message = output or "Lint complete"

        if success:
            logger.info("wetwire_lint completed successfully")
        else:
            logger.warning("wetwire_lint found issues: %s", message)

        return ToolResult(success=success, message=message)
    except Exception as e:
        logger.exception("wetwire_lint raised an exception")
        return ToolResult(success=False, message=f"Error linting package: {e!s}")


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
    logger.info("Executing wetwire_validate: files=%s, format=%s", files, format)

    try:
        from wetwire_github.cli.validate import validate_files

        exit_code, output = validate_files(
            file_paths=files or [],
            output_format=format,
        )
        success = exit_code == 0
        message = output or "Validation complete"

        if success:
            logger.info("wetwire_validate completed successfully")
        else:
            logger.warning("wetwire_validate found issues: %s", message)

        return ToolResult(success=success, message=message)
    except Exception as e:
        logger.exception("wetwire_validate raised an exception")
        return ToolResult(success=False, message=f"Error validating files: {e!s}")


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
    logger.info(
        "Executing wetwire_import: files=%s, output=%s, single_file=%s",
        files,
        output,
        single_file,
    )

    try:
        from wetwire_github.cli.import_cmd import import_workflows

        exit_code, messages = import_workflows(
            file_paths=files or [],
            output_dir=output or ".",
            single_file=single_file,
            no_scaffold=False,
        )
        success = exit_code == 0
        message = "\n".join(messages) if messages else "Import complete"

        if success:
            logger.info("wetwire_import completed successfully")
        else:
            logger.warning("wetwire_import failed: %s", message)

        return ToolResult(success=success, message=message)
    except Exception as e:
        logger.exception("wetwire_import raised an exception")
        return ToolResult(success=False, message=f"Error importing workflows: {e!s}")


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
    logger.info("Executing wetwire_list: package=%s, format=%s", package, format)

    try:
        from wetwire_github.cli.list_cmd import list_resources

        exit_code, output = list_resources(
            package_path=package or ".",
            output_format=format,
        )
        success = exit_code == 0
        message = output or "No workflows found"

        if success:
            logger.info("wetwire_list completed successfully")
        else:
            logger.warning("wetwire_list failed: %s", message)

        return ToolResult(success=success, message=message)
    except Exception as e:
        logger.exception("wetwire_list raised an exception")
        return ToolResult(success=False, message=f"Error listing workflows: {e!s}")


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
    logger.info(
        "Executing wetwire_graph: package=%s, format=%s, output=%s",
        package,
        format,
        output,
    )

    try:
        from wetwire_github.cli.graph_cmd import graph_workflows

        exit_code, graph_output = graph_workflows(
            package_path=package or ".",
            output_format=format,
            output_file=output,
        )
        success = exit_code == 0
        message = graph_output or "Graph generated"

        if success:
            logger.info("wetwire_graph completed successfully")
        else:
            logger.warning("wetwire_graph failed: %s", message)

        return ToolResult(success=success, message=message)
    except Exception as e:
        logger.exception("wetwire_graph raised an exception")
        return ToolResult(success=False, message=f"Error generating graph: {e!s}")


def create_server() -> ServerType:
    """Create and configure the MCP server.

    Returns:
        Configured MCP server instance.

    Raises:
        ImportError: If mcp package is not installed.
    """
    if not MCP_AVAILABLE or Server is None:
        logger.error("Cannot create MCP server: mcp package not installed")
        raise ImportError(_get_mcp_install_instructions())

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

        logger.debug("Tool call received: name=%s, arguments=%s", name, arguments)

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
            logger.warning("Unknown tool requested: %s", name)
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        try:
            result = handlers[name](**arguments)
            status = "Success" if result.success else "Failed"
            logger.debug("Tool %s completed: status=%s", name, status)
            return [TextContent(type="text", text=f"[{status}] {result.message}")]
        except Exception as e:
            logger.exception("Tool %s raised an exception", name)
            return [TextContent(type="text", text=f"Error: {e!s}")]

    logger.info("MCP server created successfully")
    return server


async def run_server() -> None:
    """Run the MCP server with stdio transport.

    This is the main entry point for the MCP server.
    """
    if not MCP_AVAILABLE or stdio_server is None:
        logger.error("Cannot run MCP server: mcp package not installed")
        raise ImportError(_get_mcp_install_instructions())

    logger.info("Starting MCP server...")
    server = create_server()
    async with stdio_server() as (read_stream, write_stream):
        logger.info("MCP server running on stdio transport")
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )
    logger.info("MCP server stopped")


def main() -> None:
    """Main entry point for the MCP server executable.

    This function is used as the entry point for the wetwire-github-mcp script.
    """
    import asyncio

    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("MCP server interrupted by user")
    except ImportError as e:
        # Print a user-friendly message for missing dependencies
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.exception("MCP server failed with unexpected error")
        print(f"Error: {e!s}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
