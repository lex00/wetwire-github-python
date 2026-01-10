#!/usr/bin/env bash
# Run tests for wetwire-github-python
#
# Usage:
#   ./scripts/test.sh                    # Run all tests with coverage
#   ./scripts/test.sh --no-cov           # Run tests without coverage
#   ./scripts/test.sh --fast             # Skip slow integration tests
#   ./scripts/test.sh tests/test_foo.py  # Run specific test file
#   ./scripts/test.sh --help             # Show this help

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

show_help() {
    echo "wetwire-github testing script"
    echo ""
    echo "Usage: $0 [OPTIONS] [TEST_PATH]"
    echo ""
    echo "Options:"
    echo "  --no-cov     Run tests without coverage reporting"
    echo "  --fast       Skip slow integration tests (adds -m 'not slow')"
    echo "  -v           Verbose output"
    echo "  -h, --help   Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                              # All tests with coverage"
    echo "  $0 --no-cov                     # All tests without coverage"
    echo "  $0 --fast                       # Fast tests only"
    echo "  $0 tests/test_workflow.py       # Specific test file"
    echo "  $0 tests/test_workflow.py::test_foo  # Specific test"
    exit 0
}

# Default options
COVERAGE=true
FAST=false
VERBOSE="-v"
TEST_PATH="tests/"
EXTRA_ARGS=()

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            ;;
        --no-cov)
            COVERAGE=false
            shift
            ;;
        --fast)
            FAST=true
            shift
            ;;
        -v)
            VERBOSE="-vv"
            shift
            ;;
        -*)
            EXTRA_ARGS+=("$1")
            shift
            ;;
        *)
            TEST_PATH="$1"
            shift
            ;;
    esac
done

cd "$PROJECT_ROOT"

# Build pytest command
PYTEST_ARGS=("$VERBOSE")

if [ "$COVERAGE" = true ]; then
    PYTEST_ARGS+=(--cov=wetwire_github --cov-report=term-missing)
fi

if [ "$FAST" = true ]; then
    PYTEST_ARGS+=(-m "not slow")
fi

PYTEST_ARGS+=("${EXTRA_ARGS[@]}")
PYTEST_ARGS+=("$TEST_PATH")

echo "Running tests: uv run pytest ${PYTEST_ARGS[*]}"
echo ""

uv run pytest "${PYTEST_ARGS[@]}"

echo ""
echo "✓ Tests complete"
