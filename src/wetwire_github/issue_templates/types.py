"""GitHub Issue Templates (Issue Forms) types.

Dataclasses for GitHub Issue Forms configuration files.
Based on the github-issue-forms schema.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Input:
    """Input form element for single-line text.

    Attributes:
        label: Short description of the expected input
        id: Unique identifier for the field
        description: Longer description or instructions
        placeholder: Placeholder text
        value: Pre-filled value
        required: Whether this field is required
    """

    label: str
    id: str
    description: str | None = None
    placeholder: str | None = None
    value: str | None = None
    required: bool | None = None

    @property
    def type(self) -> str:
        """Return the form element type."""
        return "input"


@dataclass
class Textarea:
    """Textarea form element for multi-line text.

    Attributes:
        label: Short description of the expected input
        id: Unique identifier for the field
        description: Longer description or instructions
        placeholder: Placeholder text
        value: Pre-filled value
        render: Language for syntax highlighting
        required: Whether this field is required
    """

    label: str
    id: str
    description: str | None = None
    placeholder: str | None = None
    value: str | None = None
    render: str | None = None
    required: bool | None = None

    @property
    def type(self) -> str:
        """Return the form element type."""
        return "textarea"


@dataclass
class Dropdown:
    """Dropdown form element for selection.

    Attributes:
        label: Short description of the expected selection
        id: Unique identifier for the field
        description: Longer description or instructions
        options: List of options to choose from
        multiple: Allow multiple selections
        default: Index of default selection (0-based)
        required: Whether this field is required
    """

    label: str
    id: str
    options: list[str] = field(default_factory=list)
    description: str | None = None
    multiple: bool | None = None
    default: int | None = None
    required: bool | None = None

    @property
    def type(self) -> str:
        """Return the form element type."""
        return "dropdown"


@dataclass
class CheckboxOption:
    """Option for a checkbox group.

    Attributes:
        label: Label for the checkbox option
        required: Whether this option must be checked
    """

    label: str
    required: bool | None = None


@dataclass
class Checkboxes:
    """Checkboxes form element for multiple selections.

    Attributes:
        label: Short description of the checkbox group
        id: Unique identifier for the field
        options: List of checkbox options
        description: Longer description or instructions
    """

    label: str
    id: str
    options: list[CheckboxOption] = field(default_factory=list)
    description: str | None = None

    @property
    def type(self) -> str:
        """Return the form element type."""
        return "checkboxes"


@dataclass
class Markdown:
    """Markdown form element for static content.

    Attributes:
        value: Markdown content to display
    """

    value: str

    @property
    def type(self) -> str:
        """Return the form element type."""
        return "markdown"


# Union type for all form elements
FormElement = Input | Textarea | Dropdown | Checkboxes | Markdown


@dataclass
class IssueTemplate:
    """GitHub Issue Form template.

    Attributes:
        name: Name shown in template chooser
        description: Description shown in template chooser
        body: List of form elements
        title: Pre-filled issue title
        labels: Labels to add to issues
        assignees: Default assignees for issues
    """

    name: str
    description: str
    body: list[FormElement] = field(default_factory=list)
    title: str | None = None
    labels: list[str] = field(default_factory=list)
    assignees: list[str] = field(default_factory=list)


def _serialize_form_element(element: FormElement) -> dict[str, Any]:
    """Serialize a form element to a dictionary.

    This is used by the serialization system to convert form elements
    to their YAML representation with the correct structure.
    """
    result: dict[str, Any] = {"type": element.type}

    if isinstance(element, Markdown):
        result["attributes"] = {"value": element.value}
    elif isinstance(element, Input):
        attrs: dict[str, Any] = {"label": element.label}
        if element.description:
            attrs["description"] = element.description
        if element.placeholder:
            attrs["placeholder"] = element.placeholder
        if element.value:
            attrs["value"] = element.value
        result["attributes"] = attrs
        result["id"] = element.id
        if element.required is not None:
            result["validations"] = {"required": element.required}
    elif isinstance(element, Textarea):
        attrs = {"label": element.label}
        if element.description:
            attrs["description"] = element.description
        if element.placeholder:
            attrs["placeholder"] = element.placeholder
        if element.value:
            attrs["value"] = element.value
        if element.render:
            attrs["render"] = element.render
        result["attributes"] = attrs
        result["id"] = element.id
        if element.required is not None:
            result["validations"] = {"required": element.required}
    elif isinstance(element, Dropdown):
        attrs = {"label": element.label, "options": element.options}
        if element.description:
            attrs["description"] = element.description
        if element.multiple is not None:
            attrs["multiple"] = element.multiple
        if element.default is not None:
            attrs["default"] = element.default
        result["attributes"] = attrs
        result["id"] = element.id
        if element.required is not None:
            result["validations"] = {"required": element.required}
    elif isinstance(element, Checkboxes):
        options = []
        for opt in element.options:
            opt_dict: dict[str, Any] = {"label": opt.label}
            if opt.required is not None:
                opt_dict["required"] = opt.required
            options.append(opt_dict)
        attrs = {"label": element.label, "options": options}
        if element.description:
            attrs["description"] = element.description
        result["attributes"] = attrs
        result["id"] = element.id

    return result
