"""Tests for EventContext for typed event payload access."""

from wetwire_github.workflow import Step
from wetwire_github.workflow.expressions import Event


class TestEventContext:
    """Tests for Event context."""

    def test_event_pull_request(self):
        """Event.pull_request returns expression for PR property."""
        expr = Event.pull_request("title")
        assert "github.event.pull_request.title" in str(expr)
        assert str(expr) == "${{ github.event.pull_request.title }}"

    def test_event_issue(self):
        """Event.issue returns expression for issue property."""
        expr = Event.issue("body")
        assert "github.event.issue.body" in str(expr)
        assert str(expr) == "${{ github.event.issue.body }}"

    def test_event_release(self):
        """Event.release returns expression for release property."""
        expr = Event.release("tag_name")
        assert "github.event.release.tag_name" in str(expr)
        assert str(expr) == "${{ github.event.release.tag_name }}"

    def test_event_discussion(self):
        """Event.discussion returns expression for discussion property."""
        expr = Event.discussion("title")
        assert "github.event.discussion.title" in str(expr)
        assert str(expr) == "${{ github.event.discussion.title }}"


class TestEventConvenienceProperties:
    """Tests for Event convenience properties."""

    def test_pr_title(self):
        """Event.pr_title returns PR title expression."""
        assert "github.event.pull_request.title" in str(Event.pr_title)
        assert str(Event.pr_title) == "${{ github.event.pull_request.title }}"

    def test_pr_body(self):
        """Event.pr_body returns PR body expression."""
        assert "github.event.pull_request.body" in str(Event.pr_body)
        assert str(Event.pr_body) == "${{ github.event.pull_request.body }}"

    def test_pr_number(self):
        """Event.pr_number returns PR number expression."""
        assert "github.event.pull_request.number" in str(Event.pr_number)
        assert str(Event.pr_number) == "${{ github.event.pull_request.number }}"

    def test_issue_title(self):
        """Event.issue_title returns issue title expression."""
        assert "github.event.issue.title" in str(Event.issue_title)
        assert str(Event.issue_title) == "${{ github.event.issue.title }}"

    def test_issue_body(self):
        """Event.issue_body returns issue body expression."""
        assert "github.event.issue.body" in str(Event.issue_body)
        assert str(Event.issue_body) == "${{ github.event.issue.body }}"

    def test_issue_number(self):
        """Event.issue_number returns issue number expression."""
        assert "github.event.issue.number" in str(Event.issue_number)
        assert str(Event.issue_number) == "${{ github.event.issue.number }}"

    def test_release_tag_name(self):
        """Event.release_tag_name returns release tag_name expression."""
        assert "github.event.release.tag_name" in str(Event.release_tag_name)
        assert str(Event.release_tag_name) == "${{ github.event.release.tag_name }}"

    def test_release_body(self):
        """Event.release_body returns release body expression."""
        assert "github.event.release.body" in str(Event.release_body)
        assert str(Event.release_body) == "${{ github.event.release.body }}"


class TestEventInStepConditions:
    """Tests for using Event in Step conditions."""

    def test_event_in_step_if_condition(self):
        """Event expressions work in Step if conditions."""
        # Using convenience property
        step = Step(
            name="Comment on PR",
            run="echo 'PR opened'",
            if_=Event.pr_title,
        )
        assert step.if_ is not None
        assert "github.event.pull_request.title" in str(step.if_)

    def test_event_method_in_step_condition(self):
        """Event methods work in Step if conditions."""
        # Using method call
        step = Step(
            name="Process release",
            run="echo 'Release created'",
            if_=Event.release("tag_name"),
        )
        assert step.if_ is not None
        assert "github.event.release.tag_name" in str(step.if_)

    def test_event_expression_combination(self):
        """Event expressions can be combined with other expressions."""
        from wetwire_github.workflow.expressions import GitHub

        # Combine Event with GitHub context
        expr = Event.pr_title.and_(GitHub.ref)
        assert "github.event.pull_request.title" in str(expr)
        assert "github.ref" in str(expr)
        assert "&&" in str(expr)
