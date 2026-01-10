"""Generated GitHub Action wrappers."""

from .attest_build_provenance import attest_build_provenance
from .cache import cache
from .checkout import checkout
from .codecov import codecov
from .configure_aws_credentials import configure_aws_credentials
from .configure_pages import configure_pages
from .create_github_app_token import create_github_app_token
from .create_pull_request import create_pull_request
from .dependency_review import dependency_review
from .deploy_pages import deploy_pages
from .docker_build_push import docker_build_push
from .docker_login import docker_login
from .docker_metadata import docker_metadata
from .download_artifact import download_artifact
from .first_interaction import first_interaction
from .gh_pages import gh_pages
from .gh_release import gh_release
from .github_script import github_script
from .labeler import labeler
from .setup_buildx import setup_buildx
from .setup_dotnet import setup_dotnet
from .setup_go import setup_go
from .setup_java import setup_java
from .setup_node import setup_node
from .setup_python import setup_python
from .setup_ruby import setup_ruby
from .stale import stale
from .upload_artifact import upload_artifact
from .upload_pages_artifact import upload_pages_artifact
from .upload_release_asset import upload_release_asset

__all__ = [
    "attest_build_provenance",
    "cache",
    "checkout",
    "codecov",
    "configure_aws_credentials",
    "configure_pages",
    "create_github_app_token",
    "create_pull_request",
    "dependency_review",
    "deploy_pages",
    "docker_build_push",
    "docker_login",
    "docker_metadata",
    "download_artifact",
    "first_interaction",
    "gh_pages",
    "gh_release",
    "github_script",
    "labeler",
    "setup_buildx",
    "setup_dotnet",
    "setup_go",
    "setup_java",
    "setup_node",
    "setup_python",
    "setup_ruby",
    "stale",
    "upload_artifact",
    "upload_pages_artifact",
    "upload_release_asset",
]
