"""Dependabot configuration types.

Dataclasses and enums for Dependabot configuration files.
Based on the dependabot-2.0 schema.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PackageEcosystem(Enum):
    """Supported package ecosystems for Dependabot."""

    BUNDLER = "bundler"
    CARGO = "cargo"
    COMPOSER = "composer"
    DEVCONTAINERS = "devcontainers"
    DOCKER = "docker"
    ELM = "elm"
    GITSUBMODULE = "gitsubmodule"
    GITHUB_ACTIONS = "github-actions"
    GOMOD = "gomod"
    GRADLE = "gradle"
    HEX = "hex"
    MAVEN = "maven"
    NPM = "npm"
    NUGET = "nuget"
    PIP = "pip"
    PUB = "pub"
    SWIFT = "swift"
    TERRAFORM = "terraform"


@dataclass
class Schedule:
    """Schedule for Dependabot updates.

    Attributes:
        interval: Update frequency (daily, weekly, monthly)
        day: Day of week for weekly updates
        time: Time of day for updates (HH:MM format)
        timezone: Timezone for scheduling
    """

    interval: str
    day: str | None = None
    time: str | None = None
    timezone: str | None = None


@dataclass
class Group:
    """Group configuration for batching updates.

    Attributes:
        patterns: List of package name patterns to group
        dependency_type: Type of dependencies (production, development)
        update_types: Types of updates to group
    """

    patterns: list[str] = field(default_factory=list)
    dependency_type: str | None = None
    update_types: list[str] = field(default_factory=list)


@dataclass
class Registry:
    """Private registry configuration.

    Attributes:
        type: Registry type (npm-registry, docker-registry, etc.)
        url: Registry URL
        username: Username for authentication
        password: Password for authentication
        token: Authentication token
        key: SSH key for authentication
        replaces_base: Whether this registry replaces the base registry
    """

    type: str
    url: str | None = None
    username: str | None = None
    password: str | None = None
    token: str | None = None
    key: str | None = None
    replaces_base: bool | None = None


@dataclass
class Update:
    """Update configuration for a package ecosystem.

    Attributes:
        package_ecosystem: The package ecosystem to update
        directory: Directory containing the manifest file
        schedule: Update schedule configuration
        allow: List of allowed dependencies to update
        assignees: List of assignees for PRs
        commit_message: Commit message configuration
        groups: Dependency grouping configuration
        ignore: List of dependencies to ignore
        insecure_external_code_execution: Allow external code execution
        labels: Labels to add to PRs
        milestone: Milestone to add to PRs
        open_pull_requests_limit: Maximum number of open PRs
        pull_request_branch_name: Branch name configuration
        rebase_strategy: Rebase strategy for updates
        registries: List of registry names to use
        reviewers: List of reviewers for PRs
        target_branch: Branch to create PRs against
        vendor: Whether to vendor dependencies
        versioning_strategy: Strategy for version updates
    """

    package_ecosystem: PackageEcosystem
    directory: str
    schedule: Schedule
    allow: list[dict[str, Any]] = field(default_factory=list)
    assignees: list[str] = field(default_factory=list)
    commit_message: dict[str, Any] | None = None
    groups: dict[str, Group] = field(default_factory=dict)
    ignore: list[dict[str, Any]] = field(default_factory=list)
    insecure_external_code_execution: str | None = None
    labels: list[str] = field(default_factory=list)
    milestone: int | None = None
    open_pull_requests_limit: int | None = None
    pull_request_branch_name: dict[str, str] | None = None
    rebase_strategy: str | None = None
    registries: list[str] = field(default_factory=list)
    reviewers: list[str] = field(default_factory=list)
    target_branch: str | None = None
    vendor: bool | None = None
    versioning_strategy: str | None = None


@dataclass
class Dependabot:
    """Dependabot configuration.

    Attributes:
        version: Configuration file version (should be 2)
        updates: List of update configurations
        registries: Dictionary of private registry configurations
        enable_beta_ecosystems: Enable beta ecosystem support
    """

    version: int = 2
    updates: list[Update] = field(default_factory=list)
    registries: dict[str, Registry] = field(default_factory=dict)
    enable_beta_ecosystems: bool | None = None
