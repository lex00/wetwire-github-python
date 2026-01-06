"""Session management for wetwire-core integration.

Provides session creation, tracking, and result persistence.
"""

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def create_session(metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create a new design session.

    Args:
        metadata: Optional metadata to include in session

    Returns:
        Session dictionary with unique ID and timestamps
    """
    session_id = str(uuid.uuid4())
    now = datetime.now(UTC).isoformat()

    session = {
        "session_id": session_id,
        "created_at": now,
        "updated_at": now,
        "status": "active",
        "metadata": metadata or {},
        "events": [],
        "result": None,
    }

    return session


def add_session_event(
    session: dict[str, Any],
    event_type: str,
    data: dict[str, Any] | None = None,
) -> None:
    """Add an event to the session history.

    Args:
        session: Session dictionary
        event_type: Type of event (e.g., "tool_call", "user_input", "output")
        data: Optional event data
    """
    now = datetime.now(UTC).isoformat()

    event = {
        "timestamp": now,
        "type": event_type,
        "data": data or {},
    }

    session["events"].append(event)
    session["updated_at"] = now


def complete_session(
    session: dict[str, Any],
    result: dict[str, Any] | None = None,
    status: str = "completed",
) -> None:
    """Mark session as completed.

    Args:
        session: Session dictionary
        result: Optional result data
        status: Session status (default: "completed")
    """
    now = datetime.now(UTC).isoformat()

    session["status"] = status
    session["result"] = result
    session["updated_at"] = now
    session["completed_at"] = now


def write_session_result(session: dict[str, Any], output_path: str) -> None:
    """Write session result to file.

    Args:
        session: Session dictionary to write
        output_path: Path to output file (JSON format)
    """
    path = Path(output_path)

    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write session as JSON
    with path.open("w") as f:
        json.dump(session, f, indent=2)


def load_session(session_path: str) -> dict[str, Any]:
    """Load session from file.

    Args:
        session_path: Path to session file

    Returns:
        Session dictionary
    """
    path = Path(session_path)

    with path.open() as f:
        return json.load(f)


def list_sessions(sessions_dir: str) -> list[dict[str, Any]]:
    """List all sessions in a directory.

    Args:
        sessions_dir: Directory containing session files

    Returns:
        List of session summaries
    """
    path = Path(sessions_dir)
    sessions = []

    if not path.exists():
        return sessions

    for session_file in path.glob("*.json"):
        try:
            session = load_session(str(session_file))
            sessions.append({
                "session_id": session.get("session_id"),
                "status": session.get("status"),
                "created_at": session.get("created_at"),
                "file": str(session_file),
            })
        except Exception:
            # Skip malformed session files
            continue

    return sorted(sessions, key=lambda s: s.get("created_at", ""), reverse=True)
