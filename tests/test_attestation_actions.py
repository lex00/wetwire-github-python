"""Tests for attestation action wrappers (issue #117)."""

from wetwire_github.actions import attest_build_provenance
from wetwire_github.workflow import Step


class TestAttestBuildProvenance:
    """Tests for actions/attest-build-provenance wrapper."""

    def test_basic_attestation_with_subject_path(self) -> None:
        """Test basic attestation with subject-path."""
        step = attest_build_provenance(
            subject_path="dist/*.tar.gz",
        )

        assert isinstance(step, Step)
        assert step.uses == "actions/attest-build-provenance@v2"
        assert step.with_["subject-path"] == "dist/*.tar.gz"

    def test_attestation_with_subject_digest(self) -> None:
        """Test attestation with subject-digest and subject-name."""
        step = attest_build_provenance(
            subject_digest="sha256:abc123def456",
            subject_name="myapp:latest",
        )

        assert isinstance(step, Step)
        assert step.uses == "actions/attest-build-provenance@v2"
        assert step.with_["subject-digest"] == "sha256:abc123def456"
        assert step.with_["subject-name"] == "myapp:latest"

    def test_attestation_with_subject_checksums(self) -> None:
        """Test attestation with checksums file."""
        step = attest_build_provenance(
            subject_checksums="checksums.txt",
        )

        assert isinstance(step, Step)
        assert step.with_["subject-checksums"] == "checksums.txt"

    def test_attestation_with_push_to_registry(self) -> None:
        """Test attestation with push to registry enabled."""
        step = attest_build_provenance(
            subject_digest="sha256:abc123",
            subject_name="ghcr.io/owner/app:v1.0.0",
            push_to_registry=True,
        )

        assert step.with_["push-to-registry"] == "true"
        assert step.with_["subject-digest"] == "sha256:abc123"
        assert step.with_["subject-name"] == "ghcr.io/owner/app:v1.0.0"

    def test_attestation_with_push_to_registry_false(self) -> None:
        """Test attestation with push to registry explicitly disabled."""
        step = attest_build_provenance(
            subject_path="dist/app",
            push_to_registry=False,
        )

        assert step.with_["push-to-registry"] == "false"

    def test_attestation_with_create_storage_record(self) -> None:
        """Test attestation with create-storage-record option."""
        step = attest_build_provenance(
            subject_path="dist/app",
            create_storage_record=True,
        )

        assert step.with_["create-storage-record"] == "true"

    def test_attestation_with_show_summary(self) -> None:
        """Test attestation with show-summary disabled."""
        step = attest_build_provenance(
            subject_path="dist/app",
            show_summary=False,
        )

        assert step.with_["show-summary"] == "false"

    def test_attestation_with_custom_token(self) -> None:
        """Test attestation with custom GitHub token."""
        step = attest_build_provenance(
            subject_path="dist/app",
            github_token="${{ secrets.CUSTOM_TOKEN }}",
        )

        assert step.with_["github-token"] == "${{ secrets.CUSTOM_TOKEN }}"

    def test_attestation_with_all_options(self) -> None:
        """Test attestation with all available options."""
        step = attest_build_provenance(
            subject_path="dist/*.whl",
            push_to_registry=False,
            create_storage_record=True,
            show_summary=True,
            github_token="${{ github.token }}",
        )

        assert step.with_["subject-path"] == "dist/*.whl"
        assert step.with_["push-to-registry"] == "false"
        assert step.with_["create-storage-record"] == "true"
        assert step.with_["show-summary"] == "true"
        assert step.with_["github-token"] == "${{ github.token }}"

    def test_attestation_minimal_no_optional_params(self) -> None:
        """Test attestation with only required parameter."""
        step = attest_build_provenance(
            subject_path="artifact.zip",
        )

        assert step.with_["subject-path"] == "artifact.zip"
        # Optional parameters should not be in with_ dict when None
        assert "push-to-registry" not in step.with_
        assert "create-storage-record" not in step.with_
        assert "show-summary" not in step.with_
        assert "github-token" not in step.with_
