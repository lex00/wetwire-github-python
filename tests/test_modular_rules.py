"""Tests for modular linter rules structure.

This tests the new modular organization of lint rules into
separate category-based files.
"""


class TestModularRulesImports:
    """Test that rules can be imported from modular structure."""

    def test_import_from_rules_base(self):
        """Can import base classes from rules.base."""
        from wetwire_github.linter.rules.base import BaseRule, LintError

        assert BaseRule is not None
        assert LintError is not None

    def test_import_action_rules(self):
        """Can import action-related rules from rules.action_rules."""
        from wetwire_github.linter.rules.action_rules import WAG001TypedActionWrappers

        rule = WAG001TypedActionWrappers()
        assert rule.id == "WAG001"

    def test_import_expression_rules(self):
        """Can import expression-related rules from rules.expression_rules."""
        from wetwire_github.linter.rules.expression_rules import (
            WAG002UseConditionBuilders,
            WAG003UseSecretsContext,
            WAG008HardcodedExpressions,
        )

        assert WAG002UseConditionBuilders().id == "WAG002"
        assert WAG003UseSecretsContext().id == "WAG003"
        assert WAG008HardcodedExpressions().id == "WAG008"

    def test_import_organization_rules(self):
        """Can import organization-related rules from rules.organization_rules."""
        from wetwire_github.linter.rules.organization_rules import (
            WAG004UseMatrixBuilder,
            WAG005ExtractInlineEnvVariables,
            WAG006DuplicateWorkflowNames,
            WAG007FileTooLarge,
        )

        assert WAG004UseMatrixBuilder().id == "WAG004"
        assert WAG005ExtractInlineEnvVariables().id == "WAG005"
        assert WAG006DuplicateWorkflowNames().id == "WAG006"
        assert WAG007FileTooLarge().id == "WAG007"

    def test_import_validation_rules(self):
        """Can import validation-related rules from rules.validation_rules."""
        from wetwire_github.linter.rules.validation_rules import (
            WAG009ValidateEventTypes,
            WAG010MissingSecretVariables,
        )

        assert WAG009ValidateEventTypes().id == "WAG009"
        assert WAG010MissingSecretVariables().id == "WAG010"

    def test_import_pattern_rules(self):
        """Can import pattern-related rules from rules.pattern_rules."""
        from wetwire_github.linter.rules.pattern_rules import (
            WAG011ComplexConditions,
            WAG012SuggestReusableWorkflows,
        )

        assert WAG011ComplexConditions().id == "WAG011"
        assert WAG012SuggestReusableWorkflows().id == "WAG012"

    def test_import_extraction_rules(self):
        """Can import extraction-related rules from rules.extraction_rules."""
        from wetwire_github.linter.rules.extraction_rules import (
            WAG013InlineEnvVariables,
            WAG014InlineMatrixConfig,
            WAG015InlineOutputs,
        )

        assert WAG013InlineEnvVariables().id == "WAG013"
        assert WAG014InlineMatrixConfig().id == "WAG014"
        assert WAG015InlineOutputs().id == "WAG015"


class TestModularRulesAggregation:
    """Test that rules/__init__.py aggregates all rules."""

    def test_import_all_rules_from_init(self):
        """All rules can be imported from rules/__init__.py."""
        from wetwire_github.linter.rules import get_default_rules

        # Verify get_default_rules returns all 26 rules
        rules = get_default_rules()
        assert len(rules) == 26

        rule_ids = {rule.id for rule in rules}
        # WAG001-WAG022 + WAG050-WAG053
        expected_ids = {f"WAG{str(i).zfill(3)}" for i in range(1, 23)} | {
            "WAG050", "WAG051", "WAG052", "WAG053"
        }
        assert rule_ids == expected_ids

        # Verify each rule class can be imported
        from wetwire_github.linter import rules as rules_module

        rule_classes = [
            "WAG001TypedActionWrappers",
            "WAG002UseConditionBuilders",
            "WAG003UseSecretsContext",
            "WAG004UseMatrixBuilder",
            "WAG005ExtractInlineEnvVariables",
            "WAG006DuplicateWorkflowNames",
            "WAG007FileTooLarge",
            "WAG008HardcodedExpressions",
            "WAG009ValidateEventTypes",
            "WAG010MissingSecretVariables",
            "WAG011ComplexConditions",
            "WAG012SuggestReusableWorkflows",
            "WAG013InlineEnvVariables",
            "WAG014InlineMatrixConfig",
            "WAG015InlineOutputs",
            "WAG016SuggestReusableWorkflowExtraction",
            "WAG050UnusedJobOutputs",
            "WAG051CircularJobDependencies",
            "WAG052OrphanSecrets",
            "WAG053StepOutputReferences",
        ]
        for class_name in rule_classes:
            assert hasattr(rules_module, class_name), f"Missing {class_name}"

    def test_known_actions_exported(self):
        """KNOWN_ACTIONS constant is exported from rules."""
        from wetwire_github.linter.rules import KNOWN_ACTIONS

        assert "actions/checkout" in KNOWN_ACTIONS
        assert "actions/setup-python" in KNOWN_ACTIONS

    def test_valid_event_types_exported(self):
        """VALID_EVENT_TYPES constant is exported from rules."""
        from wetwire_github.linter.rules import VALID_EVENT_TYPES

        assert "push" in VALID_EVENT_TYPES
        assert "pull_request" in VALID_EVENT_TYPES


class TestBackwardsCompatibility:
    """Test that old import paths still work."""

    def test_old_import_path_still_works(self):
        """Old import from wetwire_github.linter.rules still works."""
        # This should continue to work for backwards compatibility
        from wetwire_github.linter.rules import (
            WAG001TypedActionWrappers,
            WAG006DuplicateWorkflowNames,
            get_default_rules,
        )

        assert WAG001TypedActionWrappers().id == "WAG001"
        assert WAG006DuplicateWorkflowNames().id == "WAG006"
        assert len(get_default_rules()) == 26


class TestRuleFunctionality:
    """Test that rules work correctly after modular refactoring."""

    def test_wag001_detects_raw_action_strings(self):
        """WAG001 detects raw action strings after modular refactoring."""
        from wetwire_github.linter.rules.action_rules import WAG001TypedActionWrappers

        rule = WAG001TypedActionWrappers()
        source = '''
from wetwire_github.workflow import Step

step = Step(uses="actions/checkout@v4")
'''
        errors = rule.check(source, "test.py")
        assert len(errors) == 1
        assert errors[0].rule_id == "WAG001"

    def test_wag002_detects_raw_conditions(self):
        """WAG002 detects raw condition strings after modular refactoring."""
        from wetwire_github.linter.rules.expression_rules import (
            WAG002UseConditionBuilders,
        )

        rule = WAG002UseConditionBuilders()
        source = '''
from wetwire_github.workflow import Step

step = Step(run="test", if_="${{ always() }}")
'''
        errors = rule.check(source, "test.py")
        assert len(errors) == 1
        assert errors[0].rule_id == "WAG002"

    def test_wag006_detects_duplicates(self):
        """WAG006 detects duplicate workflow names after modular refactoring."""
        from wetwire_github.linter.rules.organization_rules import (
            WAG006DuplicateWorkflowNames,
        )

        rule = WAG006DuplicateWorkflowNames()
        source = '''
from wetwire_github.workflow import Workflow

ci = Workflow(name="CI")
ci_deploy = Workflow(name="CI")
'''
        errors = rule.check(source, "test.py")
        assert len(errors) == 1
        assert errors[0].rule_id == "WAG006"
