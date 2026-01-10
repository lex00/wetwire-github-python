"""Tests for labeler action wrapper (issue #168)."""

from wetwire_github.actions import labeler
from wetwire_github.serialize import to_yaml
from wetwire_github.workflow import Job, Step, Triggers, Workflow


class TestLabeler:
    """Tests for labeler wrapper."""

    def test_basic_labeler_with_defaults(self) -> None:
        """Test creating a basic labeler step with default values."""
        step = labeler()

        assert isinstance(step, Step)
        assert step.uses == "actions/labeler@v5"
        # With defaults, no with_ parameters should be set
        assert step.with_ is None or step.with_ == {}

    def test_labeler_with_custom_configuration_path(self) -> None:
        """Test labeler with custom configuration path."""
        step = labeler(configuration_path=".github/custom-labeler.yml")

        assert step.uses == "actions/labeler@v5"
        assert step.with_ is not None
        assert step.with_["configuration-path"] == ".github/custom-labeler.yml"

    def test_labeler_with_custom_repo_token(self) -> None:
        """Test labeler with custom repo token."""
        step = labeler(repo_token="${{ secrets.CUSTOM_TOKEN }}")

        assert step.with_ is not None
        assert step.with_["repo-token"] == "${{ secrets.CUSTOM_TOKEN }}"

    def test_labeler_with_sync_labels_enabled(self) -> None:
        """Test labeler with sync_labels enabled."""
        step = labeler(sync_labels=True)

        assert step.with_ is not None
        assert step.with_["sync-labels"] == "true"

    def test_labeler_with_sync_labels_disabled(self) -> None:
        """Test labeler with sync_labels explicitly disabled."""
        step = labeler(sync_labels=False)

        assert step.with_ is not None
        assert step.with_["sync-labels"] == "false"

    def test_labeler_with_dot_enabled(self) -> None:
        """Test labeler with dot files matching enabled."""
        step = labeler(dot=True)

        assert step.with_ is not None
        assert step.with_["dot"] == "true"

    def test_labeler_with_dot_disabled(self) -> None:
        """Test labeler with dot files matching explicitly disabled."""
        step = labeler(dot=False)

        assert step.with_ is not None
        assert step.with_["dot"] == "false"

    def test_labeler_with_all_parameters(self) -> None:
        """Test labeler with all parameters configured."""
        step = labeler(
            repo_token="${{ secrets.GITHUB_TOKEN }}",
            configuration_path=".github/labeler.yml",
            sync_labels=True,
            dot=True,
        )

        assert step.uses == "actions/labeler@v5"
        assert step.with_ is not None
        assert step.with_["repo-token"] == "${{ secrets.GITHUB_TOKEN }}"
        assert step.with_["configuration-path"] == ".github/labeler.yml"
        assert step.with_["sync-labels"] == "true"
        assert step.with_["dot"] == "true"

    def test_labeler_serialization_to_yaml(self) -> None:
        """Test that labeler step serializes correctly to YAML."""
        workflow = Workflow(
            name="Label PRs",
            on=Triggers(pull_request={}),
            jobs={
                "label": Job(
                    runs_on="ubuntu-latest",
                    steps=[
                        labeler(
                            configuration_path=".github/labeler.yml",
                            sync_labels=True,
                        )
                    ],
                )
            },
        )

        yaml_output = to_yaml(workflow)

        # Verify the YAML contains expected structure
        assert "name: Label PRs" in yaml_output
        assert "uses: actions/labeler@v5" in yaml_output
        assert "configuration-path: .github/labeler.yml" in yaml_output
        assert "sync-labels: 'true'" in yaml_output or "sync-labels: true" in yaml_output

    def test_labeler_in_pr_workflow(self) -> None:
        """Test labeler in a realistic PR labeling workflow."""
        workflow = Workflow(
            name="PR Labeler",
            on=Triggers(pull_request={"types": ["opened", "synchronize"]}),
            jobs={
                "label": Job(
                    runs_on="ubuntu-latest",
                    permissions={"contents": "read", "pull-requests": "write"},
                    steps=[
                        labeler(sync_labels=True),
                    ],
                )
            },
        )

        yaml_output = to_yaml(workflow)

        assert "name: PR Labeler" in yaml_output
        assert "pull_request:" in yaml_output or "pull-request:" in yaml_output
        assert "uses: actions/labeler@v5" in yaml_output
