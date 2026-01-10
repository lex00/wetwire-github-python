"""Linting rules for workflow declarations.

Each rule follows the WAG (Workflow Actions Guidelines) naming convention.

This module provides a modular organization of lint rules:
- action_rules: Rules for typed action wrappers (WAG001)
- expression_rules: Rules for expressions and secrets (WAG002, WAG003, WAG008)
- organization_rules: Rules for code organization (WAG004-WAG007)
- validation_rules: Rules for validation (WAG009, WAG010)
- pattern_rules: Rules for patterns and complexity (WAG011, WAG012, WAG016)
- extraction_rules: Rules for inline extraction (WAG013-WAG015)
- security_rules: Rules for security issues (WAG017, WAG018)
- reference_rules: Rules for reference tracking (WAG050-WAG053)
"""

from .action_rules import KNOWN_ACTIONS, WAG001TypedActionWrappers
from .base import BaseRule, LintError
from .expression_rules import (
    WAG002UseConditionBuilders,
    WAG003UseSecretsContext,
    WAG008HardcodedExpressions,
)
from .extraction_rules import (
    WAG013InlineEnvVariables,
    WAG014InlineMatrixConfig,
    WAG015InlineOutputs,
)
from .organization_rules import (
    WAG004UseMatrixBuilder,
    WAG005ExtractInlineEnvVariables,
    WAG006DuplicateWorkflowNames,
    WAG007FileTooLarge,
)
from .pattern_rules import (
    WAG011ComplexConditions,
    WAG012SuggestReusableWorkflows,
    WAG016SuggestReusableWorkflowExtraction,
)
from .reference_rules import (
    WAG050UnusedJobOutputs,
    WAG051CircularJobDependencies,
    WAG052OrphanSecrets,
    WAG053StepOutputReferences,
)
from .security_rules import (
    WAG017HardcodedSecretsInRun,
    WAG018UnpinnedActions,
    WAG019UnusedPermissions,
    WAG020OverlyPermissiveSecrets,
    WAG021MissingOIDCConfiguration,
    WAG022ImplicitEnvironmentExposure,
)
from .validation_rules import (
    VALID_EVENT_TYPES,
    WAG009ValidateEventTypes,
    WAG010MissingSecretVariables,
    WAG049ValidateWorkflowInputs,
)

__all__ = [
    # Base classes
    "BaseRule",
    "LintError",
    # Constants
    "KNOWN_ACTIONS",
    "VALID_EVENT_TYPES",
    # Action rules
    "WAG001TypedActionWrappers",
    # Expression rules
    "WAG002UseConditionBuilders",
    "WAG003UseSecretsContext",
    "WAG008HardcodedExpressions",
    # Organization rules
    "WAG004UseMatrixBuilder",
    "WAG005ExtractInlineEnvVariables",
    "WAG006DuplicateWorkflowNames",
    "WAG007FileTooLarge",
    # Validation rules
    "WAG009ValidateEventTypes",
    "WAG010MissingSecretVariables",
    "WAG049ValidateWorkflowInputs",
    # Pattern rules
    "WAG011ComplexConditions",
    "WAG012SuggestReusableWorkflows",
    "WAG016SuggestReusableWorkflowExtraction",
    # Extraction rules
    "WAG013InlineEnvVariables",
    "WAG014InlineMatrixConfig",
    "WAG015InlineOutputs",
    # Security rules
    "WAG017HardcodedSecretsInRun",
    "WAG018UnpinnedActions",
    "WAG019UnusedPermissions",
    "WAG020OverlyPermissiveSecrets",
    "WAG021MissingOIDCConfiguration",
    "WAG022ImplicitEnvironmentExposure",
    # Reference rules
    "WAG050UnusedJobOutputs",
    "WAG051CircularJobDependencies",
    "WAG052OrphanSecrets",
    "WAG053StepOutputReferences",
    # Functions
    "get_default_rules",
]


def get_default_rules() -> list[BaseRule]:
    """Return the default set of linting rules."""
    return [
        WAG001TypedActionWrappers(),
        WAG002UseConditionBuilders(),
        WAG003UseSecretsContext(),
        WAG004UseMatrixBuilder(),
        WAG005ExtractInlineEnvVariables(),
        WAG006DuplicateWorkflowNames(),
        WAG007FileTooLarge(),
        WAG008HardcodedExpressions(),
        WAG009ValidateEventTypes(),
        WAG010MissingSecretVariables(),
        WAG011ComplexConditions(),
        WAG012SuggestReusableWorkflows(),
        WAG013InlineEnvVariables(),
        WAG014InlineMatrixConfig(),
        WAG015InlineOutputs(),
        WAG016SuggestReusableWorkflowExtraction(),
        WAG017HardcodedSecretsInRun(),
        WAG018UnpinnedActions(),
        WAG019UnusedPermissions(),
        WAG020OverlyPermissiveSecrets(),
        WAG021MissingOIDCConfiguration(),
        WAG022ImplicitEnvironmentExposure(),
        WAG049ValidateWorkflowInputs(),
        WAG050UnusedJobOutputs(),
        WAG051CircularJobDependencies(),
        WAG052OrphanSecrets(),
        WAG053StepOutputReferences(),
    ]
