"""Tests for Branch Protection Rules configuration support."""

import yaml


class TestBranchProtectionTypes:
    """Tests for Branch Protection dataclass types."""

    def test_branch_protection_rule_dataclass_exists(self):
        """BranchProtectionRule dataclass can be imported."""
        from wetwire_github.branch_protection import BranchProtectionRule

        assert BranchProtectionRule is not None

    def test_status_check_dataclass_exists(self):
        """StatusCheck dataclass can be imported."""
        from wetwire_github.branch_protection import StatusCheck

        assert StatusCheck is not None

    def test_required_reviewers_dataclass_exists(self):
        """RequiredReviewers dataclass can be imported."""
        from wetwire_github.branch_protection import RequiredReviewers

        assert RequiredReviewers is not None

    def test_push_restrictions_dataclass_exists(self):
        """PushRestrictions dataclass can be imported."""
        from wetwire_github.branch_protection import PushRestrictions

        assert PushRestrictions is not None


class TestStatusCheck:
    """Tests for StatusCheck dataclass."""

    def test_basic_status_check(self):
        """Basic status check can be created."""
        from wetwire_github.branch_protection import StatusCheck

        check = StatusCheck(strict=True, contexts=["ci/tests"])
        assert check.strict is True
        assert check.contexts == ["ci/tests"]

    def test_status_check_with_multiple_contexts(self):
        """Status check with multiple contexts can be created."""
        from wetwire_github.branch_protection import StatusCheck

        check = StatusCheck(strict=False, contexts=["ci/tests", "ci/lint", "ci/build"])
        assert len(check.contexts) == 3
        assert "ci/lint" in check.contexts

    def test_status_check_with_empty_contexts(self):
        """Status check with empty contexts can be created."""
        from wetwire_github.branch_protection import StatusCheck

        check = StatusCheck(strict=True, contexts=[])
        assert check.strict is True
        assert check.contexts == []

    def test_status_check_defaults(self):
        """Status check has proper defaults."""
        from wetwire_github.branch_protection import StatusCheck

        check = StatusCheck()
        assert check.strict is False
        assert check.contexts == []


class TestRequiredReviewers:
    """Tests for RequiredReviewers dataclass."""

    def test_basic_required_reviewers(self):
        """Basic required reviewers can be created."""
        from wetwire_github.branch_protection import RequiredReviewers

        reviewers = RequiredReviewers(required_count=1)
        assert reviewers.required_count == 1

    def test_required_reviewers_with_dismiss_stale(self):
        """Required reviewers with dismiss stale reviews can be created."""
        from wetwire_github.branch_protection import RequiredReviewers

        reviewers = RequiredReviewers(required_count=2, dismiss_stale_reviews=True)
        assert reviewers.required_count == 2
        assert reviewers.dismiss_stale_reviews is True

    def test_required_reviewers_with_code_owner_reviews(self):
        """Required reviewers with code owner reviews can be created."""
        from wetwire_github.branch_protection import RequiredReviewers

        reviewers = RequiredReviewers(
            required_count=1, require_code_owner_reviews=True
        )
        assert reviewers.require_code_owner_reviews is True

    def test_required_reviewers_with_last_push_approval(self):
        """Required reviewers with last push approval can be created."""
        from wetwire_github.branch_protection import RequiredReviewers

        reviewers = RequiredReviewers(
            required_count=1, require_last_push_approval=True
        )
        assert reviewers.require_last_push_approval is True

    def test_required_reviewers_defaults(self):
        """Required reviewers has proper defaults."""
        from wetwire_github.branch_protection import RequiredReviewers

        reviewers = RequiredReviewers()
        assert reviewers.required_count == 1
        assert reviewers.dismiss_stale_reviews is None
        assert reviewers.require_code_owner_reviews is None
        assert reviewers.require_last_push_approval is None
        assert reviewers.dismissal_restrictions == []
        assert reviewers.bypass_pull_request_allowances == []


class TestPushRestrictions:
    """Tests for PushRestrictions dataclass."""

    def test_basic_push_restrictions(self):
        """Basic push restrictions can be created."""
        from wetwire_github.branch_protection import PushRestrictions

        restrictions = PushRestrictions(users=["admin"])
        assert restrictions.users == ["admin"]

    def test_push_restrictions_with_teams(self):
        """Push restrictions with teams can be created."""
        from wetwire_github.branch_protection import PushRestrictions

        restrictions = PushRestrictions(teams=["core-team", "security-team"])
        assert len(restrictions.teams) == 2
        assert "core-team" in restrictions.teams

    def test_push_restrictions_with_apps(self):
        """Push restrictions with apps can be created."""
        from wetwire_github.branch_protection import PushRestrictions

        restrictions = PushRestrictions(apps=["github-actions"])
        assert restrictions.apps == ["github-actions"]

    def test_push_restrictions_combined(self):
        """Push restrictions with users, teams, and apps can be created."""
        from wetwire_github.branch_protection import PushRestrictions

        restrictions = PushRestrictions(
            users=["admin"], teams=["security"], apps=["dependabot"]
        )
        assert restrictions.users == ["admin"]
        assert restrictions.teams == ["security"]
        assert restrictions.apps == ["dependabot"]

    def test_push_restrictions_defaults(self):
        """Push restrictions has proper defaults."""
        from wetwire_github.branch_protection import PushRestrictions

        restrictions = PushRestrictions()
        assert restrictions.users == []
        assert restrictions.teams == []
        assert restrictions.apps == []


class TestBranchProtectionRule:
    """Tests for BranchProtectionRule dataclass."""

    def test_basic_branch_protection_rule(self):
        """Basic branch protection rule can be created."""
        from wetwire_github.branch_protection import BranchProtectionRule

        rule = BranchProtectionRule(pattern="main")
        assert rule.pattern == "main"

    def test_branch_protection_with_status_checks(self):
        """Branch protection with status checks can be created."""
        from wetwire_github.branch_protection import (
            BranchProtectionRule,
            StatusCheck,
        )

        rule = BranchProtectionRule(
            pattern="main",
            require_status_checks=StatusCheck(
                strict=True, contexts=["ci/tests", "ci/lint"]
            ),
        )
        assert rule.require_status_checks is not None
        assert rule.require_status_checks.strict is True
        assert len(rule.require_status_checks.contexts) == 2

    def test_branch_protection_with_required_reviewers(self):
        """Branch protection with required reviewers can be created."""
        from wetwire_github.branch_protection import (
            BranchProtectionRule,
            RequiredReviewers,
        )

        rule = BranchProtectionRule(
            pattern="main",
            require_pull_request_reviews=RequiredReviewers(
                required_count=2, dismiss_stale_reviews=True
            ),
        )
        assert rule.require_pull_request_reviews is not None
        assert rule.require_pull_request_reviews.required_count == 2
        assert rule.require_pull_request_reviews.dismiss_stale_reviews is True

    def test_branch_protection_with_push_restrictions(self):
        """Branch protection with push restrictions can be created."""
        from wetwire_github.branch_protection import (
            BranchProtectionRule,
            PushRestrictions,
        )

        rule = BranchProtectionRule(
            pattern="main",
            restrictions=PushRestrictions(users=["admin"], teams=["security"]),
        )
        assert rule.restrictions is not None
        assert rule.restrictions.users == ["admin"]
        assert rule.restrictions.teams == ["security"]

    def test_branch_protection_combined(self):
        """Branch protection with all settings can be created."""
        from wetwire_github.branch_protection import (
            BranchProtectionRule,
            PushRestrictions,
            RequiredReviewers,
            StatusCheck,
        )

        rule = BranchProtectionRule(
            pattern="main",
            require_status_checks=StatusCheck(
                strict=True, contexts=["ci/tests", "ci/lint"]
            ),
            require_pull_request_reviews=RequiredReviewers(
                required_count=1, dismiss_stale_reviews=True
            ),
            restrictions=PushRestrictions(users=["admin"]),
            enforce_admins=True,
            require_linear_history=True,
            allow_force_pushes=False,
            allow_deletions=False,
        )
        assert rule.pattern == "main"
        assert rule.enforce_admins is True
        assert rule.require_linear_history is True
        assert rule.allow_force_pushes is False
        assert rule.allow_deletions is False

    def test_branch_protection_wildcard_pattern(self):
        """Branch protection with wildcard pattern can be created."""
        from wetwire_github.branch_protection import BranchProtectionRule

        rule = BranchProtectionRule(pattern="release/*")
        assert rule.pattern == "release/*"

    def test_branch_protection_defaults(self):
        """Branch protection has proper defaults."""
        from wetwire_github.branch_protection import BranchProtectionRule

        rule = BranchProtectionRule(pattern="main")
        assert rule.require_status_checks is None
        assert rule.require_pull_request_reviews is None
        assert rule.restrictions is None
        assert rule.enforce_admins is None
        assert rule.require_linear_history is None
        assert rule.allow_force_pushes is None
        assert rule.allow_deletions is None
        assert rule.required_conversation_resolution is None
        assert rule.lock_branch is None
        assert rule.allow_fork_syncing is None


class TestBranchProtectionSerialization:
    """Tests for Branch Protection YAML serialization."""

    def test_serialize_basic_branch_protection(self):
        """Basic branch protection rule serializes to valid dict."""
        from wetwire_github.branch_protection import BranchProtectionRule
        from wetwire_github.serialize import to_dict

        rule = BranchProtectionRule(pattern="main")

        result = to_dict(rule)
        assert result["pattern"] == "main"

    def test_serialize_with_status_checks(self):
        """Branch protection with status checks serializes correctly."""
        from wetwire_github.branch_protection import (
            BranchProtectionRule,
            StatusCheck,
        )
        from wetwire_github.serialize import to_dict

        rule = BranchProtectionRule(
            pattern="main",
            require_status_checks=StatusCheck(
                strict=True, contexts=["ci/tests", "ci/lint"]
            ),
        )

        result = to_dict(rule)
        assert result["pattern"] == "main"
        assert result["require-status-checks"]["strict"] is True
        assert len(result["require-status-checks"]["contexts"]) == 2
        assert "ci/tests" in result["require-status-checks"]["contexts"]

    def test_serialize_with_required_reviewers(self):
        """Branch protection with required reviewers serializes correctly."""
        from wetwire_github.branch_protection import (
            BranchProtectionRule,
            RequiredReviewers,
        )
        from wetwire_github.serialize import to_dict

        rule = BranchProtectionRule(
            pattern="main",
            require_pull_request_reviews=RequiredReviewers(
                required_count=2, dismiss_stale_reviews=True
            ),
        )

        result = to_dict(rule)
        assert result["require-pull-request-reviews"]["required-count"] == 2
        assert result["require-pull-request-reviews"]["dismiss-stale-reviews"] is True

    def test_serialize_with_push_restrictions(self):
        """Branch protection with push restrictions serializes correctly."""
        from wetwire_github.branch_protection import (
            BranchProtectionRule,
            PushRestrictions,
        )
        from wetwire_github.serialize import to_dict

        rule = BranchProtectionRule(
            pattern="main",
            restrictions=PushRestrictions(users=["admin"], teams=["security"]),
        )

        result = to_dict(rule)
        assert result["restrictions"]["users"] == ["admin"]
        assert result["restrictions"]["teams"] == ["security"]

    def test_serialize_to_yaml_string(self):
        """Branch protection rule can be converted to YAML string."""
        from wetwire_github.branch_protection import (
            BranchProtectionRule,
            RequiredReviewers,
            StatusCheck,
        )
        from wetwire_github.serialize import to_dict

        rule = BranchProtectionRule(
            pattern="main",
            require_status_checks=StatusCheck(
                strict=True, contexts=["ci/tests", "ci/lint"]
            ),
            require_pull_request_reviews=RequiredReviewers(
                required_count=1, dismiss_stale_reviews=True
            ),
        )

        result = to_dict(rule)
        yaml_str = yaml.dump(result, sort_keys=False)
        assert "pattern: main" in yaml_str
        assert "require-status-checks:" in yaml_str
        assert "strict: true" in yaml_str

    def test_serialize_omits_none_values(self):
        """Serialization omits None values."""
        from wetwire_github.branch_protection import BranchProtectionRule
        from wetwire_github.serialize import to_dict

        rule = BranchProtectionRule(pattern="main")

        result = to_dict(rule)
        assert "enforce-admins" not in result
        assert "require-status-checks" not in result
        assert "restrictions" not in result

    def test_serialize_omits_empty_lists(self):
        """Serialization omits empty lists."""
        from wetwire_github.branch_protection import StatusCheck
        from wetwire_github.serialize import to_dict

        check = StatusCheck(strict=True, contexts=[])

        result = to_dict(check)
        assert result["strict"] is True
        assert "contexts" not in result

    def test_serialize_preserves_false_values(self):
        """Serialization preserves False values."""
        from wetwire_github.branch_protection import BranchProtectionRule
        from wetwire_github.serialize import to_dict

        rule = BranchProtectionRule(
            pattern="main", allow_force_pushes=False, allow_deletions=False
        )

        result = to_dict(rule)
        assert result["allow-force-pushes"] is False
        assert result["allow-deletions"] is False

    def test_serialize_full_example(self):
        """Full example from issue serializes correctly."""
        from wetwire_github.branch_protection import (
            BranchProtectionRule,
            RequiredReviewers,
            StatusCheck,
        )
        from wetwire_github.serialize import to_dict

        protection = BranchProtectionRule(
            pattern="main",
            require_status_checks=StatusCheck(
                strict=True,
                contexts=["ci/tests", "ci/lint"],
            ),
            require_pull_request_reviews=RequiredReviewers(
                required_count=1,
                dismiss_stale_reviews=True,
            ),
        )

        result = to_dict(protection)
        assert result["pattern"] == "main"
        assert result["require-status-checks"]["strict"] is True
        assert result["require-status-checks"]["contexts"] == ["ci/tests", "ci/lint"]
        assert result["require-pull-request-reviews"]["required-count"] == 1
        assert result["require-pull-request-reviews"]["dismiss-stale-reviews"] is True
