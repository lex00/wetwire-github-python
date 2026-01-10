# Advanced Troubleshooting

Advanced troubleshooting topics for wetwire-github. For basic issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

## Serialization Issues

### Circular Dependencies

**Symptoms:**
- `RecursionError: maximum recursion depth exceeded`
- Build hangs or crashes

**Diagnosis:**

```bash
wetwire-github graph ci/
# Look for cycles: job_a -> job_b -> job_a
```

**Solution:** Break cycles with fan-out/fan-in pattern:

```python
# Root job
build = Job(runs_on="ubuntu-latest", steps=[...])

# Fan-out: Multiple jobs depend on build
test = Job(needs=["build"], ...)
lint = Job(needs=["build"], ...)

# Fan-in: Deploy depends on all
deploy = Job(needs=["test", "lint"], ...)
```

### Expression Evaluation Errors

**Symptoms:** Malformed `${{ }}` expressions, double-escaped like `${{{{ }}}}`

**Solutions:**

```python
# Bad: String interpolation with expressions
env = {"TOKEN": f"prefix-{Secrets.get('TOKEN')}"}

# Good: Let Expression handle syntax
env = {"TOKEN": Secrets.get("TOKEN")}

# Use str() only for if_ conditions
job = Job(if_=str(GitHub.ref == "refs/heads/main"), ...)
```

---

## Actionlint Integration Issues

### Missing Tools

**Error:** `actionlint: shellcheck is not installed`

```bash
# Install optional checkers
brew install shellcheck  # macOS
pip install pyflakes
```

### Permission Errors

```bash
# Fix permissions
chmod 644 .github/workflows/*.yml

# For containers
chown -R $(id -u):$(id -g) .github/workflows/
```

### Version Incompatibilities

```bash
# Update to fix false positives
brew upgrade actionlint
# or
go install github.com/rhysd/actionlint/cmd/actionlint@latest
```

---

## Large Monorepo Performance

### Discovery Caching

Cache is stored in `.wetwire-cache/` with keys based on file path, mtime, and size.

**Tuning:**

```bash
# Selective scanning
wetwire-github list ci/workflows/  # Only specific dirs

# Pre-warm cache in CI
- uses: actions/cache@v4
  with:
    path: .wetwire-cache
    key: wetwire-${{ hashFiles('ci/**/*.py') }}
```

### Memory Optimization

```bash
# Process packages independently
for pkg in ci/package-*/; do
    wetwire-github build "$pkg"
done

# Parallel processing
find ci/ -maxdepth 1 -type d -name 'package-*' | \
    parallel -j4 'wetwire-github build {}'
```

---

## Testing Linter Rules Locally

### Running Individual Rules

```python
from wetwire_github.linter import Linter
from wetwire_github.linter.rules import WAG001TypedActionWrappers

source = '''
from wetwire_github.workflow import Step
step = Step(uses="actions/checkout@v4")
'''

linter = Linter(rules=[WAG001TypedActionWrappers()])
result = linter.check(source, "test.py")

for error in result.errors:
    print(f"{error.rule_id}: {error.message}")
```

### Pre-Commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: wetwire-lint
        name: wetwire-github lint
        entry: wetwire-github lint
        language: system
        files: ^ci/.*\.py$
```

---

## Debugging Discovery Issues

### Discovery Not Finding Workflows

Discovery uses AST parsing. Workflows must be:
1. Module-level assignments
2. Imported from `wetwire_github.workflow`
3. Explicit instantiation (not factory functions)

**Diagnosis:**

```python
from wetwire_github.discover import discover_in_directory

resources = discover_in_directory('ci/')
for r in resources:
    print(f'{r.type}: {r.name} in {r.file_path}:{r.line_number}')
```

**Common Issues:**

```python
# NOT discovered: inside function
def get_workflow():
    return Workflow(...)

# Discovered: module level
ci = Workflow(...)

# NOT discovered: dynamic construction
workflows = [Workflow(...) for i in range(3)]

# NOT discovered: wrong import
from my_lib import Workflow
```

### Cache Debugging

```bash
# Check cache contents
ls -la .wetwire-cache/

# Clear and rebuild
rm -rf .wetwire-cache
wetwire-github list ci/
```

---

## See Also

- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Basic troubleshooting
- [INTERNALS.md](INTERNALS.md) - Architecture details
- [LINT_RULES.md](LINT_RULES.md) - Lint rule reference
- [CLI.md](CLI.md) - CLI reference
