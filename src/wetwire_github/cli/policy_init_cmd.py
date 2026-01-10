"""Policy init command - create policy configuration file."""

from pathlib import Path

# Template for .wetwire-policy.yaml with minimal preset
MINIMAL_TEMPLATE = '''# Wetwire Policy Configuration
# This file configures which policies are enabled when running `wetwire-github policy`.
#
# Preset: minimal
# Only essential policies are enabled.

policies:
  # Require all jobs to use actions/checkout
  require_checkout:
    enabled: true

  # Require all jobs to have timeout_minutes set
  require_timeouts:
    enabled: false

  # Detect hardcoded secrets in run commands
  no_hardcoded_secrets:
    enabled: true

  # Require actions to be pinned to SHA or version
  pin_actions:
    enabled: false

  # Limit the number of jobs in a workflow
  limit_job_count:
    enabled: false
    params:
      max_jobs: 10

  # Require jobs to use environment with reviewers
  require_approval:
    enabled: false
'''

# Template for .wetwire-policy.yaml with standard preset
STANDARD_TEMPLATE = '''# Wetwire Policy Configuration
# This file configures which policies are enabled when running `wetwire-github policy`.
#
# Preset: standard
# Common policies for most projects.

policies:
  # Require all jobs to use actions/checkout
  require_checkout:
    enabled: true

  # Require all jobs to have timeout_minutes set
  require_timeouts:
    enabled: true

  # Detect hardcoded secrets in run commands
  no_hardcoded_secrets:
    enabled: true

  # Require actions to be pinned to SHA or version
  pin_actions:
    enabled: true

  # Limit the number of jobs in a workflow
  limit_job_count:
    enabled: true
    params:
      max_jobs: 10

  # Require jobs to use environment with reviewers
  require_approval:
    enabled: false
'''

# Template for .wetwire-policy.yaml with strict preset
STRICT_TEMPLATE = '''# Wetwire Policy Configuration
# This file configures which policies are enabled when running `wetwire-github policy`.
#
# Preset: strict
# All policies enabled with stricter limits.

policies:
  # Require all jobs to use actions/checkout
  require_checkout:
    enabled: true

  # Require all jobs to have timeout_minutes set
  require_timeouts:
    enabled: true

  # Detect hardcoded secrets in run commands
  no_hardcoded_secrets:
    enabled: true

  # Require actions to be pinned to SHA or version
  pin_actions:
    enabled: true

  # Limit the number of jobs in a workflow
  limit_job_count:
    enabled: true
    params:
      max_jobs: 5  # Stricter limit

  # Require jobs to use environment with reviewers
  require_approval:
    enabled: true
'''


PRESET_TEMPLATES = {
    "minimal": MINIMAL_TEMPLATE,
    "standard": STANDARD_TEMPLATE,
    "strict": STRICT_TEMPLATE,
}


def init_policy_config(
    output_dir: str = ".",
    preset: str = "standard",
    force: bool = False,
) -> tuple[int, list[str]]:
    """Create a policy configuration file.

    Args:
        output_dir: Directory to create config file in
        preset: Preset to use (minimal, standard, strict)
        force: Overwrite existing config file

    Returns:
        Tuple of (exit_code, messages)
    """
    messages = []

    # Validate preset
    if preset not in PRESET_TEMPLATES:
        valid_presets = ", ".join(PRESET_TEMPLATES.keys())
        return 1, [f"Error: Invalid preset '{preset}'. Valid presets: {valid_presets}"]

    # Resolve output directory
    output_path = Path(output_dir).resolve()

    # Verify directory exists
    if not output_path.exists():
        return 1, [f"Error: Directory does not exist: {output_dir}"]

    if not output_path.is_dir():
        return 1, [f"Error: Path is not a directory: {output_dir}"]

    # Check for existing config file
    config_file = output_path / ".wetwire-policy.yaml"

    if config_file.exists() and not force:
        return 1, [
            f"Error: Config file already exists: {config_file}",
            "Use --force to overwrite",
        ]

    # Write config file
    try:
        template = PRESET_TEMPLATES[preset]
        config_file.write_text(template)
        messages.append(f"Created {config_file}")
        messages.append(f"Using preset: {preset}")
        messages.append("")
        messages.append("Next steps:")
        messages.append("  1. Edit .wetwire-policy.yaml to customize policies")
        messages.append("  2. Run 'wetwire-github policy' to check workflows")

        return 0, messages

    except OSError as e:
        return 1, [f"Error creating config file: {e}"]
