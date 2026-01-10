"""Tests for reusable workflow discovery and composition (issue #105)."""


class TestDiscoveredReusableWorkflow:
    """Tests for DiscoveredReusableWorkflow dataclass."""

    def test_dataclass_exists(self) -> None:
        """DiscoveredReusableWorkflow should exist in discover module."""
        from wetwire_github.discover import DiscoveredReusableWorkflow

        assert DiscoveredReusableWorkflow is not None

    def test_has_expected_fields(self) -> None:
        """DiscoveredReusableWorkflow should have name, inputs, outputs, secrets."""
        from wetwire_github.discover import DiscoveredReusableWorkflow

        workflow = DiscoveredReusableWorkflow(
            name="test-workflow",
            file_path="/path/to/workflow.py",
            inputs={"version": {"required": True, "type": "string"}},
            outputs={"result": "${{ jobs.build.outputs.result }}"},
            secrets=["DEPLOY_TOKEN", "NPM_TOKEN"],
        )

        assert workflow.name == "test-workflow"
        assert workflow.file_path == "/path/to/workflow.py"
        assert "version" in workflow.inputs
        assert "result" in workflow.outputs
        assert "DEPLOY_TOKEN" in workflow.secrets


class TestDiscoverReusableWorkflows:
    """Tests for discover_reusable_workflows function."""

    def test_discovers_workflow_with_workflow_call(self) -> None:
        """Should discover workflows that have on: workflow_call trigger."""
        from wetwire_github.discover import discover_reusable_workflows

        source = '''
from . import *

reusable = Workflow(
    name="Reusable Build",
    on=Triggers(
        workflow_call=WorkflowCallTrigger(
            inputs={"version": InputConfig(required=True, type="string")},
            outputs={"artifact": "${{ jobs.build.outputs.artifact }}"},
            secrets=["BUILD_TOKEN"],
        )
    ),
    jobs={"build": build_job},
)
'''
        workflows = discover_reusable_workflows(source, "reusable.py")
        assert len(workflows) == 1
        assert workflows[0].name == "Reusable Build"

    def test_ignores_non_reusable_workflows(self) -> None:
        """Should not include workflows without workflow_call trigger."""
        from wetwire_github.discover import discover_reusable_workflows

        source = '''
from . import *

ci = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger(branches=["main"])),
    jobs={"build": build_job},
)
'''
        workflows = discover_reusable_workflows(source, "ci.py")
        assert len(workflows) == 0

    def test_extracts_inputs(self) -> None:
        """Should extract input configurations from workflow_call."""
        from wetwire_github.discover import discover_reusable_workflows

        source = '''
from . import *

reusable = Workflow(
    name="Reusable",
    on=Triggers(
        workflow_call=WorkflowCallTrigger(
            inputs={
                "version": InputConfig(required=True, type="string"),
                "environment": InputConfig(required=False, type="string", default="dev"),
            },
        )
    ),
    jobs={"deploy": deploy_job},
)
'''
        workflows = discover_reusable_workflows(source, "reusable.py")
        assert len(workflows) == 1
        assert "version" in workflows[0].inputs
        assert "environment" in workflows[0].inputs

    def test_extracts_outputs(self) -> None:
        """Should extract output configurations from workflow_call."""
        from wetwire_github.discover import discover_reusable_workflows

        source = '''
from . import *

reusable = Workflow(
    name="Reusable",
    on=Triggers(
        workflow_call=WorkflowCallTrigger(
            outputs={
                "version": "${{ jobs.build.outputs.version }}",
                "sha": "${{ jobs.build.outputs.sha }}",
            },
        )
    ),
    jobs={"build": build_job},
)
'''
        workflows = discover_reusable_workflows(source, "reusable.py")
        assert len(workflows) == 1
        assert "version" in workflows[0].outputs
        assert "sha" in workflows[0].outputs

    def test_extracts_secrets(self) -> None:
        """Should extract secret names from workflow_call."""
        from wetwire_github.discover import discover_reusable_workflows

        source = '''
from . import *

reusable = Workflow(
    name="Reusable",
    on=Triggers(
        workflow_call=WorkflowCallTrigger(
            secrets=["DEPLOY_TOKEN", "NPM_TOKEN"],
        )
    ),
    jobs={"deploy": deploy_job},
)
'''
        workflows = discover_reusable_workflows(source, "reusable.py")
        assert len(workflows) == 1
        assert "DEPLOY_TOKEN" in workflows[0].secrets
        assert "NPM_TOKEN" in workflows[0].secrets


class TestWorkflowGraphComposition:
    """Tests for tracking workflow_call relationships in graph."""

    def test_add_workflow_call_edge(self) -> None:
        """Should be able to add workflow call edges to graph."""
        from wetwire_github.graph import WorkflowGraph

        graph = WorkflowGraph()
        graph.add_workflow_call("ci", "reusable-build")

        assert ("ci", "reusable-build") in graph.workflow_calls

    def test_workflow_calls_in_visualization(self) -> None:
        """Workflow calls should appear in Mermaid output."""
        from wetwire_github.graph import WorkflowGraph

        graph = WorkflowGraph()
        graph.add_workflow_call("ci", "reusable-build")

        mermaid = graph.to_mermaid()
        assert "ci" in mermaid
        assert "reusable-build" in mermaid


class TestWAG016ReusableWorkflowSuggestion:
    """Tests for WAG016: Suggest reusable workflows for duplicated patterns."""

    def test_detects_duplicated_job_patterns(self) -> None:
        """Should detect similar job patterns across multiple workflows."""
        from wetwire_github.linter.rules import WAG016SuggestReusableWorkflowExtraction

        rule = WAG016SuggestReusableWorkflowExtraction()
        source = '''
from . import *

# First workflow
ci = Workflow(
    name="CI",
    on=ci_triggers,
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            steps=[checkout(), setup_python(python_version="3.11"), Step(run="make build")],
        ),
    },
)

# Second workflow with similar job
pr = Workflow(
    name="PR",
    on=pr_triggers,
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            steps=[checkout(), setup_python(python_version="3.11"), Step(run="make build")],
        ),
    },
)
'''
        errors = rule.check(source, "workflows.py")
        assert len(errors) >= 1
        assert errors[0].rule_id == "WAG016"
        assert "reusable" in errors[0].message.lower()

    def test_no_warning_for_unique_jobs(self) -> None:
        """Should not warn when jobs are unique."""
        from wetwire_github.linter.rules import WAG016SuggestReusableWorkflowExtraction

        rule = WAG016SuggestReusableWorkflowExtraction()
        source = '''
from . import *

ci = Workflow(
    name="CI",
    on=ci_triggers,
    jobs={"build": build_job},
)

deploy = Workflow(
    name="Deploy",
    on=deploy_triggers,
    jobs={"deploy": deploy_job},
)
'''
        errors = rule.check(source, "workflows.py")
        assert len(errors) == 0

    def test_rule_in_default_set(self) -> None:
        """WAG016 should be in the default rule set."""
        from wetwire_github.linter.rules import get_default_rules

        rules = get_default_rules()
        rule_ids = [r.id for r in rules]
        assert "WAG016" in rule_ids
