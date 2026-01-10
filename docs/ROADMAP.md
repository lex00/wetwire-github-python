# Feature Roadmap

This document tracks completed and planned features for wetwire-github.

---

## Completed Features

### Core Workflow Support ✅

- [x] **Typed Workflow Declarations** - `Workflow`, `Job`, `Step` dataclasses
- [x] **All Trigger Types** - Push, PR, schedule, workflow_dispatch, workflow_call, webhooks
- [x] **Matrix Builds** - `Matrix` with include/exclude support
- [x] **Expression Helpers** - `Secrets`, `GitHub`, `Matrix`, `Env`, `Needs`
- [x] **Conditional Execution** - `if_` conditions with type-safe builders
- [x] **Job Dependencies** - `needs` with topological sorting
- [x] **Reusable Workflows** - Workflow composition with workflow_call triggers

### Action Wrappers ✅

- [x] **Setup Actions** - `setup_python`, `setup_node`, `setup_go`, `setup_java`, `setup_dotnet`, `setup_ruby`
- [x] **Core Actions** - `checkout`, `cache`, `upload_artifact`, `download_artifact`
- [x] **Utility Actions** - `github_script`
- [x] **Docker Actions** - `docker_login`, `docker_build_push`, `setup_buildx`, `docker_metadata`
- [x] **Integration Actions** - `configure_aws_credentials`, `codecov`, `create_pull_request`, `gh_release`
- [x] **Pages Actions** - `deploy_pages`, `configure_pages`
- [x] **Security Actions** - `attest_build_provenance`

### Composite Actions ✅

- [x] **Composite Actions Support** - Create composite actions using typed Python declarations

### Extended Config Types ✅

- [x] **Dependabot** - `Dependabot`, `Update`, `Schedule` with 18 package ecosystems
- [x] **Issue Templates** - Issue Forms with typed elements (Input, Textarea, Dropdown, Checkboxes, Markdown)
- [x] **Discussion Templates** - Discussion templates with category support

### CLI Commands ✅

- [x] **build** - Generate YAML from Python declarations
- [x] **validate** - Validate YAML with actionlint
- [x] **lint** - Apply 16 linter rules (WAG001-WAG016) with auto-fix
- [x] **import** - Convert YAML to typed Python code
- [x] **list** - List discovered workflows and jobs
- [x] **init** - Scaffold new project with example workflow
- [x] **graph** - Generate dependency graph (Mermaid/DOT)
- [x] **design** - AI-assisted interactive workflow design
- [x] **test** - Persona-based automated testing
- [x] **kiro** - Kiro CLI integration for AI-assisted design

### Linter Rules (WAG001-WAG016) ✅

**Type Safety (WAG001-WAG004):**
- [x] WAG001: Use typed action wrappers (auto-fix)
- [x] WAG002: Use condition builders (auto-fix)
- [x] WAG003: Use secrets context (auto-fix)
- [x] WAG004: Use Matrix builder (auto-fix)

**Organization (WAG005-WAG007):**
- [x] WAG005: Extract inline env variables
- [x] WAG006: Duplicate workflow names
- [x] WAG007: File too large

**Validation (WAG008-WAG012):**
- [x] WAG008: Hardcoded expressions (auto-fix)
- [x] WAG009: Validate webhook event types
- [x] WAG010: Document secrets usage
- [x] WAG011: Flag complex conditions
- [x] WAG012: Suggest reusable workflows

**Extraction (WAG013-WAG016):**
- [x] WAG013: Extract inline env dicts (>3 entries)
- [x] WAG014: Extract inline matrix configurations
- [x] WAG015: Extract inline outputs dicts (>2 entries)
- [x] WAG016: Suggest reusable workflow extraction for duplicated jobs

### Discovery & Analysis ✅

- [x] **AST-Based Discovery** - Parse Python source to find workflows
- [x] **Dependency Graph** - Build and visualize job dependencies
- [x] **Cycle Detection** - Detect circular dependencies
- [x] **Topological Sort** - Order jobs by dependencies
- [x] **Reusable Workflow Discovery** - Identify composable workflows

### Serialization ✅

- [x] **YAML Generation** - Convert Python dataclasses to YAML
- [x] **Field Name Conversion** - snake_case ↔ kebab-case
- [x] **Expression Serialization** - Convert helpers to `${{ ... }}` syntax
- [x] **Nested Structure Support** - Handle complex nested configurations

### Import & Export ✅

- [x] **YAML Import** - Parse existing GitHub Actions YAML
- [x] **Python Codegen** - Generate typed Python from YAML
- [x] **Name Sanitization** - Convert kebab-case to snake_case
- [x] **Expression Conversion** - Convert `${{ ... }}` to helper functions
- [x] **High-Fidelity Round-Trip** - Import → Build preserves semantics

### AI Integration ✅

- [x] **wetwire-core Integration** - Tool definitions and handlers
- [x] **Design Mode** - Interactive AI-assisted workflow creation
- [x] **Persona Testing** - Automated testing with 4 developer personas
- [x] **Quality Scoring** - 10 best practice checks
- [x] **MCP Server** - Standalone MCP server for IDE integration
- [x] **Kiro CLI** - Integration with Kiro for AI-assisted development

### Developer Experience ✅

- [x] **Loader Module** - Namespace injection pattern (`setup_all()`)
- [x] **Provider Module** - Orchestration class for build/validate/write
- [x] **GitHub Context Constants** - Type-safe pseudo-parameters (`GITHUB_REF`, etc.)
- [x] **IDE Support** - Full autocomplete and type checking
- [x] **Comprehensive Docs** - 13 documentation files covering all features

---

## Planned Features

### Near-Term (Next Release)

- [ ] **Additional Action Wrappers** - More commonly used actions
  - [ ] `slsa-framework/slsa-github-generator` (Note: This is a reusable workflow, not a simple action wrapper, and requires different abstraction patterns)
- [x] **Action Metadata Generation** - Generate `action.yml` from Python definitions (PR #123)
- [x] **Enhanced Graph Visualization** - Color coding, filtering, search (PR #123)
- [x] **Performance Optimization** - Caching for large monorepos (PR #127)

### Medium-Term

- [ ] **GitHub App Integration** - Workflow automation via GitHub App
- [x] **Branch Protection Rules** - Typed configuration for branch protection (PR #143)
- [x] **Repository Settings** - Typed configuration for repository settings (PR #147)
- [x] **Secret Scanning Configuration** - Custom patterns for secret scanning (PR #147)
- [x] **Advanced Caching Strategies** - Smart cache key generation (PR #143)
- [x] **Workflow Templates** - Organization-level workflow templates (PR #147)
- [x] **Self-Hosted Runners** - Support for self-hosted runner configurations (PR #143)

### Long-Term

- [ ] **GitLab CI Support** - Parallel support for GitLab CI/CD
- [ ] **Multi-Provider** - Unified syntax for GitHub Actions, GitLab CI, Jenkins
- [ ] **Policy Engine** - Organization-level policy enforcement
- [ ] **Cost Optimization** - Analyze and optimize workflow runtime costs
- [ ] **Security Scanning** - Built-in security analysis for workflows
- [ ] **Workflow Marketplace** - Share and discover reusable workflows

---

## Feature Parity Analysis

### Comparison with wetwire-aws-python

| Feature Category | wetwire-github | wetwire-aws | Status |
|-----------------|----------------|-------------|--------|
| **Core Types** | Workflow, Job, Step | Resource classes | ✅ Full parity |
| **Discovery** | AST-based | AST-based | ✅ Full parity |
| **Serialization** | YAML | JSON/YAML | ✅ Full parity |
| **Linter Rules** | 16 rules | 20 rules | 🟡 Similar coverage |
| **Import** | YAML → Python | CF/SAM → Python | ✅ Full parity |
| **CLI Commands** | 10 commands | 9 commands | ✅ Full parity |
| **AI Integration** | Design + Test | Design + Test | ✅ Full parity |
| **MCP Server** | ✅ Yes | ✅ Yes | ✅ Full parity |
| **Kiro CLI** | ✅ Yes | ✅ Yes | ✅ Full parity |
| **Graph Visualization** | Mermaid + DOT | Mermaid + DOT | ✅ Full parity |
| **Loader Pattern** | ✅ Yes | ✅ Yes | ✅ Full parity |
| **Provider Pattern** | ✅ Yes | ✅ Yes | ✅ Full parity |
| **Extended Configs** | 3 types | N/A | ✅ Domain-specific |
| **Action Wrappers** | 21 wrappers | N/A | ✅ Domain-specific |
| **Pseudo-Parameters** | GitHub contexts | AWS pseudo-params | ✅ Full parity |
| **PropertyTypes** | N/A | Nested types | 🟡 Different domain |
| **Intrinsics** | Expressions | Fn::* functions | 🟡 Different domain |

**Legend:**
- ✅ Full parity - Feature implemented and equivalent
- 🟡 Similar coverage - Feature implemented but differs in scope
- ❌ Missing - Feature not yet implemented

### Domain-Specific Differences

**wetwire-github unique features:**
1. Action wrappers (21 typed wrappers for common actions)
2. Extended config types (Dependabot, Issue Templates, Discussion Templates)
3. GitHub context pseudo-parameters
4. Webhook event validation
5. Reusable workflow discovery and composition

**wetwire-aws unique features:**
1. PropertyType wrapper classes for nested CloudFormation structures
2. SAM (Serverless Application Model) support with 9 resource types
3. CloudFormation intrinsic functions (Ref, GetAtt, Sub, Join, etc.)
4. AWS pseudo-parameters (AWS::Region, AWS::AccountId, etc.)
5. 263 generated CloudFormation resource types

Both packages follow the same architectural patterns and provide equivalent developer experiences within their respective domains.

---

## Community & Ecosystem

### Integration Status

- [x] **PyPI** - Published as `wetwire-github`
- [x] **wetwire-core** - Full integration with agent framework
- [x] **MCP Protocol** - Server implementation for IDE integration
- [x] **Kiro CLI** - Agent configuration for AI-assisted development
- [x] **actionlint** - External validation integration

### Documentation

- [x] Quick Start guide
- [x] CLI reference with all commands
- [x] Lint rules documentation with examples
- [x] Examples collection
- [x] Import workflow guide
- [x] Internals documentation
- [x] FAQ with common questions
- [x] Code generation guide
- [x] Versioning guide
- [x] Developer guide
- [x] Adoption/migration guide
- [x] CLAUDE.md for AI assistant guidelines

### Testing

- [x] Unit tests for core modules
- [x] Integration tests for import/build round-trip
- [x] Linter rule tests with before/after examples
- [x] Reference example tests
- [x] Persona-based testing framework

---

## Version History

### v0.1.0 (2026-01-06) - Initial Release

**Core Implementation:**
- Workflow, Job, Step dataclasses
- All GitHub trigger types
- Expression helpers
- AST-based discovery
- YAML serialization
- 8 linter rules (WAG001-WAG008)
- Import from YAML
- CLI commands: build, validate, lint, import, list, init, design, test, graph
- wetwire-core integration
- Extended config types (Dependabot, Issue Templates, Discussion Templates)

### Unreleased - Enhanced Integration

**New Features:**
- Modular linter architecture
- 8 additional lint rules (WAG009-WAG016)
- Loader module with namespace injection
- Provider module for build orchestration
- Expanded action wrappers (21 total)
- GitHub context pseudo-parameters
- Reusable workflow discovery
- MCP server
- Kiro CLI integration
- Adoption/migration guide
- Composite actions support
- New action wrappers: `deploy_pages`, `configure_pages`, `attest_build_provenance`

---

## Contributing

See planned features above for contribution ideas. Priority areas:
1. Additional action wrappers for popular actions
2. Enhanced graph visualization features
3. Performance optimization for large monorepos
4. Documentation improvements and examples
5. Integration with other CI/CD platforms

For implementation guidelines, see [DEVELOPERS.md](DEVELOPERS.md) and the [Wetwire Specification](https://github.com/lex00/wetwire/blob/main/docs/WETWIRE_SPEC.md).
