"""Test command implementation.

Persona-based testing via wetwire-core integration.
"""

from pathlib import Path
from typing import Any

from wetwire_github.core_integration import (
    get_available_personas,
    run_persona_test,
)
from wetwire_github.core_integration.personas import run_all_persona_tests


def run_persona_tests(
    persona: str | None = None,
    workflow: str | None = None,
    threshold: int = 70,
    all_personas: bool = False,
    scenario: str | None = None,
    provider: str = "anthropic",
) -> tuple[int, str]:
    """Run persona-based tests for workflow code generation.

    Args:
        persona: Persona to use for testing (e.g., "reviewer", "senior-dev")
        workflow: Path to workflow YAML file to test
        threshold: Score threshold for pass/fail (default: 70)
        all_personas: Run all personas against the workflow
        scenario: Path to scenario configuration file
        provider: AI provider to use ('anthropic' or 'kiro')

    Returns:
        Tuple of (exit_code, output_string)
    """
    if provider == "kiro":
        return _run_kiro_tests(workflow, threshold, scenario)
    return _run_tests(persona, workflow, threshold, all_personas, scenario)


def _run_tests(
    persona: str | None,
    workflow: str | None,
    threshold: int,
    all_personas: bool,
    scenario: str | None,
) -> tuple[int, str]:
    """Run the actual persona tests with wetwire-core.

    Uses the core_integration personas module for quality testing.
    """
    lines: list[str] = []

    # List available personas
    personas = get_available_personas()

    # If workflow is provided, run actual tests
    if workflow:
        workflow_path = Path(workflow)
        if not workflow_path.exists():
            return 1, f"Error: Workflow file not found: {workflow}"

        # Build scenario dict with threshold
        scenario_dict = {"threshold": threshold}
        if scenario:
            scenario_dict["file"] = scenario

        if all_personas or (not persona):
            # Run all personas against the workflow
            result = run_all_persona_tests(str(workflow_path), scenario_dict)
            return _format_all_results(result)
        else:
            # Run single persona test
            result = run_persona_test(persona, str(workflow_path), scenario_dict)
            return _format_single_result(result)

    # No workflow provided - show persona info
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

        lines.extend([
            "",
            "Use --workflow <file> to test a workflow file.",
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
            "Use --workflow <file> to test a workflow file.",
        ])

    return 0, "\n".join(lines)


def _format_single_result(result: dict[str, Any]) -> tuple[int, str]:
    """Format a single persona test result."""
    lines = []

    passed = result.get("passed", False)
    persona = result.get("persona", "unknown")
    score = result.get("score", 0)
    threshold_val = result.get("threshold", 70)

    status = "PASSED" if passed else "FAILED"
    lines.append(f"Persona Test: {persona} - {status}")
    lines.append(f"Score: {score}/100 (threshold: {threshold_val})")
    lines.append("")

    feedback = result.get("feedback", "")
    if feedback:
        lines.append(feedback)

    exit_code = 0 if passed else 1
    return exit_code, "\n".join(lines)


def _format_all_results(result: dict[str, Any]) -> tuple[int, str]:
    """Format results from all personas."""
    lines = []

    all_passed = result.get("all_passed", False)
    passed_count = result.get("personas_passed", 0)
    total_count = result.get("personas_total", 0)

    lines.append(f"Persona Test Results: {passed_count}/{total_count} passed")
    lines.append("")

    results = result.get("results", {})
    for persona_name, persona_result in results.items():
        passed = persona_result.get("passed", False)
        score = persona_result.get("score", 0)
        status = "PASS" if passed else "FAIL"
        lines.append(f"  {persona_name}: {status} ({score}/100)")

    lines.append("")

    # Show detailed feedback for failed personas
    failed = [
        (name, res)
        for name, res in results.items()
        if not res.get("passed", True)
    ]

    if failed:
        lines.append("Failed persona details:")
        for name, res in failed:
            lines.append(f"\n--- {name} ---")
            feedback = res.get("feedback", "")
            if feedback:
                lines.append(feedback)

    exit_code = 0 if all_passed else 1
    return exit_code, "\n".join(lines)


def _run_kiro_tests(
    workflow: str | None,
    threshold: int,
    scenario: str | None,
) -> tuple[int, str]:
    """Run tests using Kiro CLI provider.

    Uses the kiro module for scenario-based testing with Kiro CLI.
    """
    try:
        from wetwire_github.kiro import run_kiro_scenario
    except ImportError:
        return 1, "Kiro integration requires mcp package.\nInstall with: pip install wetwire-github[kiro]"

    if not workflow:
        return 1, "Error: --workflow is required for kiro provider"

    prompt = f"Test workflow: {workflow}"
    if scenario:
        prompt = f"Test scenario from {scenario}"

    result = run_kiro_scenario(
        prompt=prompt,
        timeout=300,
    )

    # Format results
    lines = [
        "--- Kiro Test Results ---",
        f"Success: {result.get('success', False)}",
        f"Exit code: {result.get('exit_code', 1)}",
    ]

    if result.get("stdout"):
        lines.append("")
        lines.append("--- Output ---")
        lines.append(result["stdout"][:2000])

    if result.get("stderr"):
        lines.append("")
        lines.append("--- Errors ---")
        lines.append(result["stderr"][:1000])

    exit_code = 0 if result.get("success", False) else 1
    return exit_code, "\n".join(lines)
