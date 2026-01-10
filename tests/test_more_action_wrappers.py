"""Tests for additional typed action wrappers (issue #94)."""

import pytest

from wetwire_github.actions import (
    docker_build_push,
    docker_login,
    github_script,
    setup_dotnet,
    setup_ruby,
)
from wetwire_github.workflow import Step


class TestGithubScript:
    """Tests for github_script wrapper."""

    def test_basic_script(self) -> None:
        """Test creating a basic github-script step."""
        step = github_script(script="console.log('Hello')")

        assert isinstance(step, Step)
        assert step.uses == "actions/github-script@v7"
        assert step.with_ is not None
        assert step.with_["script"] == "console.log('Hello')"

    def test_with_github_token(self) -> None:
        """Test specifying custom github token."""
        step = github_script(
            script="return 42",
            github_token="${{ secrets.CUSTOM_TOKEN }}",
        )

        assert step.with_["github-token"] == "${{ secrets.CUSTOM_TOKEN }}"

    def test_with_result_encoding(self) -> None:
        """Test result encoding option."""
        step = github_script(
            script="return {value: 1}",
            result_encoding="json",
        )

        assert step.with_["result-encoding"] == "json"


class TestDockerLogin:
    """Tests for docker_login wrapper."""

    def test_docker_hub_login(self) -> None:
        """Test Docker Hub login with username/password."""
        step = docker_login(
            username="${{ secrets.DOCKER_USER }}",
            password="${{ secrets.DOCKER_TOKEN }}",
        )

        assert isinstance(step, Step)
        assert step.uses == "docker/login-action@v3"
        assert step.with_["username"] == "${{ secrets.DOCKER_USER }}"
        assert step.with_["password"] == "${{ secrets.DOCKER_TOKEN }}"

    def test_ecr_login(self) -> None:
        """Test ECR login with registry."""
        step = docker_login(
            registry="123456789.dkr.ecr.us-east-1.amazonaws.com",
        )

        assert step.with_["registry"] == "123456789.dkr.ecr.us-east-1.amazonaws.com"

    def test_ghcr_login(self) -> None:
        """Test GitHub Container Registry login."""
        step = docker_login(
            registry="ghcr.io",
            username="${{ github.actor }}",
            password="${{ secrets.GITHUB_TOKEN }}",
        )

        assert step.with_["registry"] == "ghcr.io"


class TestDockerBuildPush:
    """Tests for docker_build_push wrapper."""

    def test_basic_build(self) -> None:
        """Test basic Docker build without push."""
        step = docker_build_push(
            context=".",
            push=False,
        )

        assert isinstance(step, Step)
        assert step.uses == "docker/build-push-action@v6"
        assert step.with_["context"] == "."
        assert step.with_["push"] == "false"

    def test_build_and_push(self) -> None:
        """Test build and push with tags."""
        step = docker_build_push(
            context=".",
            push=True,
            tags="myapp:latest,myapp:v1.0.0",
        )

        assert step.with_["push"] == "true"
        assert step.with_["tags"] == "myapp:latest,myapp:v1.0.0"

    def test_with_platforms(self) -> None:
        """Test multi-platform build."""
        step = docker_build_push(
            context=".",
            platforms="linux/amd64,linux/arm64",
            push=True,
        )

        assert step.with_["platforms"] == "linux/amd64,linux/arm64"

    def test_with_cache(self) -> None:
        """Test build with cache configuration."""
        step = docker_build_push(
            context=".",
            cache_from="type=gha",
            cache_to="type=gha,mode=max",
        )

        assert step.with_["cache-from"] == "type=gha"
        assert step.with_["cache-to"] == "type=gha,mode=max"


class TestSetupDotnet:
    """Tests for setup_dotnet wrapper."""

    def test_basic_setup(self) -> None:
        """Test basic .NET setup."""
        step = setup_dotnet(dotnet_version="8.0.x")

        assert isinstance(step, Step)
        assert step.uses == "actions/setup-dotnet@v4"
        assert step.with_["dotnet-version"] == "8.0.x"

    def test_multiple_versions(self) -> None:
        """Test setting up multiple .NET versions."""
        step = setup_dotnet(dotnet_version="6.0.x\n7.0.x\n8.0.x")

        assert "6.0.x" in step.with_["dotnet-version"]

    def test_with_global_json(self) -> None:
        """Test using global.json for version."""
        step = setup_dotnet(global_json_file="./global.json")

        assert step.with_["global-json-file"] == "./global.json"


class TestSetupRuby:
    """Tests for setup_ruby wrapper."""

    def test_basic_setup(self) -> None:
        """Test basic Ruby setup."""
        step = setup_ruby(ruby_version="3.2")

        assert isinstance(step, Step)
        assert step.uses == "ruby/setup-ruby@v1"
        assert step.with_["ruby-version"] == "3.2"

    def test_with_bundler(self) -> None:
        """Test Ruby setup with bundler caching."""
        step = setup_ruby(
            ruby_version="3.2",
            bundler_cache=True,
        )

        assert step.with_["bundler-cache"] == "true"

    def test_with_working_directory(self) -> None:
        """Test Ruby setup with custom working directory."""
        step = setup_ruby(
            ruby_version="3.2",
            working_directory="./my-app",
        )

        assert step.with_["working-directory"] == "./my-app"
