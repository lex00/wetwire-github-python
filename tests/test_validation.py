"""Tests for actionlint validation."""

from unittest.mock import MagicMock, patch

from wetwire_github.validation import (
    ValidationError,
    ValidationResult,
    is_actionlint_available,
    validate_workflow,
    validate_yaml,
)


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_validation_result_success(self):
        """ValidationResult stores success state."""
        result = ValidationResult(valid=True, errors=[])
        assert result.valid is True
        assert len(result.errors) == 0

    def test_validation_result_failure(self):
        """ValidationResult stores failure state with errors."""
        errors = [
            ValidationError(
                line=10,
                column=5,
                message="unknown property 'invalid'",
                severity="error",
            ),
        ]
        result = ValidationResult(valid=False, errors=errors)
        assert result.valid is False
        assert len(result.errors) == 1
        assert result.errors[0].line == 10


class TestValidationError:
    """Tests for ValidationError dataclass."""

    def test_validation_error(self):
        """ValidationError stores error details."""
        error = ValidationError(
            line=5,
            column=10,
            message="unexpected key",
            severity="error",
        )
        assert error.line == 5
        assert error.column == 10
        assert error.message == "unexpected key"
        assert error.severity == "error"

    def test_validation_error_with_rule(self):
        """ValidationError can include rule name."""
        error = ValidationError(
            line=1,
            column=1,
            message="test",
            severity="warning",
            rule="syntax-check",
        )
        assert error.rule == "syntax-check"


class TestIsActionlintAvailable:
    """Tests for is_actionlint_available function."""

    @patch("wetwire_github.validation.validation.subprocess.run")
    def test_actionlint_available(self, mock_run):
        """Detect when actionlint is available."""
        mock_run.return_value = MagicMock(returncode=0)
        assert is_actionlint_available() is True

    @patch("wetwire_github.validation.validation.subprocess.run")
    def test_actionlint_not_available(self, mock_run):
        """Detect when actionlint is not available."""
        mock_run.side_effect = FileNotFoundError()
        assert is_actionlint_available() is False


class TestValidateYaml:
    """Tests for validate_yaml function."""

    @patch("wetwire_github.validation.validation.subprocess.run")
    def test_validate_valid_yaml(self, mock_run):
        """Validate valid YAML returns success."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
            stderr="",
        )
        result = validate_yaml("name: CI\non: push\njobs: {}")
        assert result.valid is True
        assert len(result.errors) == 0

    @patch("wetwire_github.validation.validation.subprocess.run")
    def test_validate_invalid_yaml(self, mock_run):
        """Validate invalid YAML returns errors."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout='.github/workflows/test.yml:3:1: unexpected key "invalid" for "workflow" section [syntax-check]\n',
            stderr="",
        )
        result = validate_yaml("invalid: true")
        assert result.valid is False
        assert len(result.errors) == 1
        assert "unexpected key" in result.errors[0].message

    @patch("wetwire_github.validation.validation.subprocess.run")
    def test_validate_actionlint_not_found(self, mock_run):
        """Handle actionlint not being installed."""
        mock_run.side_effect = FileNotFoundError()
        result = validate_yaml("name: test")
        # Should return valid with a warning that actionlint isn't available
        assert result.valid is True
        assert len(result.errors) == 0
        assert result.actionlint_available is False

    @patch("wetwire_github.validation.validation.subprocess.run")
    def test_validate_parses_multiple_errors(self, mock_run):
        """Parse multiple errors from actionlint output."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout=""".github/workflows/test.yml:1:1: error one [rule-one]
.github/workflows/test.yml:5:10: error two [rule-two]
""",
            stderr="",
        )
        result = validate_yaml("test")
        assert result.valid is False
        assert len(result.errors) == 2
        assert result.errors[0].line == 1
        assert result.errors[1].line == 5


class TestValidateWorkflow:
    """Tests for validate_workflow function."""

    @patch("wetwire_github.validation.validation.subprocess.run")
    def test_validate_workflow_object(self, mock_run):
        """Validate a Workflow object."""
        from wetwire_github.workflow import Workflow

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
            stderr="",
        )
        workflow = Workflow(name="CI")
        result = validate_workflow(workflow)
        assert result.valid is True

    @patch("wetwire_github.validation.validation.subprocess.run")
    def test_validate_workflow_calls_serialize(self, mock_run):
        """validate_workflow serializes the workflow to YAML."""
        from wetwire_github.workflow import Workflow

        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        workflow = Workflow(name="Test Workflow")
        validate_workflow(workflow)

        # Check that subprocess.run was called with YAML content
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        # The YAML is passed via stdin
        assert call_args.kwargs.get("input") is not None


class TestActionlintOutputParsing:
    """Tests for parsing actionlint output format."""

    @patch("wetwire_github.validation.validation.subprocess.run")
    def test_parse_line_column(self, mock_run):
        """Parse line and column numbers from output."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout=".github/workflows/ci.yml:15:3: some error [rule]\n",
            stderr="",
        )
        result = validate_yaml("test")
        assert result.errors[0].line == 15
        assert result.errors[0].column == 3

    @patch("wetwire_github.validation.validation.subprocess.run")
    def test_parse_rule_name(self, mock_run):
        """Parse rule name from output."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout=".github/workflows/ci.yml:1:1: message [workflow-call]\n",
            stderr="",
        )
        result = validate_yaml("test")
        assert result.errors[0].rule == "workflow-call"
