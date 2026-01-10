"""Generated wrapper for Upload GitHub Pages artifact."""

from wetwire_github.workflow import Step


def upload_pages_artifact(
    path: str,
    retention_days: int | None = None,
    if_no_files_found: str | None = None,
) -> Step:
    """Upload an artifact for GitHub Pages deployment.

    Args:
        path: Path to the artifact to upload
        retention_days: Number of days to retain the artifact. Default is 1.
        if_no_files_found: Behavior if no files are found at the path: "warn", "error", or "ignore". Default is "warn".

    Returns:
        Step configured to use this action
    """
    with_dict = {
        "path": path,
        "retention-days": retention_days,
        "if-no-files-found": if_no_files_found,
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="actions/upload-pages-artifact@v4",
        with_=with_dict if with_dict else None,
    )
