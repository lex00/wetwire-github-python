"""Tests for GitHub Pages action wrappers (issue #116)."""

from wetwire_github.actions import configure_pages, deploy_pages, upload_pages_artifact
from wetwire_github.workflow import Step


class TestDeployPages:
    """Tests for actions/deploy-pages wrapper."""

    def test_basic_deploy(self) -> None:
        """Test basic pages deployment."""
        step = deploy_pages()

        assert isinstance(step, Step)
        assert step.uses == "actions/deploy-pages@v4"

    def test_with_token(self) -> None:
        """Test deployment with custom token."""
        step = deploy_pages(
            token="${{ secrets.GITHUB_TOKEN }}",
        )

        assert step.with_["token"] == "${{ secrets.GITHUB_TOKEN }}"

    def test_with_timeout(self) -> None:
        """Test deployment with custom timeout."""
        step = deploy_pages(
            timeout="300000",
        )

        assert step.with_["timeout"] == "300000"

    def test_with_error_count(self) -> None:
        """Test deployment with custom error count."""
        step = deploy_pages(
            error_count="5",
        )

        assert step.with_["error_count"] == "5"

    def test_with_reporting_interval(self) -> None:
        """Test deployment with custom reporting interval."""
        step = deploy_pages(
            reporting_interval="10000",
        )

        assert step.with_["reporting_interval"] == "10000"

    def test_with_artifact_name(self) -> None:
        """Test deployment with custom artifact name."""
        step = deploy_pages(
            artifact_name="my-pages-artifact",
        )

        assert step.with_["artifact_name"] == "my-pages-artifact"

    def test_with_preview(self) -> None:
        """Test preview deployment for pull requests."""
        step = deploy_pages(
            preview="true",
        )

        assert step.with_["preview"] == "true"

    def test_all_parameters(self) -> None:
        """Test deployment with all parameters."""
        step = deploy_pages(
            token="${{ secrets.CUSTOM_TOKEN }}",
            timeout="600000",
            error_count="10",
            reporting_interval="5000",
            artifact_name="github-pages",
            preview="false",
        )

        assert step.with_["token"] == "${{ secrets.CUSTOM_TOKEN }}"
        assert step.with_["timeout"] == "600000"
        assert step.with_["error_count"] == "10"
        assert step.with_["reporting_interval"] == "5000"
        assert step.with_["artifact_name"] == "github-pages"
        assert step.with_["preview"] == "false"


class TestConfigurePages:
    """Tests for actions/configure-pages wrapper."""

    def test_basic_configure(self) -> None:
        """Test basic pages configuration."""
        step = configure_pages()

        assert isinstance(step, Step)
        assert step.uses == "actions/configure-pages@v5"

    def test_with_static_site_generator(self) -> None:
        """Test configuration with static site generator."""
        step = configure_pages(
            static_site_generator="next",
        )

        assert step.with_["static_site_generator"] == "next"

    def test_with_generator_config_file(self) -> None:
        """Test configuration with generator config file."""
        step = configure_pages(
            generator_config_file="next.config.js",
        )

        assert step.with_["generator_config_file"] == "next.config.js"

    def test_with_token(self) -> None:
        """Test configuration with custom token."""
        step = configure_pages(
            token="${{ secrets.GITHUB_TOKEN }}",
        )

        assert step.with_["token"] == "${{ secrets.GITHUB_TOKEN }}"

    def test_with_enablement(self) -> None:
        """Test configuration with pages enablement."""
        step = configure_pages(
            enablement="true",
        )

        assert step.with_["enablement"] == "true"

    def test_nuxt_generator(self) -> None:
        """Test configuration for Nuxt static site."""
        step = configure_pages(
            static_site_generator="nuxt",
            generator_config_file="nuxt.config.ts",
        )

        assert step.with_["static_site_generator"] == "nuxt"
        assert step.with_["generator_config_file"] == "nuxt.config.ts"

    def test_gatsby_generator(self) -> None:
        """Test configuration for Gatsby static site."""
        step = configure_pages(
            static_site_generator="gatsby",
        )

        assert step.with_["static_site_generator"] == "gatsby"

    def test_sveltekit_generator(self) -> None:
        """Test configuration for SvelteKit static site."""
        step = configure_pages(
            static_site_generator="sveltekit",
        )

        assert step.with_["static_site_generator"] == "sveltekit"

    def test_all_parameters(self) -> None:
        """Test configuration with all parameters."""
        step = configure_pages(
            static_site_generator="next",
            generator_config_file="next.config.js",
            token="${{ secrets.PAT }}",
            enablement="true",
        )

        assert step.with_["static_site_generator"] == "next"
        assert step.with_["generator_config_file"] == "next.config.js"
        assert step.with_["token"] == "${{ secrets.PAT }}"
        assert step.with_["enablement"] == "true"


class TestUploadPagesArtifact:
    """Tests for actions/upload-pages-artifact wrapper (issue #164)."""

    def test_basic_upload(self) -> None:
        """Test basic pages artifact upload with required path."""
        step = upload_pages_artifact(path="./public")

        assert isinstance(step, Step)
        assert step.uses == "actions/upload-pages-artifact@v4"
        assert step.with_["path"] == "./public"

    def test_with_retention_days(self) -> None:
        """Test artifact upload with custom retention period."""
        step = upload_pages_artifact(
            path="./dist",
            retention_days=7,
        )

        assert step.with_["path"] == "./dist"
        assert step.with_["retention-days"] == 7

    def test_with_if_no_files_found_warn(self) -> None:
        """Test artifact upload with warn behavior for missing files."""
        step = upload_pages_artifact(
            path="./build",
            if_no_files_found="warn",
        )

        assert step.with_["path"] == "./build"
        assert step.with_["if-no-files-found"] == "warn"

    def test_with_if_no_files_found_error(self) -> None:
        """Test artifact upload with error behavior for missing files."""
        step = upload_pages_artifact(
            path="./output",
            if_no_files_found="error",
        )

        assert step.with_["path"] == "./output"
        assert step.with_["if-no-files-found"] == "error"

    def test_with_if_no_files_found_ignore(self) -> None:
        """Test artifact upload with ignore behavior for missing files."""
        step = upload_pages_artifact(
            path="./site",
            if_no_files_found="ignore",
        )

        assert step.with_["path"] == "./site"
        assert step.with_["if-no-files-found"] == "ignore"

    def test_all_parameters(self) -> None:
        """Test artifact upload with all parameters."""
        step = upload_pages_artifact(
            path="./docs/_build/html",
            retention_days=30,
            if_no_files_found="error",
        )

        assert step.with_["path"] == "./docs/_build/html"
        assert step.with_["retention-days"] == 30
        assert step.with_["if-no-files-found"] == "error"

    def test_path_with_expression(self) -> None:
        """Test artifact upload with GitHub expression in path."""
        step = upload_pages_artifact(
            path="${{ github.workspace }}/build",
        )

        assert step.with_["path"] == "${{ github.workspace }}/build"
