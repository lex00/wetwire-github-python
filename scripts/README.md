# Developer Scripts

Convenience scripts for common development tasks in wetwire-github-python.

## Quick Reference

| Script | Purpose | Example |
|--------|---------|---------|
| `dev-setup.sh` | Set up development environment | `./scripts/dev-setup.sh` |
| `test.sh` | Run tests with optional coverage | `./scripts/test.sh` |
| `lint.sh` | Run linting and formatting | `./scripts/lint.sh` |
| `typecheck.sh` | Run type checking | `./scripts/typecheck.sh` |
| `build.sh` | Build the package | `./scripts/build.sh` |

## Detailed Usage

### dev-setup.sh

Initial setup for new developers or fresh environments.

```bash
# Interactive setup (recommended for first-time setup)
./scripts/dev-setup.sh

# Non-interactive (CI/automated environments)
./scripts/dev-setup.sh --auto

# Show help
./scripts/dev-setup.sh --help
```

**What it does:**
1. Checks for Python 3.11+ and git
2. Installs uv package manager if not present
3. Creates virtual environment and installs dependencies
4. Optionally installs actionlint (YAML validation tool)
5. Runs initial test suite to verify setup
6. Makes all scripts executable

### test.sh

Run the test suite with various options.

```bash
# Run all tests with coverage (default)
./scripts/test.sh

# Run tests without coverage
./scripts/test.sh --no-cov

# Run only fast tests (skip slow integration tests)
./scripts/test.sh --fast

# Run specific test file
./scripts/test.sh tests/test_workflow.py

# Run specific test function
./scripts/test.sh tests/test_workflow.py::test_workflow_serialization

# Extra verbose output
./scripts/test.sh -v

# Combine options
./scripts/test.sh --fast --no-cov tests/test_linter.py
```

### lint.sh

Run code linting and formatting checks.

```bash
# Run both check and format (default)
./scripts/lint.sh

# Run linting checks only (no formatting)
./scripts/lint.sh check

# Run code formatting only
./scripts/lint.sh format

# Auto-fix linting issues and format code
./scripts/lint.sh fix

# Show help
./scripts/lint.sh --help
```

**Note:** Uses `ruff` for both linting and formatting (configured in `pyproject.toml`).

### typecheck.sh

Run type checking using the `ty` type checker.

```bash
# Type check source code only (default)
./scripts/typecheck.sh

# Type check both source and tests
./scripts/typecheck.sh --all

# Show help
./scripts/typecheck.sh --help
```

### build.sh

Build the Python package for distribution.

```bash
# Build the package
./scripts/build.sh

# Clean build artifacts before building
./scripts/build.sh --clean

# Show help
./scripts/build.sh --help
```

**Output:** Creates wheel and source distributions in `dist/` directory.

## Common Workflows

### Before Committing

```bash
# Run the full quality check suite
./scripts/lint.sh fix          # Fix and format code
./scripts/typecheck.sh         # Check types
./scripts/test.sh              # Run tests with coverage
```

### Quick Check (Fast Feedback)

```bash
# Run fast tests only
./scripts/test.sh --fast --no-cov
./scripts/lint.sh check
```

### CI/CD Pipeline Simulation

```bash
# Simulate what CI will run
./scripts/lint.sh check        # Linting
./scripts/typecheck.sh         # Type checking
./scripts/test.sh              # Full test suite with coverage
./scripts/build.sh             # Package build
```

### New Developer Setup

```bash
# First time setup
./scripts/dev-setup.sh

# Verify everything works
./scripts/test.sh
```

## Requirements

All scripts require:
- **Python 3.11+**
- **uv** package manager (will be installed by dev-setup.sh)

Optional:
- **actionlint** - For YAML validation (optional, prompted by dev-setup.sh)

## Integration with Project Tools

These scripts use the project's configuration from `pyproject.toml`:

- **ruff**: Configured for Python 3.11+, line length 88, specific rule sets
- **pytest**: Configured with coverage reporting, test discovery patterns
- **ty**: Type checker for Python type hints
- **uv**: Fast Python package manager

## See Also

- [DEVELOPERS.md](../docs/DEVELOPERS.md) - Comprehensive developer guide
- [pyproject.toml](../pyproject.toml) - Tool configurations
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines (if exists)
