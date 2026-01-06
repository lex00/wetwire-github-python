#!/usr/bin/env python3
"""Parse downloaded schemas into intermediate representations.

This module parses:
- GitHub workflow JSON schema into WorkflowSchema
- action.yml files into ActionSchema

The parsed schemas are used by the code generator to produce Python types.
"""

from dataclasses import dataclass
from typing import Any

import yaml


@dataclass
class ActionInput:
    """Parsed input from action.yml."""

    name: str
    description: str
    required: bool
    default: str | None


@dataclass
class ActionOutput:
    """Parsed output from action.yml."""

    name: str
    description: str


@dataclass
class ActionSchema:
    """Parsed action.yml schema."""

    name: str
    description: str
    author: str | None
    inputs: list[ActionInput]
    outputs: list[ActionOutput]
    branding: dict[str, str] | None = None


@dataclass
class WorkflowProperty:
    """Parsed property from workflow JSON schema."""

    name: str
    description: str | None
    type: str | None
    required: bool
    default: Any
    enum: list[str] | None


@dataclass
class WorkflowSchema:
    """Parsed workflow JSON schema."""

    properties: dict[str, WorkflowProperty]
    definitions: dict[str, dict[str, Any]]


def parse_action_yml(content: str) -> ActionSchema:
    """Parse an action.yml file into ActionSchema.

    Args:
        content: Raw YAML content of action.yml

    Returns:
        Parsed ActionSchema
    """
    data = yaml.safe_load(content)

    # Parse inputs
    inputs = []
    for name, info in data.get("inputs", {}).items():
        inputs.append(
            ActionInput(
                name=name,
                description=info.get("description", ""),
                required=info.get("required", False),
                default=info.get("default"),
            )
        )

    # Parse outputs
    outputs = []
    for name, info in data.get("outputs", {}).items():
        outputs.append(
            ActionOutput(
                name=name,
                description=info.get("description", ""),
            )
        )

    return ActionSchema(
        name=data.get("name", ""),
        description=data.get("description", ""),
        author=data.get("author"),
        inputs=inputs,
        outputs=outputs,
        branding=data.get("branding"),
    )


def parse_workflow_schema(schema: dict[str, Any]) -> WorkflowSchema:
    """Parse a workflow JSON schema into WorkflowSchema.

    Args:
        schema: Parsed JSON schema dict

    Returns:
        Parsed WorkflowSchema
    """
    required_props = set(schema.get("required", []))

    # Parse properties
    properties = {}
    for name, info in schema.get("properties", {}).items():
        prop_type = info.get("type")
        if isinstance(prop_type, list):
            # Handle union types like ["string", "object"]
            prop_type = prop_type[0] if prop_type else None

        properties[name] = WorkflowProperty(
            name=name,
            description=info.get("description"),
            type=prop_type,
            required=name in required_props,
            default=info.get("default"),
            enum=info.get("enum"),
        )

    # Parse definitions
    definitions = schema.get("definitions", {})

    return WorkflowSchema(
        properties=properties,
        definitions=definitions,
    )


def parse_action_from_file(path: str) -> ActionSchema:
    """Parse an action.yml file from disk.

    Args:
        path: Path to action.yml file

    Returns:
        Parsed ActionSchema
    """
    with open(path) as f:
        return parse_action_yml(f.read())


def parse_workflow_schema_from_file(path: str) -> WorkflowSchema:
    """Parse a workflow JSON schema from disk.

    Args:
        path: Path to JSON schema file

    Returns:
        Parsed WorkflowSchema
    """
    import json

    with open(path) as f:
        return parse_workflow_schema(json.load(f))


def main() -> int:
    """Main entry point for testing schema parsing."""
    from pathlib import Path

    specs_dir = Path(__file__).parent.parent / "specs"

    # Parse workflow schema if available
    workflow_schema_path = specs_dir / "workflow-schema.json"
    if workflow_schema_path.exists():
        print("Parsing workflow schema...")
        schema = parse_workflow_schema_from_file(str(workflow_schema_path))
        print(f"  Properties: {len(schema.properties)}")
        print(f"  Definitions: {len(schema.definitions)}")
    else:
        print("Workflow schema not found. Run fetch.py first.")

    # Parse action.yml files if available
    actions_dir = specs_dir / "actions"
    if actions_dir.exists():
        print("\nParsing action.yml files...")
        for yml_file in actions_dir.glob("*.yml"):
            action = parse_action_from_file(str(yml_file))
            print(
                f"  {yml_file.stem}: {len(action.inputs)} inputs, {len(action.outputs)} outputs"
            )
    else:
        print("Actions not found. Run fetch.py first.")

    return 0


if __name__ == "__main__":
    exit(main())
