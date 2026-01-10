"""Tests for the loader module.

The loader module provides namespace setup functions for injecting
workflow types and action wrappers into namespaces.
"""


class TestSetupWorkflowNamespace:
    """Tests for setup_workflow_namespace function."""

    def test_injects_core_types(self):
        """setup_workflow_namespace injects Workflow, Job, Step, etc."""
        from wetwire_github.loader import setup_workflow_namespace

        namespace: dict = {}
        setup_workflow_namespace(namespace)

        assert "Workflow" in namespace
        assert "Job" in namespace
        assert "Step" in namespace
        assert "Triggers" in namespace
        assert "Matrix" in namespace
        assert "Strategy" in namespace

    def test_injects_trigger_types(self):
        """setup_workflow_namespace injects trigger types."""
        from wetwire_github.loader import setup_workflow_namespace

        namespace: dict = {}
        setup_workflow_namespace(namespace)

        assert "PushTrigger" in namespace
        assert "PullRequestTrigger" in namespace
        assert "ScheduleTrigger" in namespace
        assert "WorkflowDispatchTrigger" in namespace

    def test_injects_expression_builders(self):
        """setup_workflow_namespace injects expression builders."""
        from wetwire_github.loader import setup_workflow_namespace

        namespace: dict = {}
        setup_workflow_namespace(namespace)

        assert "Secrets" in namespace
        assert "GitHub" in namespace
        assert "always" in namespace
        assert "failure" in namespace
        assert "success" in namespace
        assert "cancelled" in namespace

    def test_types_are_correct_classes(self):
        """Injected types are the correct classes."""
        from wetwire_github.loader import setup_workflow_namespace
        from wetwire_github.workflow import Job, Step, Workflow

        namespace: dict = {}
        setup_workflow_namespace(namespace)

        assert namespace["Workflow"] is Workflow
        assert namespace["Job"] is Job
        assert namespace["Step"] is Step


class TestSetupActions:
    """Tests for setup_actions function."""

    def test_injects_action_wrappers(self):
        """setup_actions injects typed action wrapper functions."""
        from wetwire_github.loader import setup_actions

        namespace: dict = {}
        setup_actions(namespace)

        assert "checkout" in namespace
        assert "setup_python" in namespace
        assert "setup_node" in namespace
        assert "setup_go" in namespace
        assert "setup_java" in namespace
        assert "cache" in namespace
        assert "upload_artifact" in namespace
        assert "download_artifact" in namespace

    def test_action_wrappers_are_callable(self):
        """Injected action wrappers are callable."""
        from wetwire_github.loader import setup_actions

        namespace: dict = {}
        setup_actions(namespace)

        for name in ["checkout", "setup_python", "cache"]:
            assert callable(namespace[name])

    def test_action_wrappers_match_actions_module(self):
        """Injected wrappers match those from actions module."""
        from wetwire_github.actions import checkout, setup_python
        from wetwire_github.loader import setup_actions

        namespace: dict = {}
        setup_actions(namespace)

        assert namespace["checkout"] is checkout
        assert namespace["setup_python"] is setup_python


class TestSetupAll:
    """Tests for setup_all function."""

    def test_injects_workflow_types_and_actions(self):
        """setup_all injects both workflow types and action wrappers."""
        from wetwire_github.loader import setup_all

        namespace: dict = {}
        setup_all(namespace)

        # Workflow types
        assert "Workflow" in namespace
        assert "Job" in namespace
        assert "Step" in namespace

        # Action wrappers
        assert "checkout" in namespace
        assert "setup_python" in namespace

        # Expression builders
        assert "Secrets" in namespace
        assert "always" in namespace

    def test_can_use_with_globals(self):
        """setup_all can be used with globals()."""
        from wetwire_github.loader import setup_all

        # Simulate using with globals()
        namespace: dict = {}
        setup_all(namespace)

        # Should be able to create a workflow using the injected types
        workflow_cls = namespace["Workflow"]
        job_cls = namespace["Job"]
        step_cls = namespace["Step"]
        triggers_cls = namespace["Triggers"]
        push_trigger_cls = namespace["PushTrigger"]

        ci = workflow_cls(
            name="CI",
            on=triggers_cls(push=push_trigger_cls(branches=["main"])),
            jobs={
                "test": job_cls(
                    runs_on="ubuntu-latest",
                    steps=[step_cls(run="pytest")],
                )
            },
        )

        assert ci.name == "CI"


class TestGetAllExports:
    """Tests for get_all_exports function."""

    def test_returns_dict_of_exports(self):
        """get_all_exports returns a dict of all exportable items."""
        from wetwire_github.loader import get_all_exports

        exports = get_all_exports()

        assert isinstance(exports, dict)
        assert "Workflow" in exports
        assert "Job" in exports
        assert "checkout" in exports
        assert "Secrets" in exports

    def test_exports_are_correct_types(self):
        """Exported items are the correct types."""
        from wetwire_github.loader import get_all_exports
        from wetwire_github.workflow import Workflow

        exports = get_all_exports()

        assert exports["Workflow"] is Workflow
