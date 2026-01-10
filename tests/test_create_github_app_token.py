"""Tests for create_github_app_token action wrapper (issue #174)."""

from wetwire_github.actions import create_github_app_token
from wetwire_github.serialize import to_yaml
from wetwire_github.workflow import Job, Step, Triggers, Workflow
from wetwire_github.workflow.triggers import PushTrigger


class TestCreateGithubAppToken:
    """Tests for create_github_app_token wrapper."""

    def test_basic_creation(self) -> None:
        """Test creating a basic GitHub App token step with required params."""
        step = create_github_app_token(
            app_id="${{ secrets.APP_ID }}",
            private_key="${{ secrets.PRIVATE_KEY }}",
        )

        assert isinstance(step, Step)
        assert step.uses == "actions/create-github-app-token@v1"
        assert step.with_ is not None
        assert step.with_["app-id"] == "${{ secrets.APP_ID }}"
        assert step.with_["private-key"] == "${{ secrets.PRIVATE_KEY }}"

    def test_with_owner(self) -> None:
        """Test specifying owner parameter."""
        step = create_github_app_token(
            app_id="${{ secrets.APP_ID }}",
            private_key="${{ secrets.PRIVATE_KEY }}",
            owner="my-org",
        )

        assert step.with_["owner"] == "my-org"

    def test_with_repositories_string(self) -> None:
        """Test repositories as a single string."""
        step = create_github_app_token(
            app_id="${{ secrets.APP_ID }}",
            private_key="${{ secrets.PRIVATE_KEY }}",
            repositories="repo1,repo2",
        )

        assert step.with_["repositories"] == "repo1,repo2"

    def test_with_repositories_list(self) -> None:
        """Test repositories as a list."""
        step = create_github_app_token(
            app_id="${{ secrets.APP_ID }}",
            private_key="${{ secrets.PRIVATE_KEY }}",
            repositories=["repo1", "repo2", "repo3"],
        )

        # When passed as a list, it should be converted to comma-separated string
        assert step.with_["repositories"] == "repo1,repo2,repo3"

    def test_with_skip_token_revoke(self) -> None:
        """Test skip_token_revoke parameter."""
        step = create_github_app_token(
            app_id="${{ secrets.APP_ID }}",
            private_key="${{ secrets.PRIVATE_KEY }}",
            skip_token_revoke=True,
        )

        assert step.with_["skip-token-revoke"] == "true"

    def test_all_parameters(self) -> None:
        """Test using all parameters together."""
        step = create_github_app_token(
            app_id="${{ secrets.APP_ID }}",
            private_key="${{ secrets.PRIVATE_KEY }}",
            owner="my-organization",
            repositories=["repo1", "repo2"],
            skip_token_revoke=False,
        )

        assert step.with_["app-id"] == "${{ secrets.APP_ID }}"
        assert step.with_["private-key"] == "${{ secrets.PRIVATE_KEY }}"
        assert step.with_["owner"] == "my-organization"
        assert step.with_["repositories"] == "repo1,repo2"
        assert step.with_["skip-token-revoke"] == "false"

    def test_none_values_filtered(self) -> None:
        """Test that None values are filtered out of with_ dict."""
        step = create_github_app_token(
            app_id="${{ secrets.APP_ID }}",
            private_key="${{ secrets.PRIVATE_KEY }}",
            owner=None,
            repositories=None,
            skip_token_revoke=None,
        )

        assert "owner" not in step.with_
        assert "repositories" not in step.with_
        assert "skip-token-revoke" not in step.with_

    def test_serialization_to_yaml(self) -> None:
        """Test that the step serializes correctly to YAML."""
        step = create_github_app_token(
            app_id="${{ secrets.APP_ID }}",
            private_key="${{ secrets.PRIVATE_KEY }}",
            owner="my-org",
        )

        # Create a simple workflow to test serialization
        workflow = Workflow(
            name="Test",
            on=Triggers(push=PushTrigger(branches=["main"])),
            jobs={
                "test": Job(
                    runs_on="ubuntu-latest",
                    steps=[step],
                )
            },
        )

        yaml_output = to_yaml(workflow)
        assert "actions/create-github-app-token@v1" in yaml_output
        assert "app-id: ${{ secrets.APP_ID }}" in yaml_output
        assert "private-key: ${{ secrets.PRIVATE_KEY }}" in yaml_output
        assert "owner: my-org" in yaml_output

    def test_usage_in_workflow(self) -> None:
        """Test complete workflow using create_github_app_token."""
        from wetwire_github.actions import checkout

        workflow = Workflow(
            name="Deploy with App Token",
            on=Triggers(push=PushTrigger(branches=["main"])),
            jobs={
                "deploy": Job(
                    runs_on="ubuntu-latest",
                    steps=[
                        checkout(),
                        create_github_app_token(
                            app_id="${{ secrets.APP_ID }}",
                            private_key="${{ secrets.PRIVATE_KEY }}",
                            owner="${{ github.repository_owner }}",
                            repositories=["repo1", "repo2"],
                        ),
                        Step(
                            name="Use token",
                            run="echo 'Token created'",
                            env={"GH_TOKEN": "${{ steps.app-token.outputs.token }}"},
                        ),
                    ],
                )
            },
        )

        yaml_output = to_yaml(workflow)
        assert "Deploy with App Token" in yaml_output
        assert "actions/create-github-app-token@v1" in yaml_output
        assert "repositories: repo1,repo2" in yaml_output
