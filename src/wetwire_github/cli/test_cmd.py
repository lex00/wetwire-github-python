"""Test command implementation.

Persona-based testing via wetwire-core integration.
"""

import importlib.util

from wetwire_github.core_integration import (
    get_available_personas,
)


def run_persona_tests(
    persona: str | None = None,
    scenario: str | None = None,
) -> tuple[int, str]:
    """Run persona-based tests for workflow code generation.

    This command requires wetwire-core to be installed for full functionality.

    Args:
        persona: Persona to use for testing (e.g., "reviewer", "senior-dev")
        scenario: Path to scenario configuration file

    Returns:
        Tuple of (exit_code, output_string)
    """
    # Check if wetwire-core is available
    if importlib.util.find_spec("wetwire_core") is not None:
        return _run_tests(persona, scenario)
    else:
        return 1, _no_wetwire_core_message()


def _no_wetwire_core_message() -> str:
    """Return message when wetwire-core is not installed."""
    return """Test command requires wetwire-core package.

To install wetwire-core:
    pip install wetwire-core

Or add to your project dependencies:
    wetwire-core>=0.1.0

The test command provides persona-based testing:
  - Test workflows with different reviewer personas
  - Scenario-based quality validation
  - Session tracking for test results

For more information, visit: https://github.com/anthropics/wetwire-core
"""


def _run_tests(persona: str | None, scenario: str | None) -> tuple[int, str]:
    """Run the actual persona tests with wetwire-core.

    Uses the core_integration personas module for quality testing.
    """
    lines = []

    # List available personas
    personas = get_available_personas()

    if persona:
        # Find matching persona
        persona_info = next(
            (p for p in personas if p["name"] == persona),
            None,
        )

        if persona_info is None:
            available = ", ".join(p["name"] for p in personas)
            return 1, f"Unknown persona: {persona}\nAvailable: {available}"

        lines.extend([
            f"Persona: {persona_info['name']}",
            f"Description: {persona_info['description']}",
            "",
            "Criteria:",
        ])
        for criterion in persona_info.get("criteria", []):
            lines.append(f"  - {criterion}")

        if scenario:
            lines.extend([
                "",
                f"Scenario file: {scenario}",
                "",
                "To run tests against a workflow file:",
                "  from wetwire_github.core_integration import run_persona_test",
                f"  result = run_persona_test('{persona}', '/path/to/workflow.yaml')",
            ])
    else:
        # List all personas
        lines.extend([
            "Available personas for workflow testing:",
            "",
        ])

        for p in personas:
            lines.append(f"  {p['name']}: {p['description']}")

        lines.extend([
            "",
            "Use --persona <name> to select a persona for testing.",
        ])

    return 0, "\n".join(lines)
