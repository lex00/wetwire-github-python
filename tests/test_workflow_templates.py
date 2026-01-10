"""Tests for GitHub workflow templates support."""

import yaml


class TestWorkflowTemplateTypes:
    """Tests for WorkflowTemplate dataclass types."""

    def test_workflow_template_dataclass_exists(self):
        """WorkflowTemplate dataclass can be imported."""
        from wetwire_github.workflow_templates import WorkflowTemplate

        assert WorkflowTemplate is not None

    def test_template_config_dataclass_exists(self):
        """TemplateConfig dataclass can be imported."""
        from wetwire_github.workflow_templates import TemplateConfig

        assert TemplateConfig is not None

    def test_template_category_dataclass_exists(self):
        """TemplateCategory dataclass can be imported."""
        from wetwire_github.workflow_templates import TemplateCategory

        assert TemplateCategory is not None


class TestWorkflowTemplate:
    """Tests for WorkflowTemplate dataclass."""

    def test_basic_workflow_template(self):
        """Basic workflow template can be created."""
        from wetwire_github.workflow import Job, Step, Triggers, Workflow
        from wetwire_github.workflow_templates import WorkflowTemplate

        workflow = Workflow(
            name="CI Template",
            on=Triggers(),
            jobs={
                "test": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(run="echo 'Hello World'")],
                )
            },
        )

        template = WorkflowTemplate(
            name="ci-template.yml",
            description="Basic CI workflow template",
            workflow=workflow,
        )

        assert template.name == "ci-template.yml"
        assert template.description == "Basic CI workflow template"
        assert template.workflow == workflow

    def test_workflow_template_with_icon(self):
        """Workflow template with icon can be created."""
        from wetwire_github.workflow import Workflow
        from wetwire_github.workflow_templates import WorkflowTemplate

        template = WorkflowTemplate(
            name="test.yml",
            description="Test template",
            workflow=Workflow(),
            icon="check",
        )

        assert template.icon == "check"

    def test_workflow_template_default_icon(self):
        """Workflow template has default icon."""
        from wetwire_github.workflow import Workflow
        from wetwire_github.workflow_templates import WorkflowTemplate

        template = WorkflowTemplate(
            name="test.yml",
            description="Test template",
            workflow=Workflow(),
        )

        assert template.icon == "rocket"

    def test_workflow_template_with_categories(self):
        """Workflow template with categories can be created."""
        from wetwire_github.workflow import Workflow
        from wetwire_github.workflow_templates import WorkflowTemplate

        template = WorkflowTemplate(
            name="test.yml",
            description="Test template",
            workflow=Workflow(),
            categories=["Continuous Integration", "Deployment"],
        )

        assert "Continuous Integration" in template.categories
        assert "Deployment" in template.categories

    def test_workflow_template_default_categories(self):
        """Workflow template has default empty categories."""
        from wetwire_github.workflow import Workflow
        from wetwire_github.workflow_templates import WorkflowTemplate

        template = WorkflowTemplate(
            name="test.yml",
            description="Test template",
            workflow=Workflow(),
        )

        assert template.categories == []


class TestTemplateVariables:
    """Tests for template variable preservation."""

    def test_template_with_default_branch_variable(self):
        """Template can use $default-branch variable."""
        from wetwire_github.workflow import Job, PushTrigger, Step, Triggers, Workflow
        from wetwire_github.workflow_templates import WorkflowTemplate

        workflow = Workflow(
            name="CI",
            on=Triggers(push=PushTrigger(branches=["$default-branch"])),
            jobs={
                "test": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(run="echo 'Testing on default branch'")],
                )
            },
        )

        _template = WorkflowTemplate(
            name="ci.yml",
            description="CI on default branch",
            workflow=workflow,
        )

        # Variables should be preserved in the workflow
        assert "$default-branch" in workflow.on.push.branches

    def test_template_with_protected_branches_variable(self):
        """Template can use $protected-branches variable."""
        from wetwire_github.workflow import Job, PushTrigger, Step, Triggers, Workflow
        from wetwire_github.workflow_templates import WorkflowTemplate

        workflow = Workflow(
            name="CI",
            on=Triggers(push=PushTrigger(branches=["$protected-branches"])),
            jobs={
                "test": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(run="echo 'Testing'")],
                )
            },
        )

        _template = WorkflowTemplate(
            name="ci.yml",
            description="CI on protected branches",
            workflow=workflow,
        )

        assert "$protected-branches" in workflow.on.push.branches

    def test_template_variables_in_step_run(self):
        """Template variables can be used in step run commands."""
        from wetwire_github.workflow import Job, Step, Triggers, Workflow
        from wetwire_github.workflow_templates import WorkflowTemplate

        workflow = Workflow(
            name="Deploy",
            on=Triggers(),
            jobs={
                "deploy": Job(
                    runs_on="ubuntu-latest",
                    steps=[
                        Step(
                            run="git push origin $default-branch"
                        )
                    ],
                )
            },
        )

        _template = WorkflowTemplate(
            name="deploy.yml",
            description="Deploy workflow",
            workflow=workflow,
        )

        assert "$default-branch" in workflow.jobs["deploy"].steps[0].run


class TestTemplateConfig:
    """Tests for TemplateConfig dataclass."""

    def test_basic_template_config(self):
        """Basic template config can be created."""
        from wetwire_github.workflow_templates import TemplateConfig

        config = TemplateConfig(
            name="CI Template",
            description="Basic CI workflow template",
            icon="check",
            categories=["Continuous Integration"],
        )

        assert config.name == "CI Template"
        assert config.description == "Basic CI workflow template"
        assert config.icon == "check"
        assert "Continuous Integration" in config.categories

    def test_template_config_to_properties(self):
        """TemplateConfig can be converted to properties format."""
        from wetwire_github.workflow_templates import TemplateConfig

        config = TemplateConfig(
            name="CI Template",
            description="Basic CI workflow template",
            icon="check",
            categories=["Continuous Integration", "Testing"],
        )

        properties = config.to_properties()

        assert "name=CI Template" in properties
        assert "description=Basic CI workflow template" in properties
        assert "iconName=check" in properties
        assert "categories=Continuous Integration,Testing" in properties

    def test_template_config_default_icon_in_properties(self):
        """TemplateConfig uses default icon in properties format."""
        from wetwire_github.workflow_templates import TemplateConfig

        config = TemplateConfig(
            name="Test",
            description="Test template",
        )

        properties = config.to_properties()

        assert "iconName=rocket" in properties

    def test_template_config_empty_categories_in_properties(self):
        """TemplateConfig handles empty categories in properties format."""
        from wetwire_github.workflow_templates import TemplateConfig

        config = TemplateConfig(
            name="Test",
            description="Test template",
        )

        properties = config.to_properties()

        # Empty categories should not be included or should be empty
        assert "categories=" not in properties or "categories=\n" in properties


class TestTemplateCategory:
    """Tests for TemplateCategory dataclass."""

    def test_predefined_categories(self):
        """Predefined categories are available."""
        from wetwire_github.workflow_templates import TemplateCategory

        assert TemplateCategory.CONTINUOUS_INTEGRATION == "Continuous Integration"
        assert TemplateCategory.DEPLOYMENT == "Deployment"
        assert TemplateCategory.TESTING == "Testing"
        assert TemplateCategory.CODE_QUALITY == "Code Quality"
        assert TemplateCategory.AUTOMATION == "Automation"


class TestWorkflowTemplateSerialization:
    """Tests for workflow template YAML serialization."""

    def test_serialize_template_workflow(self):
        """Template workflow serializes to valid YAML."""
        from wetwire_github.serialize import to_dict
        from wetwire_github.workflow import Job, PushTrigger, Step, Triggers, Workflow
        from wetwire_github.workflow_templates import WorkflowTemplate

        workflow = Workflow(
            name="CI",
            on=Triggers(push=PushTrigger(branches=["$default-branch"])),
            jobs={
                "test": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(run="echo 'Testing'")],
                )
            },
        )

        template = WorkflowTemplate(
            name="ci.yml",
            description="CI template",
            workflow=workflow,
        )

        result = to_dict(template.workflow)

        assert result["name"] == "CI"
        assert "on" in result
        assert "push" in result["on"]
        assert "$default-branch" in result["on"]["push"]["branches"]

    def test_template_variables_preserved_in_yaml(self):
        """Template variables are preserved in YAML output."""
        from wetwire_github.serialize import to_yaml
        from wetwire_github.workflow import Job, PushTrigger, Step, Triggers, Workflow
        from wetwire_github.workflow_templates import WorkflowTemplate

        workflow = Workflow(
            name="CI",
            on=Triggers(push=PushTrigger(branches=["$default-branch", "$protected-branches"])),
            jobs={
                "test": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(run="echo 'Testing'")],
                )
            },
        )

        template = WorkflowTemplate(
            name="ci.yml",
            description="CI template",
            workflow=workflow,
        )

        yaml_str = to_yaml(template.workflow)

        # Variables should be preserved as-is in YAML
        assert "$default-branch" in yaml_str
        assert "$protected-branches" in yaml_str

    def test_serialize_to_yaml_string(self):
        """Template workflow can be converted to YAML string."""
        from wetwire_github.serialize import to_dict
        from wetwire_github.workflow import Job, Step, Triggers, Workflow
        from wetwire_github.workflow_templates import WorkflowTemplate

        workflow = Workflow(
            name="Deploy",
            on=Triggers(),
            jobs={
                "deploy": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(run="make deploy")],
                )
            },
        )

        template = WorkflowTemplate(
            name="deploy.yml",
            description="Deploy template",
            workflow=workflow,
            icon="rocket",
            categories=["Deployment"],
        )

        result = to_dict(template.workflow)
        yaml_str = yaml.dump(result, sort_keys=False)

        assert "name: Deploy" in yaml_str
        assert "runs-on: ubuntu-latest" in yaml_str


class TestWorkflowTemplateToProperties:
    """Tests for WorkflowTemplate to_properties method."""

    def test_workflow_template_to_properties(self):
        """WorkflowTemplate can generate properties format."""
        from wetwire_github.workflow import Workflow
        from wetwire_github.workflow_templates import WorkflowTemplate

        template = WorkflowTemplate(
            name="ci.yml",
            description="CI workflow template",
            workflow=Workflow(name="CI"),
            icon="check",
            categories=["Continuous Integration", "Testing"],
        )

        properties = template.to_properties()

        assert "name=CI workflow template" in properties
        assert "description=CI workflow template" in properties
        assert "iconName=check" in properties
        assert "categories=Continuous Integration,Testing" in properties

    def test_workflow_template_to_properties_default_values(self):
        """WorkflowTemplate generates properties with defaults."""
        from wetwire_github.workflow import Workflow
        from wetwire_github.workflow_templates import WorkflowTemplate

        template = WorkflowTemplate(
            name="simple.yml",
            description="Simple template",
            workflow=Workflow(),
        )

        properties = template.to_properties()

        assert "name=Simple template" in properties
        assert "iconName=rocket" in properties


class TestMultipleTemplates:
    """Tests for handling multiple workflow templates."""

    def test_create_multiple_templates(self):
        """Multiple workflow templates can be created."""
        from wetwire_github.workflow import Job, Step, Triggers, Workflow
        from wetwire_github.workflow_templates import WorkflowTemplate

        ci_template = WorkflowTemplate(
            name="ci.yml",
            description="CI template",
            workflow=Workflow(
                name="CI",
                on=Triggers(),
                jobs={"test": Job(runs_on="ubuntu-latest", steps=[Step(run="test")])},
            ),
            categories=["Continuous Integration"],
        )

        deploy_template = WorkflowTemplate(
            name="deploy.yml",
            description="Deploy template",
            workflow=Workflow(
                name="Deploy",
                on=Triggers(),
                jobs={"deploy": Job(runs_on="ubuntu-latest", steps=[Step(run="deploy")])},
            ),
            categories=["Deployment"],
        )

        templates = [ci_template, deploy_template]

        assert len(templates) == 2
        assert templates[0].name == "ci.yml"
        assert templates[1].name == "deploy.yml"

    def test_templates_with_different_icons(self):
        """Templates can have different icons."""
        from wetwire_github.workflow import Workflow
        from wetwire_github.workflow_templates import WorkflowTemplate

        template1 = WorkflowTemplate(
            name="ci.yml",
            description="CI",
            workflow=Workflow(),
            icon="check",
        )

        template2 = WorkflowTemplate(
            name="deploy.yml",
            description="Deploy",
            workflow=Workflow(),
            icon="rocket",
        )

        assert template1.icon != template2.icon


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_template_with_empty_name(self):
        """Template can be created with empty name."""
        from wetwire_github.workflow import Workflow
        from wetwire_github.workflow_templates import WorkflowTemplate

        template = WorkflowTemplate(
            name="",
            description="Test",
            workflow=Workflow(),
        )

        assert template.name == ""

    def test_template_with_empty_description(self):
        """Template can be created with empty description."""
        from wetwire_github.workflow import Workflow
        from wetwire_github.workflow_templates import WorkflowTemplate

        template = WorkflowTemplate(
            name="test.yml",
            description="",
            workflow=Workflow(),
        )

        assert template.description == ""

    def test_template_config_with_special_characters(self):
        """TemplateConfig handles special characters in properties."""
        from wetwire_github.workflow_templates import TemplateConfig

        config = TemplateConfig(
            name="Test: CI/CD",
            description="A test template with special chars: =, \\n",
            icon="check",
        )

        properties = config.to_properties()

        # Properties format should handle these characters
        assert "name=" in properties
        assert "description=" in properties

    def test_template_with_many_categories(self):
        """Template can have many categories."""
        from wetwire_github.workflow import Workflow
        from wetwire_github.workflow_templates import WorkflowTemplate

        categories = [
            "Continuous Integration",
            "Deployment",
            "Testing",
            "Code Quality",
            "Automation",
            "Security",
        ]

        template = WorkflowTemplate(
            name="full.yml",
            description="Full featured template",
            workflow=Workflow(),
            categories=categories,
        )

        assert len(template.categories) == 6

    def test_properties_format_with_multiline_description(self):
        """TemplateConfig handles multiline descriptions."""
        from wetwire_github.workflow_templates import TemplateConfig

        config = TemplateConfig(
            name="Test",
            description="Line 1\nLine 2\nLine 3",
        )

        properties = config.to_properties()

        # Should handle or escape newlines appropriately
        assert "description=" in properties
