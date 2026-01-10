# Workflow Recipes

Practical workflow recipes showing both Python declarations and generated YAML.

---

## PR Review with Auto-Fix Suggestions

Lint PRs and post suggestions using GitHub's review API.

### Python

```python
from wetwire_github.workflow import (
    Workflow, Job, Step, Triggers, PullRequestTrigger, Permissions,
)
from wetwire_github.actions import checkout, setup_python

lint_job = Job(
    name="Lint and Suggest",
    runs_on="ubuntu-latest",
    permissions=Permissions(contents="read", pull_requests="write"),
    steps=[
        checkout(),
        setup_python(python_version="3.11"),
        Step(run="pip install ruff"),
        Step(
            name="Run ruff",
            id="lint",
            run="ruff check . --output-format=json > lint.json || true",
        ),
        Step(
            name="Post suggestions",
            if_="always()",
            uses="actions/github-script@v7",
            with_={"script": "/* Post review comments from lint.json */"},
        ),
    ],
)

pr_review = Workflow(
    name="PR Review",
    on=Triggers(pull_request=PullRequestTrigger(types=["opened", "synchronize"])),
    jobs={"lint": lint_job},
)
```

### Generated YAML

```yaml
name: PR Review
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  lint:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install ruff
      - name: Run ruff
        id: lint
        run: ruff check . --output-format=json > lint.json || true
      - name: Post suggestions
        if: always()
        uses: actions/github-script@v7
```

---

## Matrix Testing with Failure Notifications

Test across versions with Slack notification on failure.

### Python

```python
from wetwire_github.workflow import Workflow, Job, Step, Triggers, PushTrigger
from wetwire_github.workflow.matrix import Strategy, Matrix
from wetwire_github.workflow.expressions import Secrets, MatrixContext, failure
from wetwire_github.actions import checkout, setup_python

test_matrix = Matrix(
    values={
        "python-version": ["3.10", "3.11", "3.12"],
        "os": ["ubuntu-latest", "macos-latest"],
    },
)

test_job = Job(
    runs_on=str(MatrixContext.get("os")),
    strategy=Strategy(matrix=test_matrix, fail_fast=False),
    steps=[
        checkout(),
        setup_python(python_version=str(MatrixContext.get("python-version"))),
        Step(run="pip install -e '.[test]' && pytest"),
    ],
)

notify_job = Job(
    runs_on="ubuntu-latest",
    needs=["test"],
    if_=str(failure()),
    steps=[
        Step(
            run='curl -X POST "$SLACK_WEBHOOK" -d \'{"text":"Tests failed"}\'',
            env={"SLACK_WEBHOOK": str(Secrets.get("SLACK_WEBHOOK"))},
        ),
    ],
)

matrix_ci = Workflow(
    name="Matrix CI",
    on=Triggers(push=PushTrigger(branches=["main"])),
    jobs={"test": test_job, "notify": notify_job},
)
```

### Generated YAML

```yaml
name: Matrix CI
on:
  push:
    branches: [main]
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
        os: [ubuntu-latest, macos-latest]
      fail-fast: false
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e '.[test]' && pytest
  notify:
    runs-on: ubuntu-latest
    needs: [test]
    if: ${{ failure() }}
    steps:
      - run: curl -X POST "$SLACK_WEBHOOK" -d '{"text":"Tests failed"}'
        env:
          SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
```

---

## Docker Build with SLSA Provenance

Build and push images with supply chain attestation.

### Python

```python
from wetwire_github.workflow import Workflow, Job, Step, Triggers, PushTrigger, Permissions
from wetwire_github.workflow.expressions import Secrets, GitHub
from wetwire_github.actions import checkout, setup_buildx, docker_login, docker_build_push

docker_job = Job(
    runs_on="ubuntu-latest",
    permissions=Permissions(contents="read", packages="write", id_token="write"),
    steps=[
        checkout(),
        setup_buildx(),
        docker_login(
            registry="ghcr.io",
            username=str(GitHub.actor),
            password=str(Secrets.get("GITHUB_TOKEN")),
        ),
        docker_build_push(
            context=".",
            push="true",
            tags="ghcr.io/${{ github.repository }}:${{ github.sha }}",
            provenance="true",
            sbom="true",
        ),
    ],
)

docker_workflow = Workflow(
    name="Docker Build",
    on=Triggers(push=PushTrigger(branches=["main"], tags=["v*"])),
    jobs={"build": docker_job},
)
```

### Generated YAML

```yaml
name: Docker Build
on:
  push:
    branches: [main]
    tags: [v*]
jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: "true"
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          provenance: "true"
          sbom: "true"
```

---

## Database Integration Testing

Tests with PostgreSQL and Redis service containers.

### Python

```python
from wetwire_github.workflow import Workflow, Job, Step, Triggers, PushTrigger, Service
from wetwire_github.actions import checkout, setup_python

integration_job = Job(
    runs_on="ubuntu-latest",
    services={
        "postgres": Service(
            image="postgres:15",
            env={"POSTGRES_PASSWORD": "test", "POSTGRES_DB": "testdb"},
            ports=["5432:5432"],
            options="--health-cmd pg_isready --health-interval 10s",
        ),
        "redis": Service(image="redis:7", ports=["6379:6379"]),
    },
    steps=[
        checkout(),
        setup_python(python_version="3.11"),
        Step(run="pip install -e '.[test]'"),
        Step(
            run="pytest tests/integration/",
            env={
                "DATABASE_URL": "postgresql://postgres:test@localhost:5432/testdb",
                "REDIS_URL": "redis://localhost:6379",
            },
        ),
    ],
)

integration_workflow = Workflow(
    name="Integration Tests",
    on=Triggers(push=PushTrigger(branches=["main"])),
    jobs={"integration": integration_job},
)
```

### Generated YAML

```yaml
name: Integration Tests
on:
  push:
    branches: [main]
jobs:
  integration:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: testdb
        ports: ["5432:5432"]
        options: --health-cmd pg_isready --health-interval 10s
      redis:
        image: redis:7
        ports: ["6379:6379"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e '.[test]'
      - run: pytest tests/integration/
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/testdb
          REDIS_URL: redis://localhost:6379
```

---

## Conditional Deployment on Release Tags

Deploy only when release tags are pushed.

### Python

```python
from wetwire_github.workflow import Workflow, Job, Step, Triggers, PushTrigger, Environment
from wetwire_github.workflow.expressions import Secrets
from wetwire_github.actions import checkout, setup_python

build_job = Job(
    runs_on="ubuntu-latest",
    steps=[
        checkout(),
        setup_python(python_version="3.11"),
        Step(run="pip install build && python -m build"),
        Step(uses="actions/upload-artifact@v4", with_={"name": "dist", "path": "dist/"}),
    ],
)

deploy_job = Job(
    runs_on="ubuntu-latest",
    needs=["build"],
    if_="startsWith(github.ref, 'refs/tags/v')",
    environment=Environment(name="production"),
    steps=[
        Step(uses="actions/download-artifact@v4", with_={"name": "dist"}),
        Step(
            run="pip install twine && twine upload dist/*",
            env={"TWINE_PASSWORD": str(Secrets.get("PYPI_TOKEN"))},
        ),
    ],
)

release_workflow = Workflow(
    name="Release",
    on=Triggers(push=PushTrigger(branches=["main"], tags=["v*"])),
    jobs={"build": build_job, "deploy": deploy_job},
)
```

### Generated YAML

```yaml
name: Release
on:
  push:
    branches: [main]
    tags: [v*]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install build && python -m build
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
  deploy:
    runs-on: ubuntu-latest
    needs: [build]
    if: startsWith(github.ref, 'refs/tags/v')
    environment:
      name: production
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
      - run: pip install twine && twine upload dist/*
        env:
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
```

---

## Monorepo Multi-Package Builds

Build only changed packages in a monorepo.

### Python

```python
from wetwire_github.workflow import Workflow, Job, Step, Triggers, PushTrigger
from wetwire_github.workflow.matrix import Strategy, Matrix
from wetwire_github.actions import checkout, setup_python

detect_job = Job(
    runs_on="ubuntu-latest",
    outputs={"packages": "${{ steps.changes.outputs.packages }}"},
    steps=[
        checkout(fetch_depth="0"),
        Step(
            name="Detect changes",
            id="changes",
            run="""
CHANGED=$(git diff --name-only HEAD~1 HEAD | grep '^packages/' | cut -d/ -f2 | sort -u)
echo "packages=$(echo $CHANGED | jq -R -s -c 'split(" ") | map(select(. != ""))')" >> $GITHUB_OUTPUT
""",
        ),
    ],
)

build_job = Job(
    runs_on="ubuntu-latest",
    needs=["detect"],
    if_="needs.detect.outputs.packages != '[]'",
    strategy=Strategy(
        matrix=Matrix(values={"package": "${{ fromJson(needs.detect.outputs.packages) }}"}),
        fail_fast=False,
    ),
    steps=[
        checkout(),
        setup_python(python_version="3.11"),
        Step(run="pip install -e 'packages/${{ matrix.package }}[dev]'"),
        Step(run="pytest packages/${{ matrix.package }}/tests/"),
    ],
)

monorepo_ci = Workflow(
    name="Monorepo CI",
    on=Triggers(push=PushTrigger(branches=["main"])),
    jobs={"detect": detect_job, "build": build_job},
)
```

### Generated YAML

```yaml
name: Monorepo CI
on:
  push:
    branches: [main]
jobs:
  detect:
    runs-on: ubuntu-latest
    outputs:
      packages: ${{ steps.changes.outputs.packages }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: "0"
      - name: Detect changes
        id: changes
        run: |
          CHANGED=$(git diff --name-only HEAD~1 HEAD | grep '^packages/' | cut -d/ -f2 | sort -u)
          echo "packages=$(echo $CHANGED | jq -R -s -c 'split(" ") | map(select(. != ""))')" >> $GITHUB_OUTPUT
  build:
    runs-on: ubuntu-latest
    needs: [detect]
    if: needs.detect.outputs.packages != '[]'
    strategy:
      matrix:
        package: ${{ fromJson(needs.detect.outputs.packages) }}
      fail-fast: false
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e 'packages/${{ matrix.package }}[dev]'
      - run: pytest packages/${{ matrix.package }}/tests/
```

---

## See Also

- [EXAMPLES.md](EXAMPLES.md) - Basic examples
- [EXPRESSIONS.md](EXPRESSIONS.md) - Expression builders
- [CLI.md](CLI.md) - CLI reference
