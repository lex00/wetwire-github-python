"""Tests for expanded action wrappers (issue #103)."""

from wetwire_github.actions import (
    codecov,
    configure_aws_credentials,
    create_pull_request,
    docker_metadata,
    gh_release,
    setup_buildx,
)
from wetwire_github.workflow import Step


class TestSetupBuildx:
    """Tests for docker/setup-buildx-action wrapper."""

    def test_basic_setup(self) -> None:
        """Test basic Buildx setup."""
        step = setup_buildx()

        assert isinstance(step, Step)
        assert step.uses == "docker/setup-buildx-action@v3"

    def test_with_platforms(self) -> None:
        """Test Buildx with custom platforms."""
        step = setup_buildx(
            platforms="linux/amd64,linux/arm64",
        )

        assert step.with_["platforms"] == "linux/amd64,linux/arm64"


class TestDockerMetadata:
    """Tests for docker/metadata-action wrapper."""

    def test_basic_metadata(self) -> None:
        """Test basic metadata extraction."""
        step = docker_metadata(
            images="ghcr.io/owner/app",
        )

        assert isinstance(step, Step)
        assert step.uses == "docker/metadata-action@v5"
        assert step.with_["images"] == "ghcr.io/owner/app"

    def test_with_tags(self) -> None:
        """Test metadata with custom tags."""
        step = docker_metadata(
            images="myapp",
            tags="type=sha\ntype=ref,event=branch",
        )

        assert "type=sha" in step.with_["tags"]


class TestConfigureAwsCredentials:
    """Tests for aws-actions/configure-aws-credentials wrapper."""

    def test_basic_credentials(self) -> None:
        """Test basic AWS credentials setup."""
        step = configure_aws_credentials(
            aws_region="us-east-1",
        )

        assert isinstance(step, Step)
        assert step.uses == "aws-actions/configure-aws-credentials@v4"
        assert step.with_["aws-region"] == "us-east-1"

    def test_with_role(self) -> None:
        """Test OIDC role assumption."""
        step = configure_aws_credentials(
            aws_region="us-east-1",
            role_to_assume="arn:aws:iam::123456789:role/my-role",
        )

        assert step.with_["role-to-assume"] == "arn:aws:iam::123456789:role/my-role"

    def test_with_access_keys(self) -> None:
        """Test with access keys."""
        step = configure_aws_credentials(
            aws_region="us-east-1",
            aws_access_key_id="${{ secrets.AWS_ACCESS_KEY_ID }}",
            aws_secret_access_key="${{ secrets.AWS_SECRET_ACCESS_KEY }}",
        )

        assert step.with_["aws-access-key-id"] == "${{ secrets.AWS_ACCESS_KEY_ID }}"


class TestCodecov:
    """Tests for codecov/codecov-action wrapper."""

    def test_basic_upload(self) -> None:
        """Test basic coverage upload."""
        step = codecov()

        assert isinstance(step, Step)
        assert step.uses == "codecov/codecov-action@v4"

    def test_with_token(self) -> None:
        """Test with Codecov token."""
        step = codecov(
            token="${{ secrets.CODECOV_TOKEN }}",
        )

        assert step.with_["token"] == "${{ secrets.CODECOV_TOKEN }}"

    def test_with_files(self) -> None:
        """Test with specific coverage files."""
        step = codecov(
            files="./coverage.xml",
            flags="unittests",
        )

        assert step.with_["files"] == "./coverage.xml"
        assert step.with_["flags"] == "unittests"


class TestCreatePullRequest:
    """Tests for peter-evans/create-pull-request wrapper."""

    def test_basic_pr(self) -> None:
        """Test basic PR creation."""
        step = create_pull_request(
            title="Update dependencies",
            body="Automated dependency update",
        )

        assert isinstance(step, Step)
        assert step.uses == "peter-evans/create-pull-request@v6"
        assert step.with_["title"] == "Update dependencies"

    def test_with_branch(self) -> None:
        """Test with custom branch."""
        step = create_pull_request(
            title="Chore: update",
            branch="auto/update",
            base="main",
        )

        assert step.with_["branch"] == "auto/update"
        assert step.with_["base"] == "main"


class TestGhRelease:
    """Tests for softprops/action-gh-release wrapper."""

    def test_basic_release(self) -> None:
        """Test basic release creation."""
        step = gh_release()

        assert isinstance(step, Step)
        assert step.uses == "softprops/action-gh-release@v2"

    def test_with_files(self) -> None:
        """Test release with files."""
        step = gh_release(
            files="dist/*\n*.tar.gz",
        )

        assert step.with_["files"] == "dist/*\n*.tar.gz"

    def test_draft_release(self) -> None:
        """Test draft release."""
        step = gh_release(
            draft=True,
            prerelease=False,
        )

        assert step.with_["draft"] == "true"
