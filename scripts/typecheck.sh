#!/usr/bin/env bash
# Run type checking for wetwire-github-python
#
# Usage:
#   ./scripts/typecheck.sh           # Type check source code
#   ./scripts/typecheck.sh --all     # Type check source and tests
#   ./scripts/typecheck.sh --help    # Show this help

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

show_help() {
    echo "wetwire-github type checking script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --all       Type check both src/ and tests/"
    echo "  -h, --help  Show this help message"
    echo ""
    echo "Note: Uses 'ty' type checker (configured in dev dependencies)"
    exit 0
}

# Default: check src only
CHECK_PATH="src/wetwire_github/"

# Parse arguments
case "${1:-}" in
    -h|--help)
        show_help
        ;;
    --all)
        CHECK_PATH="src/wetwire_github/ tests/"
        ;;
    "")
        # Use default
        ;;
    *)
        echo "Error: Unknown option '$1'"
        echo "Run '$0 --help' for usage information"
        exit 1
        ;;
esac

cd "$PROJECT_ROOT"

# Exclude files with optional dependencies that may not be installed
EXCLUDE_OPTS="--exclude **/mcp_server.py"

echo "Running type check: uv run ty check $EXCLUDE_OPTS $CHECK_PATH"
echo ""

uv run ty check $EXCLUDE_OPTS $CHECK_PATH

echo ""
echo "✓ Type checking complete"
