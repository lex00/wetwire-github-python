"""Tests for Repository Settings configuration support."""

import yaml


class TestRepositorySettingsTypes:
    """Tests for Repository Settings dataclass types."""

    def test_repository_settings_dataclass_exists(self):
        """RepositorySettings dataclass can be imported."""
        from wetwire_github.repository_settings import RepositorySettings

        assert RepositorySettings is not None

    def test_security_settings_dataclass_exists(self):
        """SecuritySettings dataclass can be imported."""
        from wetwire_github.repository_settings import SecuritySettings

        assert SecuritySettings is not None

    def test_merge_settings_dataclass_exists(self):
        """MergeSettings dataclass can be imported."""
        from wetwire_github.repository_settings import MergeSettings

        assert MergeSettings is not None

    def test_feature_settings_dataclass_exists(self):
        """FeatureSettings dataclass can be imported."""
        from wetwire_github.repository_settings import FeatureSettings

        assert FeatureSettings is not None

    def test_page_settings_dataclass_exists(self):
        """PageSettings dataclass can be imported."""
        from wetwire_github.repository_settings import PageSettings

        assert PageSettings is not None


class TestSecuritySettings:
    """Tests for SecuritySettings dataclass."""

    def test_basic_security_settings(self):
        """Basic security settings can be created."""
        from wetwire_github.repository_settings import SecuritySettings

        settings = SecuritySettings(
            enable_vulnerability_alerts=True, enable_automated_security_fixes=True
        )
        assert settings.enable_vulnerability_alerts is True
        assert settings.enable_automated_security_fixes is True

    def test_security_settings_with_secret_scanning(self):
        """Security settings with secret scanning can be created."""
        from wetwire_github.repository_settings import SecuritySettings

        settings = SecuritySettings(
            enable_secret_scanning=True, enable_secret_scanning_push_protection=True
        )
        assert settings.enable_secret_scanning is True
        assert settings.enable_secret_scanning_push_protection is True

    def test_security_settings_with_dependabot(self):
        """Security settings with Dependabot can be created."""
        from wetwire_github.repository_settings import SecuritySettings

        settings = SecuritySettings(
            enable_vulnerability_alerts=True,
            enable_automated_security_fixes=True,
            enable_dependabot_alerts=True,
        )
        assert settings.enable_vulnerability_alerts is True
        assert settings.enable_automated_security_fixes is True
        assert settings.enable_dependabot_alerts is True

    def test_security_settings_all_enabled(self):
        """Security settings with all options enabled can be created."""
        from wetwire_github.repository_settings import SecuritySettings

        settings = SecuritySettings(
            enable_vulnerability_alerts=True,
            enable_automated_security_fixes=True,
            enable_secret_scanning=True,
            enable_secret_scanning_push_protection=True,
            enable_dependabot_alerts=True,
        )
        assert settings.enable_vulnerability_alerts is True
        assert settings.enable_automated_security_fixes is True
        assert settings.enable_secret_scanning is True
        assert settings.enable_secret_scanning_push_protection is True
        assert settings.enable_dependabot_alerts is True

    def test_security_settings_defaults(self):
        """Security settings has proper defaults."""
        from wetwire_github.repository_settings import SecuritySettings

        settings = SecuritySettings()
        assert settings.enable_vulnerability_alerts is False
        assert settings.enable_automated_security_fixes is False
        assert settings.enable_secret_scanning is False
        assert settings.enable_secret_scanning_push_protection is False
        assert settings.enable_dependabot_alerts is False


class TestMergeSettings:
    """Tests for MergeSettings dataclass."""

    def test_basic_merge_settings(self):
        """Basic merge settings can be created."""
        from wetwire_github.repository_settings import MergeSettings

        settings = MergeSettings(allow_squash_merge=True)
        assert settings.allow_squash_merge is True

    def test_merge_settings_with_merge_commit(self):
        """Merge settings with merge commit can be created."""
        from wetwire_github.repository_settings import MergeSettings

        settings = MergeSettings(allow_merge_commit=False)
        assert settings.allow_merge_commit is False

    def test_merge_settings_with_rebase_merge(self):
        """Merge settings with rebase merge can be created."""
        from wetwire_github.repository_settings import MergeSettings

        settings = MergeSettings(allow_rebase_merge=False)
        assert settings.allow_rebase_merge is False

    def test_merge_settings_with_delete_branch(self):
        """Merge settings with delete branch on merge can be created."""
        from wetwire_github.repository_settings import MergeSettings

        settings = MergeSettings(delete_branch_on_merge=True)
        assert settings.delete_branch_on_merge is True

    def test_merge_settings_with_auto_merge(self):
        """Merge settings with auto-merge can be created."""
        from wetwire_github.repository_settings import MergeSettings

        settings = MergeSettings(allow_auto_merge=True)
        assert settings.allow_auto_merge is True

    def test_merge_settings_combined(self):
        """Merge settings with all settings can be created."""
        from wetwire_github.repository_settings import MergeSettings

        settings = MergeSettings(
            allow_squash_merge=True,
            allow_merge_commit=False,
            allow_rebase_merge=False,
            delete_branch_on_merge=True,
            allow_auto_merge=True,
        )
        assert settings.allow_squash_merge is True
        assert settings.allow_merge_commit is False
        assert settings.allow_rebase_merge is False
        assert settings.delete_branch_on_merge is True
        assert settings.allow_auto_merge is True

    def test_merge_settings_defaults(self):
        """Merge settings has proper defaults."""
        from wetwire_github.repository_settings import MergeSettings

        settings = MergeSettings()
        assert settings.allow_squash_merge is True
        assert settings.allow_merge_commit is True
        assert settings.allow_rebase_merge is True
        assert settings.delete_branch_on_merge is False
        assert settings.allow_auto_merge is False


class TestFeatureSettings:
    """Tests for FeatureSettings dataclass."""

    def test_basic_feature_settings(self):
        """Basic feature settings can be created."""
        from wetwire_github.repository_settings import FeatureSettings

        settings = FeatureSettings(has_issues=True)
        assert settings.has_issues is True

    def test_feature_settings_with_wiki(self):
        """Feature settings with wiki can be created."""
        from wetwire_github.repository_settings import FeatureSettings

        settings = FeatureSettings(has_wiki=True)
        assert settings.has_wiki is True

    def test_feature_settings_with_discussions(self):
        """Feature settings with discussions can be created."""
        from wetwire_github.repository_settings import FeatureSettings

        settings = FeatureSettings(has_discussions=True)
        assert settings.has_discussions is True

    def test_feature_settings_with_projects(self):
        """Feature settings with projects can be created."""
        from wetwire_github.repository_settings import FeatureSettings

        settings = FeatureSettings(has_projects=True)
        assert settings.has_projects is True

    def test_feature_settings_combined(self):
        """Feature settings with all features enabled can be created."""
        from wetwire_github.repository_settings import FeatureSettings

        settings = FeatureSettings(
            has_issues=True, has_wiki=True, has_discussions=True, has_projects=True
        )
        assert settings.has_issues is True
        assert settings.has_wiki is True
        assert settings.has_discussions is True
        assert settings.has_projects is True

    def test_feature_settings_defaults(self):
        """Feature settings has proper defaults."""
        from wetwire_github.repository_settings import FeatureSettings

        settings = FeatureSettings()
        assert settings.has_issues is True
        assert settings.has_wiki is False
        assert settings.has_discussions is False
        assert settings.has_projects is False


class TestPageSettings:
    """Tests for PageSettings dataclass."""

    def test_basic_page_settings(self):
        """Basic page settings can be created."""
        from wetwire_github.repository_settings import PageSettings

        settings = PageSettings(enabled=True, branch="main")
        assert settings.enabled is True
        assert settings.branch == "main"

    def test_page_settings_with_path(self):
        """Page settings with path can be created."""
        from wetwire_github.repository_settings import PageSettings

        settings = PageSettings(enabled=True, branch="gh-pages", path="/docs")
        assert settings.enabled is True
        assert settings.branch == "gh-pages"
        assert settings.path == "/docs"

    def test_page_settings_with_cname(self):
        """Page settings with CNAME can be created."""
        from wetwire_github.repository_settings import PageSettings

        settings = PageSettings(
            enabled=True, branch="main", cname="example.com", https_enforced=True
        )
        assert settings.enabled is True
        assert settings.branch == "main"
        assert settings.cname == "example.com"
        assert settings.https_enforced is True

    def test_page_settings_disabled(self):
        """Page settings can be disabled."""
        from wetwire_github.repository_settings import PageSettings

        settings = PageSettings(enabled=False)
        assert settings.enabled is False

    def test_page_settings_defaults(self):
        """Page settings has proper defaults."""
        from wetwire_github.repository_settings import PageSettings

        settings = PageSettings()
        assert settings.enabled is False
        assert settings.branch is None
        assert settings.path is None
        assert settings.cname is None
        assert settings.https_enforced is False


class TestRepositorySettings:
    """Tests for RepositorySettings dataclass."""

    def test_basic_repository_settings(self):
        """Basic repository settings can be created."""
        from wetwire_github.repository_settings import RepositorySettings

        settings = RepositorySettings(name="my-repo")
        assert settings.name == "my-repo"

    def test_repository_settings_with_description(self):
        """Repository settings with description can be created."""
        from wetwire_github.repository_settings import RepositorySettings

        settings = RepositorySettings(
            name="my-repo", description="A test repository", homepage="https://example.com"
        )
        assert settings.name == "my-repo"
        assert settings.description == "A test repository"
        assert settings.homepage == "https://example.com"

    def test_repository_settings_with_visibility(self):
        """Repository settings with visibility can be created."""
        from wetwire_github.repository_settings import RepositorySettings

        settings = RepositorySettings(name="my-repo", private=True)
        assert settings.name == "my-repo"
        assert settings.private is True

    def test_repository_settings_with_security(self):
        """Repository settings with security settings can be created."""
        from wetwire_github.repository_settings import (
            RepositorySettings,
            SecuritySettings,
        )

        settings = RepositorySettings(
            name="my-repo",
            security=SecuritySettings(
                enable_vulnerability_alerts=True, enable_automated_security_fixes=True
            ),
        )
        assert settings.security is not None
        assert settings.security.enable_vulnerability_alerts is True
        assert settings.security.enable_automated_security_fixes is True

    def test_repository_settings_with_merge_settings(self):
        """Repository settings with merge settings can be created."""
        from wetwire_github.repository_settings import (
            MergeSettings,
            RepositorySettings,
        )

        settings = RepositorySettings(
            name="my-repo",
            merge=MergeSettings(
                allow_squash_merge=True, delete_branch_on_merge=True
            ),
        )
        assert settings.merge is not None
        assert settings.merge.allow_squash_merge is True
        assert settings.merge.delete_branch_on_merge is True

    def test_repository_settings_with_features(self):
        """Repository settings with feature settings can be created."""
        from wetwire_github.repository_settings import (
            FeatureSettings,
            RepositorySettings,
        )

        settings = RepositorySettings(
            name="my-repo",
            features=FeatureSettings(has_issues=True, has_wiki=False),
        )
        assert settings.features is not None
        assert settings.features.has_issues is True
        assert settings.features.has_wiki is False

    def test_repository_settings_with_pages(self):
        """Repository settings with page settings can be created."""
        from wetwire_github.repository_settings import (
            PageSettings,
            RepositorySettings,
        )

        settings = RepositorySettings(
            name="my-repo", pages=PageSettings(enabled=True, branch="gh-pages")
        )
        assert settings.pages is not None
        assert settings.pages.enabled is True
        assert settings.pages.branch == "gh-pages"

    def test_repository_settings_combined(self):
        """Repository settings with all settings can be created."""
        from wetwire_github.repository_settings import (
            FeatureSettings,
            MergeSettings,
            PageSettings,
            RepositorySettings,
            SecuritySettings,
        )

        settings = RepositorySettings(
            name="my-repo",
            description="A comprehensive test repository",
            homepage="https://example.com",
            private=False,
            security=SecuritySettings(
                enable_vulnerability_alerts=True,
                enable_automated_security_fixes=True,
                enable_secret_scanning=True,
            ),
            merge=MergeSettings(
                allow_squash_merge=True,
                allow_merge_commit=False,
                delete_branch_on_merge=True,
            ),
            features=FeatureSettings(
                has_issues=True, has_wiki=True, has_discussions=True
            ),
            pages=PageSettings(enabled=True, branch="main", path="/docs"),
        )
        assert settings.name == "my-repo"
        assert settings.description == "A comprehensive test repository"
        assert settings.homepage == "https://example.com"
        assert settings.private is False
        assert settings.security.enable_vulnerability_alerts is True
        assert settings.merge.allow_squash_merge is True
        assert settings.features.has_issues is True
        assert settings.pages.enabled is True

    def test_repository_settings_defaults(self):
        """Repository settings has proper defaults."""
        from wetwire_github.repository_settings import RepositorySettings

        settings = RepositorySettings(name="my-repo")
        assert settings.name == "my-repo"
        assert settings.description is None
        assert settings.homepage is None
        assert settings.private is False
        assert settings.security is None
        assert settings.merge is None
        assert settings.features is None
        assert settings.pages is None


class TestRepositorySettingsSerialization:
    """Tests for Repository Settings serialization."""

    def test_serialize_basic_repository_settings(self):
        """Basic repository settings serializes to valid dict."""
        from wetwire_github.repository_settings import RepositorySettings
        from wetwire_github.serialize import to_dict

        settings = RepositorySettings(name="my-repo")

        result = to_dict(settings)
        assert result["name"] == "my-repo"

    def test_serialize_with_description(self):
        """Repository settings with description serializes correctly."""
        from wetwire_github.repository_settings import RepositorySettings
        from wetwire_github.serialize import to_dict

        settings = RepositorySettings(
            name="my-repo", description="Test repository", homepage="https://example.com"
        )

        result = to_dict(settings)
        assert result["name"] == "my-repo"
        assert result["description"] == "Test repository"
        assert result["homepage"] == "https://example.com"

    def test_serialize_with_security_settings(self):
        """Repository settings with security settings serializes correctly."""
        from wetwire_github.repository_settings import (
            RepositorySettings,
            SecuritySettings,
        )
        from wetwire_github.serialize import to_dict

        settings = RepositorySettings(
            name="my-repo",
            security=SecuritySettings(
                enable_vulnerability_alerts=True, enable_automated_security_fixes=True
            ),
        )

        result = to_dict(settings)
        assert result["security"]["enable-vulnerability-alerts"] is True
        assert result["security"]["enable-automated-security-fixes"] is True

    def test_serialize_with_merge_settings(self):
        """Repository settings with merge settings serializes correctly."""
        from wetwire_github.repository_settings import (
            MergeSettings,
            RepositorySettings,
        )
        from wetwire_github.serialize import to_dict

        settings = RepositorySettings(
            name="my-repo",
            merge=MergeSettings(
                allow_squash_merge=True, delete_branch_on_merge=True
            ),
        )

        result = to_dict(settings)
        assert result["merge"]["allow-squash-merge"] is True
        assert result["merge"]["delete-branch-on-merge"] is True

    def test_serialize_with_feature_settings(self):
        """Repository settings with feature settings serializes correctly."""
        from wetwire_github.repository_settings import (
            FeatureSettings,
            RepositorySettings,
        )
        from wetwire_github.serialize import to_dict

        settings = RepositorySettings(
            name="my-repo", features=FeatureSettings(has_issues=True, has_wiki=False)
        )

        result = to_dict(settings)
        assert result["features"]["has-issues"] is True
        assert result["features"]["has-wiki"] is False

    def test_serialize_with_page_settings(self):
        """Repository settings with page settings serializes correctly."""
        from wetwire_github.repository_settings import (
            PageSettings,
            RepositorySettings,
        )
        from wetwire_github.serialize import to_dict

        settings = RepositorySettings(
            name="my-repo",
            pages=PageSettings(enabled=True, branch="gh-pages", path="/docs"),
        )

        result = to_dict(settings)
        assert result["pages"]["enabled"] is True
        assert result["pages"]["branch"] == "gh-pages"
        assert result["pages"]["path"] == "/docs"

    def test_serialize_to_yaml_string(self):
        """Repository settings can be converted to YAML string."""
        from wetwire_github.repository_settings import (
            MergeSettings,
            RepositorySettings,
            SecuritySettings,
        )
        from wetwire_github.serialize import to_dict

        settings = RepositorySettings(
            name="my-repo",
            description="Test repository",
            security=SecuritySettings(enable_vulnerability_alerts=True),
            merge=MergeSettings(allow_squash_merge=True),
        )

        result = to_dict(settings)
        yaml_str = yaml.dump(result, sort_keys=False)
        assert "name: my-repo" in yaml_str
        assert "description: Test repository" in yaml_str
        assert "security:" in yaml_str
        assert "merge:" in yaml_str

    def test_serialize_omits_none_values(self):
        """Serialization omits None values."""
        from wetwire_github.repository_settings import RepositorySettings
        from wetwire_github.serialize import to_dict

        settings = RepositorySettings(name="my-repo")

        result = to_dict(settings)
        assert "description" not in result
        assert "homepage" not in result
        assert "security" not in result
        assert "merge" not in result
        assert "features" not in result
        assert "pages" not in result

    def test_serialize_preserves_false_values(self):
        """Serialization preserves False values."""
        from wetwire_github.repository_settings import RepositorySettings
        from wetwire_github.serialize import to_dict

        settings = RepositorySettings(name="my-repo", private=False)

        result = to_dict(settings)
        assert result["private"] is False

    def test_serialize_full_example(self):
        """Full example serializes correctly."""
        from wetwire_github.repository_settings import (
            FeatureSettings,
            MergeSettings,
            PageSettings,
            RepositorySettings,
            SecuritySettings,
        )
        from wetwire_github.serialize import to_dict

        settings = RepositorySettings(
            name="my-awesome-repo",
            description="An awesome repository",
            homepage="https://awesome.example.com",
            private=False,
            security=SecuritySettings(
                enable_vulnerability_alerts=True,
                enable_automated_security_fixes=True,
                enable_secret_scanning=True,
                enable_secret_scanning_push_protection=True,
            ),
            merge=MergeSettings(
                allow_squash_merge=True,
                allow_merge_commit=False,
                allow_rebase_merge=False,
                delete_branch_on_merge=True,
                allow_auto_merge=True,
            ),
            features=FeatureSettings(
                has_issues=True, has_wiki=True, has_discussions=True, has_projects=True
            ),
            pages=PageSettings(
                enabled=True,
                branch="main",
                path="/docs",
                cname="docs.example.com",
                https_enforced=True,
            ),
        )

        result = to_dict(settings)
        assert result["name"] == "my-awesome-repo"
        assert result["description"] == "An awesome repository"
        assert result["homepage"] == "https://awesome.example.com"
        assert result["private"] is False
        assert result["security"]["enable-vulnerability-alerts"] is True
        assert result["security"]["enable-automated-security-fixes"] is True
        assert result["security"]["enable-secret-scanning"] is True
        assert result["security"]["enable-secret-scanning-push-protection"] is True
        assert result["merge"]["allow-squash-merge"] is True
        assert result["merge"]["allow-merge-commit"] is False
        assert result["merge"]["delete-branch-on-merge"] is True
        assert result["merge"]["allow-auto-merge"] is True
        assert result["features"]["has-issues"] is True
        assert result["features"]["has-wiki"] is True
        assert result["features"]["has-discussions"] is True
        assert result["features"]["has-projects"] is True
        assert result["pages"]["enabled"] is True
        assert result["pages"]["branch"] == "main"
        assert result["pages"]["path"] == "/docs"
        assert result["pages"]["cname"] == "docs.example.com"
        assert result["pages"]["https-enforced"] is True


class TestEdgeCases:
    """Tests for edge cases and partial configurations."""

    def test_empty_security_settings(self):
        """Empty security settings can be created."""
        from wetwire_github.repository_settings import SecuritySettings

        settings = SecuritySettings()
        assert settings.enable_vulnerability_alerts is False
        assert settings.enable_automated_security_fixes is False

    def test_empty_merge_settings(self):
        """Empty merge settings can be created with defaults."""
        from wetwire_github.repository_settings import MergeSettings

        settings = MergeSettings()
        assert settings.allow_squash_merge is True
        assert settings.allow_merge_commit is True
        assert settings.allow_rebase_merge is True

    def test_empty_feature_settings(self):
        """Empty feature settings can be created with defaults."""
        from wetwire_github.repository_settings import FeatureSettings

        settings = FeatureSettings()
        assert settings.has_issues is True
        assert settings.has_wiki is False

    def test_empty_page_settings(self):
        """Empty page settings can be created with defaults."""
        from wetwire_github.repository_settings import PageSettings

        settings = PageSettings()
        assert settings.enabled is False
        assert settings.branch is None

    def test_partial_configuration(self):
        """Partial configuration with only some settings can be created."""
        from wetwire_github.repository_settings import (
            MergeSettings,
            RepositorySettings,
        )

        settings = RepositorySettings(
            name="my-repo", merge=MergeSettings(allow_squash_merge=True)
        )
        assert settings.name == "my-repo"
        assert settings.merge is not None
        assert settings.security is None
        assert settings.features is None
        assert settings.pages is None

    def test_partial_merge_settings(self):
        """Partial merge settings can be created."""
        from wetwire_github.repository_settings import MergeSettings

        settings = MergeSettings(delete_branch_on_merge=True)
        assert settings.delete_branch_on_merge is True
        assert settings.allow_squash_merge is True  # default
        assert settings.allow_merge_commit is True  # default

    def test_partial_security_settings(self):
        """Partial security settings can be created."""
        from wetwire_github.repository_settings import SecuritySettings

        settings = SecuritySettings(enable_secret_scanning=True)
        assert settings.enable_secret_scanning is True
        assert settings.enable_vulnerability_alerts is False  # default
        assert settings.enable_automated_security_fixes is False  # default
