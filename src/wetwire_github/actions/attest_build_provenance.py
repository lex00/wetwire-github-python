"""Generated wrapper for Attest Build Provenance."""

from wetwire_github.workflow import Step


def attest_build_provenance(
    subject_path: str | None = None,
    subject_digest: str | None = None,
    subject_name: str | None = None,
    subject_checksums: str | None = None,
    push_to_registry: bool | None = None,
    create_storage_record: bool | None = None,
    show_summary: bool | None = None,
    github_token: str | None = None,
) -> Step:
    """Generate build provenance attestations for workflow artifacts.

    This action generates signed build provenance attestations for workflow
    artifacts using Sigstore. Attestations bind artifacts to details of the
    workflow run, providing tamper-proof evidence of how an artifact was built.

    Args:
        subject_path: Path to the artifact serving as the subject of the
            attestation. May contain a glob pattern or list of paths.
            Must specify exactly one of subject_path, subject_digest,
            or subject_checksums.
        subject_digest: SHA256 digest of the subject for the attestation.
            Must be in the form "sha256:hex_digest". Required when using
            subject_name. Must specify exactly one of subject_path,
            subject_digest, or subject_checksums.
        subject_name: Subject name as it should appear in the attestation.
            Required when identifying the subject with subject_digest.
        subject_checksums: Path to checksums file containing digest and
            name of subjects for attestation. Must specify exactly one of
            subject_path, subject_digest, or subject_checksums.
        push_to_registry: Whether to push the attestation to the image
            registry. Requires that subject_name specify the fully-qualified
            image name and that subject_digest be specified. Defaults to false.
        create_storage_record: Whether to create a storage record for the
            artifact. Requires push_to_registry to be true. Defaults to true.
        show_summary: Whether to attach a list of generated attestations to
            the workflow run summary page. Defaults to true.
        github_token: The GitHub token used to make authenticated API requests.
            Defaults to ${{ github.token }}.

    Returns:
        Step configured to use this action

    Example:
        Basic attestation with subject path:

        >>> from wetwire_github.actions import attest_build_provenance
        >>> step = attest_build_provenance(subject_path="dist/*.tar.gz")

        Attestation with digest for container images:

        >>> step = attest_build_provenance(
        ...     subject_digest="sha256:abc123",
        ...     subject_name="ghcr.io/owner/app:v1.0.0",
        ...     push_to_registry=True,
        ... )
    """
    with_dict = {
        "subject-path": subject_path,
        "subject-digest": subject_digest,
        "subject-name": subject_name,
        "subject-checksums": subject_checksums,
        "push-to-registry": (
            "true"
            if push_to_registry
            else ("false" if push_to_registry is False else None)
        ),
        "create-storage-record": (
            "true"
            if create_storage_record
            else ("false" if create_storage_record is False else None)
        ),
        "show-summary": (
            "true" if show_summary else ("false" if show_summary is False else None)
        ),
        "github-token": github_token,
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="actions/attest-build-provenance@v2",
        with_=with_dict if with_dict else None,
    )
