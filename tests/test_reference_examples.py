"""Reference example tests for import/build cycle validation.

Tests the import and build commands against real-world workflow examples.
"""

import subprocess
import sys

import pytest
import yaml

# Sample starter workflow YAML templates for testing
STARTER_WORKFLOWS = {
    "python": '''
name: Python application

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4
    - name: Set up Python 3.10
      uses: actions/setup-python@v5
      with:
        python-version: "3.10"
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install flake8 pytest
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    - name: Test with pytest
      run: |
        pytest
''',
    "node": '''
name: Node.js CI

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  build:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18.x, 20.x, 22.x]

    steps:
    - uses: actions/checkout@v4
    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
    - run: npm ci
    - run: npm run build --if-present
    - run: npm test
''',
    "docker": '''
name: Docker Build

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Build the Docker image
      run: docker build . --file Dockerfile --tag my-image:$(date +%s)
''',
}


class TestImportBuildCycle:
    """Tests for the import/rebuild cycle."""

    @pytest.mark.parametrize("workflow_name", list(STARTER_WORKFLOWS.keys()))
    def test_import_produces_valid_python(self, workflow_name, tmp_path):
        """Import command produces valid Python for starter workflows."""
        # Write workflow YAML
        yaml_file = tmp_path / f"{workflow_name}.yaml"
        yaml_file.write_text(STARTER_WORKFLOWS[workflow_name])

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Run import
        result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "import",
                "-o", str(output_dir),
                "--no-scaffold",
                str(yaml_file),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Import failed: {result.stderr}"

        # Find generated Python file
        python_files = list(output_dir.glob("*.py"))
        assert len(python_files) > 0, "No Python files generated"

        # Verify Python code compiles
        for py_file in python_files:
            code = py_file.read_text()
            compile(code, str(py_file), "exec")

    @pytest.mark.parametrize("workflow_name", list(STARTER_WORKFLOWS.keys()))
    def test_import_build_roundtrip(self, workflow_name, tmp_path):
        """Import and build produce valid YAML output."""
        # Write workflow YAML
        yaml_file = tmp_path / f"{workflow_name}.yaml"
        yaml_file.write_text(STARTER_WORKFLOWS[workflow_name])

        import_dir = tmp_path / "imported"
        import_dir.mkdir()

        # Run import
        import_result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "import",
                "-o", str(import_dir),
                "--no-scaffold",
                str(yaml_file),
            ],
            capture_output=True,
            text=True,
        )

        assert import_result.returncode == 0, f"Import failed: {import_result.stderr}"

        # Run build
        build_dir = tmp_path / "built"

        build_result = subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "build",
                "-o", str(build_dir),
                str(import_dir),
            ],
            capture_output=True,
            text=True,
        )

        assert build_result.returncode == 0, f"Build failed: {build_result.stderr}"

        # Verify output YAML is valid
        yaml_files = list(build_dir.glob("*.yaml")) + list(build_dir.glob("*.yml"))
        assert len(yaml_files) > 0, "No YAML files generated"

        for output_yaml in yaml_files:
            content = output_yaml.read_text()
            data = yaml.safe_load(content)
            assert data is not None, "YAML parse failed"
            assert "jobs" in data or "name" in data, "Missing expected fields"


class TestRoundTripValidation:
    """Tests that round-trip preserves workflow semantics."""

    def test_workflow_name_preserved(self, tmp_path):
        """Workflow name is preserved through import/build cycle."""
        yaml_content = '''
name: My Custom Workflow
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo test
'''
        yaml_file = tmp_path / "custom.yaml"
        yaml_file.write_text(yaml_content)

        # Import
        import_dir = tmp_path / "imported"
        subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "import",
                "-o", str(import_dir),
                "--no-scaffold",
                str(yaml_file),
            ],
            check=True,
            capture_output=True,
        )

        # Build
        build_dir = tmp_path / "built"
        subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "build",
                "-o", str(build_dir),
                str(import_dir),
            ],
            check=True,
            capture_output=True,
        )

        # Check name preserved
        output_yaml = list(build_dir.glob("*.yaml"))[0]
        data = yaml.safe_load(output_yaml.read_text())
        assert data["name"] == "My Custom Workflow"

    def test_job_dependencies_preserved(self, tmp_path):
        """Job dependencies are preserved through import/build cycle."""
        yaml_content = '''
name: Pipeline
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: make build
  test:
    runs-on: ubuntu-latest
    needs: [build]
    steps:
      - run: make test
  deploy:
    runs-on: ubuntu-latest
    needs: [test]
    steps:
      - run: make deploy
'''
        yaml_file = tmp_path / "pipeline.yaml"
        yaml_file.write_text(yaml_content)

        # Import
        import_dir = tmp_path / "imported"
        subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "import",
                "-o", str(import_dir),
                "--no-scaffold",
                str(yaml_file),
            ],
            check=True,
            capture_output=True,
        )

        # Build
        build_dir = tmp_path / "built"
        subprocess.run(
            [
                sys.executable, "-m", "wetwire_github.cli", "build",
                "-o", str(build_dir),
                str(import_dir),
            ],
            check=True,
            capture_output=True,
        )

        # Check dependencies preserved
        output_yaml = list(build_dir.glob("*.yaml"))[0]
        data = yaml.safe_load(output_yaml.read_text())
        assert "test" in data["jobs"]
        assert data["jobs"]["test"]["needs"] == ["build"]
        assert data["jobs"]["deploy"]["needs"] == ["test"]


class TestSuccessRateTracking:
    """Tests for tracking success rates across workflows."""

    def test_all_starter_workflows_import_successfully(self, tmp_path):
        """All starter workflows import without errors."""
        success_count = 0
        total = len(STARTER_WORKFLOWS)

        for name, content in STARTER_WORKFLOWS.items():
            yaml_file = tmp_path / f"{name}.yaml"
            yaml_file.write_text(content)

            output_dir = tmp_path / f"output_{name}"
            output_dir.mkdir()

            result = subprocess.run(
                [
                    sys.executable, "-m", "wetwire_github.cli", "import",
                    "-o", str(output_dir),
                    "--no-scaffold",
                    str(yaml_file),
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                success_count += 1

        success_rate = success_count / total
        assert success_rate >= 1.0, f"Success rate {success_rate:.1%} below 100%"

    def test_all_starter_workflows_roundtrip_successfully(self, tmp_path):
        """All starter workflows complete import/build cycle."""
        success_count = 0
        total = len(STARTER_WORKFLOWS)

        for name, content in STARTER_WORKFLOWS.items():
            yaml_file = tmp_path / f"{name}.yaml"
            yaml_file.write_text(content)

            import_dir = tmp_path / f"import_{name}"
            build_dir = tmp_path / f"build_{name}"

            # Import
            import_result = subprocess.run(
                [
                    sys.executable, "-m", "wetwire_github.cli", "import",
                    "-o", str(import_dir),
                    "--no-scaffold",
                    str(yaml_file),
                ],
                capture_output=True,
            )

            if import_result.returncode != 0:
                continue

            # Build
            build_result = subprocess.run(
                [
                    sys.executable, "-m", "wetwire_github.cli", "build",
                    "-o", str(build_dir),
                    str(import_dir),
                ],
                capture_output=True,
            )

            if build_result.returncode == 0:
                success_count += 1

        success_rate = success_count / total
        assert success_rate >= 1.0, f"Round-trip success rate {success_rate:.1%} below 100%"
