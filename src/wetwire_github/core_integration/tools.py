"""Tool definitions and handlers for wetwire-core integration.

Provides RunnerAgent tool definitions and implementations for
AI-assisted workflow design sessions.
"""

from typing import Any


def get_tool_definitions() -> list[dict[str, Any]]:
    """Get tool definitions for wetwire-core RunnerAgent.

    Returns:
        List of tool specifications with name, description, and parameters.
    """
    return [
        {
            "name": "build_workflow",
            "description": "Build GitHub Actions YAML from Python workflow declarations",
            "parameters": {
                "type": "object",
                "properties": {
                    "package_path": {
                        "type": "string",
                        "description": "Path to Python package containing workflow declarations",
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Directory to write generated YAML files",
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["yaml", "json"],
                        "default": "yaml",
                        "description": "Output format",
                    },
                },
                "required": ["package_path"],
            },
        },
        {
            "name": "validate_workflow",
            "description": "Validate GitHub Actions YAML files using actionlint",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Paths to YAML files to validate",
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["text", "json"],
                        "default": "text",
                        "description": "Output format",
                    },
                },
                "required": ["file_paths"],
            },
        },
        {
            "name": "lint_workflow",
            "description": "Apply code quality rules (WAG001-WAG0XX) to workflow Python code",
            "parameters": {
                "type": "object",
                "properties": {
                    "package_path": {
                        "type": "string",
                        "description": "Path to Python package to lint",
                    },
                    "fix": {
                        "type": "boolean",
                        "default": False,
                        "description": "Automatically fix fixable issues",
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["text", "json"],
                        "default": "text",
                        "description": "Output format",
                    },
                },
                "required": ["package_path"],
            },
        },
        {
            "name": "list_workflows",
            "description": "List discovered workflows and jobs from Python packages",
            "parameters": {
                "type": "object",
                "properties": {
                    "package_path": {
                        "type": "string",
                        "description": "Path to Python package to scan",
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["table", "json"],
                        "default": "table",
                        "description": "Output format",
                    },
                },
                "required": ["package_path"],
            },
        },
        {
            "name": "import_workflow",
            "description": "Convert existing YAML workflow to Python declarations",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Paths to YAML files to import",
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Directory for generated Python code",
                    },
                    "single_file": {
                        "type": "boolean",
                        "default": False,
                        "description": "Generate all code in single file",
                    },
                },
                "required": ["file_paths"],
            },
        },
        {
            "name": "graph_workflow",
            "description": "Generate dependency graph visualization of workflow jobs",
            "parameters": {
                "type": "object",
                "properties": {
                    "package_path": {
                        "type": "string",
                        "description": "Path to Python package to analyze",
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["mermaid", "dot"],
                        "default": "mermaid",
                        "description": "Graph output format",
                    },
                },
                "required": ["package_path"],
            },
        },
    ]


def handle_tool_call(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Handle a tool call from wetwire-core RunnerAgent.

    Args:
        tool_name: Name of the tool to invoke
        arguments: Tool arguments

    Returns:
        Result dictionary with success status and output/error
    """
    handlers = {
        "build_workflow": _handle_build_workflow,
        "validate_workflow": _handle_validate_workflow,
        "lint_workflow": _handle_lint_workflow,
        "list_workflows": _handle_list_workflows,
        "import_workflow": _handle_import_workflow,
        "graph_workflow": _handle_graph_workflow,
    }

    handler = handlers.get(tool_name)
    if handler is None:
        return {"success": False, "error": f"Unknown tool: {tool_name}"}

    try:
        return handler(arguments)
    except Exception as e:
        return {"success": False, "error": str(e)}


def _handle_build_workflow(arguments: dict[str, Any]) -> dict[str, Any]:
    """Handle build_workflow tool call."""
    from wetwire_github.cli.build import build_workflows

    package_path = arguments.get("package_path", ".")
    output_dir = arguments.get("output_dir", ".github/workflows/")
    output_format = arguments.get("output_format", "yaml")

    exit_code, messages = build_workflows(
        package_path=package_path,
        output_dir=output_dir,
        output_format=output_format,
    )

    return {
        "success": exit_code == 0,
        "exit_code": exit_code,
        "files": messages if exit_code == 0 else [],
        "errors": messages if exit_code != 0 else [],
    }


def _handle_validate_workflow(arguments: dict[str, Any]) -> dict[str, Any]:
    """Handle validate_workflow tool call."""
    from wetwire_github.cli.validate import validate_files

    file_paths = arguments.get("file_paths", [])
    output_format = arguments.get("output_format", "text")

    exit_code, output = validate_files(
        file_paths=file_paths,
        output_format=output_format,
    )

    return {
        "success": exit_code == 0,
        "exit_code": exit_code,
        "output": output,
    }


def _handle_lint_workflow(arguments: dict[str, Any]) -> dict[str, Any]:
    """Handle lint_workflow tool call."""
    from wetwire_github.cli.lint_cmd import lint_package

    package_path = arguments.get("package_path", ".")
    fix = arguments.get("fix", False)
    output_format = arguments.get("output_format", "text")

    exit_code, output = lint_package(
        package_path=package_path,
        output_format=output_format,
        fix=fix,
    )

    return {
        "success": exit_code == 0,
        "exit_code": exit_code,
        "output": output,
    }


def _handle_list_workflows(arguments: dict[str, Any]) -> dict[str, Any]:
    """Handle list_workflows tool call."""
    from wetwire_github.cli.list_cmd import list_resources

    package_path = arguments.get("package_path", ".")
    output_format = arguments.get("output_format", "table")

    exit_code, output = list_resources(
        package_path=package_path,
        output_format=output_format,
    )

    # Parse output to extract workflow info for structured result
    workflows = []
    if exit_code == 0 and output:
        # Simple extraction from table output
        for line in output.split("\n"):
            if "Workflow" in line:
                parts = line.split()
                if len(parts) >= 3:
                    workflows.append({"type": "Workflow", "name": parts[1]})

    return {
        "success": exit_code == 0,
        "exit_code": exit_code,
        "workflows": workflows,
        "output": output,
    }


def _handle_import_workflow(arguments: dict[str, Any]) -> dict[str, Any]:
    """Handle import_workflow tool call."""
    from wetwire_github.cli.import_cmd import import_workflows

    file_paths = arguments.get("file_paths", [])
    output_dir = arguments.get("output_dir", ".")
    single_file = arguments.get("single_file", False)

    exit_code, messages = import_workflows(
        file_paths=file_paths,
        output_dir=output_dir,
        single_file=single_file,
        no_scaffold=True,
    )

    return {
        "success": exit_code == 0,
        "exit_code": exit_code,
        "files": messages if exit_code == 0 else [],
        "errors": messages if exit_code != 0 else [],
    }


def _handle_graph_workflow(arguments: dict[str, Any]) -> dict[str, Any]:
    """Handle graph_workflow tool call."""
    from wetwire_github.cli.graph_cmd import graph_workflows

    package_path = arguments.get("package_path", ".")
    output_format = arguments.get("output_format", "mermaid")

    exit_code, output = graph_workflows(
        package_path=package_path,
        output_format=output_format,
    )

    return {
        "success": exit_code == 0,
        "exit_code": exit_code,
        "output": output,
    }
