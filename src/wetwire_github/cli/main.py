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
    design_parser.add_argument(
        "--output",
        "-o",
        dest="output_dir",
        help="Output directory for generated workflows",
    )
    design_parser.add_argument(
        "--prompt",
        "-p",
        help="Initial prompt for design session",
    )

    # test command
    test_parser = subparsers.add_parser(
        "test",
        help="Persona-based testing via wetwire-core",
        description="Run persona-based tests for code generation quality.",
    )
    test_parser.add_argument(
        "--persona",
        help="Persona to use for testing (reviewer, senior-dev, security, beginner)",
    )
    test_parser.add_argument(
        "--workflow",
        help="Workflow YAML file to test",
    )
    test_parser.add_argument(
        "--threshold",
        type=int,
        default=70,
        help="Score threshold for pass/fail (default: 70)",
    )
    test_parser.add_argument(
        "--all",
        action="store_true",
        dest="all_personas",
        help="Run all personas against the workflow",
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

    # mcp-server command
    subparsers.add_parser(
        "mcp-server",
        help="Start MCP server for AI agent integration",
        description="Run the Model Context Protocol server for AI tools like Kiro CLI.",
    )

    # kiro command
    kiro_parser = subparsers.add_parser(
        "kiro",
        help="Launch Kiro CLI with wetwire-github-runner agent",
        description="Launch Kiro CLI for AI-assisted workflow design with the wetwire-github-runner agent.",
    )
    kiro_parser.add_argument(
        "--prompt",
        "-p",
        help="Initial prompt for the conversation",
    )
    kiro_parser.add_argument(
        "--install-only",
        action="store_true",
        help="Only install configs without launching Kiro",
    )
    kiro_parser.add_argument(
        "--force",
        action="store_true",
        help="Force reinstall of configurations",
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
    from wetwire_github.cli.list_cmd import list_resources

    # Use current directory if no package specified
    package_path = args.package or "."

    exit_code, output = list_resources(
        package_path=package_path,
        output_format=args.format,
    )

    if output:
        print(output)

    return exit_code


def cmd_lint(args: argparse.Namespace) -> int:
    """Execute lint command."""
    from wetwire_github.cli.lint_cmd import lint_package

    # Use current directory if no package specified
    package_path = args.package or "."

    exit_code, output = lint_package(
        package_path=package_path,
        output_format=args.format,
        fix=args.fix,
    )

    if output:
        print(output)

    return exit_code


def cmd_import(args: argparse.Namespace) -> int:
    """Execute import command."""
    from wetwire_github.cli.import_cmd import import_workflows

    exit_code, messages = import_workflows(
        file_paths=args.files or [],
        output_dir=args.output or ".",
        single_file=args.single_file,
        no_scaffold=args.no_scaffold,
    )

    for msg in messages:
        if exit_code == 0:
            print(msg)
        else:
            print(msg, file=sys.stderr)

    return exit_code


def cmd_init(args: argparse.Namespace) -> int:
    """Execute init command."""
    from wetwire_github.cli.init_cmd import init_project

    exit_code, messages = init_project(
        name=args.name,
        output_dir=args.output,
    )

    for msg in messages:
        print(msg)

    return exit_code


def cmd_design(args: argparse.Namespace) -> int:
    """Execute design command."""
    from wetwire_github.cli.design_cmd import design_workflow

    exit_code, output = design_workflow(
        stream=args.stream,
        max_lint_cycles=args.max_lint_cycles,
        output_dir=args.output_dir,
        prompt=args.prompt,
    )

    if output:
        print(output)

    return exit_code


def cmd_test(args: argparse.Namespace) -> int:
    """Execute test command."""
    from wetwire_github.cli.test_cmd import run_persona_tests

    exit_code, output = run_persona_tests(
        persona=args.persona,
        workflow=args.workflow,
        threshold=args.threshold,
        all_personas=args.all_personas,
        scenario=args.scenario,
    )

    if output:
        print(output)

    return exit_code


def cmd_graph(args: argparse.Namespace) -> int:
    """Execute graph command."""
    from wetwire_github.cli.graph_cmd import graph_workflows

    # Use current directory if no package specified
    package_path = args.package or "."

    exit_code, output = graph_workflows(
        package_path=package_path,
        output_format=args.format,
        output_file=args.output,
    )

    if output:
        print(output)

    return exit_code


def cmd_mcp_server(args: argparse.Namespace) -> int:
    """Execute mcp-server command."""
    import asyncio

    from wetwire_github.mcp_server import run_server

    try:
        asyncio.run(run_server())
        return 0
    except ImportError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("Install mcp package: pip install mcp", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 0


def cmd_kiro(args: argparse.Namespace) -> int:
    """Execute kiro command."""
    from wetwire_github.kiro import install_kiro_configs, launch_kiro

    if args.install_only:
        results = install_kiro_configs(force=args.force, verbose=True)
        if results["agent"] or results["mcp"]:
            print("Kiro configurations installed successfully.")
        else:
            print("Configurations already exist. Use --force to overwrite.")
        return 0

    return launch_kiro(prompt=args.prompt)


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
        "mcp-server": cmd_mcp_server,
        "kiro": cmd_kiro,
    }

    if args.command in commands:
        return commands[args.command](args)

    # Unknown command (shouldn't happen with argparse)
    print(f"Unknown command: {args.command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
