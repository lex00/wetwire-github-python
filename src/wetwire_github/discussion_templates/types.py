"""GitHub Discussion Templates types.

Dataclasses and enums for GitHub Discussion Forms configuration files.
"""

from dataclasses import dataclass, field
from enum import Enum

from wetwire_github.issue_templates.types import FormElement


class DiscussionCategory(Enum):
    """Standard GitHub Discussion categories.

    Note: Repositories can have custom categories, but these are
    the common default categories.
    """

    ANNOUNCEMENTS = "announcements"
    GENERAL = "general"
    IDEAS = "ideas"
    POLLS = "polls"
    QA = "q-a"
    SHOW_AND_TELL = "show-and-tell"


@dataclass
class DiscussionTemplate:
    """GitHub Discussion Form template.

    Discussion templates are similar to issue templates but are used
    for GitHub Discussions. They share the same form elements.

    Attributes:
        title: Pre-filled discussion title
        labels: Labels to add to discussions
        body: List of form elements
    """

    title: str
    body: list[FormElement] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)
