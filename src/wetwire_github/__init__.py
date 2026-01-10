"""wetwire-github: Generate GitHub YAML configurations from typed Python declarations."""

__version__ = "0.1.0"

# Core workflow types
# MCP server
from wetwire_github import mcp_server
from wetwire_github.workflow import (
    Job,
    Matrix,
    Step,
    Strategy,
    Triggers,
    Workflow,
)

# Expression builders
from wetwire_github.workflow.expressions import (
    GitHub,
    Secrets,
    always,
    cancelled,
    failure,
    success,
)
from wetwire_github.workflow.expressions import (
    Matrix as MatrixContext,
)

# Trigger types
from wetwire_github.workflow.triggers import (
    PullRequestTrigger,
    PushTrigger,
    ScheduleTrigger,
    WorkflowDispatchTrigger,
)

__all__ = [
    # Version
    "__version__",
    # Core types
    "Job",
    "Matrix",
    "Step",
    "Strategy",
    "Triggers",
    "Workflow",
    # Trigger types
    "PullRequestTrigger",
    "PushTrigger",
    "ScheduleTrigger",
    "WorkflowDispatchTrigger",
    # Expression builders
    "GitHub",
    "MatrixContext",
    "Secrets",
    "always",
    "cancelled",
    "failure",
    "success",
    # MCP
    "mcp_server",
]
