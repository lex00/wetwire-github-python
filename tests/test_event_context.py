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


class TestEventPushMethod:
    """Tests for Event.push() method."""

    def test_push_ref(self):
        """Event.push returns expression for push ref property."""
        expr = Event.push("ref")
        assert "github.event.ref" in str(expr)
        assert str(expr) == "${{ github.event.ref }}"

    def test_push_before(self):
        """Event.push returns expression for push before property."""
        expr = Event.push("before")
        assert "github.event.before" in str(expr)
        assert str(expr) == "${{ github.event.before }}"

    def test_push_after(self):
        """Event.push returns expression for push after property."""
        expr = Event.push("after")
        assert "github.event.after" in str(expr)
        assert str(expr) == "${{ github.event.after }}"


class TestEventWorkflowRunMethod:
    """Tests for Event.workflow_run() method."""

    def test_workflow_run_conclusion(self):
        """Event.workflow_run returns expression for workflow_run conclusion."""
        expr = Event.workflow_run("conclusion")
        assert "github.event.workflow_run.conclusion" in str(expr)
        assert str(expr) == "${{ github.event.workflow_run.conclusion }}"

    def test_workflow_run_name(self):
        """Event.workflow_run returns expression for workflow_run name."""
        expr = Event.workflow_run("name")
        assert "github.event.workflow_run.name" in str(expr)
        assert str(expr) == "${{ github.event.workflow_run.name }}"

    def test_workflow_run_head_sha(self):
        """Event.workflow_run returns expression for workflow_run head_sha."""
        expr = Event.workflow_run("head_sha")
        assert "github.event.workflow_run.head_sha" in str(expr)
        assert str(expr) == "${{ github.event.workflow_run.head_sha }}"


class TestEventSenderMethod:
    """Tests for Event.sender() method."""

    def test_sender_login(self):
        """Event.sender returns expression for sender login."""
        expr = Event.sender("login")
        assert "github.event.sender.login" in str(expr)
        assert str(expr) == "${{ github.event.sender.login }}"

    def test_sender_id(self):
        """Event.sender returns expression for sender id."""
        expr = Event.sender("id")
        assert "github.event.sender.id" in str(expr)
        assert str(expr) == "${{ github.event.sender.id }}"

    def test_sender_type(self):
        """Event.sender returns expression for sender type."""
        expr = Event.sender("type")
        assert "github.event.sender.type" in str(expr)
        assert str(expr) == "${{ github.event.sender.type }}"


class TestEventRepositoryMethod:
    """Tests for Event.repository() method."""

    def test_repository_full_name(self):
        """Event.repository returns expression for repository full_name."""
        expr = Event.repository("full_name")
        assert "github.event.repository.full_name" in str(expr)
        assert str(expr) == "${{ github.event.repository.full_name }}"

    def test_repository_name(self):
        """Event.repository returns expression for repository name."""
        expr = Event.repository("name")
        assert "github.event.repository.name" in str(expr)
        assert str(expr) == "${{ github.event.repository.name }}"

    def test_repository_default_branch(self):
        """Event.repository returns expression for repository default_branch."""
        expr = Event.repository("default_branch")
        assert "github.event.repository.default_branch" in str(expr)
        assert str(expr) == "${{ github.event.repository.default_branch }}"


class TestEventNewConvenienceProperties:
    """Tests for new Event convenience properties."""

    def test_head_commit_message(self):
        """Event.head_commit_message returns head commit message expression."""
        assert "github.event.head_commit.message" in str(Event.head_commit_message)
        assert str(Event.head_commit_message) == "${{ github.event.head_commit.message }}"

    def test_head_commit_id(self):
        """Event.head_commit_id returns head commit id expression."""
        assert "github.event.head_commit.id" in str(Event.head_commit_id)
        assert str(Event.head_commit_id) == "${{ github.event.head_commit.id }}"

    def test_sender_login_property(self):
        """Event.sender_login returns sender login expression."""
        assert "github.event.sender.login" in str(Event.sender_login)
        assert str(Event.sender_login) == "${{ github.event.sender.login }}"

    def test_repo_full_name(self):
        """Event.repo_full_name returns repository full_name expression."""
        assert "github.event.repository.full_name" in str(Event.repo_full_name)
        assert str(Event.repo_full_name) == "${{ github.event.repository.full_name }}"

    def test_repo_name(self):
        """Event.repo_name returns repository name expression."""
        assert "github.event.repository.name" in str(Event.repo_name)
        assert str(Event.repo_name) == "${{ github.event.repository.name }}"


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
