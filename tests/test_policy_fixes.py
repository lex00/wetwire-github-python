"""Tests for policy engine auto-fix functionality."""

from wetwire_github.policy import (
    LimitJobCount,
    NoHardcodedSecrets,
    PinActions,
    PolicyEngine,
    RequireApproval,
    RequireCheckout,
    RequireTimeouts,
)
from wetwire_github.workflow import Job, Step, Workflow
from wetwire_github.workflow.triggers import Triggers


class TestPolicyResultCanFix:
    """Tests for PolicyResult.can_fix property."""

    def test_policy_result_can_fix_when_fixable(self):
        """PolicyResult.can_fix returns True when policy is fixable."""
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
        assert result.can_fix is True

    def test_policy_result_can_fix_false_when_not_fixable(self):
        """PolicyResult.can_fix returns False when policy cannot be auto-fixed."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(run="export TOKEN=abc123")],
                )
            },
        )

        policy = NoHardcodedSecrets()
        result = policy.evaluate(workflow)

        assert result.passed is False
        assert result.can_fix is False

    def test_policy_result_can_fix_false_when_passed(self):
        """PolicyResult.can_fix returns False when policy already passed."""
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

        policy = RequireCheckout()
        result = policy.evaluate(workflow)

        assert result.passed is True
        assert result.can_fix is False


class TestRequireCheckoutFix:
    """Tests for RequireCheckout.fix() method."""

    def test_fix_adds_checkout_to_job_without_it(self):
        """RequireCheckout.fix() adds checkout step as first step."""
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
        fixed = policy.fix(workflow)

        # Should now pass
        result = policy.evaluate(fixed)
        assert result.passed is True

        # Checkout should be first step
        assert "checkout" in fixed.jobs["build"].steps[0].uses

    def test_fix_adds_checkout_to_multiple_jobs(self):
        """RequireCheckout.fix() adds checkout to all jobs missing it."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(run="make build")],
                ),
                "test": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(run="make test")],
                ),
            },
        )

        policy = RequireCheckout()
        fixed = policy.fix(workflow)

        result = policy.evaluate(fixed)
        assert result.passed is True

        # Both jobs should have checkout as first step
        assert "checkout" in fixed.jobs["build"].steps[0].uses
        assert "checkout" in fixed.jobs["test"].steps[0].uses

    def test_fix_preserves_existing_checkout(self):
        """RequireCheckout.fix() does not duplicate checkout step."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[
                        Step(uses="actions/checkout@v4"),
                        Step(run="make build"),
                    ],
                ),
                "test": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(run="make test")],
                ),
            },
        )

        policy = RequireCheckout()
        fixed = policy.fix(workflow)

        # Build job should still have only 2 steps
        assert len(fixed.jobs["build"].steps) == 2
        # Test job should now have 2 steps (checkout added)
        assert len(fixed.jobs["test"].steps) == 2

    def test_fix_returns_unchanged_when_all_compliant(self):
        """RequireCheckout.fix() returns workflow unchanged when compliant."""
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

        policy = RequireCheckout()
        fixed = policy.fix(workflow)

        assert len(fixed.jobs["build"].steps) == 1


class TestRequireTimeoutsFix:
    """Tests for RequireTimeouts.fix() method."""

    def test_fix_adds_default_timeout(self):
        """RequireTimeouts.fix() adds timeout_minutes=60 to jobs without it."""
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
        fixed = policy.fix(workflow)

        result = policy.evaluate(fixed)
        assert result.passed is True
        assert fixed.jobs["build"].timeout_minutes == 60

    def test_fix_adds_timeout_to_multiple_jobs(self):
        """RequireTimeouts.fix() adds timeout to all jobs missing it."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(run="make build")],
                ),
                "test": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(run="make test")],
                ),
            },
        )

        policy = RequireTimeouts()
        fixed = policy.fix(workflow)

        result = policy.evaluate(fixed)
        assert result.passed is True
        assert fixed.jobs["build"].timeout_minutes == 60
        assert fixed.jobs["test"].timeout_minutes == 60

    def test_fix_preserves_existing_timeout(self):
        """RequireTimeouts.fix() does not override existing timeout."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    timeout_minutes=30,
                    steps=[Step(run="make build")],
                ),
                "test": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(run="make test")],
                ),
            },
        )

        policy = RequireTimeouts()
        fixed = policy.fix(workflow)

        # Build should keep its 30-minute timeout
        assert fixed.jobs["build"].timeout_minutes == 30
        # Test should get 60-minute timeout
        assert fixed.jobs["test"].timeout_minutes == 60


class TestPinActionsFix:
    """Tests for PinActions.fix() method."""

    def test_fix_pins_unpinned_action(self):
        """PinActions.fix() pins unpinned actions to @v4."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(uses="actions/checkout")],
                )
            },
        )

        policy = PinActions()
        fixed = policy.fix(workflow)

        result = policy.evaluate(fixed)
        assert result.passed is True
        assert "@v4" in fixed.jobs["build"].steps[0].uses

    def test_fix_pins_branch_to_version(self):
        """PinActions.fix() replaces branch reference with version."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(uses="actions/checkout@main")],
                )
            },
        )

        policy = PinActions()
        fixed = policy.fix(workflow)

        result = policy.evaluate(fixed)
        assert result.passed is True
        assert "@v4" in fixed.jobs["build"].steps[0].uses

    def test_fix_preserves_already_pinned(self):
        """PinActions.fix() does not change already-pinned actions."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[
                        Step(uses="actions/checkout@v3"),
                        Step(uses="actions/setup-python@v5.0.0"),
                    ],
                )
            },
        )

        policy = PinActions()
        fixed = policy.fix(workflow)

        # Should preserve existing versions
        assert fixed.jobs["build"].steps[0].uses == "actions/checkout@v3"
        assert fixed.jobs["build"].steps[1].uses == "actions/setup-python@v5.0.0"

    def test_fix_pins_multiple_unpinned_actions(self):
        """PinActions.fix() pins all unpinned actions."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[
                        Step(uses="actions/checkout"),
                        Step(uses="actions/setup-python"),
                    ],
                )
            },
        )

        policy = PinActions()
        fixed = policy.fix(workflow)

        result = policy.evaluate(fixed)
        assert result.passed is True


class TestLimitJobCountFix:
    """Tests for LimitJobCount.fix() method."""

    def test_fix_returns_unchanged(self):
        """LimitJobCount.fix() returns workflow unchanged (can't auto-fix)."""
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

        policy = LimitJobCount(max_jobs=2)
        fixed = policy.fix(workflow)

        # Should still fail - can't auto-fix
        result = policy.evaluate(fixed)
        assert result.passed is False
        assert len(fixed.jobs) == 4


class TestNoHardcodedSecretsFix:
    """Tests for NoHardcodedSecrets.fix() method."""

    def test_fix_returns_unchanged(self):
        """NoHardcodedSecrets.fix() returns workflow unchanged (can't auto-fix)."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(run="export TOKEN=abc123")],
                )
            },
        )

        policy = NoHardcodedSecrets()
        fixed = policy.fix(workflow)

        # Should still fail - can't auto-fix
        result = policy.evaluate(fixed)
        assert result.passed is False


class TestRequireApprovalFix:
    """Tests for RequireApproval.fix() method."""

    def test_fix_returns_unchanged(self):
        """RequireApproval.fix() returns workflow unchanged (can't auto-fix)."""
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
        fixed = policy.fix(workflow)

        # Should still fail - can't auto-fix
        result = policy.evaluate(fixed)
        assert result.passed is False


class TestPolicyEngineFix:
    """Tests for PolicyEngine.fix_all() method."""

    def test_fix_all_applies_all_fixable_policies(self):
        """PolicyEngine.fix_all() applies all fixable policies."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(run="make build")],
                )
            },
        )

        engine = PolicyEngine(policies=[RequireCheckout(), RequireTimeouts()])
        fixed = engine.fix_all(workflow)

        # Both policies should now pass
        results = engine.evaluate(fixed)
        assert all(r.passed for r in results)

    def test_fix_all_with_unfixable_policies(self):
        """PolicyEngine.fix_all() applies what it can and skips unfixable."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[
                        Step(run="make build"),
                        Step(run="export TOKEN=abc123"),  # Unfixable
                    ],
                )
            },
        )

        engine = PolicyEngine(
            policies=[RequireCheckout(), RequireTimeouts(), NoHardcodedSecrets()]
        )
        fixed = engine.fix_all(workflow)

        results = engine.evaluate(fixed)
        # RequireCheckout and RequireTimeouts should pass
        # NoHardcodedSecrets should still fail
        passed_count = sum(1 for r in results if r.passed)
        assert passed_count == 2

    def test_fix_all_returns_unchanged_when_all_pass(self):
        """PolicyEngine.fix_all() returns workflow unchanged when already compliant."""
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
        fixed = engine.fix_all(workflow)

        # Should remain compliant
        results = engine.evaluate(fixed)
        assert all(r.passed for r in results)

    def test_fix_all_empty_policies(self):
        """PolicyEngine.fix_all() with no policies returns workflow unchanged."""
        workflow = Workflow(
            name="Test",
            on=Triggers(),
            jobs={
                "build": Job(
                    runs_on="ubuntu-latest",
                    steps=[Step(run="echo test")],
                )
            },
        )

        engine = PolicyEngine(policies=[])
        fixed = engine.fix_all(workflow)

        assert len(fixed.jobs) == 1
        assert len(fixed.jobs["build"].steps) == 1


class TestPolicyFixMethod:
    """Tests for Policy.fix() base method behavior."""

    def test_policy_fix_method_exists(self):
        """All policies have a fix() method."""
        policies = [
            RequireCheckout(),
            RequireTimeouts(),
            NoHardcodedSecrets(),
            RequireApproval(),
            PinActions(),
            LimitJobCount(),
        ]

        workflow = Workflow(name="Test", on=Triggers(), jobs={})

        for policy in policies:
            assert hasattr(policy, "fix")
            # Should be callable and return a Workflow
            result = policy.fix(workflow)
            assert isinstance(result, Workflow)
