# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

- Spec-standard personas for testing (per WETWIRE_SPEC.md Section 7)
  - `expert` - Deep knowledge, precise requirements, minimal hand-holding
  - `terse` - Minimal information, expects system to infer defaults
  - `verbose` - Over-explains, buries requirements in prose
  - Complements existing domain personas (reviewer, senior-dev, security, beginner)
- Single-line imports from root package
  - Core types: `from wetwire_github import Workflow, Job, Step, Triggers`
  - Trigger types: `PushTrigger, PullRequestTrigger, ScheduleTrigger`
  - Expression builders: `Secrets, GitHub, always, failure, success, cancelled`
- Modular linter rules architecture (`wetwire_github.linter.rules/`)
  - Organized by category: action, expression, organization, validation, pattern, extraction
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
- Expanded auto-fix support for lint rules
  - WAG004: Auto-fix raw strategy/matrix dicts with Strategy/Matrix classes
  - WAG008: Auto-fix common GitHub context expressions (github.ref, etc.)
  - WAG019: Auto-remove unused permission declarations from Job configurations
  - WAG050: Auto-remove unreferenced output definitions from Job declarations
  - WAG052: Auto-remove orphan secret declarations from workflow/job env
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
  - Lint rules reference (WAG001-WAG053)
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
- New lint rules (WAG009-WAG016):
  - WAG009: Validate webhook event types in triggers
  - WAG010: Detect secrets used to help document requirements
  - WAG011: Flag overly complex conditional logic
  - WAG012: Suggest reusable workflows for duplicated patterns
  - WAG013: Extract inline env dicts (>3 entries) to named variables
  - WAG014: Extract complex inline matrix configurations
  - WAG015: Extract inline outputs dicts (>2 entries) to named variables
  - WAG016: Suggest reusable workflow extraction for duplicated inline jobs
- Security lint rules (WAG017-WAG022):
  - WAG017: Detect hardcoded secrets in run commands
  - WAG018: Detect unpinned actions (with auto-fix)
  - WAG019: Flag unused permissions grants
  - WAG020: Warn about secrets interpolated directly in run commands
  - WAG021: Suggest OIDC for cloud provider authentication
  - WAG022: Detect unescaped user-controlled input in shell commands
- Reference tracking rules (WAG050-WAG053):
  - WAG050: Flag unused job outputs
  - WAG051: Detect circular job dependencies
  - WAG052: Flag orphan secrets
  - WAG053: Validate step output references
- Input validation rule (WAG049):
  - WAG049: Validate workflow_call inputs and secrets references
- Additional typed action wrappers (`wetwire_github.actions`)
  - `github_script` - Run JavaScript using GitHub API (actions/github-script@v7)
  - `docker_login` - Log in to Docker registries (docker/login-action@v3)
  - `docker_build_push` - Build and push Docker images (docker/build-push-action@v6)
  - `setup_dotnet` - Set up .NET SDK environment (actions/setup-dotnet@v4)
  - `setup_ruby` - Set up Ruby environment (ruby/setup-ruby@v1)
- Standalone graph module (`wetwire_github.graph`)
  - `WorkflowGraph` class for dependency analysis
  - `DependencyNode` dataclass for graph nodes
  - `topological_sort()` - Kahn's algorithm for dependency ordering
  - `detect_cycles()` - Cycle detection in dependency graphs
  - `to_mermaid()` / `to_dot()` - Visualization output
  - `add_workflow_call()` - Track workflow composition relationships
  - Workflow calls shown as dashed edges in visualization
  - Refactored `graph_cmd.py` to use the new module
- Reusable workflow discovery (`wetwire_github.discover`)
  - `DiscoveredReusableWorkflow` dataclass for reusable workflows
  - `discover_reusable_workflows()` - Discover workflows with workflow_call trigger
  - Extracts inputs, outputs, and secrets from workflow_call configuration
- GitHub context pseudo-parameters (`wetwire_github.pseudo`)
  - Constants for common GitHub context values (GITHUB_REF, GITHUB_SHA, etc.)
  - Follows AWS pseudo-parameter pattern for consistency
  - IDE autocomplete and type safety for GitHub contexts
- Expanded action wrapper registry with 6 new wrappers:
  - `setup_buildx` - Set up Docker Buildx (docker/setup-buildx-action@v3)
  - `docker_metadata` - Extract Docker metadata (docker/metadata-action@v5)
  - `configure_aws_credentials` - AWS credentials setup (aws-actions/configure-aws-credentials@v4)
  - `codecov` - Upload coverage to Codecov (codecov/codecov-action@v4)
  - `create_pull_request` - Create PRs (peter-evans/create-pull-request@v6)
  - `gh_release` - Create GitHub releases (softprops/action-gh-release@v2)

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
