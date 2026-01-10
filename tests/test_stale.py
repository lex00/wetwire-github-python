"""Tests for actions/stale wrapper (issue #182)."""

from wetwire_github.actions import stale
from wetwire_github.serialize import to_yaml
from wetwire_github.workflow import Step


class TestStale:
    """Tests for actions/stale@v9 wrapper."""

    def test_basic_creation_with_repo_token(self) -> None:
        """Test basic creation with required repo_token."""
        step = stale(
            repo_token="${{ secrets.GITHUB_TOKEN }}",
        )

        assert isinstance(step, Step)
        assert step.uses == "actions/stale@v9"
        assert step.with_["repo-token"] == "${{ secrets.GITHUB_TOKEN }}"

    def test_with_stale_messages(self) -> None:
        """Test with stale_issue_message and stale_pr_message."""
        step = stale(
            repo_token="${{ secrets.GITHUB_TOKEN }}",
            stale_issue_message="This issue is stale.",
            stale_pr_message="This PR is stale.",
        )

        assert step.with_["repo-token"] == "${{ secrets.GITHUB_TOKEN }}"
        assert step.with_["stale-issue-message"] == "This issue is stale."
        assert step.with_["stale-pr-message"] == "This PR is stale."

    def test_with_days_before_stale_and_close(self) -> None:
        """Test with days_before_stale and days_before_close (integers)."""
        step = stale(
            repo_token="${{ secrets.GITHUB_TOKEN }}",
            days_before_stale=60,
            days_before_close=7,
        )

        assert step.with_["days-before-stale"] == "60"
        assert step.with_["days-before-close"] == "7"

    def test_with_stale_labels(self) -> None:
        """Test with stale_issue_label and stale_pr_label."""
        step = stale(
            repo_token="${{ secrets.GITHUB_TOKEN }}",
            stale_issue_label="stale-issue",
            stale_pr_label="stale-pr",
        )

        assert step.with_["stale-issue-label"] == "stale-issue"
        assert step.with_["stale-pr-label"] == "stale-pr"

    def test_with_exempt_labels(self) -> None:
        """Test with exempt_issue_labels and exempt_pr_labels (strings)."""
        step = stale(
            repo_token="${{ secrets.GITHUB_TOKEN }}",
            exempt_issue_labels="pinned,security",
            exempt_pr_labels="wip,do-not-close",
        )

        assert step.with_["exempt-issue-labels"] == "pinned,security"
        assert step.with_["exempt-pr-labels"] == "wip,do-not-close"

    def test_serialization_to_yaml(self) -> None:
        """Test that step serializes correctly to YAML."""
        step = stale(
            repo_token="${{ secrets.GITHUB_TOKEN }}",
            stale_issue_message="This issue is stale.",
            days_before_stale=60,
            days_before_close=7,
            stale_issue_label="stale",
        )

        yaml_output = to_yaml(step)

        assert "uses: actions/stale@v9" in yaml_output
        assert "repo-token: ${{ secrets.GITHUB_TOKEN }}" in yaml_output
        assert "stale-issue-message: This issue is stale." in yaml_output
        assert "days-before-stale: '60'" in yaml_output or "days-before-stale: \"60\"" in yaml_output
        assert "days-before-close: '7'" in yaml_output or "days-before-close: \"7\"" in yaml_output
        assert "stale-issue-label: stale" in yaml_output

    def test_none_values_not_included(self) -> None:
        """Test that None values are filtered out from with_ dict."""
        step = stale(
            repo_token="${{ secrets.GITHUB_TOKEN }}",
            stale_issue_message=None,
            stale_pr_message=None,
            days_before_stale=None,
            days_before_close=None,
        )

        assert "stale-issue-message" not in step.with_
        assert "stale-pr-message" not in step.with_
        assert "days-before-stale" not in step.with_
        assert "days-before-close" not in step.with_

    def test_all_parameters(self) -> None:
        """Test with all parameters set."""
        step = stale(
            repo_token="${{ secrets.GITHUB_TOKEN }}",
            stale_issue_message="Issue is stale.",
            stale_pr_message="PR is stale.",
            days_before_stale=30,
            days_before_close=14,
            stale_issue_label="stale-issue",
            stale_pr_label="stale-pr",
            exempt_issue_labels="pinned,important",
            exempt_pr_labels="wip,hold",
        )

        assert step.uses == "actions/stale@v9"
        assert step.with_["repo-token"] == "${{ secrets.GITHUB_TOKEN }}"
        assert step.with_["stale-issue-message"] == "Issue is stale."
        assert step.with_["stale-pr-message"] == "PR is stale."
        assert step.with_["days-before-stale"] == "30"
        assert step.with_["days-before-close"] == "14"
        assert step.with_["stale-issue-label"] == "stale-issue"
        assert step.with_["stale-pr-label"] == "stale-pr"
        assert step.with_["exempt-issue-labels"] == "pinned,important"
        assert step.with_["exempt-pr-labels"] == "wip,hold"

    def test_integer_values_converted_to_strings(self) -> None:
        """Test that integer values are converted to strings for YAML."""
        step = stale(
            repo_token="${{ secrets.GITHUB_TOKEN }}",
            days_before_stale=90,
            days_before_close=0,
        )

        # Integer values should be strings in with_ dict
        assert step.with_["days-before-stale"] == "90"
        assert step.with_["days-before-close"] == "0"
