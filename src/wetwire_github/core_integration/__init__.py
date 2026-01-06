"""wetwire-core integration module.

Provides integration with wetwire-core for AI-assisted workflow design,
including tool definitions, handlers, streaming, and session management.
"""

from wetwire_github.core_integration.personas import (
    get_available_personas,
    run_persona_test,
)
from wetwire_github.core_integration.scoring import score_workflow
from wetwire_github.core_integration.session import (
    create_session,
    write_session_result,
)
from wetwire_github.core_integration.stream import create_stream_handler
from wetwire_github.core_integration.tools import (
    get_tool_definitions,
    handle_tool_call,
)

__all__ = [
    "get_tool_definitions",
    "handle_tool_call",
    "create_stream_handler",
    "create_session",
    "write_session_result",
    "score_workflow",
    "get_available_personas",
    "run_persona_test",
]
