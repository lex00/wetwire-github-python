# Implementation Plan

This document tracks the phased implementation of wetwire-github following the [Wetwire Specification](https://github.com/lex00/wetwire/blob/main/docs/WETWIRE_SPEC.md).

---

## Phase 1: Core (MVP) ✅

**Goal:** Generate GitHub Actions YAML from typed Python declarations.

### 1.1 Core Types ✅

- [x] `Workflow`, `Job`, `Step` dataclasses
- [x] `Triggers` with support for all GitHub event types
  - [x] `PushTrigger`, `PullRequestTrigger`, `ScheduleTrigger`
  - [x] `WorkflowDispatchTrigger`, `WorkflowCallTrigger`
  - [x] All webhook event types (issues, releases, etc.)
- [x] `Matrix` for build matrices with include/exclude
- [x] Expression helpers (`Secrets`, `GitHub`, `Matrix`, `Env`, `Needs`)
- [x] YAML serialization with field name conversion (snake_case ↔ kebab-case)

### 1.2 Discovery ✅

- [x] AST-based workflow discovery in Python packages
- [x] Top-level variable detection (Workflow instances)
- [x] Dependency graph construction
- [x] File and line number tracking

### 1.3 Template Builder ✅

- [x] Workflow discovery
- [x] Reference validation
- [x] Topological sorting (Kahn's algorithm)
- [x] YAML serialization
- [x] Output to `.github/workflows/`

### 1.4 CLI: `build` Command ✅

- [x] `wetwire-github build [package]` - Generate YAML from Python declarations
- [x] Package path resolution (relative/absolute)
- [x] Validation before output
- [x] File overwrite handling

---

## Phase 2: Extended Capabilities ✅

**Goal:** Add linting, validation, import, and extended config types.

### 2.1 Schema Integration ✅

- [x] Schema fetching from json.schemastore.org
- [x] Action schema parsing
- [x] Input parameter extraction

### 2.2 Action Code Generation ✅

- [x] Parse action metadata from schema
- [x] Generate typed wrapper functions
- [x] Parameter validation with types
- [x] IDE autocomplete support
- [x] Wrappers for common actions:
  - [x] `checkout`, `setup_python`, `setup_node`, `setup_go`, `setup_java`
  - [x] `setup_dotnet`, `setup_ruby`
  - [x] `cache`, `upload_artifact`, `download_artifact`
  - [x] `github_script`, `docker_login`, `docker_build_push`
  - [x] `setup_buildx`, `docker_metadata`
  - [x] `configure_aws_credentials`, `codecov`, `create_pull_request`, `gh_release`

### 2.3 Linter ✅

- [x] WAG001: Use typed action wrappers (with auto-fix)
- [x] WAG002: Use condition builders (with auto-fix)
- [x] WAG003: Use secrets context (with auto-fix)
- [x] WAG004: Use Matrix builder (with auto-fix)
- [x] WAG005: Extract inline env variables
- [x] WAG006: Duplicate workflow names
- [x] WAG007: File too large
- [x] WAG008: Hardcoded expressions (with auto-fix)
- [x] WAG009: Validate webhook event types
- [x] WAG010: Document secrets usage
- [x] WAG011: Flag complex conditions
- [x] WAG012: Suggest reusable workflows
- [x] WAG013: Extract inline env dicts (>3 entries)
- [x] WAG014: Extract inline matrix configurations
- [x] WAG015: Extract inline outputs dicts (>2 entries)
- [x] WAG016: Suggest reusable workflow extraction for duplicated jobs
- [x] Modular rules architecture (action, expression, organization, validation, pattern, extraction)

### 2.4 YAML Parser & Importer ✅

- [x] Parse existing GitHub Actions YAML
- [x] Convert YAML to intermediate representation
- [x] Generate typed Python code
- [x] Name sanitization (kebab-case → snake_case)
- [x] Expression conversion (`${{ ... }}` → helper functions)
- [x] Trigger conversion
- [x] Matrix conversion
- [x] Secrets conversion to `Secrets.get()`

### 2.5 CLI: Extended Commands ✅

- [x] `validate` - Validate YAML with actionlint
- [x] `lint` - Apply linter rules (with `--fix` support)
- [x] `import` - Convert YAML to Python
- [x] `list` - List discovered workflows and jobs
- [x] `graph` - Generate dependency graph (Mermaid/DOT)

### 2.6 Extended Config Types ✅

- [x] Dependabot configuration
  - [x] `Dependabot`, `Update`, `Schedule` dataclasses
  - [x] `PackageEcosystem` enum (18 ecosystems)
  - [x] `Registry` and `Group` configuration
- [x] Issue Templates (Issue Forms)
  - [x] `IssueTemplate` dataclass
  - [x] Form elements: `Input`, `Textarea`, `Dropdown`, `Checkboxes`, `Markdown`
- [x] Discussion Templates
  - [x] `DiscussionTemplate` dataclass
  - [x] `DiscussionCategory` enum
  - [x] Reuses form elements from Issue Templates

---

## Phase 3: Polish & Integration ✅

**Goal:** Developer experience improvements and wetwire-core integration.

### 3.1 CLI: Project Scaffolding ✅

- [x] `init` - Create new project scaffold
- [x] Example workflow generation
- [x] `pyproject.toml` template

### 3.2 wetwire-core Integration ✅

- [x] Tool definitions for RunnerAgent
- [x] Tool handlers for all CLI commands
- [x] Stream handler for output capture
- [x] Session management
- [x] Workflow quality scoring (10 best practice checks)
- [x] Persona-based testing (reviewer, senior-dev, security, beginner)

### 3.3 CLI: AI-Assisted Design ✅

- [x] `design` - Interactive design session with AI
- [x] `test` - Automated persona-based testing

### 3.4 Loader Module ✅

- [x] `setup_workflow_namespace()` - Inject core types into namespace
- [x] `setup_actions()` - Inject action wrappers into namespace
- [x] `setup_all()` - Inject all types and actions
- [x] `get_all_exports()` - Return dict of all exportable items
- [x] Single-line import pattern support

### 3.5 Provider Module ✅

- [x] `WorkflowProvider` class for build orchestration
- [x] `build()` - Generate YAML content
- [x] `validate()` - Validate workflows before building
- [x] `write()` - Write workflow files to output directory

### 3.6 Reusable Workflow Support ✅

- [x] `DiscoveredReusableWorkflow` dataclass
- [x] `discover_reusable_workflows()` - Discover workflows with workflow_call trigger
- [x] Extract inputs, outputs, and secrets from workflow_call configuration
- [x] Graph visualization with workflow call relationships

### 3.7 GitHub Context Pseudo-Parameters ✅

- [x] Constants for common GitHub context values
- [x] `GITHUB_REF`, `GITHUB_SHA`, `GITHUB_ACTOR`, etc.
- [x] IDE autocomplete and type safety
- [x] Follows AWS pseudo-parameter pattern

---

## Phase 4: Advanced Integration 🔄

**Goal:** MCP integration and advanced tooling.

### 4.1 MCP Server ✅

- [x] Standalone MCP server executable (`wetwire-github-mcp`)
- [x] Entry point in pyproject.toml
- [x] `main()` function for direct server startup
- [x] Works with Kiro/Cursor/Claude Code

### 4.2 Kiro CLI Integration ✅

- [x] `install_kiro_configs()` - Install agent and MCP configs
- [x] `launch_kiro()` - Launch Kiro CLI with wetwire-github-runner agent
- [x] `run_kiro_scenario()` - Non-interactive scenario execution
- [x] `check_kiro_installed()` - Check if Kiro CLI is available
- [x] `kiro` CLI command with `--prompt`, `--install-only`, `--force` options
- [x] GitHub Actions-specific agent configuration
- [x] Lint-fix loop enforcement in agent prompt
- [x] Syntax documentation and lint rules reference

### 4.3 Advanced Graph Features ✅

- [x] `WorkflowGraph` class for dependency analysis
- [x] `DependencyNode` dataclass for graph nodes
- [x] `topological_sort()` - Kahn's algorithm for dependency ordering
- [x] `detect_cycles()` - Cycle detection in dependency graphs
- [x] `to_mermaid()` / `to_dot()` - Visualization output
- [x] Workflow call tracking with dashed edges

### 4.4 Documentation 🔄

- [x] Quick Start guide
- [x] CLI reference
- [x] Lint rules documentation
- [x] Examples collection
- [x] Import workflow guide
- [x] Internals documentation
- [x] FAQ
- [x] Code generation guide
- [x] Versioning guide
- [x] Developer guide
- [x] Adoption/migration guide
- [ ] PLAN.md (this document)
- [ ] ROADMAP.md

---

## Implementation Notes

### Completed Features

All core functionality is complete and production-ready:
- Full workflow definition support with typed dataclasses
- Comprehensive linter with 16 rules (WAG001-WAG016)
- YAML import/export with high fidelity
- Extended config types (Dependabot, Issue Templates, Discussion Templates)
- AI-assisted design and testing via wetwire-core
- MCP server integration
- Kiro CLI integration
- Rich visualization and graph analysis

### Design Decisions

1. **Loader Pattern**: Uses namespace injection (`setup_all()`) for clean imports instead of star imports
2. **Action Wrappers**: Pre-generated typed wrappers for common actions instead of dynamic generation
3. **Expression Helpers**: Typed builders (`Secrets.get()`, `GitHub.ref`) instead of raw string expressions
4. **Modular Linter**: Rules organized by category (action, expression, organization, validation, pattern, extraction)
5. **AST Discovery**: Parse Python source to find Workflow instances instead of module imports
6. **Provider Pattern**: Orchestration class (`WorkflowProvider`) for build/validate/write operations

### Testing Strategy

- Unit tests for all core modules (discover, serialize, linter, importer)
- Integration tests for import/build round-trip
- Linter rule tests with before/after examples
- Reference example tests from imported YAML
- Persona-based testing via wetwire-core
