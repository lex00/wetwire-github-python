"""Generated wrapper for softprops/action-gh-release."""

from wetwire_github.workflow import Step


def gh_release(
    body: str | None = None,
    body_path: str | None = None,
    name: str | None = None,
    tag_name: str | None = None,
    draft: bool | None = None,
    prerelease: bool | None = None,
    files: str | None = None,
    fail_on_unmatched_files: bool | None = None,
    repository: str | None = None,
    token: str | None = None,
    target_commitish: str | None = None,
    discussion_category_name: str | None = None,
    generate_release_notes: bool | None = None,
    append_body: bool | None = None,
    make_latest: str | None = None,
) -> Step:
    """Create a GitHub Release.

    This action creates a GitHub release with optional file uploads.

    Args:
        body: Text describing the contents of the release.
        body_path: Path to a file containing the release body.
        name: Name of the release.
        tag_name: Tag name for the release.
        draft: Create a draft release.
        prerelease: Identify the release as a prerelease.
        files: Newline-separated list of file globs to upload.
        fail_on_unmatched_files: Fail if file globs match nothing.
        repository: Owner/repo for the release.
        token: GitHub token for authentication.
        target_commitish: Commitish value for the release tag.
        discussion_category_name: Category for release discussion.
        generate_release_notes: Automatically generate release notes.
        append_body: Append body to existing release body.
        make_latest: Mark release as latest (true, false, legacy).

    Returns:
        Step configured to use softprops/action-gh-release
    """
    with_dict = {
        "body": body,
        "body_path": body_path,
        "name": name,
        "tag_name": tag_name,
        "draft": "true" if draft else ("false" if draft is False else None),
        "prerelease": "true" if prerelease else ("false" if prerelease is False else None),
        "files": files,
        "fail_on_unmatched_files": "true" if fail_on_unmatched_files else ("false" if fail_on_unmatched_files is False else None),
        "repository": repository,
        "token": token,
        "target_commitish": target_commitish,
        "discussion_category_name": discussion_category_name,
        "generate_release_notes": "true" if generate_release_notes else ("false" if generate_release_notes is False else None),
        "append_body": "true" if append_body else ("false" if append_body is False else None),
        "make_latest": make_latest,
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="softprops/action-gh-release@v2",
        with_=with_dict if with_dict else None,
    )
