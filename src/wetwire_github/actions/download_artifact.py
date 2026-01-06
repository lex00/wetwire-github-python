"""Generated wrapper for Download a Build Artifact."""

from wetwire_github.workflow import Step


def download_artifact(
    name: str | None = None,
    artifact_ids: str | None = None,
    path: str | None = None,
    pattern: str | None = None,
    merge_multiple: str | None = None,
    github_token: str | None = None,
    repository: str | None = None,
    run_id: str | None = None,
) -> Step:
    """Download a build artifact that was previously uploaded in the workflow by the upload-artifact action

    Args:
        name: Name of the artifact to download. If unspecified, all artifacts for the run are downloaded.
        artifact_ids: IDs of the artifacts to download, comma-separated. Either inputs `artifact-ids` or `name` can be used, but not both.
        path: Destination path. Supports basic tilde expansion. Defaults to $GITHUB_WORKSPACE
        pattern: A glob pattern matching the artifacts that should be downloaded. Ignored if name is specified.
        merge_multiple: When multiple artifacts are matched, this changes the behavior of the destination directories. If true, the downloaded artifacts will be in the same directory specified by path. If false, the downloaded artifacts will be extracted into individual named directories within the specified path.
        github_token: The GitHub token used to authenticate with the GitHub API. This is required when downloading artifacts from a different repository or from a different workflow run. If this is not specified, the action will attempt to download artifacts from the current repository and the current workflow run.
        repository: The repository owner and the repository name joined together by "/". If github-token is specified, this is the repository that artifacts will be downloaded from.
        run_id: The id of the workflow run where the desired download artifact was uploaded from. If github-token is specified, this is the run that artifacts will be downloaded from.

    Returns:
        Step configured to use this action
    """
    with_dict = {
        "name": name,
        "artifact-ids": artifact_ids,
        "path": path,
        "pattern": pattern,
        "merge-multiple": merge_multiple,
        "github-token": github_token,
        "repository": repository,
        "run-id": run_id,
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="actions/download-artifact@v4",
        with_=with_dict if with_dict else None,
    )
