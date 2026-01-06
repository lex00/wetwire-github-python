"""Generated wrapper for Upload a Build Artifact."""

from wetwire_github.workflow import Step


def upload_artifact(
    path: str,
    name: str | None = None,
    if_no_files_found: str | None = None,
    retention_days: str | None = None,
    compression_level: str | None = None,
    overwrite: str | None = None,
    include_hidden_files: str | None = None,
) -> Step:
    """Upload a build artifact that can be used by subsequent workflow steps

        Args:
            path: A file, directory or wildcard pattern that describes what to upload
            name: Artifact name
            if_no_files_found: The desired behavior if no files are found using the provided path.
    Available Options:
      warn: Output a warning but do not fail the action
      error: Fail the action with an error message
      ignore: Do not output any warnings or errors, the action does not fail

            retention_days: Duration after which artifact will expire in days. 0 means using default retention.
    Minimum 1 day. Maximum 90 days unless changed from the repository settings page.

            compression_level: The level of compression for Zlib to be applied to the artifact archive. The value can range from 0 to 9: - 0: No compression - 1: Best speed - 6: Default compression (same as GNU Gzip) - 9: Best compression Higher levels will result in better compression, but will take longer to complete. For large files that are not easily compressed, a value of 0 is recommended for significantly faster uploads.

            overwrite: If true, an artifact with a matching name will be deleted before a new one is uploaded. If false, the action will fail if an artifact for the given name already exists. Does not fail if the artifact does not exist.

            include_hidden_files: If true, hidden files will be included in the artifact. If false, hidden files will be excluded from the artifact.


        Returns:
            Step configured to use this action
    """
    with_dict = {
        "path": path,
        "name": name,
        "if-no-files-found": if_no_files_found,
        "retention-days": retention_days,
        "compression-level": compression_level,
        "overwrite": overwrite,
        "include-hidden-files": include_hidden_files,
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="actions/upload-artifact@v4",
        with_=with_dict if with_dict else None,
    )
