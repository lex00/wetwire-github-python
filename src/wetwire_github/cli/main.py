"""Main CLI entry point for wetwire-github."""

import argparse
import sys

from wetwire_github import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="wetwire-github",
        description="Generate GitHub YAML configurations from typed Python declarations.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # build command
    build_parser = subparsers.add_parser(
        "build",
        help="Generate YAML from Python declarations",
        description="Discover workflow declarations from Python packages and serialize to GitHub Actions YAML.",
    )
    build_parser.add_argument(
        "--output",
        "-o",
        help="Output directory (default: .github/workflows/)",
        default=".github/workflows/",
    )
    build_parser.add_argument(
        "--format",
        "-f",
        choices=["yaml", "json"],
        default="yaml",
        help="Output format (default: yaml)",
    )
    build_parser.add_argument(
        "--type",
        "-t",
        choices=["workflow", "dependabot", "issue-template"],
        default="workflow",
        help="Config type to build (default: workflow)",
    )
    build_parser.add_argument(
        "package",
        nargs="?",
        help="Python package to discover workflows from",
    )

    # validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate generated YAML via actionlint",
        description="Run actionlint on generated YAML files.",
    )
    validate_parser.add_argument(
        "--format",
        "-f",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    validate_parser.add_argument(
        "files",
        nargs="*",
        help="YAML files to validate",
    )

    # list command
    list_parser = subparsers.add_parser(
        "list",
        help="List discovered workflows and jobs",
        description="List discovered workflows and jobs from Python packages.",
    )
    list_parser.add_argument(
        "--format",
        "-f",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )
    list_parser.add_argument(
        "package",
        nargs="?",
        help="Python package to discover workflows from",
    )

    # lint command
    lint_parser = subparsers.add_parser(
        "lint",
        help="Apply code quality rules (WAG001-WAG0XX)",
        description="Run Python code quality rules for workflow declarations.",
    )
    lint_parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix fixable issues",
    )
    lint_parser.add_argument(
        "--format",
        "-f",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    lint_parser.add_argument(
        "package",
        nargs="?",
        help="Python package to lint",
    )

    # import command
    import_parser = subparsers.add_parser(
        "import",
        help="Convert existing workflow YAML to Python code",
        description="Import existing YAML files and convert to typed Python declarations.",
    )
    import_parser.add_argument(
        "--output",
        "-o",
        help="Output directory for generated Python code",
    )
    import_parser.add_argument(
        "--single-file",
        action="store_true",
        help="Generate all code in a single file",
    )
    import_parser.add_argument(
        "--no-scaffold",
        action="store_true",
        help="Skip project scaffolding (pyproject.toml, etc.)",
    )
    import_parser.add_argument(
        "--type",
        "-t",
        choices=["workflow", "dependabot", "issue-template"],
        default="workflow",
        help="Config type to import (default: workflow)",
    )
    import_parser.add_argument(
        "files",
        nargs="*",
        help="YAML files to import",
    )

    # init command
    init_parser = subparsers.add_parser(
        "init",
        help="Create new project with example workflow",
        description="Scaffold a new wetwire-github project structure.",
    )
    init_parser.add_argument(
        "name",
        nargs="?",
        help="Project name",
    )
    init_parser.add_argument(
        "--output",
        "-o",
        help="Output directory",
        default=".",
    )

    # design command
    design_parser = subparsers.add_parser(
        "design",
        help="AI-assisted infrastructure design via wetwire-core",
        description="Interactive AI-assisted workflow design session.",
    )
    design_parser.add_argument(
        "--stream",
        action="store_true",
        help="Stream output",
    )
    design_parser.add_argument(
        "--max-lint-cycles",
        type=int,
        default=3,
        help="Maximum lint feedback cycles (default: 3)",
    )

    # test command
    test_parser = subparsers.add_parser(
        "test",
        help="Persona-based testing via wetwire-core",
        description="Run persona-based tests for code generation quality.",
    )
    test_parser.add_argument(
        "--persona",
        help="Persona to use for testing",
    )
    test_parser.add_argument(
        "--scenario",
        help="Scenario configuration file",
    )

    # graph command
    graph_parser = subparsers.add_parser(
        "graph",
        help="Generate DAG visualization of workflow jobs",
        description="Generate a dependency graph of workflow jobs.",
    )
    graph_parser.add_argument(
        "--format",
        "-f",
        choices=["dot", "mermaid"],
        default="mermaid",
        help="Output format (default: mermaid)",
    )
    graph_parser.add_argument(
        "--output",
        "-o",
        help="Output file",
    )
    graph_parser.add_argument(
        "package",
        nargs="?",
        help="Python package to analyze",
    )

    return parser


def cmd_build(args: argparse.Namespace) -> int:
    """Execute build command."""
    from wetwire_github.cli.build import build_workflows

    # Use current directory if no package specified
    package_path = args.package or "."

    exit_code, messages = build_workflows(
        package_path=package_path,
        output_dir=args.output,
        output_format=args.format,
    )

    for msg in messages:
        if exit_code == 0:
            print(f"Generated: {msg}")
        else:
            print(msg, file=sys.stderr)

    return exit_code


def cmd_validate(args: argparse.Namespace) -> int:
    """Execute validate command."""
    from wetwire_github.cli.validate import validate_files

    exit_code, output = validate_files(
        file_paths=args.files or [],
        output_format=args.format,
    )

    if output:
        print(output)

    return exit_code


def cmd_list(args: argparse.Namespace) -> int:
    """Execute list command."""
    print(f"List command not yet implemented (package={args.package})")
    return 1


def cmd_lint(args: argparse.Namespace) -> int:
    """Execute lint command."""
    print(f"Lint command not yet implemented (package={args.package})")
    return 1


def cmd_import(args: argparse.Namespace) -> int:
    """Execute import command."""
    print(f"Import command not yet implemented (files={args.files})")
    return 1


def cmd_init(args: argparse.Namespace) -> int:
    """Execute init command."""
    print(f"Init command not yet implemented (name={args.name})")
    return 1


def cmd_design(args: argparse.Namespace) -> int:
    """Execute design command."""
    print("Design command not yet implemented")
    return 1


def cmd_test(args: argparse.Namespace) -> int:
    """Execute test command."""
    print("Test command not yet implemented")
    return 1


def cmd_graph(args: argparse.Namespace) -> int:
    """Execute graph command."""
    print(f"Graph command not yet implemented (package={args.package})")
    return 1


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    # Command dispatch
    commands = {
        "build": cmd_build,
        "validate": cmd_validate,
        "list": cmd_list,
        "lint": cmd_lint,
        "import": cmd_import,
        "init": cmd_init,
        "design": cmd_design,
        "test": cmd_test,
        "graph": cmd_graph,
    }

    if args.command in commands:
        return commands[args.command](args)

    # Unknown command (shouldn't happen with argparse)
    print(f"Unknown command: {args.command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
