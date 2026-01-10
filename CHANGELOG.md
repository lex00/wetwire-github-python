# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

- Single-line imports from root package
  - Core types: `from wetwire_github import Workflow, Job, Step, Triggers`
  - Trigger types: `PushTrigger, PullRequestTrigger, ScheduleTrigger`
  - Expression builders: `Secrets, GitHub, always, failure, success, cancelled`
- Modular linter rules architecture (`wetwire_github.linter.rules/`)
  - Organized by category: action, expression, organization, validation, pattern
  - Backwards compatible with existing imports
  - Easier to navigate, test, and extend
- Loader module (`wetwire_github.loader`)
  - `setup_workflow_namespace()` - Injects core types into a namespace
  - `setup_actions()` - Injects action wrappers into a namespace
  - `setup_all()` - Injects all types and actions
  - `get_all_exports()` - Returns dict of all exportable items
- Provider module (`wetwire_github.provider`)
  - `WorkflowProvider` class for build orchestration
  - `build()` - Generates YAML content for workflows
  - `validate()` - Validates workflows before building
  - `write()` - Writes workflow files to output directory
- Kiro CLI integration module (`wetwire_github.kiro`)
  - `install_kiro_configs()` - Installs agent and MCP configs for Kiro CLI
  - `launch_kiro()` - Launches Kiro CLI with wetwire-github-runner agent
  - `run_kiro_scenario()` - Non-interactive scenario execution for testing
  - `check_kiro_installed()` - Checks if Kiro CLI is available
- `kiro` CLI command for AI-assisted workflow design
  - `--prompt` - Initial prompt for conversation
  - `--install-only` - Only install configs without launching
  - `--force` - Force reinstall of configurations
- GitHub Actions-specific agent configuration with:
  - Lint-fix loop enforcement
  - wetwire-github syntax documentation
  - Lint rules reference (WAG001-WAG008)
  - Design workflow guidance
- Standalone MCP server executable (`wetwire-github-mcp`)
  - Entry point added to pyproject.toml
  - `main()` function for direct server startup
  - Works with Kiro/Cursor/Claude Code MCP integration
- Adoption/Migration Guide (`docs/ADOPTION.md`)
  - Side-by-side adoption strategies
  - Incremental migration path
  - Import command usage
  - Escape hatches and workarounds
  - Team onboarding playbook
  - Integration patterns
- New lint rules (WAG009-WAG012):
  - WAG009: Validate webhook event types in triggers
  - WAG010: Detect secrets used to help document requirements
  - WAG011: Flag overly complex conditional logic
  - WAG012: Suggest reusable workflows for duplicated patterns

## [0.1.0] - 2026-01-06

### Added

#### Core Types (Phase 1)
- `Workflow`, `Job`, `Step` dataclasses for workflow definitions
- `Triggers` with support for all GitHub event types
- `Matrix` for build matrices with include/exclude
- Expression helpers (`secrets`, `env`, `github`, `needs`, `matrix`)
- YAML serialization with proper field name conversion

#### Core Capabilities (Phase 2)
- Schema fetching from json.schemastore.org
- Action code generation for typed wrappers
- AST-based workflow discovery in Python packages
- Actionlint integration for YAML validation
- Linter rules (WAG001-WAG008) for workflow quality
  - WAG001: Use typed action wrappers
  - WAG002: Use condition builders
  - WAG003: Use secrets context (with auto-fix)
  - WAG004: Use Matrix builder
  - WAG005: Extract inline env variables
  - WAG006: Duplicate workflow names
  - WAG007: File too large
  - WAG008: Hardcoded expressions
- YAML parser for importing existing workflows
- Runner for extracting workflow values
- Template builder for YAML generation

#### CLI Commands (Phase 3)
- `build` - Generate YAML from Python declarations
- `validate` - Validate YAML with actionlint
- `lint` - Apply code quality rules (with --fix support)
- `import` - Convert YAML to Python code
- `list` - List discovered workflows and jobs
- `init` - Create new project scaffold
- `design` - AI-assisted design (requires wetwire-core)
- `test` - Persona-based testing (requires wetwire-core)
- `graph` - Generate DAG visualization (Mermaid/DOT)

#### Polish & Integration (Phase 4)
- Reference example tests for import/build cycle
- wetwire-core integration module
  - Tool definitions for RunnerAgent
  - Tool handlers for all CLI commands
  - Stream handler for output capture
  - Session management for design sessions
  - Workflow quality scoring (10 best practice checks)
  - Persona-based testing (reviewer, senior-dev, security, beginner)

#### Extended Config Types (Phase 5)
- Dependabot configuration support
  - `Dependabot`, `Update`, `Schedule` dataclasses
  - `PackageEcosystem` enum (18 ecosystems)
  - `Registry` and `Group` configuration
- Issue Templates (Issue Forms) support
  - `IssueTemplate` dataclass
  - Form elements: `Input`, `Textarea`, `Dropdown`, `Checkboxes`, `Markdown`
  - `CheckboxOption` for checkbox configuration
- Discussion Templates support
  - `DiscussionTemplate` dataclass
  - `DiscussionCategory` enum
  - Reuses form elements from Issue Templates

### Dependencies
- Python >= 3.11
- wetwire-core
- dataclass-dsl >= 1.0.1
- pyyaml >= 6.0
