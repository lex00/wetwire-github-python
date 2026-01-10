#!/usr/bin/env bash
# Set up development environment for wetwire-github-python
#
# Usage:
#   ./scripts/dev-setup.sh           # Interactive setup
#   ./scripts/dev-setup.sh --auto    # Non-interactive (skip optional tools)
#   ./scripts/dev-setup.sh --help    # Show this help

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

show_help() {
    echo "wetwire-github development setup script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --auto      Non-interactive mode (skip optional tools)"
    echo "  -h, --help  Show this help message"
    echo ""
    echo "This script will:"
    echo "  1. Check for required tools (Python 3.11+)"
    echo "  2. Install uv if not present"
    echo "  3. Create virtual environment and install dependencies"
    echo "  4. Optionally install actionlint (YAML validation)"
    echo "  5. Run initial test suite to verify setup"
    exit 0
}

info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_python() {
    info "Checking Python version..."

    if ! command -v python3 &> /dev/null; then
        error "python3 not found. Please install Python 3.11 or higher."
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f2)

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
        error "Python 3.11+ required (found $PYTHON_VERSION)"
        exit 1
    fi

    info "✓ Python $PYTHON_VERSION"
}

check_git() {
    info "Checking git..."

    if ! command -v git &> /dev/null; then
        error "git not found. Please install git."
        exit 1
    fi

    GIT_VERSION=$(git --version | cut -d' ' -f3)
    info "✓ git $GIT_VERSION"
}

install_uv() {
    if command -v uv &> /dev/null; then
        UV_VERSION=$(uv --version | cut -d' ' -f2)
        info "✓ uv $UV_VERSION already installed"
        return
    fi

    info "Installing uv package manager..."

    if command -v curl &> /dev/null; then
        curl -LsSf https://astral.sh/uv/install.sh | sh

        # Source the shell config to get uv in PATH
        export PATH="$HOME/.cargo/bin:$PATH"

        if command -v uv &> /dev/null; then
            info "✓ uv installed successfully"
        else
            warn "uv installed but not in PATH. Please restart your shell."
        fi
    else
        warn "curl not found. Please install uv manually: https://github.com/astral-sh/uv"
    fi
}

install_dependencies() {
    info "Installing project dependencies..."

    cd "$PROJECT_ROOT"

    if command -v uv &> /dev/null; then
        uv sync
        info "✓ Dependencies installed"
    else
        error "uv not available. Cannot install dependencies."
        exit 1
    fi
}

install_actionlint() {
    if [ "$AUTO_MODE" = true ]; then
        warn "Skipping actionlint installation (auto mode)"
        return
    fi

    if command -v actionlint &> /dev/null; then
        ACTIONLINT_VERSION=$(actionlint --version 2>&1 | head -n1)
        info "✓ actionlint already installed: $ACTIONLINT_VERSION"
        return
    fi

    echo ""
    read -p "Install actionlint for YAML validation? (y/N) " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        warn "Skipping actionlint installation"
        return
    fi

    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            info "Installing actionlint via Homebrew..."
            brew install actionlint
            info "✓ actionlint installed"
        else
            warn "Homebrew not found. Please install actionlint manually:"
            warn "  https://github.com/rhysd/actionlint"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v go &> /dev/null; then
            info "Installing actionlint via go..."
            go install github.com/rhysd/actionlint/cmd/actionlint@latest
            info "✓ actionlint installed"
        else
            warn "Go not found. Please install actionlint manually:"
            warn "  https://github.com/rhysd/actionlint"
        fi
    else
        warn "Unsupported OS for automatic actionlint installation"
        warn "Please install manually: https://github.com/rhysd/actionlint"
    fi
}

run_tests() {
    info "Running test suite to verify setup..."

    cd "$PROJECT_ROOT"

    if uv run pytest tests/ -v; then
        info "✓ All tests passed"
    else
        warn "Some tests failed. Setup may be incomplete."
    fi
}

make_scripts_executable() {
    info "Making scripts executable..."
    cd "$PROJECT_ROOT/scripts"
    chmod +x *.sh
    info "✓ Scripts are executable"
}

# Parse arguments
AUTO_MODE=false

case "${1:-}" in
    -h|--help)
        show_help
        ;;
    --auto)
        AUTO_MODE=true
        ;;
    "")
        # Interactive mode
        ;;
    *)
        echo "Error: Unknown option '$1'"
        echo "Run '$0 --help' for usage information"
        exit 1
        ;;
esac

# Main setup sequence
echo "========================================"
echo "wetwire-github Development Setup"
echo "========================================"
echo ""

check_python
check_git
install_uv
install_dependencies
make_scripts_executable
install_actionlint
run_tests

echo ""
echo "========================================"
info "✓ Development environment ready!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  - Run tests:      ./scripts/test.sh"
echo "  - Run linting:    ./scripts/lint.sh"
echo "  - Type check:     ./scripts/typecheck.sh"
echo "  - Build package:  ./scripts/build.sh"
echo ""
echo "See docs/DEVELOPERS.md for more information"
