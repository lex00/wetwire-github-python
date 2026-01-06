"""Tests for action code generation."""

import sys
from pathlib import Path

# Add codegen to path
sys.path.insert(0, str(Path(__file__).parent.parent / "codegen"))

from generate import (
    ActionTemplate,
    generate_action_function,
    generate_action_module,
    generate_all_actions,
    snake_case,
    to_python_identifier,
)
from parse import ActionInput, ActionOutput, ActionSchema


class TestSnakeCase:
    """Tests for snake_case conversion."""

    def test_simple_kebab(self):
        """Convert kebab-case to snake_case."""
        assert snake_case("fetch-depth") == "fetch_depth"

    def test_simple_camel(self):
        """Convert camelCase to snake_case."""
        assert snake_case("fetchDepth") == "fetch_depth"

    def test_already_snake(self):
        """Leave snake_case unchanged."""
        assert snake_case("fetch_depth") == "fetch_depth"

    def test_with_numbers(self):
        """Handle strings with numbers."""
        assert snake_case("setup-python3") == "setup_python3"

    def test_uppercase(self):
        """Convert UPPERCASE to lowercase."""
        assert snake_case("GITHUB_TOKEN") == "github_token"


class TestToPythonIdentifier:
    """Tests for converting names to valid Python identifiers."""

    def test_simple(self):
        """Simple name conversion."""
        assert to_python_identifier("token") == "token"

    def test_kebab_case(self):
        """Convert kebab-case."""
        assert to_python_identifier("fetch-depth") == "fetch_depth"

    def test_reserved_keyword(self):
        """Handle Python reserved keywords."""
        assert to_python_identifier("with") == "with_"
        assert to_python_identifier("if") == "if_"
        assert to_python_identifier("from") == "from_"

    def test_starts_with_digit(self):
        """Handle names starting with digits."""
        assert to_python_identifier("3scale") == "_3scale"


class TestActionTemplate:
    """Tests for ActionTemplate dataclass."""

    def test_action_template(self):
        """ActionTemplate stores template info."""
        template = ActionTemplate(
            function_name="checkout",
            action_ref="actions/checkout@v4",
            description="Checkout a repository",
            inputs=[
                {"name": "repository", "python_name": "repository", "required": False},
                {"name": "ref", "python_name": "ref", "required": False},
            ],
            outputs=[{"name": "ref", "description": "The ref that was checked out"}],
        )
        assert template.function_name == "checkout"
        assert template.action_ref == "actions/checkout@v4"
        assert len(template.inputs) == 2


class TestGenerateActionFunction:
    """Tests for generate_action_function."""

    def test_generate_simple_function(self):
        """Generate function for simple action."""
        schema = ActionSchema(
            name="Simple Action",
            description="A simple action",
            author="Test",
            inputs=[
                ActionInput("token", "Auth token", True, None),
            ],
            outputs=[],
        )

        code = generate_action_function(schema, "owner/simple-action", "v1")
        assert "def simple_action(" in code
        assert "token:" in code
        assert 'uses="owner/simple-action@v1"' in code

    def test_generate_function_with_optional_inputs(self):
        """Generate function with optional parameters."""
        schema = ActionSchema(
            name="Checkout",
            description="Checkout repo",
            author="GitHub",
            inputs=[
                ActionInput("repository", "Repository", False, "${{ github.repository }}"),
                ActionInput("ref", "The ref", False, None),
            ],
            outputs=[],
        )

        code = generate_action_function(schema, "actions/checkout", "v4")
        assert "repository: str | None = None" in code
        assert "ref: str | None = None" in code

    def test_generate_function_with_required_inputs(self):
        """Generate function with required parameters."""
        schema = ActionSchema(
            name="Required Action",
            description="Action with required input",
            author="Test",
            inputs=[
                ActionInput("api-key", "API key", True, None),
                ActionInput("optional-param", "Optional", False, "default"),
            ],
            outputs=[],
        )

        code = generate_action_function(schema, "owner/required-action", "v1")
        # Required params should come before optional
        assert "api_key: str," in code

    def test_generate_function_kebab_to_snake(self):
        """Convert kebab-case inputs to snake_case parameters."""
        schema = ActionSchema(
            name="Test",
            description="Test",
            author="Test",
            inputs=[
                ActionInput("fetch-depth", "Depth", False, "1"),
                ActionInput("sparse-checkout", "Sparse", False, None),
            ],
            outputs=[],
        )

        code = generate_action_function(schema, "actions/checkout", "v4")
        assert "fetch_depth:" in code
        assert "sparse_checkout:" in code
        # The with_ dict should use original names
        assert '"fetch-depth":' in code


class TestGenerateActionModule:
    """Tests for generate_action_module."""

    def test_generate_module(self):
        """Generate a complete action module."""
        schemas = [
            ActionSchema(
                name="Checkout",
                description="Checkout",
                author="GitHub",
                inputs=[ActionInput("ref", "Ref", False, None)],
                outputs=[ActionOutput("ref", "Checked out ref")],
            ),
        ]

        code = generate_action_module(schemas, {"Checkout": ("actions/checkout", "v4")})
        assert "from wetwire_github.workflow import Step" in code
        assert "def checkout(" in code
        assert "__all__" in code


class TestGenerateAllActions:
    """Tests for generate_all_actions."""

    def test_generate_all_returns_dict(self):
        """generate_all_actions returns dict of module name to code."""
        # This test uses mocked schemas
        schemas = {
            "checkout": ActionSchema(
                name="Checkout",
                description="Checkout a repository",
                author="GitHub",
                inputs=[ActionInput("ref", "The ref", False, None)],
                outputs=[],
            ),
        }
        action_refs = {
            "checkout": ("actions/checkout", "v4"),
        }

        result = generate_all_actions(schemas, action_refs)
        assert "checkout" in result
        assert "def checkout(" in result["checkout"]


class TestGeneratedCodeValidity:
    """Tests that generated code is valid Python."""

    def test_generated_code_compiles(self):
        """Generated code can be compiled."""
        schema = ActionSchema(
            name="Test Action",
            description="Test",
            author="Test",
            inputs=[
                ActionInput("param-one", "First param", True, None),
                ActionInput("param-two", "Second param", False, "default"),
            ],
            outputs=[],
        )

        code = generate_action_function(schema, "owner/test", "v1")
        # Should compile without errors
        compile(code, "<string>", "exec")

    def test_generated_module_compiles(self):
        """Generated module can be compiled."""
        schemas = [
            ActionSchema(
                name="Test",
                description="Test",
                author="Test",
                inputs=[ActionInput("param", "Param", False, None)],
                outputs=[],
            ),
        ]

        code = generate_action_module(schemas, {"Test": ("owner/test", "v1")})
        compile(code, "<string>", "exec")


class TestCompositeActionSupport:
    """Tests for composite action wrapper support."""

    def test_composite_action_wrapper(self):
        """Generate wrapper for composite action."""
        schema = ActionSchema(
            name="My Composite Action",
            description="A composite action",
            author="Me",
            inputs=[
                ActionInput("input1", "First input", True, None),
                ActionInput("input2", "Second input", False, "default"),
            ],
            outputs=[
                ActionOutput("output1", "First output"),
            ],
        )

        # Composite actions use local paths like ./.github/actions/my-action
        code = generate_action_function(schema, "./.github/actions/my-action", "")
        assert "def my_composite_action(" in code
        assert 'uses="./.github/actions/my-action"' in code
