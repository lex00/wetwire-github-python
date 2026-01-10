"""Tests for policy engine."""


from wetwire_github.policy import (
    LimitJobCount,
    NoHardcodedSecrets,
    PinActions,
    PolicyEngine,
    PolicyResult,
    RequireApproval,
    RequireCheckout,
    RequireTimeouts,
)
from wetwire_github.workflow import Job, Step, Workflow
from wetwire_github.workflow.triggers import Triggers


class TestPolicyResult:
    """Tests for PolicyResult dataclass."""

    def test_policy_result_passed(self):
        """PolicyResult stores successful check."""
        result = PolicyResult(
            policy_name="RequireCheckout",
            passed=True,
            message="All jobs use checkout action",
        )
        assert result.policy_name == "RequireCheckout"
        assert result.passed is True
        assert result.message == "All jobs use checkout action"

    def test_policy_result_failed(self):
        """PolicyResult stores failed check."""
        result = PolicyResult(
            policy_name="RequireTimeouts",
            passed=False,
            message="Job 'build' missing timeout_minutes",
        )
        assert result.policy_name == "RequireTimeouts"
        assert result.passed is False
        assert "missing timeout_minutes" in result.message

    def test_policy_result_empty_message(self):
        """PolicyResult can have empty message."""
        result = PolicyResult(
            policy_name="TestPolicy",
            passed=True,
        )
        assert result.message == ""


class TestPolicyEngine:
    """Tests for PolicyEngine."""

    def test_engine_single_policy(self):
        """PolicyEngine evaluates single policy."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(uses="actions/checkout@v4")],
                )
            },
        )

        engine = PolicyEngine(policies=[RequireCheckout()])
        results = engine.evaluate(workflow)

        assert len(results) == 1
        assert results[0].passed is True

    def test_engine_multiple_policies(self):
        """PolicyEngine evaluates multiple policies."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    timeout_minutes=30,
                    steps=[Step(uses="actions/checkout@v4")],
                )
            },
        )

        engine = PolicyEngine(policies=[RequireCheckout(), RequireTimeouts()])
        results = engine.evaluate(workflow)

        assert len(results) == 2
        assert all(r.passed for r in results)

    def test_engine_empty_policies(self):
        """PolicyEngine with no policies returns empty results."""
        workflow = Workflow(name="Test", on=Triggers(), jobs={})
        engine = PolicyEngine(policies=[])
        results = engine.evaluate(workflow)

        assert len(results) == 0

    def test_engine_mixed_results(self):
        """PolicyEngine returns both passing and failing results."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(run="echo 'test'")],  # No checkout
                )
            },
        )

        engine = PolicyEngine(policies=[RequireCheckout(), LimitJobCount(max_jobs=5)])
        results = engine.evaluate(workflow)

        assert len(results) == 2
        # RequireCheckout should fail, LimitJobCount should pass
        assert sum(1 for r in results if r.passed) == 1
        assert sum(1 for r in results if not r.passed) == 1


class TestRequireCheckout:
    """Tests for RequireCheckout policy."""

    def test_require_checkout_passes(self):
        """RequireCheckout passes when all jobs use checkout."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(uses="actions/checkout@v4")],
                ),
                "test": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(uses="actions/checkout@v3")],
                ),
            },
        )

        policy = RequireCheckout()
        result = policy.evaluate(workflow)

        assert result.passed is True
        assert result.policy_name == "RequireCheckout"

    def test_require_checkout_fails(self):
        """RequireCheckout fails when job missing checkout."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(run="echo 'test'")],
                )
            },
        )

        policy = RequireCheckout()
        result = policy.evaluate(workflow)

        assert result.passed is False
        assert "build" in result.message

    def test_require_checkout_empty_workflow(self):
        """RequireCheckout passes for workflow with no jobs."""
        workflow = Workflow(name="Test", on=Triggers(), jobs={})

        policy = RequireCheckout()
        result = policy.evaluate(workflow)

        assert result.passed is True

    def test_require_checkout_partial(self):
        """RequireCheckout fails when only some jobs have checkout."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(uses="actions/checkout@v4")],
                ),
                "test": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(run="echo 'test'")],
                ),
            },
        )

        policy = RequireCheckout()
        result = policy.evaluate(workflow)

        assert result.passed is False
        assert "test" in result.message


class TestRequireTimeouts:
    """Tests for RequireTimeouts policy."""

    def test_require_timeouts_passes(self):
        """RequireTimeouts passes when all jobs have timeout."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    timeout_minutes=30,
                    steps=[Step(run="echo 'test'")],
                ),
                "test": Job(
                    runs_on="ubuntu-latest",
                    timeout_minutes=15,
                    steps=[Step(run="echo 'test'")],
                ),
            },
        )

        policy = RequireTimeouts()
        result = policy.evaluate(workflow)

        assert result.passed is True
        assert result.policy_name == "RequireTimeouts"

    def test_require_timeouts_fails(self):
        """RequireTimeouts fails when job missing timeout."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(run="echo 'test'")],
                )
            },
        )

        policy = RequireTimeouts()
        result = policy.evaluate(workflow)

        assert result.passed is False
        assert "build" in result.message

    def test_require_timeouts_empty_workflow(self):
        """RequireTimeouts passes for workflow with no jobs."""
        workflow = Workflow(name="Test", on=Triggers(), jobs={})

        policy = RequireTimeouts()
        result = policy.evaluate(workflow)

        assert result.passed is True


class TestNoHardcodedSecrets:
    """Tests for NoHardcodedSecrets policy."""

    def test_no_hardcoded_secrets_passes(self):
        """NoHardcodedSecrets passes when no secrets in run commands."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[
                        Step(run="echo 'Hello'"),
                        Step(run="make build"),
                    ],
                )
            },
        )

        policy = NoHardcodedSecrets()
        result = policy.evaluate(workflow)

        assert result.passed is True

    def test_no_hardcoded_secrets_fails_token(self):
        """NoHardcodedSecrets fails when TOKEN found in run."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[
                        Step(run="export TOKEN=abc123"),
                    ],
                )
            },
        )

        policy = NoHardcodedSecrets()
        result = policy.evaluate(workflow)

        assert result.passed is False
        assert "TOKEN" in result.message

    def test_no_hardcoded_secrets_fails_password(self):
        """NoHardcodedSecrets fails when password found in run."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[
                        Step(run="curl -u user:password123 example.com"),
                    ],
                )
            },
        )

        policy = NoHardcodedSecrets()
        result = policy.evaluate(workflow)

        assert result.passed is False
        assert "password" in result.message.lower()

    def test_no_hardcoded_secrets_fails_api_key(self):
        """NoHardcodedSecrets fails when API_KEY found in run."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[
                        Step(run="export API_KEY=secret123"),
                    ],
                )
            },
        )

        policy = NoHardcodedSecrets()
        result = policy.evaluate(workflow)

        assert result.passed is False
        assert "API_KEY" in result.message


class TestRequireApproval:
    """Tests for RequireApproval policy."""

    def test_require_approval_passes(self):
        """RequireApproval passes when jobs use environment."""
        from wetwire_github.workflow.types import Environment

        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "deploy": Job(
                    runs_on="ubuntu-latest",
                    environment=Environment(name="production"),
                    steps=[Step(run="echo 'deploy'")],
                )
            },
        )

        policy = RequireApproval()
        result = policy.evaluate(workflow)

        assert result.passed is True

    def test_require_approval_detection_only(self):
        """RequireApproval only detects environment, not reviewers."""
        from wetwire_github.workflow.types import Environment

        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "deploy": Job(
                    runs_on="ubuntu-latest",
                    environment=Environment(name="staging"),
                    steps=[Step(run="echo 'deploy'")],
                )
            },
        )

        policy = RequireApproval()
        result = policy.evaluate(workflow)

        # Should pass as long as environment is set
        assert result.passed is True

    def test_require_approval_info_for_missing(self):
        """RequireApproval provides info when environment missing."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "deploy": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(run="echo 'deploy'")],
                )
            },
        )

        policy = RequireApproval()
        result = policy.evaluate(workflow)

        # This is detection only, so it might pass but include info
        assert "deploy" in result.message or result.passed is False


class TestPinActions:
    """Tests for PinActions policy."""

    def test_pin_actions_passes_sha(self):
        """PinActions passes when actions pinned to SHA."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[
                        Step(
                            uses="actions/checkout@8e5e7e5ab8b370d6c329ec480221332ada57f0ab"
                        ),
                    ],
                )
            },
        )

        policy = PinActions()
        result = policy.evaluate(workflow)

        assert result.passed is True

    def test_pin_actions_passes_version(self):
        """PinActions passes when actions pinned to version."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[
                        Step(uses="actions/checkout@v4"),
                        Step(uses="actions/setup-python@v5.0.0"),
                    ],
                )
            },
        )

        policy = PinActions()
        result = policy.evaluate(workflow)

        assert result.passed is True

    def test_pin_actions_fails_unpinned(self):
        """PinActions fails when actions not pinned."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[
                        Step(uses="actions/checkout"),
                    ],
                )
            },
        )

        policy = PinActions()
        result = policy.evaluate(workflow)

        assert result.passed is False
        assert "checkout" in result.message

    def test_pin_actions_fails_branch(self):
        """PinActions fails when actions pinned to branch."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[
                        Step(uses="actions/checkout@main"),
                    ],
                )
            },
        )

        policy = PinActions()
        result = policy.evaluate(workflow)

        assert result.passed is False
        assert "main" in result.message or "branch" in result.message.lower()

    def test_pin_actions_ignores_run_steps(self):
        """PinActions only checks steps with uses field."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[
                        Step(run="echo 'test'"),
                    ],
                )
            },
        )

        policy = PinActions()
        result = policy.evaluate(workflow)

        assert result.passed is True


class TestLimitJobCount:
    """Tests for LimitJobCount policy."""

    def test_limit_job_count_passes(self):
        """LimitJobCount passes when under limit."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(runs_on="ubuntu-latest", steps=[]),
                "test": Job(runs_on="ubuntu-latest", steps=[]),
            },
        )

        policy = LimitJobCount(max_jobs=5)
        result = policy.evaluate(workflow)

        assert result.passed is True

    def test_limit_job_count_passes_at_limit(self):
        """LimitJobCount passes when exactly at limit."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "job1": Job(runs_on="ubuntu-latest", steps=[]),
                "job2": Job(runs_on="ubuntu-latest", steps=[]),
                "job3": Job(runs_on="ubuntu-latest", steps=[]),
            },
        )

        policy = LimitJobCount(max_jobs=3)
        result = policy.evaluate(workflow)

        assert result.passed is True

    def test_limit_job_count_fails(self):
        """LimitJobCount fails when over limit."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "job1": Job(runs_on="ubuntu-latest", steps=[]),
                "job2": Job(runs_on="ubuntu-latest", steps=[]),
                "job3": Job(runs_on="ubuntu-latest", steps=[]),
                "job4": Job(runs_on="ubuntu-latest", steps=[]),
            },
        )

        policy = LimitJobCount(max_jobs=3)
        result = policy.evaluate(workflow)

        assert result.passed is False
        assert "4" in result.message
        assert "3" in result.message

    def test_limit_job_count_empty_workflow(self):
        """LimitJobCount passes for empty workflow."""
        workflow = Workflow(name="Test", on=Triggers(), jobs={})

        policy = LimitJobCount(max_jobs=5)
        result = policy.evaluate(workflow)

        assert result.passed is True

    def test_limit_job_count_custom_limit(self):
        """LimitJobCount uses custom limit."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "job1": Job(runs_on="ubuntu-latest", steps=[]),
                "job2": Job(runs_on="ubuntu-latest", steps=[]),
            },
        )

        policy = LimitJobCount(max_jobs=1)
        result = policy.evaluate(workflow)

        assert result.passed is False


class TestPolicyBase:
    """Tests for Policy base class behavior."""

    def test_policy_has_name(self):
        """All policies have a name attribute."""
        policy = RequireCheckout()
        assert hasattr(policy, "name")
        assert policy.name == "RequireCheckout"

    def test_policy_has_description(self):
        """All policies have a description attribute."""
        policy = RequireCheckout()
        assert hasattr(policy, "description")
        assert len(policy.description) > 0

    def test_policy_evaluate_returns_result(self):
        """Policy evaluate method returns PolicyResult."""
        workflow = Workflow(name="Test", on=Triggers(), jobs={})
        policy = RequireCheckout()
        result = policy.evaluate(workflow)

        assert isinstance(result, PolicyResult)
        assert result.policy_name == policy.name
