#!/usr/bin/env bash
# Build the wetwire-github package
#
# Usage:
#   ./scripts/build.sh           # Build the package
#   ./scripts/build.sh --clean   # Clean before building
#   ./scripts/build.sh --help    # Show this help

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

show_help() {
    echo "wetwire-github build script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --clean     Remove dist/ and build artifacts before building"
    echo "  -h, --help  Show this help message"
    echo ""
    echo "The package will be built to dist/ directory"
    exit 0
}

clean_build() {
    echo "Cleaning build artifacts..."
    cd "$PROJECT_ROOT"
    rm -rf dist/ build/ *.egg-info src/*.egg-info
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    echo "✓ Cleaned"
}

build_package() {
    echo "Building package..."
    cd "$PROJECT_ROOT"

    # Use uv to build if available, otherwise fall back to python -m build
    if command -v uv &> /dev/null; then
        uv build
    else
        python -m build
    fi

    echo ""
    echo "✓ Build complete"
    echo ""
    echo "Output:"
    ls -lh dist/
}

# Parse arguments
case "${1:-}" in
    -h|--help)
        show_help
        ;;
    --clean)
        clean_build
        build_package
        ;;
    "")
        build_package
        ;;
    *)
        echo "Error: Unknown option '$1'"
        echo "Run '$0 --help' for usage information"
        exit 1
        ;;
esac
