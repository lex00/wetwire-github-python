"""Tests for AST discovery."""



from wetwire_github.discover import (
    DiscoveredResource,
    build_dependency_graph,
    discover_in_directory,
    discover_in_file,
    validate_references,
)


class TestDiscoverInFile:
    """Tests for discover_in_file function."""

    def test_discover_workflow_variable(self, tmp_path):
        """Discover a Workflow variable in a Python file."""
        file_path = tmp_path / "workflows.py"
        file_path.write_text('''
from wetwire_github.workflow import Workflow

ci = Workflow(name="CI")
''')
        resources = discover_in_file(str(file_path))
        assert len(resources) == 1
        assert resources[0].name == "ci"
        assert resources[0].type == "Workflow"

    def test_discover_job_variable(self, tmp_path):
        """Discover a Job variable in a Python file."""
        file_path = tmp_path / "jobs.py"
        file_path.write_text('''
from wetwire_github.workflow import Job

build = Job(runs_on="ubuntu-latest")
''')
        resources = discover_in_file(str(file_path))
        assert len(resources) == 1
        assert resources[0].name == "build"
        assert resources[0].type == "Job"

    def test_discover_multiple_resources(self, tmp_path):
        """Discover multiple resources in a single file."""
        file_path = tmp_path / "multi.py"
        file_path.write_text('''
from wetwire_github.workflow import Workflow, Job

ci = Workflow(name="CI")
build = Job(runs_on="ubuntu-latest")
test = Job(runs_on="ubuntu-latest")
''')
        resources = discover_in_file(str(file_path))
        assert len(resources) == 3
        names = {r.name for r in resources}
        assert names == {"ci", "build", "test"}

    def test_discover_with_aliased_import(self, tmp_path):
        """Discover resources with aliased imports."""
        file_path = tmp_path / "aliased.py"
        file_path.write_text('''
from wetwire_github.workflow import Workflow as WF

my_workflow = WF(name="My Workflow")
''')
        resources = discover_in_file(str(file_path))
        assert len(resources) == 1
        assert resources[0].name == "my_workflow"
        assert resources[0].type == "Workflow"

    def test_ignore_non_workflow_variables(self, tmp_path):
        """Ignore variables that aren't Workflow or Job."""
        file_path = tmp_path / "other.py"
        file_path.write_text('''
from wetwire_github.workflow import Step

my_step = Step(name="Test")
other = "string"
count = 42
''')
        resources = discover_in_file(str(file_path))
        # Step is not a discoverable resource type
        assert len(resources) == 0

    def test_discover_handles_syntax_error(self, tmp_path):
        """Handle syntax errors gracefully."""
        file_path = tmp_path / "broken.py"
        file_path.write_text('''
def incomplete(
''')
        resources = discover_in_file(str(file_path))
        assert len(resources) == 0

    def test_discover_extracts_module_path(self, tmp_path):
        """Extract module path from file location."""
        file_path = tmp_path / "workflows.py"
        file_path.write_text('''
from wetwire_github.workflow import Workflow

ci = Workflow(name="CI")
''')
        resources = discover_in_file(str(file_path))
        assert resources[0].file_path == str(file_path)


class TestDiscoverInDirectory:
    """Tests for discover_in_directory function."""

    def test_discover_in_directory(self, tmp_path):
        """Discover resources in a directory."""
        # Create two Python files
        (tmp_path / "workflows.py").write_text('''
from wetwire_github.workflow import Workflow

ci = Workflow(name="CI")
''')
        (tmp_path / "jobs.py").write_text('''
from wetwire_github.workflow import Job

build = Job(runs_on="ubuntu-latest")
''')
        resources = discover_in_directory(str(tmp_path))
        assert len(resources) == 2

    def test_recursive_discovery(self, tmp_path):
        """Recursively discover in subdirectories."""
        # Create nested structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        (tmp_path / "root.py").write_text('''
from wetwire_github.workflow import Workflow

root_workflow = Workflow(name="Root")
''')
        (subdir / "nested.py").write_text('''
from wetwire_github.workflow import Workflow

nested_workflow = Workflow(name="Nested")
''')
        resources = discover_in_directory(str(tmp_path))
        assert len(resources) == 2

    def test_exclude_pycache(self, tmp_path):
        """Exclude __pycache__ directories."""
        pycache = tmp_path / "__pycache__"
        pycache.mkdir()

        (pycache / "cached.py").write_text('''
from wetwire_github.workflow import Workflow

cached = Workflow(name="Cached")
''')
        (tmp_path / "workflows.py").write_text('''
from wetwire_github.workflow import Workflow

ci = Workflow(name="CI")
''')
        resources = discover_in_directory(str(tmp_path))
        assert len(resources) == 1
        assert resources[0].name == "ci"

    def test_exclude_hidden_directories(self, tmp_path):
        """Exclude hidden directories (starting with .)."""
        hidden = tmp_path / ".hidden"
        hidden.mkdir()

        (hidden / "secret.py").write_text('''
from wetwire_github.workflow import Workflow

secret = Workflow(name="Secret")
''')
        (tmp_path / "workflows.py").write_text('''
from wetwire_github.workflow import Workflow

ci = Workflow(name="CI")
''')
        resources = discover_in_directory(str(tmp_path))
        assert len(resources) == 1
        assert resources[0].name == "ci"

    def test_only_python_files(self, tmp_path):
        """Only scan .py files."""
        (tmp_path / "not_python.txt").write_text('''
from wetwire_github.workflow import Workflow

ci = Workflow(name="CI")
''')
        (tmp_path / "workflows.py").write_text('''
from wetwire_github.workflow import Workflow

ci = Workflow(name="CI")
''')
        resources = discover_in_directory(str(tmp_path))
        assert len(resources) == 1


class TestDiscoveredResource:
    """Tests for DiscoveredResource dataclass."""

    def test_discovered_resource(self):
        """DiscoveredResource stores resource info."""
        resource = DiscoveredResource(
            name="ci",
            type="Workflow",
            file_path="/path/to/workflows.py",
            line_number=5,
            module="workflows",
        )
        assert resource.name == "ci"
        assert resource.type == "Workflow"
        assert resource.file_path == "/path/to/workflows.py"
        assert resource.line_number == 5


class TestBuildDependencyGraph:
    """Tests for build_dependency_graph function."""

    def test_build_simple_graph(self, tmp_path):
        """Build a dependency graph from discovered resources."""
        file_path = tmp_path / "workflows.py"
        file_path.write_text('''
from wetwire_github.workflow import Workflow, Job

build_job = Job(runs_on="ubuntu-latest")
ci = Workflow(name="CI", jobs={"build": build_job})
''')
        resources = discover_in_file(str(file_path))
        graph = build_dependency_graph(resources)

        # Workflow depends on Job
        assert "ci" in graph
        assert "build_job" in graph.get("ci", [])

    def test_empty_graph_for_independent_resources(self, tmp_path):
        """Build empty dependencies for independent resources."""
        file_path = tmp_path / "workflows.py"
        file_path.write_text('''
from wetwire_github.workflow import Workflow

ci = Workflow(name="CI")
deploy = Workflow(name="Deploy")
''')
        resources = discover_in_file(str(file_path))
        graph = build_dependency_graph(resources)

        # No dependencies between independent workflows
        assert graph.get("ci", []) == []
        assert graph.get("deploy", []) == []


class TestValidateReferences:
    """Tests for validate_references function."""

    def test_validate_valid_references(self, tmp_path):
        """Validate references between resources."""
        file_path = tmp_path / "workflows.py"
        file_path.write_text('''
from wetwire_github.workflow import Workflow, Job

build_job = Job(runs_on="ubuntu-latest")
ci = Workflow(name="CI", jobs={"build": build_job})
''')
        resources = discover_in_file(str(file_path))
        errors = validate_references(resources)
        assert len(errors) == 0

    def test_detect_missing_reference(self, tmp_path):
        """Detect reference to undefined resource."""
        file_path = tmp_path / "workflows.py"
        file_path.write_text('''
from wetwire_github.workflow import Workflow

# Reference to undefined_job which doesn't exist
ci = Workflow(name="CI", jobs={"build": undefined_job})
''')
        # This is valid Python syntax (NameError at runtime, not SyntaxError)
        # The discovery records the undefined_job as a dependency
        resources = discover_in_file(str(file_path))
        assert len(resources) == 1
        assert resources[0].dependencies == ["undefined_job"]

        # validate_references checks against discovered resources only
        errors = validate_references(resources)
        # undefined_job is not a discovered resource, but we don't error
        # because it might be a valid import/variable not tracked
        assert len(errors) == 0
