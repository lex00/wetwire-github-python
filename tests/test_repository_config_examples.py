"""Tests to validate that repository config examples compile and are well-formed."""

import re


class TestBranchProtectionExamples:
    """Tests for branch_protection_example.py."""

    def test_main_branch_protection_exists(self):
        """Main branch protection example can be imported."""
        from examples.branch_protection_example import main_branch_protection

        assert main_branch_protection is not None
        assert main_branch_protection.pattern == "main"

    def test_main_branch_has_status_checks(self):
        """Main branch protection has status checks configured."""
        from examples.branch_protection_example import main_branch_protection

        assert main_branch_protection.require_status_checks is not None
        assert main_branch_protection.require_status_checks.strict is True
        assert len(main_branch_protection.require_status_checks.contexts) >= 3

    def test_main_branch_has_reviewers(self):
        """Main branch protection has reviewer requirements."""
        from examples.branch_protection_example import main_branch_protection

        assert main_branch_protection.require_pull_request_reviews is not None
        assert main_branch_protection.require_pull_request_reviews.required_count == 2
        assert main_branch_protection.require_pull_request_reviews.dismiss_stale_reviews is True

    def test_release_branch_protection_exists(self):
        """Release branch protection example can be imported."""
        from examples.branch_protection_example import release_branch_protection

        assert release_branch_protection is not None
        assert release_branch_protection.pattern == "release/*"

    def test_develop_branch_protection_exists(self):
        """Develop branch protection example can be imported."""
        from examples.branch_protection_example import develop_branch_protection

        assert develop_branch_protection is not None
        assert develop_branch_protection.pattern == "develop"

    def test_feature_branch_protection_exists(self):
        """Feature branch protection example can be imported."""
        from examples.branch_protection_example import feature_branch_protection

        assert feature_branch_protection is not None
        assert feature_branch_protection.pattern == "feature/*"

    def test_hotfix_branch_protection_exists(self):
        """Hotfix branch protection example can be imported."""
        from examples.branch_protection_example import hotfix_branch_protection

        assert hotfix_branch_protection is not None
        assert hotfix_branch_protection.pattern == "hotfix/*"

    def test_archive_branch_protection_exists(self):
        """Archive branch protection example can be imported."""
        from examples.branch_protection_example import archive_branch_protection

        assert archive_branch_protection is not None
        assert archive_branch_protection.pattern == "archive/*"
        assert archive_branch_protection.lock_branch is True

    def test_branch_protection_serializes(self):
        """Branch protection examples can be serialized."""
        from examples.branch_protection_example import main_branch_protection
        from wetwire_github.serialize import to_dict

        result = to_dict(main_branch_protection)
        assert "pattern" in result
        assert result["pattern"] == "main"
        assert "require-status-checks" in result


class TestRepositorySettingsExamples:
    """Tests for repository_settings_example.py."""

    def test_open_source_settings_exists(self):
        """Open source settings example can be imported."""
        from examples.repository_settings_example import open_source_settings

        assert open_source_settings is not None
        assert open_source_settings.name == "awesome-library"
        assert open_source_settings.private is False

    def test_open_source_has_full_features(self):
        """Open source settings has community features enabled."""
        from examples.repository_settings_example import open_source_settings

        assert open_source_settings.features is not None
        assert open_source_settings.features.has_issues is True
        assert open_source_settings.features.has_discussions is True
        assert open_source_settings.features.has_wiki is True

    def test_open_source_has_pages(self):
        """Open source settings has GitHub Pages configured."""
        from examples.repository_settings_example import open_source_settings

        assert open_source_settings.pages is not None
        assert open_source_settings.pages.enabled is True
        assert open_source_settings.pages.https_enforced is True

    def test_production_service_settings_exists(self):
        """Production service settings example can be imported."""
        from examples.repository_settings_example import production_service_settings

        assert production_service_settings is not None
        assert production_service_settings.name == "payment-service"
        assert production_service_settings.private is True

    def test_production_service_has_security(self):
        """Production service has security settings enabled."""
        from examples.repository_settings_example import production_service_settings

        assert production_service_settings.security is not None
        assert production_service_settings.security.enable_vulnerability_alerts is True
        assert production_service_settings.security.enable_secret_scanning is True

    def test_documentation_settings_exists(self):
        """Documentation settings example can be imported."""
        from examples.repository_settings_example import documentation_settings

        assert documentation_settings is not None
        assert documentation_settings.name == "company-docs"

    def test_prototype_settings_exists(self):
        """Prototype settings example can be imported."""
        from examples.repository_settings_example import prototype_settings

        assert prototype_settings is not None
        assert prototype_settings.name == "ml-experiment-2024"
        assert prototype_settings.private is True

    def test_archived_settings_exists(self):
        """Archived settings example can be imported."""
        from examples.repository_settings_example import archived_settings

        assert archived_settings is not None
        assert archived_settings.name == "legacy-api-v1"

    def test_repository_settings_serializes(self):
        """Repository settings examples can be serialized."""
        from examples.repository_settings_example import open_source_settings
        from wetwire_github.serialize import to_dict

        result = to_dict(open_source_settings)
        assert "name" in result
        assert result["name"] == "awesome-library"
        assert "security" in result


class TestSecretScanningExamples:
    """Tests for secret_scanning_example.py."""

    def test_basic_config_exists(self):
        """Basic config example can be imported."""
        from examples.secret_scanning_example import basic_config

        assert basic_config is not None
        assert basic_config.enabled is True
        assert basic_config.push_protection is True

    def test_internal_api_config_exists(self):
        """Internal API config example can be imported."""
        from examples.secret_scanning_example import internal_api_config

        assert internal_api_config is not None
        assert len(internal_api_config.patterns) >= 2

    def test_internal_api_patterns_have_valid_regex(self):
        """Internal API patterns have valid regex."""
        from examples.secret_scanning_example import internal_api_patterns

        for pattern in internal_api_patterns:
            # Should not raise
            compiled = re.compile(pattern.pattern)
            assert compiled is not None

    def test_infrastructure_config_exists(self):
        """Infrastructure config example can be imported."""
        from examples.secret_scanning_example import infrastructure_config

        assert infrastructure_config is not None
        assert len(infrastructure_config.patterns) >= 3

    def test_cloud_config_exists(self):
        """Cloud config example can be imported."""
        from examples.secret_scanning_example import cloud_config

        assert cloud_config is not None
        assert len(cloud_config.patterns) >= 3

    def test_application_config_exists(self):
        """Application config example can be imported."""
        from examples.secret_scanning_example import application_config

        assert application_config is not None
        assert len(application_config.patterns) >= 3

    def test_third_party_config_exists(self):
        """Third party config example can be imported."""
        from examples.secret_scanning_example import third_party_config

        assert third_party_config is not None
        assert len(third_party_config.patterns) >= 3

    def test_comprehensive_config_exists(self):
        """Comprehensive config example can be imported."""
        from examples.secret_scanning_example import comprehensive_config

        assert comprehensive_config is not None
        assert comprehensive_config.enabled is True
        assert comprehensive_config.push_protection is True
        assert len(comprehensive_config.patterns) >= 5

    def test_all_patterns_have_valid_regex(self):
        """All pattern examples have valid regex."""
        from examples.secret_scanning_example import (
            application_patterns,
            cloud_patterns,
            infrastructure_patterns,
            internal_api_patterns,
            third_party_patterns,
        )

        all_patterns = (
            internal_api_patterns
            + infrastructure_patterns
            + cloud_patterns
            + application_patterns
            + third_party_patterns
        )

        for pattern in all_patterns:
            # Should not raise
            compiled = re.compile(pattern.pattern)
            assert compiled is not None
            assert pattern.name is not None
            assert len(pattern.name) > 0

    def test_secret_scanning_serializes(self):
        """Secret scanning examples can be serialized."""
        from examples.secret_scanning_example import comprehensive_config
        from wetwire_github.serialize import to_dict

        result = to_dict(comprehensive_config)
        assert "enabled" in result
        assert result["enabled"] is True
        assert "patterns" in result
        assert len(result["patterns"]) >= 5


class TestCrossModuleIntegration:
    """Tests that verify examples work together."""

    def test_all_examples_import_successfully(self):
        """All example modules can be imported together."""
        from examples import (
            branch_protection_example,
            repository_settings_example,
            secret_scanning_example,
        )

        assert branch_protection_example is not None
        assert repository_settings_example is not None
        assert secret_scanning_example is not None

    def test_examples_use_consistent_types(self):
        """Examples use the correct types from wetwire_github modules."""
        from examples.branch_protection_example import main_branch_protection
        from examples.repository_settings_example import open_source_settings
        from examples.secret_scanning_example import comprehensive_config
        from wetwire_github.branch_protection import BranchProtectionRule
        from wetwire_github.repository_settings import RepositorySettings
        from wetwire_github.secret_scanning import SecretScanningConfig

        assert isinstance(main_branch_protection, BranchProtectionRule)
        assert isinstance(open_source_settings, RepositorySettings)
        assert isinstance(comprehensive_config, SecretScanningConfig)
