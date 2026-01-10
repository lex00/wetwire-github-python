"""Persona-based testing for wetwire-core integration.

Provides personas for testing workflow quality from different perspectives.

The personas are organized into two categories:

Domain Personas (workflow quality focus):
- reviewer: Code review perspective
- senior-dev: Reliability and performance focus
- security: Supply chain and access control focus
- beginner: Learning-friendly workflow evaluation

Spec-Standard Personas (per WETWIRE_SPEC.md Section 7):
- expert: Deep knowledge, precise requirements
- terse: Minimal information, expects inference
- verbose: Over-explains, buries requirements in prose
"""

from typing import Any

from wetwire_github.core_integration.scoring import score_workflow

# Define available personas
PERSONAS = [
    {
        "name": "reviewer",
        "description": "Code reviewer focused on maintainability and best practices",
        "criteria": [
            "Workflow has clear, descriptive name",
            "Jobs are well-organized and named",
            "Uses pinned action versions for reproducibility",
            "Has appropriate permissions defined",
            "Follows GitHub Actions best practices",
        ],
        "weight_overrides": {
            "has_name": 1.5,
            "job_naming": 1.5,
            "uses_pinned_actions": 2.0,
            "has_permissions": 2.0,
        },
    },
    {
        "name": "senior-dev",
        "description": "Senior developer focused on reliability and performance",
        "criteria": [
            "Workflow is efficient with caching enabled",
            "Has timeout limits to prevent runaway jobs",
            "Uses concurrency control to avoid resource waste",
            "Properly uses checkout for repository access",
            "Has reasonable job dependencies",
        ],
        "weight_overrides": {
            "uses_cache": 2.0,
            "has_timeout": 2.0,
            "has_concurrency": 2.0,
            "uses_checkout": 1.5,
        },
    },
    {
        "name": "security",
        "description": "Security engineer focused on supply chain and access control",
        "criteria": [
            "Uses least-privilege permissions",
            "Actions are pinned to specific versions/SHAs",
            "No secrets exposed in workflow",
            "Uses protected branches appropriately",
            "Has proper token handling",
        ],
        "weight_overrides": {
            "has_permissions": 3.0,
            "uses_pinned_actions": 3.0,
        },
    },
    {
        "name": "beginner",
        "description": "New developer learning GitHub Actions",
        "criteria": [
            "Workflow structure is clear and understandable",
            "Comments or descriptions explain purpose",
            "Uses common, well-documented actions",
            "Has reasonable defaults",
            "Not overly complex",
        ],
        "weight_overrides": {
            "has_name": 2.0,
            "has_triggers": 1.5,
            "has_jobs": 1.5,
        },
    },
    # Spec-standard personas per WETWIRE_SPEC.md Section 7
    {
        "name": "expert",
        "description": "Deep knowledge, precise requirements, minimal hand-holding",
        "criteria": [
            "Workflow uses advanced features appropriately",
            "Optimized for performance and efficiency",
            "Uses precise action versioning",
            "Follows security best practices",
            "No unnecessary complexity",
        ],
        "weight_overrides": {
            "uses_pinned_actions": 2.5,
            "uses_cache": 2.0,
            "has_concurrency": 2.0,
            "has_permissions": 2.5,
            "has_timeout": 1.5,
        },
    },
    {
        "name": "terse",
        "description": "Minimal information, expects system to infer defaults",
        "criteria": [
            "Workflow is concise without unnecessary verbosity",
            "Uses sensible defaults where possible",
            "Minimal configuration overhead",
            "Simple and direct step commands",
            "No redundant steps or jobs",
        ],
        "weight_overrides": {
            "has_name": 1.0,
            "has_jobs": 2.0,
            "uses_checkout": 1.5,
        },
    },
    {
        "name": "verbose",
        "description": "Over-explains, buries requirements in prose",
        "criteria": [
            "Workflow handles edge cases gracefully",
            "Has comprehensive error handling",
            "Covers multiple scenarios",
            "Uses matrix builds for coverage",
            "Has proper job dependencies",
        ],
        "weight_overrides": {
            "has_name": 1.5,
            "has_triggers": 2.0,
            "uses_cache": 1.5,
            "has_concurrency": 1.5,
        },
    },
]


def get_available_personas() -> list[dict[str, Any]]:
    """Get list of available testing personas.

    Returns:
        List of persona dictionaries with name, description, and criteria
    """
    return PERSONAS.copy()


def get_persona(name: str) -> dict[str, Any] | None:
    """Get a specific persona by name.

    Args:
        name: Persona name

    Returns:
        Persona dictionary or None if not found
    """
    for persona in PERSONAS:
        if persona["name"] == name:
            return persona.copy()
    return None


def run_persona_test(
    persona_name: str,
    workflow_path: str,
    scenario: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run a persona-based test against a workflow.

    Args:
        persona_name: Name of persona to use
        workflow_path: Path to workflow YAML file
        scenario: Optional scenario configuration

    Returns:
        Test result with passed status and feedback
    """
    persona = get_persona(persona_name)
    if persona is None:
        return {
            "passed": False,
            "feedback": f"Unknown persona: {persona_name}",
            "score": 0,
        }

    # Score the workflow
    base_score = score_workflow(workflow_path)

    # Apply persona weight overrides
    weighted_score = _apply_persona_weights(base_score, persona)

    # Determine pass/fail based on persona threshold
    threshold = scenario.get("threshold", 70) if scenario else 70
    passed = weighted_score["total_score"] >= threshold

    # Generate feedback based on persona perspective
    feedback = _generate_persona_feedback(persona, base_score, weighted_score, passed)

    return {
        "passed": passed,
        "persona": persona_name,
        "score": weighted_score["total_score"],
        "threshold": threshold,
        "feedback": feedback,
        "details": weighted_score.get("details", {}),
    }


def _apply_persona_weights(
    score: dict[str, Any],
    persona: dict[str, Any],
) -> dict[str, Any]:
    """Apply persona-specific weights to scores.

    Args:
        score: Base score from score_workflow
        persona: Persona with weight_overrides

    Returns:
        Weighted score dictionary
    """
    weights = persona.get("weight_overrides", {})
    details = score.get("details", {})
    checks = details.get("checks", [])

    if not checks:
        return score.copy()

    # Apply weights to checks
    weighted_points = 0
    weighted_max = 0

    for check in checks:
        check_name = check.get("name", "")
        weight = weights.get(check_name, 1.0)

        weighted_points += check.get("score", 0) * weight
        weighted_max += check.get("max_score", 0) * weight

    percentage = (weighted_points / weighted_max * 100) if weighted_max > 0 else 0

    return {
        "total_score": round(percentage, 1),
        "weighted_points": round(weighted_points, 1),
        "weighted_max": round(weighted_max, 1),
        "details": details,
    }


def _generate_persona_feedback(
    persona: dict[str, Any],
    base_score: dict[str, Any],
    weighted_score: dict[str, Any],
    passed: bool,
) -> str:
    """Generate feedback from persona's perspective.

    Args:
        persona: Persona dictionary
        base_score: Original score
        weighted_score: Persona-weighted score
        passed: Whether the test passed

    Returns:
        Feedback string
    """
    persona_name = persona["name"]
    score = weighted_score["total_score"]

    if passed:
        intro = f"As a {persona_name}, this workflow meets my standards."
    else:
        intro = f"As a {persona_name}, this workflow needs improvement."

    # Find failed checks
    details = base_score.get("details", {})
    checks = details.get("checks", [])
    failed_checks = [c for c in checks if not c.get("passed", True)]

    feedback_lines = [intro, f"Score: {score}/100", ""]

    if failed_checks:
        feedback_lines.append("Issues to address:")
        for check in failed_checks:
            desc = check.get("description", check.get("name", "unknown"))
            feedback_lines.append(f"  - {desc}")

    # Add persona-specific advice
    weights = persona.get("weight_overrides", {})
    priority_checks = [c for c in failed_checks if c.get("name") in weights]

    if priority_checks:
        feedback_lines.append("")
        feedback_lines.append("Priority improvements for this persona:")
        for check in priority_checks:
            desc = check.get("description", check.get("name", "unknown"))
            feedback_lines.append(f"  * {desc}")

    return "\n".join(feedback_lines)


def run_all_persona_tests(
    workflow_path: str,
    scenario: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run all persona tests against a workflow.

    Args:
        workflow_path: Path to workflow YAML file
        scenario: Optional scenario configuration

    Returns:
        Combined test results from all personas
    """
    results: dict[str, dict[str, Any]] = {}
    all_passed = True

    for persona in PERSONAS:
        persona_name = str(persona["name"])
        result = run_persona_test(persona_name, workflow_path, scenario)
        results[persona_name] = result
        if not result["passed"]:
            all_passed = False

    return {
        "all_passed": all_passed,
        "results": results,
        "personas_passed": sum(1 for r in results.values() if r["passed"]),
        "personas_total": len(PERSONAS),
    }
