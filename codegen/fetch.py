#!/usr/bin/env python3
"""Fetch JSON schemas and action.yml files for code generation.

This script downloads:
- GitHub workflow JSON schema from SchemaStore
- Dependabot JSON schema from SchemaStore
- Issue forms JSON schema from SchemaStore
- action.yml files from popular GitHub Actions repositories

The fetched files are stored in the specs/ directory for use by the code generator.
"""

import json
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Schema URLs from SchemaStore
SCHEMA_URLS = {
    "workflow": "https://json.schemastore.org/github-workflow.json",
    "dependabot": "https://json.schemastore.org/dependabot-2.0.json",
    "issue-forms": "https://json.schemastore.org/github-issue-forms.json",
}

# Popular GitHub Actions to fetch action.yml from
ACTION_REPOS = {
    "checkout": "actions/checkout",
    "setup-python": "actions/setup-python",
    "setup-node": "actions/setup-node",
    "setup-go": "actions/setup-go",
    "setup-java": "actions/setup-java",
    "cache": "actions/cache",
    "upload-artifact": "actions/upload-artifact",
    "download-artifact": "actions/download-artifact",
}

# Default specs directory
DEFAULT_SPECS_DIR = Path(__file__).parent.parent / "specs"


def get_action_url(repo: str, branch: str = "main") -> str:
    """Get the raw URL for an action.yml file.

    Args:
        repo: Repository in format "owner/repo"
        branch: Branch name (default: main)

    Returns:
        URL to the raw action.yml file
    """
    return f"https://raw.githubusercontent.com/{repo}/{branch}/action.yml"


def fetch_with_retry(
    url: str,
    retries: int = 3,
    delay: float = 1.0,
    timeout: int = 30,
) -> bytes:
    """Fetch a URL with retry logic.

    Args:
        url: URL to fetch
        retries: Number of retry attempts
        delay: Delay between retries in seconds
        timeout: Request timeout in seconds

    Returns:
        Response content as bytes

    Raises:
        Exception: If all retries fail
    """
    last_error = None
    request = Request(url, headers={"User-Agent": "wetwire-github/0.1.0"})

    for attempt in range(retries):
        try:
            with urlopen(request, timeout=timeout) as response:
                return response.read()
        except (URLError, HTTPError) as e:
            last_error = e
            if attempt < retries - 1:
                time.sleep(delay * (attempt + 1))  # Exponential backoff

    raise last_error or Exception(f"Failed to fetch {url}")


def fetch_workflow_schema() -> dict:
    """Fetch the GitHub workflow JSON schema.

    Returns:
        Parsed JSON schema as dict
    """
    content = fetch_with_retry(SCHEMA_URLS["workflow"])
    return json.loads(content)


def fetch_dependabot_schema() -> dict:
    """Fetch the Dependabot JSON schema.

    Returns:
        Parsed JSON schema as dict
    """
    content = fetch_with_retry(SCHEMA_URLS["dependabot"])
    return json.loads(content)


def fetch_issue_forms_schema() -> dict:
    """Fetch the GitHub issue forms JSON schema.

    Returns:
        Parsed JSON schema as dict
    """
    content = fetch_with_retry(SCHEMA_URLS["issue-forms"])
    return json.loads(content)


def fetch_action_yml(repo: str, branch: str = "main") -> str:
    """Fetch an action.yml file from a GitHub repository.

    Args:
        repo: Repository in format "owner/repo"
        branch: Branch name (default: main)

    Returns:
        Raw action.yml content as string
    """
    url = get_action_url(repo, branch)
    content = fetch_with_retry(url)
    return content.decode("utf-8")


def fetch_all_schemas(
    output_dir: Path | None = None,
    save: bool = True,
) -> dict:
    """Fetch all schemas and action.yml files.

    Args:
        output_dir: Directory to save fetched files (default: specs/)
        save: Whether to save files to disk

    Returns:
        Dict containing fetched schemas and actions
    """
    if output_dir is None:
        output_dir = DEFAULT_SPECS_DIR

    output_dir.mkdir(parents=True, exist_ok=True)
    actions_dir = output_dir / "actions"
    actions_dir.mkdir(exist_ok=True)

    result = {
        "workflow": None,
        "dependabot": None,
        "issue-forms": None,
        "actions": {},
    }

    # Fetch JSON schemas
    print("Fetching workflow schema...")
    try:
        result["workflow"] = fetch_workflow_schema()
        if save:
            with open(output_dir / "workflow-schema.json", "w") as f:
                json.dump(result["workflow"], f, indent=2)
        print("  ✓ workflow-schema.json")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

    print("Fetching dependabot schema...")
    try:
        result["dependabot"] = fetch_dependabot_schema()
        if save:
            with open(output_dir / "dependabot-schema.json", "w") as f:
                json.dump(result["dependabot"], f, indent=2)
        print("  ✓ dependabot-schema.json")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

    print("Fetching issue-forms schema...")
    try:
        result["issue-forms"] = fetch_issue_forms_schema()
        if save:
            with open(output_dir / "issue-forms-schema.json", "w") as f:
                json.dump(result["issue-forms"], f, indent=2)
        print("  ✓ issue-forms-schema.json")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

    # Fetch action.yml files
    print("Fetching action.yml files...")
    for name, repo in ACTION_REPOS.items():
        try:
            content = fetch_action_yml(repo)
            result["actions"][name] = content
            if save:
                with open(actions_dir / f"{name}.yml", "w") as f:
                    f.write(content)
            print(f"  ✓ {name}.yml")
        except Exception as e:
            print(f"  ✗ {name}: {e}")

    # Update manifest
    if save:
        update_manifest(output_dir, result)

    return result


def update_manifest(output_dir: Path, schemas: dict) -> None:
    """Update the manifest.json file with fetch metadata.

    Args:
        output_dir: Directory containing fetched files
        schemas: Dict of fetched schemas and actions
    """
    manifest = {
        "fetched_at": datetime.now(UTC).isoformat(),
        "schemas": {
            "workflow": "workflow-schema.json" if schemas.get("workflow") else None,
            "dependabot": "dependabot-schema.json"
            if schemas.get("dependabot")
            else None,
            "issue-forms": "issue-forms-schema.json"
            if schemas.get("issue-forms")
            else None,
        },
        "actions": {
            name: f"actions/{name}.yml" for name in schemas.get("actions", {}).keys()
        },
    }

    with open(output_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)


def main() -> int:
    """Main entry point for the schema fetcher.

    Returns:
        Exit code (0 for success)
    """
    print("wetwire-github schema fetcher")
    print("=" * 40)
    print()

    result = fetch_all_schemas()

    print()
    print("Summary:")
    schemas_fetched = sum(
        1 for k in ["workflow", "dependabot", "issue-forms"] if result.get(k)
    )
    actions_fetched = len(result.get("actions", {}))
    print(f"  Schemas: {schemas_fetched}/3")
    print(f"  Actions: {actions_fetched}/{len(ACTION_REPOS)}")

    return 0


if __name__ == "__main__":
    exit(main())
