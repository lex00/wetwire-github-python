"""Tests for peaceiris/actions-gh-pages wrapper (issue #178)."""

from wetwire_github.actions import gh_pages
from wetwire_github.serialize import to_yaml
from wetwire_github.workflow import Step


class TestGhPages:
    """Tests for peaceiris/actions-gh-pages@v4 wrapper."""

    def test_basic_creation_with_github_token(self) -> None:
        """Test basic pages deployment with github_token."""
        step = gh_pages(
            github_token="${{ secrets.GITHUB_TOKEN }}",
            publish_dir="./public",
        )

        assert isinstance(step, Step)
        assert step.uses == "peaceiris/actions-gh-pages@v4"
        assert step.with_["github_token"] == "${{ secrets.GITHUB_TOKEN }}"
        assert step.with_["publish_dir"] == "./public"

    def test_with_deploy_key(self) -> None:
        """Test deployment with SSH deploy key instead of token."""
        step = gh_pages(
            deploy_key="${{ secrets.ACTIONS_DEPLOY_KEY }}",
            publish_dir="./dist",
        )

        assert step.with_["deploy_key"] == "${{ secrets.ACTIONS_DEPLOY_KEY }}"
        assert step.with_["publish_dir"] == "./dist"

    def test_with_personal_token(self) -> None:
        """Test deployment with personal access token."""
        step = gh_pages(
            personal_token="${{ secrets.PERSONAL_TOKEN }}",
            publish_dir="./build",
        )

        assert step.with_["personal_token"] == "${{ secrets.PERSONAL_TOKEN }}"
        assert step.with_["publish_dir"] == "./build"

    def test_with_custom_cname(self) -> None:
        """Test deployment with custom CNAME."""
        step = gh_pages(
            github_token="${{ secrets.GITHUB_TOKEN }}",
            publish_dir="./public",
            cname="docs.example.com",
        )

        assert step.with_["github_token"] == "${{ secrets.GITHUB_TOKEN }}"
        assert step.with_["publish_dir"] == "./public"
        assert step.with_["cname"] == "docs.example.com"

    def test_with_publish_branch(self) -> None:
        """Test deployment to custom branch."""
        step = gh_pages(
            github_token="${{ secrets.GITHUB_TOKEN }}",
            publish_dir="./docs",
            publish_branch="docs",
        )

        assert step.with_["publish_branch"] == "docs"

    def test_with_keep_files(self) -> None:
        """Test deployment with keep_files option."""
        step = gh_pages(
            github_token="${{ secrets.GITHUB_TOKEN }}",
            publish_dir="./public",
            keep_files=True,
        )

        assert step.with_["keep_files"] == "true"

    def test_with_force_orphan(self) -> None:
        """Test deployment with force_orphan option."""
        step = gh_pages(
            github_token="${{ secrets.GITHUB_TOKEN }}",
            publish_dir="./public",
            force_orphan=True,
        )

        assert step.with_["force_orphan"] == "true"

    def test_with_external_repository(self) -> None:
        """Test deployment to external repository."""
        step = gh_pages(
            personal_token="${{ secrets.PERSONAL_TOKEN }}",
            publish_dir="./public",
            external_repository="org/external-repo",
        )

        assert step.with_["external_repository"] == "org/external-repo"

    def test_with_custom_commit_message(self) -> None:
        """Test deployment with custom commit message."""
        step = gh_pages(
            github_token="${{ secrets.GITHUB_TOKEN }}",
            publish_dir="./public",
            commit_message="Deploy documentation",
        )

        assert step.with_["commit_message"] == "Deploy documentation"

    def test_with_custom_git_user(self) -> None:
        """Test deployment with custom git user."""
        step = gh_pages(
            github_token="${{ secrets.GITHUB_TOKEN }}",
            publish_dir="./public",
            user_name="GitHub Actions",
            user_email="actions@github.com",
        )

        assert step.with_["user_name"] == "GitHub Actions"
        assert step.with_["user_email"] == "actions@github.com"

    def test_all_parameters(self) -> None:
        """Test deployment with all parameters."""
        step = gh_pages(
            github_token="${{ secrets.GITHUB_TOKEN }}",
            publish_dir="./dist",
            publish_branch="gh-pages",
            cname="docs.example.com",
            keep_files=True,
            force_orphan=False,
            commit_message="Deploy site",
            user_name="Bot",
            user_email="bot@example.com",
        )

        assert step.with_["github_token"] == "${{ secrets.GITHUB_TOKEN }}"
        assert step.with_["publish_dir"] == "./dist"
        assert step.with_["publish_branch"] == "gh-pages"
        assert step.with_["cname"] == "docs.example.com"
        assert step.with_["keep_files"] == "true"
        assert step.with_["force_orphan"] == "false"
        assert step.with_["commit_message"] == "Deploy site"
        assert step.with_["user_name"] == "Bot"
        assert step.with_["user_email"] == "bot@example.com"

    def test_boolean_parameters_convert_to_strings(self) -> None:
        """Test that boolean parameters are converted to lowercase strings."""
        step = gh_pages(
            github_token="${{ secrets.GITHUB_TOKEN }}",
            keep_files=True,
            force_orphan=False,
        )

        assert step.with_["keep_files"] == "true"
        assert step.with_["force_orphan"] == "false"

    def test_serialization_to_yaml(self) -> None:
        """Test that step serializes correctly to YAML."""
        step = gh_pages(
            github_token="${{ secrets.GITHUB_TOKEN }}",
            publish_dir="./dist",
            publish_branch="gh-pages",
            cname="docs.example.com",
        )

        yaml_output = to_yaml(step)

        assert "uses: peaceiris/actions-gh-pages@v4" in yaml_output
        assert "github_token: ${{ secrets.GITHUB_TOKEN }}" in yaml_output
        assert "publish_dir: ./dist" in yaml_output
        assert "publish_branch: gh-pages" in yaml_output
        assert "cname: docs.example.com" in yaml_output

    def test_default_publish_dir(self) -> None:
        """Test that default publish_dir is './public'."""
        step = gh_pages(
            github_token="${{ secrets.GITHUB_TOKEN }}",
        )

        assert step.with_["publish_dir"] == "./public"

    def test_minimal_with_only_token(self) -> None:
        """Test minimal deployment with only github_token."""
        step = gh_pages(
            github_token="${{ secrets.GITHUB_TOKEN }}",
        )

        assert isinstance(step, Step)
        assert step.uses == "peaceiris/actions-gh-pages@v4"
        assert step.with_["github_token"] == "${{ secrets.GITHUB_TOKEN }}"
        assert step.with_["publish_dir"] == "./public"
        # None values should not be in with_ dict
        assert "publish_branch" not in step.with_
        assert "cname" not in step.with_

    def test_none_values_not_included(self) -> None:
        """Test that None values are filtered out from with_ dict."""
        step = gh_pages(
            github_token="${{ secrets.GITHUB_TOKEN }}",
            publish_dir="./public",
            cname=None,
            keep_files=None,
        )

        assert "cname" not in step.with_
        assert "keep_files" not in step.with_
