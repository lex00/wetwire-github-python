"""Tests for actions/dependency-review-action wrapper (issue #185)."""

from wetwire_github.actions import dependency_review
from wetwire_github.serialize import to_yaml
from wetwire_github.workflow import Step


class TestDependencyReview:
    """Tests for actions/dependency-review-action@v4 wrapper."""

    def test_basic_creation_no_parameters(self) -> None:
        """Test basic creation with no parameters (all optional)."""
        step = dependency_review()

        assert isinstance(step, Step)
        assert step.uses == "actions/dependency-review-action@v4"
        assert step.with_ is None

    def test_with_fail_on_severity(self) -> None:
        """Test with fail_on_severity parameter."""
        step = dependency_review(fail_on_severity="high")

        assert step.uses == "actions/dependency-review-action@v4"
        assert step.with_["fail-on-severity"] == "high"

    def test_with_allow_licenses_list(self) -> None:
        """Test with allow_licenses parameter (list converted to comma-separated string)."""
        step = dependency_review(allow_licenses=["MIT", "Apache-2.0", "BSD-3-Clause"])

        assert step.with_["allow-licenses"] == "MIT, Apache-2.0, BSD-3-Clause"

    def test_with_deny_licenses_list(self) -> None:
        """Test with deny_licenses parameter (list converted to comma-separated string)."""
        step = dependency_review(deny_licenses=["GPL-3.0", "AGPL-3.0"])

        assert step.with_["deny-licenses"] == "GPL-3.0, AGPL-3.0"

    def test_with_config_file(self) -> None:
        """Test with config_file parameter."""
        step = dependency_review(config_file=".github/dependency-review-config.yml")

        assert step.with_["config-file"] == ".github/dependency-review-config.yml"

    def test_serialization_to_yaml(self) -> None:
        """Test that step serializes correctly to YAML."""
        step = dependency_review(
            fail_on_severity="moderate",
            allow_licenses=["MIT", "Apache-2.0"],
            config_file=".github/dependency-review-config.yml",
        )

        yaml_output = to_yaml(step)

        assert "uses: actions/dependency-review-action@v4" in yaml_output
        assert "fail-on-severity: moderate" in yaml_output
        assert "allow-licenses: MIT, Apache-2.0" in yaml_output
        assert "config-file: .github/dependency-review-config.yml" in yaml_output

    def test_none_values_not_included(self) -> None:
        """Test that None values are filtered out from with_ dict."""
        step = dependency_review(
            fail_on_severity=None,
            allow_licenses=None,
            deny_licenses=None,
            config_file=None,
        )

        assert step.with_ is None

    def test_all_parameters(self) -> None:
        """Test with all parameters set."""
        step = dependency_review(
            fail_on_severity="critical",
            allow_licenses=["MIT", "Apache-2.0"],
            deny_licenses=["GPL-3.0"],
            config_file=".github/dependency-review-config.yml",
        )

        assert step.uses == "actions/dependency-review-action@v4"
        assert step.with_["fail-on-severity"] == "critical"
        assert step.with_["allow-licenses"] == "MIT, Apache-2.0"
        assert step.with_["deny-licenses"] == "GPL-3.0"
        assert step.with_["config-file"] == ".github/dependency-review-config.yml"

    def test_single_item_license_lists(self) -> None:
        """Test that single-item license lists work correctly."""
        step = dependency_review(
            allow_licenses=["MIT"],
            deny_licenses=["GPL-3.0"],
        )

        assert step.with_["allow-licenses"] == "MIT"
        assert step.with_["deny-licenses"] == "GPL-3.0"

    def test_empty_license_lists_not_included(self) -> None:
        """Test that empty license lists are treated as None."""
        step = dependency_review(
            allow_licenses=[],
            deny_licenses=[],
        )

        # Empty lists should not produce keys in with_
        assert step.with_ is None or "allow-licenses" not in step.with_
        assert step.with_ is None or "deny-licenses" not in step.with_
