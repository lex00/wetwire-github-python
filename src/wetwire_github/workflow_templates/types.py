"""Workflow template types.

Dataclasses for GitHub organization-level workflow templates.
Based on GitHub's workflow template format.
"""

from dataclasses import dataclass, field

from wetwire_github.workflow import Workflow


class TemplateCategory:
    """Predefined template categories for organization workflow templates."""

    CONTINUOUS_INTEGRATION = "Continuous Integration"
    DEPLOYMENT = "Deployment"
    TESTING = "Testing"
    CODE_QUALITY = "Code Quality"
    AUTOMATION = "Automation"
    SECURITY = "Security"


@dataclass
class TemplateConfig:
    """Template configuration for workflow-templates.properties file.

    Attributes:
        name: Display name for the template
        description: Description of the template
        icon: Icon name for the template (default: rocket)
        categories: List of categories for the template
    """

    name: str
    description: str
    icon: str = "rocket"
    categories: list[str] = field(default_factory=list)

    def to_properties(self) -> str:
        """Generate workflow-templates.properties format.

        Returns:
            Properties file content as a string
        """
        lines = []
        lines.append(f"name={self.name}")
        lines.append(f"description={self.description}")
        lines.append(f"iconName={self.icon}")

        if self.categories:
            categories_str = ",".join(self.categories)
            lines.append(f"categories={categories_str}")

        return "\n".join(lines)


@dataclass
class WorkflowTemplate:
    """GitHub organization workflow template.

    Workflow templates are stored in .github/workflow-templates/ directory
    in organization's .github repository. They appear when users create new
    workflows in repositories within the organization.

    Template variables like $default-branch and $protected-branches are
    replaced by GitHub when the template is used.

    Attributes:
        name: Filename for the template (e.g., "ci.yml")
        description: Description of the template
        workflow: The workflow definition
        icon: Icon name for the template (default: rocket)
        categories: List of categories for template discovery
    """

    name: str
    description: str
    workflow: Workflow
    icon: str = "rocket"
    categories: list[str] = field(default_factory=list)

    def to_properties(self) -> str:
        """Generate workflow-templates.properties format.

        Returns:
            Properties file content as a string
        """
        config = TemplateConfig(
            name=self.description,  # Use description as the display name
            description=self.description,
            icon=self.icon,
            categories=self.categories,
        )
        return config.to_properties()
