"""Init command - create new wetwire-github project scaffold."""

from pathlib import Path

# Template for pyproject.toml
PYPROJECT_TEMPLATE = '''[project]
name = "{name}"
version = "0.1.0"
description = "GitHub Actions workflows defined in Python"
requires-python = ">= 3.11"
dependencies = [
    "wetwire-github",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
'''

# Template for README.md
README_TEMPLATE = '''# {name}

GitHub Actions workflows defined in Python using wetwire-github.

## Usage

```bash
# Generate YAML from Python declarations
wetwire-github build

# Validate generated YAML
wetwire-github validate .github/workflows/*.yaml

# Lint Python workflow code
wetwire-github lint
```

## Structure

- `ci/` - Python workflow definitions
- `.github/workflows/` - Generated YAML files (do not edit manually)
'''

# Template for workflows.py
WORKFLOWS_TEMPLATE = '''"""CI workflow definitions."""

from wetwire_github.workflow import (
    Job,
    PullRequestTrigger,
    PushTrigger,
    Step,
    Triggers,
    Workflow,
)
from wetwire_github.actions import checkout, setup_python


ci = Workflow(
    name="CI",
    on=Triggers(
        push=PushTrigger(branches=["main"]),
        pull_request=PullRequestTrigger(branches=["main"]),
    ),
    jobs={{
        "build": Job(
            runs_on="ubuntu-latest",
            steps=[
                checkout(),
                setup_python(python_version="3.11"),
                Step(run="pip install -e ."),
                Step(run="pytest"),
            ],
        ),
    }},
)
'''


def _sanitize_name(name: str) -> str:
    """Convert project name to valid Python package name."""
    # Replace hyphens and spaces with underscores
    sanitized = name.replace("-", "_").replace(" ", "_")
    # Remove any characters that aren't alphanumeric or underscore
    sanitized = "".join(c for c in sanitized if c.isalnum() or c == "_")
    # Ensure it doesn't start with a number
    if sanitized and sanitized[0].isdigit():
        sanitized = "_" + sanitized
    return sanitized or "my_project"


def init_project(
    name: str | None,
    output_dir: str,
) -> tuple[int, list[str]]:
    """Create a new wetwire-github project scaffold.

    Args:
        name: Project name (defaults to directory name)
        output_dir: Directory to create project in

    Returns:
        Tuple of (exit_code, messages)
    """
    messages = []

    # Resolve output directory
    output_path = Path(output_dir).resolve()

    # Determine project name
    if name:
        project_name = name
    elif output_dir == ".":
        project_name = output_path.name
    else:
        project_name = output_path.name

    # Create directory structure
    try:
        # Create output directory if needed
        output_path.mkdir(parents=True, exist_ok=True)

        # Create ci package directory
        ci_dir = output_path / "ci"
        ci_dir.mkdir(exist_ok=True)

        # Create .github/workflows directory
        workflows_dir = output_path / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)

        # Write __init__.py
        init_file = ci_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text('"""CI workflow definitions."""\n')
            messages.append(f"Created {init_file}")

        # Write workflows.py
        workflows_file = ci_dir / "workflows.py"
        if not workflows_file.exists():
            workflows_file.write_text(WORKFLOWS_TEMPLATE)
            messages.append(f"Created {workflows_file}")
        else:
            messages.append(f"Skipped {workflows_file} (already exists)")

        # Write pyproject.toml
        pyproject_file = output_path / "pyproject.toml"
        if not pyproject_file.exists():
            pyproject_file.write_text(PYPROJECT_TEMPLATE.format(name=project_name))
            messages.append(f"Created {pyproject_file}")
        else:
            messages.append(f"Skipped {pyproject_file} (already exists)")

        # Write README.md
        readme_file = output_path / "README.md"
        if not readme_file.exists():
            readme_file.write_text(README_TEMPLATE.format(name=project_name))
            messages.append(f"Created {readme_file}")
        else:
            messages.append(f"Skipped {readme_file} (already exists)")

        # Write .gitkeep in workflows directory
        gitkeep_file = workflows_dir / ".gitkeep"
        if not gitkeep_file.exists():
            gitkeep_file.write_text("")
            messages.append(f"Created {gitkeep_file}")

        messages.append(f"\nProject '{project_name}' initialized successfully!")
        messages.append("\nNext steps:")
        messages.append("  1. Edit ci/workflows.py to define your workflows")
        messages.append("  2. Run 'wetwire-github build' to generate YAML")
        messages.append("  3. Commit both the Python and generated YAML files")

        return 0, messages

    except OSError as e:
        return 1, [f"Error creating project: {e}"]
