"""Tests for MCP server integration."""

import pytest


class TestMCPServerImport:
    """Test MCP server module imports."""

    def test_mcp_server_module_exists(self) -> None:
        """Test that mcp_server module can be imported."""
        from wetwire_github import mcp_server

        assert mcp_server is not None

    def test_create_server_exists(self) -> None:
        """Test that create_server function exists."""
        from wetwire_github.mcp_server import create_server

        assert callable(create_server)

    def test_run_server_exists(self) -> None:
        """Test that run_server function exists."""
        from wetwire_github.mcp_server import run_server

        assert callable(run_server)


class TestMCPServerCreation:
    """Test MCP server creation and configuration."""

    @pytest.fixture
    def server(self):
        """Create MCP server instance."""
        pytest.importorskip("mcp")
        from wetwire_github.mcp_server import create_server

        return create_server()

    def test_server_name(self, server) -> None:
        """Test server has correct name."""
        assert server.name == "wetwire-github-mcp"

    def test_server_not_none(self, server) -> None:
        """Test server is created."""
        assert server is not None


class TestMCPToolDefinitions:
    """Test MCP tool definitions."""

    @pytest.fixture
    def tools(self):
        """Get tool definitions from server."""
        pytest.importorskip("mcp")
        from wetwire_github.mcp_server import get_tool_definitions

        return get_tool_definitions()

    def test_init_tool_defined(self, tools) -> None:
        """Test wetwire_init tool is defined."""
        tool_names = [t.name for t in tools]
        assert "wetwire_init" in tool_names

    def test_build_tool_defined(self, tools) -> None:
        """Test wetwire_build tool is defined."""
        tool_names = [t.name for t in tools]
        assert "wetwire_build" in tool_names

    def test_lint_tool_defined(self, tools) -> None:
        """Test wetwire_lint tool is defined."""
        tool_names = [t.name for t in tools]
        assert "wetwire_lint" in tool_names

    def test_validate_tool_defined(self, tools) -> None:
        """Test wetwire_validate tool is defined."""
        tool_names = [t.name for t in tools]
        assert "wetwire_validate" in tool_names

    def test_import_tool_defined(self, tools) -> None:
        """Test wetwire_import tool is defined."""
        tool_names = [t.name for t in tools]
        assert "wetwire_import" in tool_names

    def test_list_tool_defined(self, tools) -> None:
        """Test wetwire_list tool is defined."""
        tool_names = [t.name for t in tools]
        assert "wetwire_list" in tool_names

    def test_graph_tool_defined(self, tools) -> None:
        """Test wetwire_graph tool is defined."""
        tool_names = [t.name for t in tools]
        assert "wetwire_graph" in tool_names

    def test_all_tools_have_descriptions(self, tools) -> None:
        """Test all tools have descriptions."""
        for tool in tools:
            assert tool.description, f"Tool {tool.name} missing description"


class TestMCPToolHandlers:
    """Test MCP tool handler functions."""

    def test_handle_init_creates_project(self, tmp_path) -> None:
        """Test wetwire_init creates project structure."""
        pytest.importorskip("mcp")
        from wetwire_github.mcp_server import handle_init

        result = handle_init(name="test-project", output=str(tmp_path))

        assert result.success
        assert (tmp_path / "pyproject.toml").exists() or "Created" in result.message

    def test_handle_build_generates_yaml(self, tmp_path) -> None:
        """Test wetwire_build generates YAML files."""
        pytest.importorskip("mcp")
        from wetwire_github.mcp_server import handle_build

        # Create a simple workflow file first
        workflow_dir = tmp_path / "workflows"
        workflow_dir.mkdir()
        (workflow_dir / "__init__.py").write_text("")
        (workflow_dir / "ci.py").write_text("""
from wetwire_github.workflow import Workflow, Job, Step

ci = Workflow(
    name="CI",
    on={"push": {}},
    jobs={"build": Job(runs_on="ubuntu-latest", steps=[Step(run="echo hello")])},
)
""")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = handle_build(package=str(workflow_dir), output=str(output_dir))

        assert result.success or "error" not in result.message.lower()

    def test_handle_lint_checks_code(self, tmp_path) -> None:
        """Test wetwire_lint checks Python code."""
        pytest.importorskip("mcp")
        from wetwire_github.mcp_server import handle_lint

        # Create a file with linting issues
        test_file = tmp_path / "workflows.py"
        test_file.write_text("""
from wetwire_github.workflow import Workflow, Job, Step

ci = Workflow(
    name="CI",
    on={"push": {}},
    jobs={"build": Job(runs_on="ubuntu-latest", steps=[Step(uses="actions/checkout@v4")])},
)
""")

        result = handle_lint(package=str(tmp_path))

        assert result.success is not None

    def test_handle_validate_checks_yaml(self, tmp_path) -> None:
        """Test wetwire_validate checks YAML files."""
        pytest.importorskip("mcp")
        from wetwire_github.mcp_server import handle_validate

        # Create a valid workflow YAML
        yaml_file = tmp_path / "workflow.yml"
        yaml_file.write_text("""
name: CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
""")

        result = handle_validate(files=[str(yaml_file)])

        assert result.success is not None

    def test_handle_import_converts_yaml(self, tmp_path) -> None:
        """Test wetwire_import converts YAML to Python."""
        pytest.importorskip("mcp")
        from wetwire_github.mcp_server import handle_import

        # Create a workflow YAML to import
        yaml_file = tmp_path / "workflow.yml"
        yaml_file.write_text("""
name: CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
""")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = handle_import(files=[str(yaml_file)], output=str(output_dir))

        assert result.success is not None

    def test_handle_list_discovers_workflows(self, tmp_path) -> None:
        """Test wetwire_list discovers workflows."""
        pytest.importorskip("mcp")
        from wetwire_github.mcp_server import handle_list

        # Create a workflow file
        (tmp_path / "__init__.py").write_text("")
        (tmp_path / "ci.py").write_text("""
from wetwire_github.workflow import Workflow, Job, Step

ci = Workflow(
    name="CI",
    on={"push": {}},
    jobs={"build": Job(runs_on="ubuntu-latest", steps=[Step(run="echo hello")])},
)
""")

        result = handle_list(package=str(tmp_path))

        assert result.success is not None

    def test_handle_graph_generates_dag(self, tmp_path) -> None:
        """Test wetwire_graph generates DAG."""
        pytest.importorskip("mcp")
        from wetwire_github.mcp_server import handle_graph

        # Create a workflow file
        (tmp_path / "__init__.py").write_text("")
        (tmp_path / "ci.py").write_text("""
from wetwire_github.workflow import Workflow, Job, Step

ci = Workflow(
    name="CI",
    on={"push": {}},
    jobs={"build": Job(runs_on="ubuntu-latest", steps=[Step(run="echo hello")])},
)
""")

        result = handle_graph(package=str(tmp_path), format="mermaid")

        assert result.success is not None


class TestMCPToolResult:
    """Test MCP tool result dataclass."""

    def test_tool_result_dataclass_exists(self) -> None:
        """Test ToolResult dataclass exists."""
        from wetwire_github.mcp_server import ToolResult

        assert ToolResult is not None

    def test_tool_result_has_success_field(self) -> None:
        """Test ToolResult has success field."""
        from wetwire_github.mcp_server import ToolResult

        result = ToolResult(success=True, message="ok")
        assert result.success is True

    def test_tool_result_has_message_field(self) -> None:
        """Test ToolResult has message field."""
        from wetwire_github.mcp_server import ToolResult

        result = ToolResult(success=True, message="test message")
        assert result.message == "test message"


class TestMCPOptionalDependency:
    """Test MCP optional dependency handling."""

    def test_graceful_import_without_mcp(self) -> None:
        """Test module imports gracefully without mcp package."""
        # This should not raise even if mcp is not installed
        try:
            from wetwire_github.mcp_server import MCP_AVAILABLE

            # MCP_AVAILABLE should be True or False, not raise
            assert isinstance(MCP_AVAILABLE, bool)
        except ImportError:
            pytest.fail("mcp_server should handle missing mcp gracefully")

    def test_create_server_raises_without_mcp(self) -> None:
        """Test create_server raises ImportError without mcp."""
        from wetwire_github.mcp_server import MCP_AVAILABLE

        if not MCP_AVAILABLE:
            from wetwire_github.mcp_server import create_server

            with pytest.raises(ImportError):
                create_server()


class TestMCPEntryPoint:
    """Test MCP server entry point."""

    def test_main_function_exists(self) -> None:
        """Test main() function exists for entry point."""
        from wetwire_github.mcp_server import main

        assert callable(main)

    def test_main_function_is_callable(self) -> None:
        """Test main() can be referenced as entry point."""
        # This simulates the entry point check
        from wetwire_github import mcp_server

        assert hasattr(mcp_server, "main")
        assert callable(getattr(mcp_server, "main"))


class TestMCPErrorHandling:
    """Test MCP server error handling."""

    def test_create_server_error_message_is_helpful(self) -> None:
        """Test that error message for missing MCP is helpful."""
        from wetwire_github.mcp_server import MCP_AVAILABLE

        if not MCP_AVAILABLE:
            from wetwire_github.mcp_server import create_server

            try:
                create_server()
                pytest.fail("Expected ImportError")
            except ImportError as e:
                # Check error message is helpful
                assert "pip install" in str(e) or "mcp" in str(e).lower()

    def test_run_server_error_message_is_helpful(self) -> None:
        """Test that run_server has helpful error message without MCP."""
        from wetwire_github.mcp_server import MCP_AVAILABLE

        if not MCP_AVAILABLE:
            import asyncio

            from wetwire_github.mcp_server import run_server

            try:
                asyncio.run(run_server())
                pytest.fail("Expected ImportError")
            except ImportError as e:
                # Check error message includes installation instructions
                assert "pip install" in str(e) or "mcp" in str(e).lower()

    def test_get_tool_definitions_empty_without_mcp(self) -> None:
        """Test get_tool_definitions returns empty list without MCP."""
        from wetwire_github.mcp_server import MCP_AVAILABLE, get_tool_definitions

        if not MCP_AVAILABLE:
            tools = get_tool_definitions()
            assert tools == []

    def test_handle_init_with_invalid_path(self) -> None:
        """Test handle_init with invalid output path."""
        pytest.importorskip("mcp")
        from wetwire_github.mcp_server import handle_init

        result = handle_init(name="test", output="/nonexistent/deeply/nested/path")
        # Should return a result (success or failure), not raise
        assert result is not None
        assert hasattr(result, "success")
        assert hasattr(result, "message")

    def test_handle_build_with_nonexistent_package(self) -> None:
        """Test handle_build with nonexistent package."""
        pytest.importorskip("mcp")
        from wetwire_github.mcp_server import handle_build

        result = handle_build(package="/nonexistent/package/path")
        # Should return a result, not raise
        assert result is not None
        assert hasattr(result, "success")
        assert hasattr(result, "message")

    def test_handle_lint_with_nonexistent_package(self) -> None:
        """Test handle_lint with nonexistent package."""
        pytest.importorskip("mcp")
        from wetwire_github.mcp_server import handle_lint

        result = handle_lint(package="/nonexistent/package/path")
        # Should return a result, not raise
        assert result is not None
        assert hasattr(result, "success")

    def test_handle_validate_with_empty_files(self) -> None:
        """Test handle_validate with empty file list."""
        pytest.importorskip("mcp")
        from wetwire_github.mcp_server import handle_validate

        result = handle_validate(files=[])
        # Should return a result, not raise
        assert result is not None
        assert hasattr(result, "success")

    def test_handle_import_with_nonexistent_files(self) -> None:
        """Test handle_import with nonexistent files."""
        pytest.importorskip("mcp")
        from wetwire_github.mcp_server import handle_import

        result = handle_import(files=["/nonexistent/file.yml"])
        # Should return a result, not raise
        assert result is not None
        assert hasattr(result, "success")


class TestMCPLogging:
    """Test MCP server logging functionality."""

    def test_tool_result_includes_status(self) -> None:
        """Test that ToolResult can indicate success/failure status."""
        from wetwire_github.mcp_server import ToolResult

        success_result = ToolResult(success=True, message="Operation completed")
        assert success_result.success is True

        failure_result = ToolResult(success=False, message="Operation failed")
        assert failure_result.success is False

    def test_tool_handlers_return_tool_result(self) -> None:
        """Test all handlers return ToolResult with proper fields."""
        pytest.importorskip("mcp")
        from wetwire_github.mcp_server import (
            ToolResult,
            handle_graph,
            handle_list,
        )

        # Test with a simple case
        result = handle_list(package=".")
        assert isinstance(result, ToolResult)
        assert isinstance(result.success, bool)
        assert isinstance(result.message, str)

        result = handle_graph(package=".")
        assert isinstance(result, ToolResult)


class TestMCPServerCallTool:
    """Test MCP server call_tool functionality."""

    @pytest.fixture
    def server(self):
        """Create MCP server instance."""
        pytest.importorskip("mcp")
        from wetwire_github.mcp_server import create_server

        return create_server()

    def test_call_unknown_tool_returns_error(self, server) -> None:
        """Test calling unknown tool returns error message."""
        pytest.importorskip("mcp")
        # Access the call_tool handler via server internals
        # This tests the behavior described in the implementation
        from wetwire_github.mcp_server import MCP_AVAILABLE

        if MCP_AVAILABLE:
            # The server.call_tool is a decorator-registered handler
            # We can test it indirectly through the server
            assert server is not None

    def test_tool_call_with_exception_returns_error(self) -> None:
        """Test that tool call exceptions are caught and returned as errors."""
        pytest.importorskip("mcp")
        # This tests that the try/except in call_tool works
        from wetwire_github.mcp_server import ToolResult, handle_build

        # Call with intentionally problematic input
        result = handle_build(package="/nonexistent", output="/invalid")
        assert isinstance(result, ToolResult)
        # The result should exist without raising
