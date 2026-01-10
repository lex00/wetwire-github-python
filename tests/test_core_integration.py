"""Tests for wetwire-core integration module."""



class TestToolDefinitions:
    """Tests for RunnerAgent tool definitions."""

    def test_get_tool_definitions_returns_list(self):
        """Tool definitions returns a list of tool specs."""
        from wetwire_github.core_integration import get_tool_definitions

        tools = get_tool_definitions()
        assert isinstance(tools, list)
        assert len(tools) > 0

    def test_build_workflow_tool_defined(self):
        """Build workflow tool is defined."""
        from wetwire_github.core_integration import get_tool_definitions

        tools = get_tool_definitions()
        tool_names = [t["name"] for t in tools]
        assert "build_workflow" in tool_names

    def test_validate_workflow_tool_defined(self):
        """Validate workflow tool is defined."""
        from wetwire_github.core_integration import get_tool_definitions

        tools = get_tool_definitions()
        tool_names = [t["name"] for t in tools]
        assert "validate_workflow" in tool_names

    def test_lint_workflow_tool_defined(self):
        """Lint workflow tool is defined."""
        from wetwire_github.core_integration import get_tool_definitions

        tools = get_tool_definitions()
        tool_names = [t["name"] for t in tools]
        assert "lint_workflow" in tool_names

    def test_list_workflows_tool_defined(self):
        """List workflows tool is defined."""
        from wetwire_github.core_integration import get_tool_definitions

        tools = get_tool_definitions()
        tool_names = [t["name"] for t in tools]
        assert "list_workflows" in tool_names

    def test_tool_has_required_fields(self):
        """Each tool has required fields: name, description, parameters."""
        from wetwire_github.core_integration import get_tool_definitions

        tools = get_tool_definitions()
        for tool in tools:
            assert "name" in tool, f"Tool missing name: {tool}"
            assert "description" in tool, f"Tool missing description: {tool}"
            assert "parameters" in tool, f"Tool missing parameters: {tool}"


class TestToolHandlers:
    """Tests for tool handler implementations."""

    def test_handle_tool_call_exists(self):
        """Handle tool call function exists."""
        from wetwire_github.core_integration import handle_tool_call

        assert callable(handle_tool_call)

    def test_handle_build_workflow(self, tmp_path):
        """Build workflow tool handler works."""
        from wetwire_github.core_integration import handle_tool_call

        # Create a test workflow file
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        (pkg_dir / "ci.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step, PushTrigger, Triggers

ci = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger()),
    jobs={
        "build": Job(runs_on="ubuntu-latest", steps=[Step(run="make build")]),
    },
)
''')

        output_dir = tmp_path / "output"

        result = handle_tool_call(
            "build_workflow",
            {"package_path": str(pkg_dir), "output_dir": str(output_dir)},
        )

        assert result["success"] is True
        assert "files" in result

    def test_handle_validate_workflow(self, tmp_path):
        """Validate workflow tool handler works."""
        from wetwire_github.core_integration import handle_tool_call

        # Create a valid workflow file
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("""
name: Test
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo test
""")

        result = handle_tool_call(
            "validate_workflow",
            {"file_paths": [str(yaml_file)]},
        )

        # Should return result (success depends on actionlint availability)
        assert "success" in result

    def test_handle_lint_workflow(self, tmp_path):
        """Lint workflow tool handler works."""
        from wetwire_github.core_integration import handle_tool_call

        # Create a test workflow file
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        (pkg_dir / "ci.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step, PushTrigger, Triggers

ci = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger()),
    jobs={
        "build": Job(runs_on="ubuntu-latest", steps=[Step(run="make build")]),
    },
)
''')

        result = handle_tool_call(
            "lint_workflow",
            {"package_path": str(pkg_dir)},
        )

        assert "success" in result

    def test_handle_list_workflows(self, tmp_path):
        """List workflows tool handler works."""
        from wetwire_github.core_integration import handle_tool_call

        # Create a test workflow file
        pkg_dir = tmp_path / "workflows"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        (pkg_dir / "ci.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step, PushTrigger, Triggers

ci = Workflow(
    name="CI",
    on=Triggers(push=PushTrigger()),
    jobs={
        "build": Job(runs_on="ubuntu-latest", steps=[Step(run="make build")]),
    },
)
''')

        result = handle_tool_call(
            "list_workflows",
            {"package_path": str(pkg_dir)},
        )

        assert result["success"] is True
        assert "workflows" in result

    def test_handle_unknown_tool(self):
        """Unknown tool returns error."""
        from wetwire_github.core_integration import handle_tool_call

        result = handle_tool_call("unknown_tool", {})

        assert result["success"] is False
        assert "error" in result


class TestStreamHandler:
    """Tests for stream handler support."""

    def test_create_stream_handler(self):
        """Stream handler can be created."""
        from wetwire_github.core_integration import create_stream_handler

        handler = create_stream_handler()
        assert handler is not None

    def test_stream_handler_has_write_method(self):
        """Stream handler has write method."""
        from wetwire_github.core_integration import create_stream_handler

        handler = create_stream_handler()
        assert hasattr(handler, "write")
        assert callable(handler.write)

    def test_stream_handler_captures_output(self):
        """Stream handler captures written output."""
        from wetwire_github.core_integration import create_stream_handler

        handler = create_stream_handler()
        handler.write("test output")

        # Should be able to get captured content
        assert handler.get_output() == "test output"


class TestSessionManagement:
    """Tests for session result writing."""

    def test_create_session(self):
        """Session can be created."""
        from wetwire_github.core_integration import create_session

        session = create_session()
        assert session is not None
        assert "session_id" in session

    def test_session_has_id(self):
        """Session has unique ID."""
        from wetwire_github.core_integration import create_session

        session1 = create_session()
        session2 = create_session()
        assert session1["session_id"] != session2["session_id"]

    def test_write_session_result(self, tmp_path):
        """Session result can be written to file."""
        from wetwire_github.core_integration import create_session, write_session_result

        session = create_session()
        session["result"] = {"status": "success", "output": "test"}

        output_file = tmp_path / "session.json"
        write_session_result(session, str(output_file))

        assert output_file.exists()
        import json

        data = json.loads(output_file.read_text())
        assert data["session_id"] == session["session_id"]
        assert data["result"]["status"] == "success"


class TestScoringIntegration:
    """Tests for quality scoring integration."""

    def test_score_workflow_exists(self):
        """Score workflow function exists."""
        from wetwire_github.core_integration import score_workflow

        assert callable(score_workflow)

    def test_score_workflow_returns_score(self, tmp_path):
        """Score workflow returns a score object."""
        from wetwire_github.core_integration import score_workflow

        # Create a test workflow
        yaml_content = """
name: CI
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make build
"""
        yaml_file = tmp_path / "ci.yaml"
        yaml_file.write_text(yaml_content)

        score = score_workflow(str(yaml_file))

        assert "total_score" in score
        assert "details" in score
        assert isinstance(score["total_score"], (int, float))

    def test_score_workflow_checks_best_practices(self, tmp_path):
        """Score workflow checks for best practices."""
        from wetwire_github.core_integration import score_workflow

        # Create workflow without checkout step (common issue)
        yaml_content = """
name: CI
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: make build
"""
        yaml_file = tmp_path / "ci.yaml"
        yaml_file.write_text(yaml_content)

        score = score_workflow(str(yaml_file))

        # Score should reflect missing checkout
        assert "details" in score


class TestPersonaTesting:
    """Tests for agent testing with personas."""

    def test_get_available_personas(self):
        """Available personas can be retrieved."""
        from wetwire_github.core_integration import get_available_personas

        personas = get_available_personas()
        assert isinstance(personas, list)
        assert len(personas) > 0

    def test_reviewer_persona_exists(self):
        """Reviewer persona is available."""
        from wetwire_github.core_integration import get_available_personas

        personas = get_available_personas()
        persona_names = [p["name"] for p in personas]
        assert "reviewer" in persona_names

    def test_senior_dev_persona_exists(self):
        """Senior dev persona is available."""
        from wetwire_github.core_integration import get_available_personas

        personas = get_available_personas()
        persona_names = [p["name"] for p in personas]
        assert "senior-dev" in persona_names

    def test_expert_persona_exists(self):
        """Expert persona is available (spec-standard)."""
        from wetwire_github.core_integration import get_available_personas

        personas = get_available_personas()
        persona_names = [p["name"] for p in personas]
        assert "expert" in persona_names

    def test_terse_persona_exists(self):
        """Terse persona is available (spec-standard)."""
        from wetwire_github.core_integration import get_available_personas

        personas = get_available_personas()
        persona_names = [p["name"] for p in personas]
        assert "terse" in persona_names

    def test_verbose_persona_exists(self):
        """Verbose persona is available (spec-standard)."""
        from wetwire_github.core_integration import get_available_personas

        personas = get_available_personas()
        persona_names = [p["name"] for p in personas]
        assert "verbose" in persona_names

    def test_persona_has_required_fields(self):
        """Personas have required fields."""
        from wetwire_github.core_integration import get_available_personas

        personas = get_available_personas()
        for persona in personas:
            assert "name" in persona
            assert "description" in persona
            assert "criteria" in persona

    def test_run_persona_test(self, tmp_path):
        """Persona test can be run against workflow."""
        from wetwire_github.core_integration import run_persona_test

        # Create a test workflow
        yaml_content = """
name: CI
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make build
"""
        yaml_file = tmp_path / "ci.yaml"
        yaml_file.write_text(yaml_content)

        result = run_persona_test("reviewer", str(yaml_file))

        assert "passed" in result
        assert "feedback" in result
