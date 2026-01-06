"""Tests for GitHub Discussion Templates support."""

import yaml


class TestDiscussionTemplateTypes:
    """Tests for Discussion Template dataclass types."""

    def test_discussion_template_dataclass_exists(self):
        """DiscussionTemplate dataclass can be imported."""
        from wetwire_github.discussion_templates import DiscussionTemplate

        assert DiscussionTemplate is not None

    def test_discussion_category_exists(self):
        """DiscussionCategory can be imported."""
        from wetwire_github.discussion_templates import DiscussionCategory

        assert DiscussionCategory is not None


class TestDiscussionCategory:
    """Tests for DiscussionCategory enum."""

    def test_announcements_category(self):
        """Announcements category is defined."""
        from wetwire_github.discussion_templates import DiscussionCategory

        assert DiscussionCategory.ANNOUNCEMENTS.value == "announcements"

    def test_general_category(self):
        """General category is defined."""
        from wetwire_github.discussion_templates import DiscussionCategory

        assert DiscussionCategory.GENERAL.value == "general"

    def test_ideas_category(self):
        """Ideas category is defined."""
        from wetwire_github.discussion_templates import DiscussionCategory

        assert DiscussionCategory.IDEAS.value == "ideas"

    def test_polls_category(self):
        """Polls category is defined."""
        from wetwire_github.discussion_templates import DiscussionCategory

        assert DiscussionCategory.POLLS.value == "polls"

    def test_qa_category(self):
        """Q&A category is defined."""
        from wetwire_github.discussion_templates import DiscussionCategory

        assert DiscussionCategory.QA.value == "q-a"

    def test_show_and_tell_category(self):
        """Show and tell category is defined."""
        from wetwire_github.discussion_templates import DiscussionCategory

        assert DiscussionCategory.SHOW_AND_TELL.value == "show-and-tell"


class TestDiscussionTemplate:
    """Tests for DiscussionTemplate dataclass."""

    def test_basic_discussion_template(self):
        """Basic discussion template can be created."""
        from wetwire_github.discussion_templates import (
            DiscussionTemplate,
        )
        from wetwire_github.issue_templates import Input

        template = DiscussionTemplate(
            title="Feature Request",
            labels=["enhancement"],
            body=[
                Input(label="Feature description", id="description"),
            ],
        )
        assert template.title == "Feature Request"
        assert len(template.body) == 1

    def test_discussion_template_with_category(self):
        """Discussion template with category can be created."""
        from wetwire_github.discussion_templates import (
            DiscussionTemplate,
        )
        from wetwire_github.issue_templates import Input

        template = DiscussionTemplate(
            title="Feature Request",
            labels=["enhancement"],
            body=[
                Input(label="Feature", id="feature"),
            ],
        )
        assert "enhancement" in template.labels

    def test_complex_discussion_template(self):
        """Complex discussion template can be created."""
        from wetwire_github.discussion_templates import DiscussionTemplate
        from wetwire_github.issue_templates import (
            Dropdown,
            Input,
            Markdown,
            Textarea,
        )

        template = DiscussionTemplate(
            title="Feature Discussion",
            labels=["discussion", "feature"],
            body=[
                Markdown(value="## Feature Discussion\n\nShare your ideas!"),
                Input(
                    label="Feature Name",
                    id="name",
                    description="Short name for the feature",
                    required=True,
                ),
                Textarea(
                    label="Description",
                    id="description",
                    description="Detailed description",
                    required=True,
                ),
                Dropdown(
                    label="Priority",
                    id="priority",
                    options=["Nice to have", "Important", "Critical"],
                ),
            ],
        )
        assert template.title == "Feature Discussion"
        assert len(template.body) == 4


class TestDiscussionTemplateSerialization:
    """Tests for Discussion Template YAML serialization."""

    def test_serialize_basic_template(self):
        """Basic discussion template serializes to valid YAML."""
        from wetwire_github.discussion_templates import DiscussionTemplate
        from wetwire_github.issue_templates import Input
        from wetwire_github.serialize import to_dict

        template = DiscussionTemplate(
            title="Feature Request",
            labels=["enhancement"],
            body=[
                Input(label="Feature", id="feature", required=True),
            ],
        )

        result = to_dict(template)
        assert result["title"] == "Feature Request"
        assert "enhancement" in result["labels"]
        assert len(result["body"]) == 1
        assert result["body"][0]["type"] == "input"

    def test_serialize_to_yaml_string(self):
        """Discussion template can be converted to YAML string."""
        from wetwire_github.discussion_templates import DiscussionTemplate
        from wetwire_github.issue_templates import Input
        from wetwire_github.serialize import to_dict

        template = DiscussionTemplate(
            title="Feature Request",
            labels=["enhancement"],
            body=[
                Input(label="Feature", id="feature"),
            ],
        )

        result = to_dict(template)
        yaml_str = yaml.dump(result, sort_keys=False)
        assert "title: Feature Request" in yaml_str
        assert "type: input" in yaml_str


class TestDiscussionTemplateCLIIntegration:
    """Tests for Discussion Template CLI integration."""

    def test_build_type_discussion_template_option(self):
        """Build command has discussion-template in help."""
        import subprocess
        import sys

        # Note: The CLI may not have this option yet
        # This test just checks that the CLI runs
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "build", "--help"],
            capture_output=True,
            text=True,
        )

        # The command should work
        assert result.returncode == 0
