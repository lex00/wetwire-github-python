#!/usr/bin/env bash
# Run linting checks for wetwire-github-python
#
# Usage:
#   ./scripts/lint.sh           # Run both check and format
#   ./scripts/lint.sh check     # Run linting checks only
#   ./scripts/lint.sh format    # Run code formatting only
#   ./scripts/lint.sh fix       # Auto-fix linting issues
#   ./scripts/lint.sh --help    # Show this help

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

show_help() {
    echo "wetwire-github linting script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  check      Run linting checks only (no formatting)"
    echo "  format     Run code formatting only"
    echo "  fix        Auto-fix linting issues"
    echo "  (default)  Run both check and format"
    echo ""
    echo "Options:"
    echo "  -h, --help Show this help message"
    exit 0
}

run_check() {
    echo "Running ruff check..."
    cd "$PROJECT_ROOT"
    uv run ruff check src/ tests/
}

run_format() {
    echo "Running ruff format..."
    cd "$PROJECT_ROOT"
    uv run ruff format src/ tests/
}

run_fix() {
    echo "Running ruff check with auto-fix..."
    cd "$PROJECT_ROOT"
    uv run ruff check --fix src/ tests/
    echo "Running ruff format..."
    uv run ruff format src/ tests/
}

# Parse arguments
case "${1:-}" in
    -h|--help)
        show_help
        ;;
    check)
        run_check
        ;;
    format)
        run_format
        ;;
    fix)
        run_fix
        ;;
    "")
        run_check
        run_format
        ;;
    *)
        echo "Error: Unknown command '$1'"
        echo "Run '$0 --help' for usage information"
        exit 1
        ;;
esac

echo "✓ Linting complete"
