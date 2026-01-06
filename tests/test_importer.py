"""Tests for YAML workflow importer."""


from wetwire_github.importer import (
    IRJob,
    IRStep,
    IRWorkflow,
    build_reference_graph,
    parse_workflow_file,
    parse_workflow_yaml,
)


class TestIRStep:
    """Tests for IRStep dataclass."""

    def test_ir_step_run(self):
        """IRStep stores run step info."""
        step = IRStep(
            id="build",
            name="Build project",
            run="npm run build",
        )
        assert step.id == "build"
        assert step.name == "Build project"
        assert step.run == "npm run build"

    def test_ir_step_uses(self):
        """IRStep stores uses step info."""
        step = IRStep(
            id="checkout",
            name="Checkout code",
            uses="actions/checkout@v4",
            with_={"ref": "main"},
        )
        assert step.uses == "actions/checkout@v4"
        assert step.with_["ref"] == "main"


class TestIRJob:
    """Tests for IRJob dataclass."""

    def test_ir_job(self):
        """IRJob stores job info."""
        job = IRJob(
            id="build",
            name="Build",
            runs_on="ubuntu-latest",
            steps=[
                IRStep(id=None, name="Test", run="npm test"),
            ],
        )
        assert job.id == "build"
        assert job.runs_on == "ubuntu-latest"
        assert len(job.steps) == 1

    def test_ir_job_with_needs(self):
        """IRJob stores job dependencies."""
        job = IRJob(
            id="deploy",
            name="Deploy",
            runs_on="ubuntu-latest",
            needs=["build", "test"],
            steps=[],
        )
        assert job.needs == ["build", "test"]


class TestIRWorkflow:
    """Tests for IRWorkflow dataclass."""

    def test_ir_workflow(self):
        """IRWorkflow stores workflow info."""
        workflow = IRWorkflow(
            name="CI",
            on={"push": {"branches": ["main"]}},
            jobs={
                "build": IRJob(
                    id="build",
                    name="Build",
                    runs_on="ubuntu-latest",
                    steps=[],
                ),
            },
        )
        assert workflow.name == "CI"
        assert "build" in workflow.jobs


class TestParseWorkflowYaml:
    """Tests for parse_workflow_yaml function."""

    def test_parse_minimal_workflow(self):
        """Parse minimal workflow YAML."""
        yaml_content = """
name: CI
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Hello"
"""
        workflow = parse_workflow_yaml(yaml_content)
        assert workflow.name == "CI"
        assert "build" in workflow.jobs
        assert workflow.jobs["build"].runs_on == "ubuntu-latest"

    def test_parse_workflow_with_multiple_jobs(self):
        """Parse workflow with multiple jobs."""
        yaml_content = """
name: CI
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: npm build
  test:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - run: npm test
"""
        workflow = parse_workflow_yaml(yaml_content)
        assert len(workflow.jobs) == 2
        assert workflow.jobs["test"].needs == ["build"]

    def test_parse_workflow_with_uses_step(self):
        """Parse workflow with action uses."""
        yaml_content = """
name: CI
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: main
"""
        workflow = parse_workflow_yaml(yaml_content)
        step = workflow.jobs["build"].steps[0]
        assert step.uses == "actions/checkout@v4"
        assert step.with_["ref"] == "main"

    def test_parse_workflow_with_triggers(self):
        """Parse workflow with complex triggers."""
        yaml_content = """
name: CI
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
"""
        workflow = parse_workflow_yaml(yaml_content)
        assert "push" in workflow.on
        assert "pull_request" in workflow.on

    def test_parse_workflow_preserves_env(self):
        """Parse workflow with environment variables."""
        yaml_content = """
name: CI
on: push
env:
  NODE_ENV: production
jobs:
  build:
    runs-on: ubuntu-latest
    env:
      CI: "true"
    steps:
      - run: echo "test"
"""
        workflow = parse_workflow_yaml(yaml_content)
        assert workflow.env == {"NODE_ENV": "production"}
        assert workflow.jobs["build"].env == {"CI": "true"}


class TestParseWorkflowFile:
    """Tests for parse_workflow_file function."""

    def test_parse_workflow_file(self, tmp_path):
        """Parse workflow from file."""
        file_path = tmp_path / "ci.yml"
        file_path.write_text("""
name: CI
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
""")
        workflow = parse_workflow_file(str(file_path))
        assert workflow.name == "CI"

    def test_parse_workflow_file_not_found(self, tmp_path):
        """Handle missing file gracefully."""
        file_path = tmp_path / "missing.yml"
        workflow = parse_workflow_file(str(file_path))
        assert workflow is None


class TestBuildReferenceGraph:
    """Tests for build_reference_graph function."""

    def test_build_job_dependency_graph(self):
        """Build graph of job dependencies."""
        yaml_content = """
name: CI
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: npm build
  test:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - run: npm test
  deploy:
    runs-on: ubuntu-latest
    needs: [build, test]
    steps:
      - run: npm deploy
"""
        workflow = parse_workflow_yaml(yaml_content)
        graph = build_reference_graph(workflow)

        # deploy depends on build and test
        assert "build" in graph["deploy"]
        assert "test" in graph["deploy"]
        # test depends on build
        assert "build" in graph["test"]
        # build has no dependencies
        assert graph["build"] == []

    def test_build_action_reference_graph(self):
        """Track action references."""
        yaml_content = """
name: CI
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
"""
        workflow = parse_workflow_yaml(yaml_content)
        graph = build_reference_graph(workflow, include_actions=True)

        # Check that action references are tracked
        assert "actions" in graph
        assert "actions/checkout@v4" in graph["actions"]
        assert "actions/setup-node@v4" in graph["actions"]
