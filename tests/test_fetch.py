"""Tests for schema fetching."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add codegen to path
sys.path.insert(0, str(Path(__file__).parent.parent / "codegen"))

from fetch import (
    ACTION_REPOS,
    SCHEMA_URLS,
    fetch_action_yml,
    fetch_all_schemas,
    fetch_with_retry,
    fetch_workflow_schema,
    get_action_url,
    update_manifest,
)


class TestSchemaURLs:
    """Tests for schema URL constants."""

    def test_workflow_schema_url_defined(self):
        """Workflow schema URL is defined."""
        assert "workflow" in SCHEMA_URLS
        assert "json.schemastore.org" in SCHEMA_URLS["workflow"]

    def test_dependabot_schema_url_defined(self):
        """Dependabot schema URL is defined."""
        assert "dependabot" in SCHEMA_URLS
        assert "json.schemastore.org" in SCHEMA_URLS["dependabot"]

    def test_issue_forms_schema_url_defined(self):
        """Issue forms schema URL is defined."""
        assert "issue-forms" in SCHEMA_URLS
        assert "json.schemastore.org" in SCHEMA_URLS["issue-forms"]


class TestActionRepos:
    """Tests for action repository constants."""

    def test_checkout_repo_defined(self):
        """checkout action repo is defined."""
        assert "checkout" in ACTION_REPOS
        assert ACTION_REPOS["checkout"] == "actions/checkout"

    def test_setup_python_repo_defined(self):
        """setup-python action repo is defined."""
        assert "setup-python" in ACTION_REPOS
        assert ACTION_REPOS["setup-python"] == "actions/setup-python"

    def test_setup_node_repo_defined(self):
        """setup-node action repo is defined."""
        assert "setup-node" in ACTION_REPOS
        assert ACTION_REPOS["setup-node"] == "actions/setup-node"

    def test_setup_go_repo_defined(self):
        """setup-go action repo is defined."""
        assert "setup-go" in ACTION_REPOS
        assert ACTION_REPOS["setup-go"] == "actions/setup-go"

    def test_cache_repo_defined(self):
        """cache action repo is defined."""
        assert "cache" in ACTION_REPOS
        assert ACTION_REPOS["cache"] == "actions/cache"

    def test_upload_artifact_repo_defined(self):
        """upload-artifact action repo is defined."""
        assert "upload-artifact" in ACTION_REPOS
        assert ACTION_REPOS["upload-artifact"] == "actions/upload-artifact"

    def test_download_artifact_repo_defined(self):
        """download-artifact action repo is defined."""
        assert "download-artifact" in ACTION_REPOS
        assert ACTION_REPOS["download-artifact"] == "actions/download-artifact"


class TestGetActionUrl:
    """Tests for get_action_url function."""

    def test_get_action_url(self):
        """get_action_url returns correct URL."""
        url = get_action_url("actions/checkout")
        assert "raw.githubusercontent.com" in url
        assert "actions/checkout" in url
        assert "action.yml" in url


class TestFetchWithRetry:
    """Tests for fetch_with_retry function."""

    @patch("fetch.urlopen")
    def test_fetch_success(self, mock_urlopen):
        """fetch_with_retry returns content on success."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"test": "data"}'
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = fetch_with_retry("https://example.com/test.json")
        assert result == b'{"test": "data"}'

    @patch("fetch.urlopen")
    def test_fetch_retry_on_failure(self, mock_urlopen):
        """fetch_with_retry retries on URLError."""
        from urllib.error import URLError

        mock_urlopen.side_effect = [
            URLError("Connection error"),
            URLError("Connection error"),
        ]

        with pytest.raises(URLError):
            fetch_with_retry("https://example.com/test.json", retries=2, delay=0)

        assert mock_urlopen.call_count == 2


class TestFetchWorkflowSchema:
    """Tests for fetch_workflow_schema function."""

    @patch("fetch.fetch_with_retry")
    def test_fetch_workflow_schema(self, mock_fetch):
        """fetch_workflow_schema fetches and parses JSON."""
        mock_fetch.return_value = (
            b'{"$schema": "http://json-schema.org/draft-07/schema#"}'
        )

        result = fetch_workflow_schema()
        assert result["$schema"] == "http://json-schema.org/draft-07/schema#"


class TestFetchActionYml:
    """Tests for fetch_action_yml function."""

    @patch("fetch.fetch_with_retry")
    def test_fetch_action_yml(self, mock_fetch):
        """fetch_action_yml fetches action.yml content."""
        mock_fetch.return_value = b"name: 'Checkout'\ndescription: 'Checkout a repo'"

        result = fetch_action_yml("actions/checkout")
        assert "name:" in result
        assert "Checkout" in result


class TestFetchAllSchemas:
    """Tests for fetch_all_schemas function."""

    @patch("fetch.fetch_workflow_schema")
    @patch("fetch.fetch_action_yml")
    def test_fetch_all_schemas(self, mock_action, mock_workflow, tmp_path):
        """fetch_all_schemas fetches all schemas and actions."""
        mock_workflow.return_value = {"$schema": "test"}
        mock_action.return_value = "name: Test"

        result = fetch_all_schemas(output_dir=tmp_path)

        assert result["workflow"] is not None
        assert len(result["actions"]) > 0


class TestUpdateManifest:
    """Tests for update_manifest function."""

    def test_update_manifest(self, tmp_path):
        """update_manifest creates/updates manifest.json."""
        schemas = {
            "workflow": {"$schema": "test"},
            "dependabot": {"version": 2},
            "actions": {"checkout": "name: Checkout"},
        }

        update_manifest(tmp_path, schemas)

        manifest_path = tmp_path / "manifest.json"
        assert manifest_path.exists()

        with open(manifest_path) as f:
            manifest = json.load(f)

        assert "fetched_at" in manifest
        assert "schemas" in manifest
        assert "actions" in manifest
