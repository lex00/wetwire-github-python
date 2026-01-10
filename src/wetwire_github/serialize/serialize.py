"""Serialization functions for converting dataclasses to YAML."""

from dataclasses import fields, is_dataclass
from enum import Enum
from typing import Any

import yaml

# Fields that should NOT be converted to kebab-case
# These are GitHub Actions event names and other special fields
_PRESERVE_SNAKE_CASE = {
    "pull_request",
    "pull_request_target",
    "pull_request_review",
    "pull_request_review_comment",
    "workflow_dispatch",
    "workflow_call",
    "workflow_run",
    "repository_dispatch",
    "issue_comment",
    "project_card",
    "project_column",
    "discussion_comment",
    "deployment_status",
    "page_build",
    "check_run",
    "check_suite",
    "org_block",
    "team_add",
    "merge_group",
    "branch_protection_rule",
}


def _snake_to_kebab(name: str) -> str:
    """Convert snake_case to kebab-case."""
    return name.replace("_", "-")


def _convert_field_name(name: str) -> str:
    """Convert Python field name to YAML field name.

    Handles:
    - Reserved Python keywords (if_ -> if, with_ -> with)
    - Snake case to kebab case (working_directory -> working-directory)
    - Preserves certain field names that shouldn't be converted
    """
    # Handle reserved keywords
    if name.endswith("_") and name[:-1] in ("if", "with"):
        name = name[:-1]

    # Preserve certain field names
    if name in _PRESERVE_SNAKE_CASE:
        return name

    # Convert snake_case to kebab-case
    return _snake_to_kebab(name)


def _is_empty(value: Any) -> bool:
    """Check if a value should be considered empty and omitted."""
    if value is None:
        return True
    if isinstance(value, str) and value == "":
        return True
    if isinstance(value, list) and len(value) == 0:
        return True
    if isinstance(value, dict) and len(value) == 0:
        return True
    return False


def _serialize_value(value: Any) -> Any:
    """Recursively serialize a value."""
    if _is_job_output(value):
        # JobOutput serializes to just its value string
        return value.value
    elif _is_form_element(value):
        # Import here to avoid circular imports
        from wetwire_github.issue_templates.types import _serialize_form_element
        return _serialize_form_element(value)
    elif is_dataclass(value) and not isinstance(value, type):
        return to_dict(value)
    elif isinstance(value, Enum):
        return value.value
    elif isinstance(value, list):
        return [_serialize_value(item) for item in value]
    elif isinstance(value, dict):
        result = {}
        for k, v in value.items():
            serialized = _serialize_value(v)
            if not _is_empty(serialized):
                result[k] = serialized
        return result
    else:
        return value


def _is_job_output(obj: Any) -> bool:
    """Check if obj is a JobOutput dataclass instance."""
    return (
        is_dataclass(obj)
        and not isinstance(obj, type)
        and obj.__class__.__name__ == "JobOutput"
    )


def _is_matrix_class(obj: Any) -> bool:
    """Check if obj is a Matrix dataclass instance."""
    return (
        is_dataclass(obj)
        and not isinstance(obj, type)
        and obj.__class__.__name__ == "Matrix"
    )


def _is_form_element(obj: Any) -> bool:
    """Check if obj is a form element from issue_templates."""
    return (
        is_dataclass(obj)
        and not isinstance(obj, type)
        and obj.__class__.__name__ in ("Input", "Textarea", "Dropdown", "Checkboxes", "Markdown")
        and hasattr(obj, "type")
    )


def to_dict(obj: Any) -> dict[str, Any]:
    """Convert a dataclass instance to a dictionary.

    - Converts field names from snake_case to kebab-case
    - Handles reserved Python keywords (if_, with_)
    - Omits None, empty strings, empty lists, and empty dicts
    - Preserves False and 0 values
    - Flattens Matrix.values into the matrix dict directly
    """
    if not is_dataclass(obj) or isinstance(obj, type):
        raise TypeError(f"Expected dataclass instance, got {type(obj)}")

    result: dict[str, Any] = {}

    # Special handling for Matrix class - flatten values field
    if _is_matrix_class(obj):
        values = getattr(obj, "values", {})
        for k, v in values.items():
            result[k] = v
        # Handle include/exclude separately
        include = getattr(obj, "include", None)
        exclude = getattr(obj, "exclude", None)
        if include:
            result["include"] = include
        if exclude:
            result["exclude"] = exclude
        return result

    for field in fields(obj):
        value = getattr(obj, field.name)

        # Skip empty values (but preserve False and 0)
        if _is_empty(value):
            continue

        # Convert field name
        yaml_name = _convert_field_name(field.name)

        # Serialize the value
        serialized = _serialize_value(value)

        # Check again after serialization (nested empty dicts)
        # BUT: preserve empty dicts if the original value was a dataclass
        # This is important for triggers like PullRequestTrigger() which
        # serialize to {} but should still appear in the output
        is_dataclass_value = is_dataclass(value) and not isinstance(value, type)
        if not _is_empty(serialized) or (is_dataclass_value and serialized == {}):
            result[yaml_name] = serialized

    return result


class _LiteralScalarString(str):
    """String that should use literal block scalar style in YAML."""

    pass


def _literal_representer(dumper: yaml.Dumper, data: _LiteralScalarString) -> Any:
    """Custom representer for literal block scalar strings."""
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


def to_yaml(obj: Any) -> str:
    """Convert a dataclass instance to YAML string.

    - Uses literal block scalar (|) for multiline strings
    - Produces clean, readable YAML output
    """
    data = to_dict(obj)

    # Process multiline strings
    data = _process_multiline_strings(data)

    # Register custom representer
    yaml.add_representer(_LiteralScalarString, _literal_representer)

    return yaml.dump(
        data,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )


def _process_multiline_strings(data: Any) -> Any:
    """Recursively convert multiline strings to literal scalar style."""
    if isinstance(data, str):
        if "\n" in data:
            return _LiteralScalarString(data)
        return data
    elif isinstance(data, dict):
        return {k: _process_multiline_strings(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_process_multiline_strings(item) for item in data]
    else:
        return data
