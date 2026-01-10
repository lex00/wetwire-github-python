"""Kiro CLI integration for wetwire-github.

This module provides integration with Kiro CLI for AI-assisted
workflow design using the wetwire-github toolchain.

Usage:
    from wetwire_github.kiro import install_kiro_configs, launch_kiro

    # Install configurations (first run)
    install_kiro_configs()

    # Launch Kiro with wetwire-runner agent
    launch_kiro(prompt="Create a CI workflow for Python")
"""

from wetwire_github.kiro.installer import (
    check_kiro_installed,
    install_kiro_configs,
    launch_kiro,
    run_kiro_scenario,
)

__all__ = [
    "check_kiro_installed",
    "install_kiro_configs",
    "launch_kiro",
    "run_kiro_scenario",
]
