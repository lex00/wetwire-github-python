"""Supporting types for workflow definitions."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Concurrency:
    """Concurrency settings for a workflow or job."""

    group: str = ""
    cancel_in_progress: bool | None = None


@dataclass
class DefaultsRun:
    """Default run settings."""

    shell: str = ""
    working_directory: str = ""


@dataclass
class Defaults:
    """Default settings for a workflow."""

    run: DefaultsRun | None = None


@dataclass
class Environment:
    """Deployment environment configuration."""

    name: str = ""
    url: str = ""


@dataclass
class Container:
    """Container configuration for a job."""

    image: str = ""
    credentials: dict[str, Any] | None = None
    env: dict[str, Any] | None = None
    ports: list[str] | None = None
    volumes: list[str] | None = None
    options: str = ""


@dataclass
class Service:
    """Service container configuration."""

    image: str = ""
    credentials: dict[str, Any] | None = None
    env: dict[str, Any] | None = None
    ports: list[str] | None = None
    volumes: list[str] | None = None
    options: str = ""


@dataclass
class Permissions:
    """Workflow or job permissions."""

    # Special values
    read_all: bool | None = None
    write_all: bool | None = None

    # Individual permissions
    actions: str | None = None
    attestations: str | None = None
    checks: str | None = None
    contents: str | None = None
    deployments: str | None = None
    discussions: str | None = None
    id_token: str | None = None
    issues: str | None = None
    models: str | None = None
    packages: str | None = None
    pages: str | None = None
    pull_requests: str | None = None
    repository_projects: str | None = None
    security_events: str | None = None
    statuses: str | None = None


@dataclass
class WorkflowInput:
    """Input definition for workflow_dispatch or workflow_call triggers."""

    description: str = ""
    required: bool | None = None
    default: str | None = None
    type: str = ""  # string, boolean, choice, number, environment
    options: list[str] | None = None  # for choice type


@dataclass
class WorkflowOutput:
    """Output definition for workflow_call trigger."""

    description: str = ""
    value: str = ""


@dataclass
class WorkflowSecret:
    """Secret definition for workflow_call trigger."""

    description: str = ""
    required: bool | None = None
