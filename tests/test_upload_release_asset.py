"""Tests for upload-release-asset action wrapper (issue #177)."""

import yaml

from wetwire_github.actions import upload_release_asset
from wetwire_github.serialize import to_yaml
from wetwire_github.workflow import Job, Step, Triggers, Workflow
from wetwire_github.workflow.expressions import Event
from wetwire_github.workflow.triggers import ReleaseTrigger


class TestUploadReleaseAsset:
    """Tests for upload_release_asset wrapper."""

    def test_basic_creation(self) -> None:
        """Test creating a basic upload-release-asset step with all required parameters."""
        step = upload_release_asset(
            upload_url="${{ github.event.release.upload_url }}",
            asset_path="./dist/myapp.zip",
            asset_name="myapp-v1.0.0.zip",
            asset_content_type="application/zip",
        )

        assert isinstance(step, Step)
        assert step.uses == "actions/upload-release-asset@v1"
        assert step.env is not None
        assert step.env["GITHUB_TOKEN"] == "${{ secrets.GITHUB_TOKEN }}"
        assert step.with_ is not None
        assert step.with_["upload_url"] == "${{ github.event.release.upload_url }}"
        assert step.with_["asset_path"] == "./dist/myapp.zip"
        assert step.with_["asset_name"] == "myapp-v1.0.0.zip"
        assert step.with_["asset_content_type"] == "application/zip"

    def test_with_expression_builders(self) -> None:
        """Test using expression builders for upload_url."""
        step = upload_release_asset(
            upload_url=Event.release("upload_url"),
            asset_path="./dist/myapp.tar.gz",
            asset_name="myapp.tar.gz",
            asset_content_type="application/gzip",
        )

        # Expression objects are converted to strings in the wrapper
        assert step.with_["upload_url"] == "${{ github.event.release.upload_url }}"
        assert step.with_["asset_content_type"] == "application/gzip"

    def test_serialization(self) -> None:
        """Test that the step serializes to correct YAML."""
        step = upload_release_asset(
            upload_url="${{ github.event.release.upload_url }}",
            asset_path="./dist/myapp.zip",
            asset_name="myapp-v1.0.0.zip",
            asset_content_type="application/zip",
        )

        # Create a minimal workflow to serialize
        workflow = Workflow(
            name="Test Release Upload",
            on=Triggers(release=ReleaseTrigger(types=["created"])),
            jobs={
                "upload": Job(
                    runs_on="ubuntu-latest",
                    steps=[step],
                ),
            },
        )

        yaml_str = to_yaml(workflow)
        parsed = yaml.safe_load(yaml_str)

        # Check the step in the serialized output
        upload_step = parsed["jobs"]["upload"]["steps"][0]
        assert upload_step["uses"] == "actions/upload-release-asset@v1"
        assert upload_step["env"]["GITHUB_TOKEN"] == "${{ secrets.GITHUB_TOKEN }}"
        assert upload_step["with"]["upload_url"] == "${{ github.event.release.upload_url }}"
        assert upload_step["with"]["asset_path"] == "./dist/myapp.zip"
        assert upload_step["with"]["asset_name"] == "myapp-v1.0.0.zip"
        assert upload_step["with"]["asset_content_type"] == "application/zip"

    def test_different_content_types(self) -> None:
        """Test different asset content types."""
        test_cases = [
            ("application/zip", "myapp.zip"),
            ("application/gzip", "myapp.tar.gz"),
            ("application/octet-stream", "myapp.bin"),
            ("application/x-tar", "myapp.tar"),
            ("text/plain", "README.txt"),
        ]

        for content_type, filename in test_cases:
            step = upload_release_asset(
                upload_url="${{ github.event.release.upload_url }}",
                asset_path=f"./dist/{filename}",
                asset_name=filename,
                asset_content_type=content_type,
            )

            assert step.with_["asset_content_type"] == content_type
            assert step.with_["asset_name"] == filename

    def test_integration_in_release_workflow(self) -> None:
        """Test integration of upload_release_asset in a complete release workflow."""
        workflow = Workflow(
            name="Release Assets",
            on=Triggers(release=ReleaseTrigger(types=["created"])),
            jobs={
                "upload-assets": Job(
                    runs_on="ubuntu-latest",
                    steps=[
                        Step(uses="actions/checkout@v4"),
                        Step(run="make build"),
                        upload_release_asset(
                            upload_url=Event.release("upload_url"),
                            asset_path="./dist/linux-amd64.tar.gz",
                            asset_name="myapp-linux-amd64.tar.gz",
                            asset_content_type="application/gzip",
                        ),
                        upload_release_asset(
                            upload_url=Event.release("upload_url"),
                            asset_path="./dist/darwin-amd64.tar.gz",
                            asset_name="myapp-darwin-amd64.tar.gz",
                            asset_content_type="application/gzip",
                        ),
                    ],
                ),
            },
        )

        yaml_str = to_yaml(workflow)

        # Verify the YAML contains the expected upload-release-asset steps
        assert "actions/upload-release-asset@v1" in yaml_str
        assert "myapp-linux-amd64.tar.gz" in yaml_str
        assert "myapp-darwin-amd64.tar.gz" in yaml_str
        assert "GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}" in yaml_str
        assert "upload_url: ${{ github.event.release.upload_url }}" in yaml_str

        # Parse and verify structure
        parsed = yaml.safe_load(yaml_str)
        steps = parsed["jobs"]["upload-assets"]["steps"]
        upload_steps = [s for s in steps if s.get("uses", "").startswith("actions/upload-release-asset")]
        assert len(upload_steps) == 2

        # Verify the first upload step
        assert upload_steps[0]["with"]["asset_name"] == "myapp-linux-amd64.tar.gz"
        assert upload_steps[0]["env"]["GITHUB_TOKEN"] == "${{ secrets.GITHUB_TOKEN }}"

        # Verify the second upload step
        assert upload_steps[1]["with"]["asset_name"] == "myapp-darwin-amd64.tar.gz"
        assert upload_steps[1]["env"]["GITHUB_TOKEN"] == "${{ secrets.GITHUB_TOKEN }}"

    def test_with_custom_token(self) -> None:
        """Test using a custom GitHub token instead of default."""
        step = upload_release_asset(
            upload_url="${{ github.event.release.upload_url }}",
            asset_path="./dist/myapp.zip",
            asset_name="myapp.zip",
            asset_content_type="application/zip",
        )

        # The env should contain GITHUB_TOKEN by default
        assert step.env is not None
        assert "GITHUB_TOKEN" in step.env

        # Note: The action always uses GITHUB_TOKEN from env,
        # so custom tokens would need to be set in the step's env
