"""Tests for GitHub context pseudo-parameters (issue #102)."""

from wetwire_github.pseudo import (
    GITHUB_ACTOR,
    GITHUB_BASE_REF,
    GITHUB_EVENT_NAME,
    GITHUB_HEAD_REF,
    GITHUB_REF,
    GITHUB_REF_NAME,
    GITHUB_REPOSITORY,
    GITHUB_REPOSITORY_OWNER,
    GITHUB_RUN_ID,
    GITHUB_RUN_NUMBER,
    GITHUB_SHA,
    GITHUB_WORKFLOW,
)


class TestGitHubPseudoParameters:
    """Tests for GitHub context pseudo-parameters."""

    def test_github_ref(self) -> None:
        """Test GITHUB_REF constant."""
        assert GITHUB_REF == "${{ github.ref }}"

    def test_github_ref_name(self) -> None:
        """Test GITHUB_REF_NAME constant."""
        assert GITHUB_REF_NAME == "${{ github.ref_name }}"

    def test_github_sha(self) -> None:
        """Test GITHUB_SHA constant."""
        assert GITHUB_SHA == "${{ github.sha }}"

    def test_github_repository(self) -> None:
        """Test GITHUB_REPOSITORY constant."""
        assert GITHUB_REPOSITORY == "${{ github.repository }}"

    def test_github_repository_owner(self) -> None:
        """Test GITHUB_REPOSITORY_OWNER constant."""
        assert GITHUB_REPOSITORY_OWNER == "${{ github.repository_owner }}"

    def test_github_actor(self) -> None:
        """Test GITHUB_ACTOR constant."""
        assert GITHUB_ACTOR == "${{ github.actor }}"

    def test_github_workflow(self) -> None:
        """Test GITHUB_WORKFLOW constant."""
        assert GITHUB_WORKFLOW == "${{ github.workflow }}"

    def test_github_run_id(self) -> None:
        """Test GITHUB_RUN_ID constant."""
        assert GITHUB_RUN_ID == "${{ github.run_id }}"

    def test_github_run_number(self) -> None:
        """Test GITHUB_RUN_NUMBER constant."""
        assert GITHUB_RUN_NUMBER == "${{ github.run_number }}"

    def test_github_head_ref(self) -> None:
        """Test GITHUB_HEAD_REF constant."""
        assert GITHUB_HEAD_REF == "${{ github.head_ref }}"

    def test_github_base_ref(self) -> None:
        """Test GITHUB_BASE_REF constant."""
        assert GITHUB_BASE_REF == "${{ github.base_ref }}"

    def test_github_event_name(self) -> None:
        """Test GITHUB_EVENT_NAME constant."""
        assert GITHUB_EVENT_NAME == "${{ github.event_name }}"


class TestPseudoParametersInWorkflow:
    """Tests for using pseudo-parameters in workflows."""

    def test_use_in_step_env(self) -> None:
        """Test using pseudo-parameters in step environment."""
        from wetwire_github.workflow import Step

        step = Step(
            run="echo $REF",
            env={"REF": GITHUB_REF},
        )

        assert step.env is not None
        assert step.env["REF"] == "${{ github.ref }}"

    def test_use_in_job_env(self) -> None:
        """Test using pseudo-parameters in job environment."""
        from wetwire_github.workflow import Job, Step

        job = Job(
            runs_on="ubuntu-latest",
            steps=[Step(run="echo $ACTOR")],
            env={"ACTOR": GITHUB_ACTOR},
        )

        assert job.env is not None
        assert job.env["ACTOR"] == "${{ github.actor }}"
