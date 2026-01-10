"""Custom exceptions for workflow loading and extraction.

Provides structured error types with context information for better
debugging and error handling in workflow processing.
"""


class WorkflowLoadError(Exception):
    """Base exception for workflow loading errors.

    All workflow-related exceptions inherit from this class, allowing
    callers to catch all workflow errors with a single except clause.

    Attributes:
        message: Human-readable error description
        file_path: Path to the file that caused the error
        module_name: Name of the module being loaded
    """

    def __init__(
        self,
        message: str,
        *,
        file_path: str | None = None,
        module_name: str | None = None,
    ) -> None:
        self.message = message
        self.file_path = file_path
        self.module_name = module_name
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format the error message with context."""
        parts = [self.message]
        if self.file_path:
            parts.append(f"file: {self.file_path}")
        if self.module_name:
            parts.append(f"module: {self.module_name}")
        return " | ".join(parts)


class WorkflowSyntaxError(WorkflowLoadError):
    """Exception raised when a workflow file has Python syntax errors.

    This exception is raised when Python's parser cannot parse the
    workflow file due to syntax issues.

    Attributes:
        line_number: Line number where the syntax error occurred
        offset: Character offset within the line
    """

    def __init__(
        self,
        message: str,
        *,
        file_path: str | None = None,
        module_name: str | None = None,
        line_number: int | None = None,
        offset: int | None = None,
    ) -> None:
        self.line_number = line_number
        self.offset = offset
        super().__init__(message, file_path=file_path, module_name=module_name)

    def _format_message(self) -> str:
        """Format the error message with syntax context."""
        parts = [f"Syntax error: {self.message}"]
        if self.file_path:
            location = self.file_path
            if self.line_number is not None:
                location += f":{self.line_number}"
                if self.offset is not None:
                    location += f":{self.offset}"
            parts.append(f"at {location}")
        if self.module_name:
            parts.append(f"module: {self.module_name}")
        return " | ".join(parts)


class WorkflowImportError(WorkflowLoadError):
    """Exception raised when a workflow file cannot import required modules.

    This exception is raised when the workflow file attempts to import
    a module that cannot be found or has its own import errors.

    Attributes:
        missing_module: Name of the module that could not be imported
    """

    def __init__(
        self,
        message: str,
        *,
        file_path: str | None = None,
        module_name: str | None = None,
        missing_module: str | None = None,
    ) -> None:
        self.missing_module = missing_module
        super().__init__(message, file_path=file_path, module_name=module_name)

    def _format_message(self) -> str:
        """Format the error message with import context."""
        parts = [f"Import error: {self.message}"]
        if self.file_path:
            parts.append(f"file: {self.file_path}")
        if self.module_name:
            parts.append(f"module: {self.module_name}")
        if self.missing_module:
            parts.append(f"missing: {self.missing_module}")
        return " | ".join(parts)


class WorkflowRuntimeError(WorkflowLoadError):
    """Exception raised when a workflow file encounters a runtime error.

    This exception is raised when the workflow file has valid syntax
    but raises an exception during execution (e.g., NameError,
    TypeError, etc.).

    Attributes:
        original_exception: The original exception that was raised
    """

    def __init__(
        self,
        message: str,
        *,
        file_path: str | None = None,
        module_name: str | None = None,
        original_exception: BaseException | None = None,
    ) -> None:
        self.original_exception = original_exception
        super().__init__(message, file_path=file_path, module_name=module_name)

    def _format_message(self) -> str:
        """Format the error message with runtime context."""
        parts = [f"Runtime error: {self.message}"]
        if self.file_path:
            parts.append(f"file: {self.file_path}")
        if self.module_name:
            parts.append(f"module: {self.module_name}")
        if self.original_exception:
            exc_type = type(self.original_exception).__name__
            parts.append(f"exception: {exc_type}")
        return " | ".join(parts)


__all__ = [
    "WorkflowLoadError",
    "WorkflowSyntaxError",
    "WorkflowImportError",
    "WorkflowRuntimeError",
]
