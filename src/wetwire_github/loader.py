"""Namespace setup functions for workflow types and actions.

This module provides functions to inject workflow types and action
wrappers into a namespace, enabling simplified imports and dynamic
loading patterns.

Usage:
    # Inject all workflow types into globals
    from wetwire_github.loader import setup_workflow_namespace
    setup_workflow_namespace(globals())

    # Now you can use Workflow, Job, Step directly
    ci = Workflow(name="CI", ...)

    # Or inject everything including actions
    from wetwire_github.loader import setup_all
    setup_all(globals())
"""

from typing import Any

__all__ = [
    "setup_workflow_namespace",
    "setup_actions",
    "setup_all",
    "get_all_exports",
]


def setup_workflow_namespace(namespace: dict[str, Any]) -> None:
    """Inject workflow types into a namespace.

    This function adds all core workflow types, trigger types, and
    expression builders to the provided namespace dictionary.

    Args:
        namespace: Dictionary to inject types into (e.g., globals())

    Example:
        from wetwire_github.loader import setup_workflow_namespace
        setup_workflow_namespace(globals())

        # Now you can use types directly
        ci = Workflow(
            name="CI",
            on=Triggers(push=PushTrigger(branches=["main"])),
            jobs={"build": Job(runs_on="ubuntu-latest", steps=[...])},
        )
    """
    # Core workflow types
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

    # Trigger types
    from wetwire_github.workflow.triggers import (
        PullRequestTrigger,
        PushTrigger,
        ScheduleTrigger,
        WorkflowDispatchTrigger,
    )

    namespace.update(
        {
            # Core types
            "Workflow": Workflow,
            "Job": Job,
            "Step": Step,
            "Triggers": Triggers,
            "Matrix": Matrix,
            "Strategy": Strategy,
            # Trigger types
            "PushTrigger": PushTrigger,
            "PullRequestTrigger": PullRequestTrigger,
            "ScheduleTrigger": ScheduleTrigger,
            "WorkflowDispatchTrigger": WorkflowDispatchTrigger,
            # Expression builders
            "Secrets": Secrets,
            "GitHub": GitHub,
            "always": always,
            "failure": failure,
            "success": success,
            "cancelled": cancelled,
        }
    )


def setup_actions(namespace: dict[str, Any]) -> None:
    """Inject typed action wrappers into a namespace.

    This function adds all typed action wrapper functions to the
    provided namespace dictionary.

    Args:
        namespace: Dictionary to inject actions into (e.g., globals())

    Example:
        from wetwire_github.loader import setup_actions
        setup_actions(globals())

        # Now you can use action wrappers directly
        steps = [
            checkout(fetch_depth=0),
            setup_python(python_version="3.11"),
        ]
    """
    from wetwire_github.actions import (
        cache,
        checkout,
        create_github_app_token,
        download_artifact,
        gh_pages,
        labeler,
        setup_go,
        setup_java,
        setup_node,
        setup_python,
        upload_artifact,
        upload_pages_artifact,
        upload_release_asset,
    )

    namespace.update(
        {
            "checkout": checkout,
            "setup_python": setup_python,
            "setup_node": setup_node,
            "setup_go": setup_go,
            "setup_java": setup_java,
            "cache": cache,
            "create_github_app_token": create_github_app_token,
            "gh_pages": gh_pages,
            "labeler": labeler,
            "upload_artifact": upload_artifact,
            "download_artifact": download_artifact,
            "upload_pages_artifact": upload_pages_artifact,
            "upload_release_asset": upload_release_asset,
        }
    )


def setup_all(namespace: dict[str, Any]) -> None:
    """Inject all workflow types and action wrappers into a namespace.

    This is a convenience function that calls both setup_workflow_namespace
    and setup_actions.

    Args:
        namespace: Dictionary to inject into (e.g., globals())

    Example:
        from wetwire_github.loader import setup_all
        setup_all(globals())

        # Now everything is available
        ci = Workflow(
            name="CI",
            on=Triggers(push=PushTrigger(branches=["main"])),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[
                        checkout(),
                        setup_python(python_version="3.11"),
                        Step(run="pytest"),
                    ],
                ),
            },
        )
    """
    setup_workflow_namespace(namespace)
    setup_actions(namespace)


def get_all_exports() -> dict[str, Any]:
    """Get a dictionary of all exportable workflow types and actions.

    Returns:
        Dictionary mapping names to their corresponding types/functions.

    Example:
        from wetwire_github.loader import get_all_exports

        exports = get_all_exports()
        Workflow = exports["Workflow"]
        checkout = exports["checkout"]
    """
    exports: dict[str, Any] = {}
    setup_all(exports)
    return exports
