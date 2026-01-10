"""Design command implementation.

AI-assisted infrastructure design via wetwire-core integration.
"""

from typing import Any

from wetwire_github.core_integration import (
    create_session,
    create_stream_handler,
    get_tool_definitions,
    handle_tool_call,
)


def design_workflow(
    stream: bool = False,
    max_lint_cycles: int = 3,
    output_dir: str | None = None,
    prompt: str | None = None,
    tool: str | None = None,
    tool_args: dict[str, Any] | None = None,
) -> tuple[int, str]:
    """Run AI-assisted workflow design session.

    Args:
        stream: Whether to stream output
        max_lint_cycles: Maximum lint feedback cycles
        output_dir: Output directory for generated workflows
        prompt: Initial prompt for design session
        tool: Tool to execute directly (for scripting)
        tool_args: Arguments for direct tool execution

    Returns:
        Tuple of (exit_code, output_string)
    """
    # If tool is specified, execute it directly
    if tool:
        return _execute_tool(tool, tool_args or {})

    # Run the design session
    return _run_design_session(stream, max_lint_cycles, output_dir, prompt)


def _execute_tool(tool_name: str, arguments: dict[str, Any]) -> tuple[int, str]:
    """Execute a tool directly and return results."""
    result = handle_tool_call(tool_name, arguments)

    if result.get("success", False):
        output_parts = [f"Tool: {tool_name}", "Status: Success", ""]

        # Format output based on tool type
        if "output" in result:
            output_parts.append(result["output"])
        elif "files" in result:
            output_parts.append("Files:")
            for f in result.get("files", []):
                output_parts.append(f"  - {f}")
        elif "workflows" in result:
            output_parts.append("Workflows:")
            for w in result.get("workflows", []):
                output_parts.append(f"  - {w.get('name', 'unnamed')}")

        return 0, "\n".join(output_parts)
    else:
        error = result.get("error", "Unknown error")
        output = result.get("output", "")
        message = f"Tool: {tool_name}\nStatus: Failed\nError: {error}"
        if output:
            message += f"\n\nOutput:\n{output}"
        return 1, message


def _run_design_session(
    stream: bool,
    max_lint_cycles: int,
    output_dir: str | None,
    prompt: str | None,
) -> tuple[int, str]:
    """Run the actual design session with wetwire-core.

    Integrates with wetwire-core RunnerAgent for AI-assisted workflow design.
    """
    # Create session and stream handler
    session_metadata = {"max_lint_cycles": max_lint_cycles}
    if output_dir:
        session_metadata["output_dir"] = output_dir
    if prompt:
        session_metadata["initial_prompt"] = prompt

    session = create_session(session_metadata)
    handler = create_stream_handler() if stream else None

    # Get available tools for the agent
    tools = get_tool_definitions()

    # Build output message
    lines = [
        f"Design session started: {session['session_id'][:8]}...",
        f"Available tools: {len(tools)}",
    ]

    if output_dir:
        lines.append(f"Output directory: {output_dir}")

    if prompt:
        lines.extend(["", f"Initial prompt: {prompt}"])

    lines.extend(["", "Tools available:"])

    for tool in tools:
        lines.append(f"  - {tool['name']}: {tool['description']}")

    lines.extend([
        "",
        "Session ready for AI-assisted workflow design.",
        "",
        "To use this session with wetwire-core:",
        "  from wetwire_core import RunnerAgent",
        "  agent = RunnerAgent(tools=tools, session=session)",
        "  agent.run(prompt)",
    ])

    output = "\n".join(lines)

    if handler:
        handler.write(output)

    return 0, output
