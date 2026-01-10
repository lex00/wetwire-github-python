# Advanced FAQ

Advanced questions for wetwire-github power users. For basics, see [FAQ.md](FAQ.md).

---

## Migration from Hand-Written YAML

### How do I migrate a complex workflow?

1. Import to understand structure:
   ```bash
   wetwire-github import .github/workflows/complex.yml -o ci/
   ```

2. Refactor incrementally:
   ```python
   # Extract conditions to named variables
   is_main = GitHub.ref == "refs/heads/main"
   should_deploy = is_main.and_(Expression("github.event_name == 'push'"))

   deploy_job = Job(if_=str(should_deploy), ...)
   ```

3. Run linter to find improvements:
   ```bash
   wetwire-github lint ci/ --fix
   ```

### How do I handle external scripts?

Keep scripts external:

```python
# Good: reference external script
Step(run="./scripts/build.sh")

# Avoid: large inline scripts
Step(run="# 50 lines of bash...")
```

### How do I call reusable workflows from other repos?

Use raw `uses` in Job:

```python
build_job = Job(
    uses="org/shared-workflows/.github/workflows/build.yml@main",
    with_={"python-version": "3.11"},
    secrets="inherit",
)
```

---

## Debugging Workflow Discovery

### Why doesn't my workflow appear in `list`?

Discovery uses AST parsing. Requirements:
1. Module-level assignment
2. Import from `wetwire_github.workflow`
3. Explicit instantiation

```python
# NOT discovered
def get_workflow():
    return Workflow(...)

workflows = [Workflow(...) for i in range(3)]

from my_lib import Workflow  # wrong source

# Discovered
from wetwire_github.workflow import Workflow
ci = Workflow(...)
```

### How do I debug discovery?

```python
from wetwire_github.discover import discover_in_directory

for r in discover_in_directory('ci/'):
    print(f'{r.type}: {r.name} in {r.file_path}:{r.line_number}')
```

---

## Performance Profiling

### How do I profile discovery?

```python
import timeit
from wetwire_github.discover import discover_in_directory

time = timeit.timeit(lambda: discover_in_directory("ci/"), number=10)
print(f"Average: {time/10:.3f}s")
```

### How do I benchmark cache effectiveness?

```python
from wetwire_github.discover import discover_in_directory
from wetwire_github.discover.cache import DiscoveryCache
import time

# Cold run
start = time.time()
discover_in_directory("ci/")
cold = time.time() - start

# Warm run with cache
cache = DiscoveryCache()
start = time.time()
discover_in_directory("ci/", cache=cache)
warm = time.time() - start

print(f"Cold: {cold:.3f}s, Warm: {warm:.3f}s, Speedup: {cold/warm:.1f}x")
```

---

## Contributing New Action Wrappers

### How do I add a wrapper for a new action?

1. Add to `codegen/fetch.py`:
   ```python
   ACTION_REPOS = {
       "my-action": "org/my-action",
   }
   ```

2. Run codegen:
   ```bash
   uv run python -m codegen.fetch
   uv run python -m codegen.generate
   ```

3. Verify:
   ```bash
   cat src/wetwire_github/actions/my_action.py
   ```

4. Test:
   ```python
   from wetwire_github.actions import my_action
   step = my_action(param="value")
   assert step.uses == "org/my-action@v4"
   ```

---

## Creating Custom Linter Rules

### How do I create a custom rule?

```python
import ast
from wetwire_github.linter import BaseRule, LintError

class WAG100MyRule(BaseRule):
    @property
    def id(self) -> str:
        return "WAG100"

    @property
    def description(self) -> str:
        return "Description of what rule checks"

    def check(self, source: str, file_path: str) -> list[LintError]:
        errors = []
        tree = ast.parse(source)
        # Walk AST and find issues
        for node in ast.walk(tree):
            if isinstance(node, ast.keyword) and node.arg == "runs_on":
                if isinstance(node.value, ast.Constant):
                    errors.append(LintError(
                        rule_id=self.id,
                        message="Found hardcoded runner",
                        file_path=file_path,
                        line=node.lineno,
                        column=node.col_offset,
                    ))
        return errors
```

### How do I use custom rules?

```python
from wetwire_github.linter import Linter
from my_rules import WAG100MyRule

linter = Linter(rules=[WAG100MyRule()])
result = linter.check(source, "workflows.py")
```

### How do I create a fixable rule?

```python
class WAG101Fixable(BaseRule):
    def check(self, source: str, file_path: str) -> list[LintError]:
        # Detection logic
        pass

    def fix(self, source: str, file_path: str) -> tuple[str, int, list[LintError]]:
        import re
        fixed_source, count = re.subn(r'old_pattern', 'new_pattern', source)
        remaining = self.check(fixed_source, file_path)
        return fixed_source, count, remaining
```

---

## See Also

- [FAQ.md](FAQ.md) - Basic FAQ
- [DEVELOPERS.md](DEVELOPERS.md) - Developer guide
- [INTERNALS.md](INTERNALS.md) - Architecture
- [LINT_RULES.md](LINT_RULES.md) - Built-in rules
- [CODEGEN.md](CODEGEN.md) - Code generation
