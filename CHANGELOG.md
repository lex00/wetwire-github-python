# Changelog

All notable changes to this project will be documented in this file.

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
- Linter rules (WAG001-WAG003) for workflow quality
- YAML parser for importing existing workflows
- Runner for extracting workflow values
- Template builder for YAML generation

#### CLI Commands (Phase 3)
- `build` - Generate YAML from Python declarations
- `validate` - Validate YAML with actionlint
- `lint` - Apply code quality rules
- `import` - Convert YAML to Python code
- `list` - List discovered workflows and jobs
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
