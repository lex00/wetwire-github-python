"""Tests for actions/first-interaction wrapper (issue #181)."""

from wetwire_github.actions import first_interaction
from wetwire_github.serialize import to_yaml
from wetwire_github.workflow import Step


class TestFirstInteraction:
    """Tests for actions/first-interaction@v1 wrapper."""

    def test_basic_creation_with_repo_token(self) -> None:
        """Test basic creation with required repo_token parameter."""
        step = first_interaction(
            repo_token="${{ secrets.GITHUB_TOKEN }}",
        )

        assert isinstance(step, Step)
        assert step.uses == "actions/first-interaction@v1"
        assert step.with_["repo-token"] == "${{ secrets.GITHUB_TOKEN }}"

    def test_with_issue_message(self) -> None:
        """Test creation with issue_message parameter."""
        step = first_interaction(
            repo_token="${{ secrets.GITHUB_TOKEN }}",
            issue_message="Welcome to our project! Thanks for opening your first issue.",
        )

        assert step.with_["repo-token"] == "${{ secrets.GITHUB_TOKEN }}"
        assert step.with_["issue-message"] == "Welcome to our project! Thanks for opening your first issue."

    def test_with_pr_message(self) -> None:
        """Test creation with pr_message parameter."""
        step = first_interaction(
            repo_token="${{ secrets.GITHUB_TOKEN }}",
            pr_message="Thanks for your first contribution!",
        )

        assert step.with_["repo-token"] == "${{ secrets.GITHUB_TOKEN }}"
        assert step.with_["pr-message"] == "Thanks for your first contribution!"

    def test_with_all_parameters(self) -> None:
        """Test creation with all parameters."""
        step = first_interaction(
            repo_token="${{ secrets.GITHUB_TOKEN }}",
            issue_message="Welcome! Thanks for opening your first issue.",
            pr_message="Thanks for your first PR!",
        )

        assert isinstance(step, Step)
        assert step.uses == "actions/first-interaction@v1"
        assert step.with_["repo-token"] == "${{ secrets.GITHUB_TOKEN }}"
        assert step.with_["issue-message"] == "Welcome! Thanks for opening your first issue."
        assert step.with_["pr-message"] == "Thanks for your first PR!"

    def test_serialization_to_yaml(self) -> None:
        """Test that step serializes correctly to YAML."""
        step = first_interaction(
            repo_token="${{ secrets.GITHUB_TOKEN }}",
            issue_message="Welcome to our project!",
            pr_message="Thanks for contributing!",
        )

        yaml_output = to_yaml(step)

        assert "uses: actions/first-interaction@v1" in yaml_output
        assert "repo-token: ${{ secrets.GITHUB_TOKEN }}" in yaml_output
        assert "issue-message: Welcome to our project!" in yaml_output
        assert "pr-message: Thanks for contributing!" in yaml_output

    def test_none_values_not_included(self) -> None:
        """Test that None values are filtered out from with_ dict."""
        step = first_interaction(
            repo_token="${{ secrets.GITHUB_TOKEN }}",
            issue_message=None,
            pr_message=None,
        )

        assert "repo-token" in step.with_
        assert "issue-message" not in step.with_
        assert "pr-message" not in step.with_

    def test_only_repo_token_minimal(self) -> None:
        """Test minimal creation with only repo_token (no optional params)."""
        step = first_interaction(
            repo_token="${{ secrets.GITHUB_TOKEN }}",
        )

        assert isinstance(step, Step)
        assert step.uses == "actions/first-interaction@v1"
        assert step.with_ == {"repo-token": "${{ secrets.GITHUB_TOKEN }}"}
