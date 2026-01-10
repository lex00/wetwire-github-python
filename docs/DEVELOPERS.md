# Developer Guide

Comprehensive guide for developers working on wetwire-github.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [Code Generation](#code-generation)
- [Contributing](#contributing)

---

## Development Setup

### Prerequisites

- **Python 3.11+** (required)
- **uv** (recommended package manager)
- **git** (version control)
- **actionlint** (optional, for YAML validation)

### Clone and Setup

```bash
# Clone repository
git clone https://github.com/lex00/wetwire-github-python.git
cd wetwire-github-python

# Install dependencies (creates .venv automatically)
uv sync

# Verify installation
uv run pytest tests/ -v
```

### Install actionlint (Optional)

For YAML validation functionality:

```bash
# macOS
brew install actionlint

# Linux
go install github.com/rhysd/actionlint/cmd/actionlint@latest

# Verify
actionlint --version
```

---

## Project Structure

```
wetwire-github-python/
├── src/wetwire_github/           # Source code
│   ├── __init__.py               # Package entry point
│   ├── contracts.py              # Interface contracts
│   ├── workflow/                 # Core workflow types
│   │   ├── workflow.py           # Workflow dataclass
│   │   ├── job.py                # Job dataclass
│   │   ├── step.py               # Step dataclass
│   │   ├── triggers.py           # Event triggers
│   │   ├── matrix.py             # Matrix builds
│   │   └── expressions.py        # Expression helpers
│   ├── actions/                  # Typed action wrappers
│   │   ├── checkout.py
│   │   ├── setup_python.py
│   │   └── ...
│   ├── cli/                      # CLI commands
│   │   ├── main.py               # CLI entry point
│   │   ├── build.py              # build command
│   │   ├── lint_cmd.py           # lint command
│   │   └── ...
│   ├── linter/                   # Code quality rules
│   │   ├── linter.py             # Linter orchestration
│   │   └── rules.py              # WAG001-WAG008 rules
│   ├── discover/                 # AST-based discovery
│   ├── serialize/                # Python to YAML conversion
│   ├── importer/                 # YAML to Python conversion
│   ├── validation/               # actionlint integration
│   ├── dependabot/               # Dependabot types
│   ├── issue_templates/          # Issue form types
│   ├── discussion_templates/     # Discussion types
│   └── core_integration/         # wetwire-core integration
├── codegen/                      # Code generation tools
│   ├── fetch.py                  # Fetch action schemas
│   ├── parse.py                  # Parse action.yml
│   └── generate.py               # Generate Python wrappers
├── tests/                        # Test suite
├── docs/                         # Documentation
├── pyproject.toml                # Package configuration
├── README.md                     # Project overview
└── CLAUDE.md                     # AI assistant guidelines
```

---

## Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# With coverage
uv run pytest tests/ --cov=wetwire_github --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_workflow.py -v

# Run specific test
uv run pytest tests/test_workflow.py::test_workflow_serialization -v

# Run only fast tests (skip slow integration tests)
uv run pytest tests/ -v -m "not slow"
```

---

## Code Generation

The `codegen/` directory contains tools for generating typed action wrappers.

### Overview

1. **fetch.py** - Download action.yml from GitHub Actions
2. **parse.py** - Parse action.yml into intermediate format
3. **generate.py** - Generate Python wrapper functions

### Running Code Generation

```bash
# Fetch action schemas (requires network)
uv run python -m codegen.fetch

# Parse schemas
uv run python -m codegen.parse

# Generate Python wrappers
uv run python -m codegen.generate
```

### Adding New Action Wrappers

1. Add action reference to `codegen/fetch.py`
2. Run the codegen pipeline
3. Verify generated code in `src/wetwire_github/actions/`
4. Add tests for the new wrapper

---

## Contributing

### Code Style

- **Formatting**: Use `ruff format`
- **Linting**: Use `ruff check`
- **Type Hints**: Required for all public APIs

```bash
# Format code
uv run ruff format src/ tests/

# Lint
uv run ruff check src/ tests/

# Type check
uv run ty check src/wetwire_github/
```

### Commit Messages

Follow conventional commits:

```
feat: Add support for workflow_dispatch trigger
fix: Correct matrix serialization
docs: Update installation instructions
test: Add tests for expression helpers
chore: Update dependencies
```

### Pull Request Process

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes with tests
3. Run tests: `uv run pytest tests/`
4. Run linting: `uv run ruff check src/ tests/`
5. Commit with clear messages
6. Push and open Pull Request
7. Address review comments

### Adding New Lint Rules

1. Add rule to `src/wetwire_github/linter/rules.py`
2. Follow naming convention: `WAG0XX`
3. Implement `check()` method
4. Add tests in `tests/test_linter.py`
5. Document in `docs/LINT_RULES.md`

---

## See Also

- [Quick Start](QUICK_START.md) - Getting started
- [CLI Reference](CLI.md) - CLI commands
- [Internals](INTERNALS.md) - Architecture details
- [Lint Rules](LINT_RULES.md) - Lint rule documentation
