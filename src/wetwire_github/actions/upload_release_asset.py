"""Generated wrapper for actions/upload-release-asset."""

from wetwire_github.workflow import Step


def upload_release_asset(
    upload_url: str,
    asset_path: str,
    asset_name: str,
    asset_content_type: str,
) -> Step:
    """Create a step that uploads an asset to a GitHub release.

    Args:
        upload_url: The release upload URL (from release event)
        asset_path: Path to the asset file
        asset_name: Name for the uploaded asset
        asset_content_type: MIME type (e.g., "application/zip")

    Returns:
        Step configured to upload the asset
    """
    with_dict = {
        "upload_url": str(upload_url),
        "asset_path": asset_path,
        "asset_name": asset_name,
        "asset_content_type": asset_content_type,
    }

    env_dict = {
        "GITHUB_TOKEN": "${{ secrets.GITHUB_TOKEN }}",
    }

    return Step(
        uses="actions/upload-release-asset@v1",
        env=env_dict,
        with_=with_dict,
    )
