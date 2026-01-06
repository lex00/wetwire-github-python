"""Tests for GitHub Issue Templates (Issue Forms) support."""

import yaml


class TestIssueTemplateTypes:
    """Tests for Issue Template dataclass types."""

    def test_issue_template_dataclass_exists(self):
        """IssueTemplate dataclass can be imported."""
        from wetwire_github.issue_templates import IssueTemplate

        assert IssueTemplate is not None

    def test_input_element_exists(self):
        """Input element can be imported."""
        from wetwire_github.issue_templates import Input

        assert Input is not None

    def test_textarea_element_exists(self):
        """Textarea element can be imported."""
        from wetwire_github.issue_templates import Textarea

        assert Textarea is not None

    def test_dropdown_element_exists(self):
        """Dropdown element can be imported."""
        from wetwire_github.issue_templates import Dropdown

        assert Dropdown is not None

    def test_checkboxes_element_exists(self):
        """Checkboxes element can be imported."""
        from wetwire_github.issue_templates import Checkboxes

        assert Checkboxes is not None

    def test_markdown_element_exists(self):
        """Markdown element can be imported."""
        from wetwire_github.issue_templates import Markdown

        assert Markdown is not None


class TestInputElement:
    """Tests for Input form element."""

    def test_basic_input(self):
        """Basic input can be created."""
        from wetwire_github.issue_templates import Input

        inp = Input(
            label="Your name",
            id="name",
        )
        assert inp.label == "Your name"
        assert inp.id == "name"

    def test_input_with_description(self):
        """Input with description can be created."""
        from wetwire_github.issue_templates import Input

        inp = Input(
            label="Your name",
            id="name",
            description="Enter your full name",
        )
        assert inp.description == "Enter your full name"

    def test_input_with_placeholder(self):
        """Input with placeholder can be created."""
        from wetwire_github.issue_templates import Input

        inp = Input(
            label="Your name",
            id="name",
            placeholder="John Doe",
        )
        assert inp.placeholder == "John Doe"

    def test_input_required(self):
        """Required input can be created."""
        from wetwire_github.issue_templates import Input

        inp = Input(
            label="Your name",
            id="name",
            required=True,
        )
        assert inp.required is True

    def test_input_with_value(self):
        """Input with default value can be created."""
        from wetwire_github.issue_templates import Input

        inp = Input(
            label="Version",
            id="version",
            value="1.0.0",
        )
        assert inp.value == "1.0.0"


class TestTextareaElement:
    """Tests for Textarea form element."""

    def test_basic_textarea(self):
        """Basic textarea can be created."""
        from wetwire_github.issue_templates import Textarea

        ta = Textarea(
            label="Description",
            id="description",
        )
        assert ta.label == "Description"
        assert ta.id == "description"

    def test_textarea_with_render(self):
        """Textarea with render language can be created."""
        from wetwire_github.issue_templates import Textarea

        ta = Textarea(
            label="Code",
            id="code",
            render="python",
        )
        assert ta.render == "python"

    def test_textarea_with_value(self):
        """Textarea with default value can be created."""
        from wetwire_github.issue_templates import Textarea

        ta = Textarea(
            label="Steps",
            id="steps",
            value="1. First step\n2. Second step",
        )
        assert "First step" in ta.value


class TestDropdownElement:
    """Tests for Dropdown form element."""

    def test_basic_dropdown(self):
        """Basic dropdown can be created."""
        from wetwire_github.issue_templates import Dropdown

        dd = Dropdown(
            label="Priority",
            id="priority",
            options=["Low", "Medium", "High"],
        )
        assert dd.label == "Priority"
        assert len(dd.options) == 3

    def test_dropdown_multiple(self):
        """Multiple selection dropdown can be created."""
        from wetwire_github.issue_templates import Dropdown

        dd = Dropdown(
            label="Labels",
            id="labels",
            options=["bug", "feature", "docs"],
            multiple=True,
        )
        assert dd.multiple is True

    def test_dropdown_default(self):
        """Dropdown with default selection can be created."""
        from wetwire_github.issue_templates import Dropdown

        dd = Dropdown(
            label="Priority",
            id="priority",
            options=["Low", "Medium", "High"],
            default=1,  # Medium
        )
        assert dd.default == 1


class TestCheckboxesElement:
    """Tests for Checkboxes form element."""

    def test_basic_checkboxes(self):
        """Basic checkboxes can be created."""
        from wetwire_github.issue_templates import Checkboxes, CheckboxOption

        cb = Checkboxes(
            label="Acknowledgements",
            id="ack",
            options=[
                CheckboxOption(label="I have read the docs", required=True),
                CheckboxOption(label="This is not a duplicate"),
            ],
        )
        assert cb.label == "Acknowledgements"
        assert len(cb.options) == 2

    def test_checkbox_option_required(self):
        """Required checkbox option can be created."""
        from wetwire_github.issue_templates import CheckboxOption

        opt = CheckboxOption(label="Terms agreed", required=True)
        assert opt.required is True


class TestMarkdownElement:
    """Tests for Markdown form element."""

    def test_basic_markdown(self):
        """Basic markdown element can be created."""
        from wetwire_github.issue_templates import Markdown

        md = Markdown(
            value="## Instructions\n\nPlease fill out this form.",
        )
        assert "Instructions" in md.value


class TestIssueTemplate:
    """Tests for IssueTemplate dataclass."""

    def test_basic_issue_template(self):
        """Basic issue template can be created."""
        from wetwire_github.issue_templates import Input, IssueTemplate

        template = IssueTemplate(
            name="Bug Report",
            description="Report a bug",
            body=[
                Input(label="Title", id="title"),
            ],
        )
        assert template.name == "Bug Report"
        assert len(template.body) == 1

    def test_issue_template_with_labels(self):
        """Issue template with labels can be created."""
        from wetwire_github.issue_templates import Input, IssueTemplate

        template = IssueTemplate(
            name="Bug Report",
            description="Report a bug",
            labels=["bug", "triage"],
            body=[
                Input(label="Title", id="title"),
            ],
        )
        assert "bug" in template.labels

    def test_issue_template_with_title(self):
        """Issue template with title prefix can be created."""
        from wetwire_github.issue_templates import Input, IssueTemplate

        template = IssueTemplate(
            name="Bug Report",
            description="Report a bug",
            title="[BUG] ",
            body=[
                Input(label="Title", id="title"),
            ],
        )
        assert template.title == "[BUG] "

    def test_issue_template_with_assignees(self):
        """Issue template with assignees can be created."""
        from wetwire_github.issue_templates import Input, IssueTemplate

        template = IssueTemplate(
            name="Bug Report",
            description="Report a bug",
            assignees=["maintainer"],
            body=[
                Input(label="Title", id="title"),
            ],
        )
        assert "maintainer" in template.assignees

    def test_complex_issue_template(self):
        """Complex issue template with multiple elements can be created."""
        from wetwire_github.issue_templates import (
            Checkboxes,
            CheckboxOption,
            Dropdown,
            Input,
            IssueTemplate,
            Markdown,
            Textarea,
        )

        template = IssueTemplate(
            name="Bug Report",
            description="Report a bug in the project",
            labels=["bug"],
            body=[
                Markdown(value="## Bug Report\n\nThank you for reporting!"),
                Input(
                    label="Bug Title",
                    id="title",
                    description="Short summary",
                    required=True,
                ),
                Textarea(
                    label="Description",
                    id="description",
                    description="Detailed description",
                    required=True,
                ),
                Dropdown(
                    label="Severity",
                    id="severity",
                    options=["Low", "Medium", "High", "Critical"],
                ),
                Checkboxes(
                    label="Verification",
                    id="verification",
                    options=[
                        CheckboxOption(label="I searched for duplicates", required=True),
                    ],
                ),
            ],
        )
        assert template.name == "Bug Report"
        assert len(template.body) == 5


class TestIssueTemplateSerialization:
    """Tests for Issue Template YAML serialization."""

    def test_serialize_basic_template(self):
        """Basic template serializes to valid YAML."""
        from wetwire_github.issue_templates import Input, IssueTemplate
        from wetwire_github.serialize import to_dict

        template = IssueTemplate(
            name="Bug Report",
            description="Report a bug",
            body=[
                Input(label="Title", id="title", required=True),
            ],
        )

        result = to_dict(template)
        assert result["name"] == "Bug Report"
        assert result["description"] == "Report a bug"
        assert len(result["body"]) == 1
        assert result["body"][0]["type"] == "input"

    def test_serialize_to_yaml_string(self):
        """Template can be converted to YAML string."""
        from wetwire_github.issue_templates import Input, IssueTemplate
        from wetwire_github.serialize import to_dict

        template = IssueTemplate(
            name="Bug Report",
            description="Report a bug",
            body=[
                Input(label="Title", id="title"),
            ],
        )

        result = to_dict(template)
        yaml_str = yaml.dump(result, sort_keys=False)
        assert "name: Bug Report" in yaml_str
        assert "type: input" in yaml_str

    def test_serialize_all_element_types(self):
        """All element types serialize correctly."""
        from wetwire_github.issue_templates import (
            Checkboxes,
            CheckboxOption,
            Dropdown,
            Input,
            IssueTemplate,
            Markdown,
            Textarea,
        )
        from wetwire_github.serialize import to_dict

        template = IssueTemplate(
            name="Test",
            description="Test form",
            body=[
                Markdown(value="Hello"),
                Input(label="Name", id="name"),
                Textarea(label="Desc", id="desc"),
                Dropdown(label="Type", id="type", options=["A", "B"]),
                Checkboxes(
                    label="Check",
                    id="check",
                    options=[CheckboxOption(label="Yes")],
                ),
            ],
        )

        result = to_dict(template)
        types = [elem["type"] for elem in result["body"]]
        assert "markdown" in types
        assert "input" in types
        assert "textarea" in types
        assert "dropdown" in types
        assert "checkboxes" in types


class TestIssueTemplateCLIIntegration:
    """Tests for Issue Template CLI integration."""

    def test_build_type_issue_template_accepted(self):
        """Build command accepts --type issue-template."""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "build", "--help"],
            capture_output=True,
            text=True,
        )

        assert "issue-template" in result.stdout

    def test_import_type_issue_template_accepted(self):
        """Import command accepts --type issue-template."""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "import", "--help"],
            capture_output=True,
            text=True,
        )

        assert "issue-template" in result.stdout
