"""Design command implementation.

AI-assisted infrastructure design via wetwire-core integration.
"""

import importlib.util

from wetwire_github.core_integration import (
    create_session,
    create_stream_handler,
    get_tool_definitions,
)


def design_workflow(
    stream: bool = False,
    max_lint_cycles: int = 3,
) -> tuple[int, str]:
    """Run AI-assisted workflow design session.

    This command requires wetwire-core to be installed for full functionality.

    Args:
        stream: Whether to stream output
        max_lint_cycles: Maximum lint feedback cycles

    Returns:
        Tuple of (exit_code, output_string)
    """
    # Check if wetwire-core is available
    if importlib.util.find_spec("wetwire_core") is not None:
        return _run_design_session(stream, max_lint_cycles)
    else:
        return 1, _no_wetwire_core_message()


def _no_wetwire_core_message() -> str:
    """Return message when wetwire-core is not installed."""
    return """Design command requires wetwire-core package.

To install wetwire-core:
    pip install wetwire-core

Or add to your project dependencies:
    wetwire-core>=0.1.0

The design command provides AI-assisted workflow generation:
  - Interactive design sessions
  - Lint feedback integration
  - Workflow templating

For more information, visit: https://github.com/anthropics/wetwire-core
"""


def _run_design_session(stream: bool, max_lint_cycles: int) -> tuple[int, str]:
    """Run the actual design session with wetwire-core.

    Integrates with wetwire-core RunnerAgent for AI-assisted workflow design.
    """
    # Create session and stream handler
    session = create_session({"max_lint_cycles": max_lint_cycles})
    handler = create_stream_handler() if stream else None

    # Get available tools for the agent
    tools = get_tool_definitions()

    # Build output message
    lines = [
        f"Design session started: {session['session_id'][:8]}...",
        f"Available tools: {len(tools)}",
        "",
        "Tools available:",
    ]

    for tool in tools:
        lines.append(f"  - {tool['name']}: {tool['description']}")

    lines.extend([
        "",
        "wetwire-core integration ready.",
        "Use wetwire-core RunnerAgent with these tools for AI-assisted design.",
    ])

    output = "\n".join(lines)

    if handler:
        handler.write(output)

    return 0, output
