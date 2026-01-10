# Versioning

This document describes the versioning practices for `wetwire-github`.

## Table of Contents

- [Semantic Versioning](#semantic-versioning)
- [Version Management](#version-management)
- [Release Process](#release-process)
- [Changelog Conventions](#changelog-conventions)
- [Compatibility Guidelines](#compatibility-guidelines)

---

## Semantic Versioning

`wetwire-github` follows [Semantic Versioning 2.0.0](https://semver.org/) (`MAJOR.MINOR.PATCH`):

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
```

### Version Components

- **MAJOR** - Breaking changes to public API
- **MINOR** - New features, backwards-compatible
- **PATCH** - Bug fixes, backwards-compatible

### Examples

```
0.1.0       - Initial alpha release
0.2.0       - New features added
0.2.1       - Bug fixes
1.0.0       - First stable release
1.1.0       - New features (stable)
2.0.0       - Breaking changes
```

### Pre-release Versions

Pre-release versions are indicated with a suffix:

```
0.1.0-alpha.1    - Alpha release
0.1.0-beta.1     - Beta release
0.1.0-rc.1       - Release candidate
```

---

## Version Management

### Current Version

The version is maintained in a single source of truth:

**pyproject.toml:**
```toml
[project]
name = "wetwire-github"
version = "0.1.0"
```

### Development Status

Track development status via PyPI classifiers in `pyproject.toml`:

```toml
classifiers = [
    "Development Status :: 3 - Alpha",
    # ...
]
```

**Development Status Levels:**
- `3 - Alpha` - Early development (0.x versions)
- `4 - Beta` - Feature complete, stabilizing
- `5 - Production/Stable` - Ready for production (1.0+)

### Python Version Support

Minimum Python version is specified in `pyproject.toml`:

```toml
requires-python = ">=3.11"
```

Supported versions are listed in classifiers:

```toml
classifiers = [
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]
```

---

## Release Process

### 1. Pre-Release Checklist

Before creating a release:

- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] Linting passes: `uv run ruff check src/ tests/`
- [ ] Type checking passes: `uv run ty check src/wetwire_github/`
- [ ] Documentation is up to date
- [ ] CHANGELOG.md is updated with all changes
- [ ] Version number is updated in `pyproject.toml`

### 2. Update Version

Edit `pyproject.toml`:

```toml
[project]
version = "0.2.0"  # Increment according to SemVer
```

### 3. Update Changelog

Add release section to `CHANGELOG.md`:

```markdown
## [0.2.0] - 2026-01-15

### Added
- New feature X
- New feature Y

### Changed
- Updated behavior of Z

### Fixed
- Bug fix for issue #123

### Deprecated
- Feature A is deprecated, use B instead
```

### 4. Commit and Tag

```bash
# Commit version bump
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 0.2.0"

# Create annotated tag
git tag -a v0.2.0 -m "Release v0.2.0"

# Push changes and tag
git push origin main
git push origin v0.2.0
```

### 5. Build and Publish

```bash
# Build distribution packages
uv build

# Publish to PyPI (requires credentials)
uv publish

# Or publish to Test PyPI first
uv publish --repository testpypi
```

### 6. Create GitHub Release

1. Go to https://github.com/lex00/wetwire-github-python/releases
2. Click "Draft a new release"
3. Select the tag (e.g., `v0.2.0`)
4. Copy changelog section as release notes
5. Publish release

---

## Changelog Conventions

The `CHANGELOG.md` follows [Keep a Changelog](https://keepachangelog.com/) format.

### Structure

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- New features not yet released

## [0.2.0] - 2026-01-15

### Added
- New features

### Changed
- Changes to existing functionality

### Deprecated
- Features marked for removal

### Removed
- Features removed in this release

### Fixed
- Bug fixes

### Security
- Security fixes
```

### Change Categories

- **Added** - New features, capabilities, or commands
- **Changed** - Changes to existing functionality
- **Deprecated** - Features marked for future removal
- **Removed** - Features removed in this version
- **Fixed** - Bug fixes
- **Security** - Security vulnerability fixes

### Writing Style

- Use present tense: "Add feature X" not "Added feature X"
- Be specific: Reference issue numbers when applicable
- Group related changes together
- List breaking changes prominently

### Example Entry

```markdown
## [0.2.0] - 2026-01-15

### Added
- `wetwire-github init` command for project scaffolding (#53)
- Auto-fix support for WAG003 lint rule (#54)
- Discussion template configuration support

### Changed
- **BREAKING**: Renamed `validate_yaml()` to `validate()` for consistency
- Improved error messages in linter output

### Fixed
- Fixed matrix serialization for complex include/exclude patterns (#52)
- Corrected expression parsing for nested contexts

### Deprecated
- `Workflow.validate_yaml()` - Use `validate()` instead
```

---

## Compatibility Guidelines

### Alpha Phase (0.x versions)

Current status: **Alpha** (version 0.1.0)

**Expectations:**
- API may change between minor versions
- Breaking changes allowed in MINOR releases
- PATCH releases are backwards-compatible
- No guarantees on stability or completeness

**Migration:**
- Check CHANGELOG.md for each upgrade
- Expect to update code for minor version bumps
- Run linter after upgrades: `wetwire-github lint`

### Stable Phase (1.0+ versions)

When released (not yet):

**Expectations:**
- Public API is stable
- Breaking changes only in MAJOR releases
- MINOR releases add features, stay compatible
- PATCH releases fix bugs only

### What's Considered Public API

**Public API** (semver guarantees apply):
- All classes in `wetwire_github.workflow.*`
- All functions in `wetwire_github.actions.*`
- CLI commands and their flags
- Serialized YAML output format

**Private API** (no guarantees):
- Internal modules (prefixed with `_`)
- Functions marked with `@deprecated`
- Experimental features (documented as such)

### Deprecation Policy

**Alpha (0.x):**
- Features may be deprecated and removed in next minor version
- Deprecation warnings added when possible

**Stable (1.0+):**
- Deprecated features maintained for one MAJOR version
- Clear migration path provided in documentation
- Runtime warnings issued for deprecated usage

### Python Version Support

**Support Policy:**
- Support last 3 Python minor versions
- Drop support in MINOR releases (0.x) or MAJOR releases (1.0+)
- Announce deprecation at least 3 months in advance

**Current Support:**
- Python 3.11, 3.12, 3.13 (as of 0.1.0)

### Upgrade Recommendations

**Between PATCH versions (0.1.0 → 0.1.1):**
```bash
# Safe to upgrade
uv sync --upgrade-package wetwire-github
```

**Between MINOR versions (0.1.0 → 0.2.0):**
```bash
# Read CHANGELOG.md first
uv sync --upgrade-package wetwire-github

# Re-run linter to check for issues
wetwire-github lint ci/ --fix

# Regenerate YAML
wetwire-github build ci/
```

**Between MAJOR versions (1.0.0 → 2.0.0):**
```bash
# Read migration guide in CHANGELOG.md
# Review breaking changes carefully
uv sync --upgrade-package wetwire-github

# Expect code changes required
wetwire-github lint ci/
```

---

## Version History

| Version | Date       | Status | Notes                          |
|---------|------------|--------|--------------------------------|
| 0.1.0   | 2026-01-06 | Alpha  | Initial release with core features |

---

## See Also

- [CHANGELOG.md](../CHANGELOG.md) - Full version history
- [Semantic Versioning](https://semver.org/) - SemVer specification
- [Keep a Changelog](https://keepachangelog.com/) - Changelog format
- [Developer Guide](DEVELOPERS.md) - Contributing guidelines
