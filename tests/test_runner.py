"""Tests for runner/value extraction."""

import sys

from wetwire_github.runner import (
    ExtractedJob,
    ExtractedWorkflow,
    extract_jobs,
    extract_workflows,
    find_package_root,
    resolve_module_path,
)


class TestFindPackageRoot:
    """Tests for find_package_root function."""

    def test_find_pyproject_root(self, tmp_path):
        """Find package root from pyproject.toml."""
        # Create pyproject.toml
        (tmp_path / "pyproject.toml").write_text("""
[project]
name = "myproject"
""")
        subdir = tmp_path / "src" / "myproject"
        subdir.mkdir(parents=True)

        root = find_package_root(str(subdir))
        assert root == str(tmp_path)

    def test_find_setup_py_root(self, tmp_path):
        """Find package root from setup.py."""
        (tmp_path / "setup.py").write_text("# setup")
        subdir = tmp_path / "mypackage"
        subdir.mkdir()

        root = find_package_root(str(subdir))
        assert root == str(tmp_path)

    def test_no_package_root(self, tmp_path):
        """Return None when no package root found."""
        subdir = tmp_path / "random"
        subdir.mkdir()

        root = find_package_root(str(subdir))
        assert root is None


class TestResolveModulePath:
    """Tests for resolve_module_path function."""

    def test_resolve_simple_module(self, tmp_path):
        """Resolve simple module path."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'")
        (tmp_path / "workflows.py").write_text("x = 1")

        module_path = resolve_module_path(
            str(tmp_path / "workflows.py"),
            str(tmp_path),
        )
        assert module_path == "workflows"

    def test_resolve_nested_module(self, tmp_path):
        """Resolve nested module path."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'")
        pkg = tmp_path / "mypackage" / "workflows"
        pkg.mkdir(parents=True)
        (pkg / "ci.py").write_text("x = 1")

        module_path = resolve_module_path(
            str(pkg / "ci.py"),
            str(tmp_path),
        )
        assert module_path == "mypackage.workflows.ci"


class TestExtractedWorkflow:
    """Tests for ExtractedWorkflow dataclass."""

    def test_extracted_workflow(self):
        """ExtractedWorkflow stores extracted info."""
        from wetwire_github.workflow import Workflow

        wf = Workflow(name="CI")
        extracted = ExtractedWorkflow(
            name="ci",
            module="workflows",
            workflow=wf,
        )
        assert extracted.name == "ci"
        assert extracted.workflow.name == "CI"


class TestExtractedJob:
    """Tests for ExtractedJob dataclass."""

    def test_extracted_job(self):
        """ExtractedJob stores extracted info."""
        from wetwire_github.workflow import Job

        job = Job(runs_on="ubuntu-latest")
        extracted = ExtractedJob(
            name="build",
            module="jobs",
            job=job,
        )
        assert extracted.name == "build"
        assert extracted.job.runs_on == "ubuntu-latest"


class TestExtractWorkflows:
    """Tests for extract_workflows function."""

    def test_extract_workflow_from_module(self, tmp_path):
        """Extract Workflow objects from a module."""
        # Create a simple module with a Workflow
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'")
        (tmp_path / "workflows.py").write_text('''
from wetwire_github.workflow import Workflow

ci = Workflow(name="CI")
deploy = Workflow(name="Deploy")
''')
        # Add tmp_path to sys.path temporarily
        sys.path.insert(0, str(tmp_path))
        try:
            workflows = extract_workflows(str(tmp_path / "workflows.py"))
            assert len(workflows) >= 2
            names = {w.name for w in workflows}
            assert "ci" in names
            assert "deploy" in names
        finally:
            sys.path.remove(str(tmp_path))

    def test_extract_skips_non_workflows(self, tmp_path):
        """Don't extract non-Workflow objects."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'")
        (tmp_path / "mixed.py").write_text('''
from wetwire_github.workflow import Workflow, Job

ci = Workflow(name="CI")
job = Job(runs_on="ubuntu-latest")
other = "not a workflow"
''')
        sys.path.insert(0, str(tmp_path))
        try:
            workflows = extract_workflows(str(tmp_path / "mixed.py"))
            # Should only get Workflow objects
            assert all(hasattr(w.workflow, "jobs") for w in workflows)
        finally:
            sys.path.remove(str(tmp_path))


class TestExtractJobs:
    """Tests for extract_jobs function."""

    def test_extract_job_from_module(self, tmp_path):
        """Extract Job objects from a module."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'")
        (tmp_path / "jobs.py").write_text('''
from wetwire_github.workflow import Job

build = Job(runs_on="ubuntu-latest")
test = Job(runs_on="ubuntu-latest")
''')
        sys.path.insert(0, str(tmp_path))
        try:
            jobs = extract_jobs(str(tmp_path / "jobs.py"))
            assert len(jobs) >= 2
            names = {j.name for j in jobs}
            assert "build" in names
            assert "test" in names
        finally:
            sys.path.remove(str(tmp_path))


class TestExtractFromDirectory:
    """Tests for extracting from directories."""

    def test_extract_all_from_directory(self, tmp_path):
        """Extract all workflows from a directory."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'")

        # Create multiple files
        (tmp_path / "ci.py").write_text('''
from wetwire_github.workflow import Workflow
ci = Workflow(name="CI")
''')
        (tmp_path / "deploy.py").write_text('''
from wetwire_github.workflow import Workflow
deploy = Workflow(name="Deploy")
''')

        sys.path.insert(0, str(tmp_path))
        try:
            # Extract from individual files
            ci_workflows = extract_workflows(str(tmp_path / "ci.py"))
            deploy_workflows = extract_workflows(str(tmp_path / "deploy.py"))

            assert len(ci_workflows) >= 1
            assert len(deploy_workflows) >= 1
        finally:
            sys.path.remove(str(tmp_path))
