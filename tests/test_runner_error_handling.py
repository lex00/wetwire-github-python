"""Tests for runner error handling and structured logging."""

import logging
import sys

import pytest

from wetwire_github.runner import (
    extract_jobs,
    extract_workflows,
)
from wetwire_github.runner.exceptions import (
    WorkflowImportError,
    WorkflowLoadError,
    WorkflowRuntimeError,
    WorkflowSyntaxError,
)


class TestWorkflowLoadError:
    """Tests for the base WorkflowLoadError exception."""

    def test_base_error_message(self):
        """WorkflowLoadError can be raised with a message."""
        error = WorkflowLoadError("test error")
        assert str(error) == "test error"

    def test_base_error_with_file_path(self):
        """WorkflowLoadError stores file path context."""
        error = WorkflowLoadError("test error", file_path="/path/to/file.py")
        assert error.file_path == "/path/to/file.py"
        assert "file.py" in str(error)

    def test_base_error_with_module_name(self):
        """WorkflowLoadError stores module name context."""
        error = WorkflowLoadError("test error", module_name="mymodule")
        assert error.module_name == "mymodule"


class TestWorkflowSyntaxError:
    """Tests for WorkflowSyntaxError exception."""

    def test_syntax_error_message(self):
        """WorkflowSyntaxError provides helpful message."""
        error = WorkflowSyntaxError(
            "invalid syntax",
            file_path="/path/to/file.py",
            line_number=10,
            offset=5,
        )
        assert error.file_path == "/path/to/file.py"
        assert error.line_number == 10
        assert error.offset == 5
        assert "syntax" in str(error).lower()

    def test_syntax_error_inherits_from_base(self):
        """WorkflowSyntaxError inherits from WorkflowLoadError."""
        error = WorkflowSyntaxError("invalid syntax")
        assert isinstance(error, WorkflowLoadError)


class TestWorkflowImportError:
    """Tests for WorkflowImportError exception."""

    def test_import_error_message(self):
        """WorkflowImportError provides helpful message."""
        error = WorkflowImportError(
            "No module named 'nonexistent'",
            file_path="/path/to/file.py",
            module_name="nonexistent",
        )
        assert error.file_path == "/path/to/file.py"
        assert error.module_name == "nonexistent"
        assert "import" in str(error).lower() or "module" in str(error).lower()

    def test_import_error_inherits_from_base(self):
        """WorkflowImportError inherits from WorkflowLoadError."""
        error = WorkflowImportError("import failed")
        assert isinstance(error, WorkflowLoadError)


class TestWorkflowRuntimeError:
    """Tests for WorkflowRuntimeError exception."""

    def test_runtime_error_message(self):
        """WorkflowRuntimeError provides helpful message."""
        error = WorkflowRuntimeError(
            "NameError: name 'undefined' is not defined",
            file_path="/path/to/file.py",
            module_name="mymodule",
        )
        assert error.file_path == "/path/to/file.py"
        assert error.module_name == "mymodule"

    def test_runtime_error_with_original_exception(self):
        """WorkflowRuntimeError can store original exception."""
        original = NameError("undefined variable")
        error = WorkflowRuntimeError(
            "runtime error",
            original_exception=original,
        )
        assert error.original_exception is original

    def test_runtime_error_inherits_from_base(self):
        """WorkflowRuntimeError inherits from WorkflowLoadError."""
        error = WorkflowRuntimeError("runtime failed")
        assert isinstance(error, WorkflowLoadError)


class TestExtractWorkflowsErrorHandling:
    """Tests for extract_workflows error handling."""

    def test_syntax_error_raises_workflow_syntax_error(self, tmp_path):
        """extract_workflows raises WorkflowSyntaxError for syntax errors."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'")
        (tmp_path / "broken.py").write_text("""
# Invalid Python syntax
def foo(
    # Missing closing parenthesis
""")
        sys.path.insert(0, str(tmp_path))
        try:
            with pytest.raises(WorkflowSyntaxError) as exc_info:
                extract_workflows(str(tmp_path / "broken.py"))
            assert "broken.py" in str(exc_info.value) or exc_info.value.file_path
        finally:
            sys.path.remove(str(tmp_path))

    def test_import_error_raises_workflow_import_error(self, tmp_path):
        """extract_workflows raises WorkflowImportError for import errors."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'")
        (tmp_path / "badimport.py").write_text("""
from nonexistent_module_xyz123 import something
""")
        sys.path.insert(0, str(tmp_path))
        try:
            with pytest.raises(WorkflowImportError) as exc_info:
                extract_workflows(str(tmp_path / "badimport.py"))
            assert exc_info.value.file_path is not None
        finally:
            sys.path.remove(str(tmp_path))

    def test_runtime_error_raises_workflow_runtime_error(self, tmp_path):
        """extract_workflows raises WorkflowRuntimeError for runtime errors."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'")
        (tmp_path / "runtime_fail.py").write_text("""
from wetwire_github.workflow import Workflow

# This will raise a runtime error at import time
undefined_variable + 1
""")
        sys.path.insert(0, str(tmp_path))
        try:
            with pytest.raises(WorkflowRuntimeError) as exc_info:
                extract_workflows(str(tmp_path / "runtime_fail.py"))
            assert exc_info.value.original_exception is not None
        finally:
            sys.path.remove(str(tmp_path))


class TestExtractJobsErrorHandling:
    """Tests for extract_jobs error handling."""

    def test_syntax_error_raises_workflow_syntax_error(self, tmp_path):
        """extract_jobs raises WorkflowSyntaxError for syntax errors."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'")
        (tmp_path / "broken_jobs.py").write_text("""
# Invalid Python syntax
class BadClass:
    def method(self
        # Missing closing parenthesis
""")
        sys.path.insert(0, str(tmp_path))
        try:
            with pytest.raises(WorkflowSyntaxError) as exc_info:
                extract_jobs(str(tmp_path / "broken_jobs.py"))
            assert exc_info.value.file_path is not None
        finally:
            sys.path.remove(str(tmp_path))


class TestErrorLogging:
    """Tests for structured error logging."""

    def test_syntax_error_logged(self, tmp_path, caplog):
        """Syntax errors are logged with context."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'")
        (tmp_path / "syntax_log.py").write_text("""
# Bad syntax
if True
    pass
""")
        sys.path.insert(0, str(tmp_path))
        try:
            with caplog.at_level(logging.ERROR, logger="wetwire_github.runner"):
                with pytest.raises(WorkflowSyntaxError):
                    extract_workflows(str(tmp_path / "syntax_log.py"))
            # Check that error was logged
            assert any("syntax" in record.message.lower() for record in caplog.records)
        finally:
            sys.path.remove(str(tmp_path))

    def test_import_error_logged(self, tmp_path, caplog):
        """Import errors are logged with context."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'")
        (tmp_path / "import_log.py").write_text("""
import nonexistent_module_abc999
""")
        sys.path.insert(0, str(tmp_path))
        try:
            with caplog.at_level(logging.ERROR, logger="wetwire_github.runner"):
                with pytest.raises(WorkflowImportError):
                    extract_workflows(str(tmp_path / "import_log.py"))
            # Check that error was logged
            assert any("import" in record.message.lower() or "module" in record.message.lower() for record in caplog.records)
        finally:
            sys.path.remove(str(tmp_path))


class TestErrorMessageFormat:
    """Tests for error message formatting."""

    def test_syntax_error_includes_line_info(self, tmp_path):
        """Syntax errors include line number information."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'")
        (tmp_path / "line_info.py").write_text("""# Line 1
# Line 2
def bad_function(
    # Missing close
""")
        sys.path.insert(0, str(tmp_path))
        try:
            with pytest.raises(WorkflowSyntaxError) as exc_info:
                extract_workflows(str(tmp_path / "line_info.py"))
            # Error should have line number
            assert exc_info.value.line_number is not None
            assert exc_info.value.line_number > 0
        finally:
            sys.path.remove(str(tmp_path))

    def test_error_message_includes_file_path(self, tmp_path):
        """All errors include file path in message."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'")
        (tmp_path / "path_test.py").write_text("""
import missing_lib_xyz
""")
        sys.path.insert(0, str(tmp_path))
        try:
            with pytest.raises(WorkflowImportError) as exc_info:
                extract_workflows(str(tmp_path / "path_test.py"))
            error_msg = str(exc_info.value)
            # File path should be in the error message
            assert "path_test.py" in error_msg or exc_info.value.file_path is not None
        finally:
            sys.path.remove(str(tmp_path))
