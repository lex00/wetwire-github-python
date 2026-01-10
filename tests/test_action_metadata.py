"""Tests for action metadata generation for composite actions."""

import subprocess
import sys

import yaml


class TestWriteAction:
    """Tests for write_action() function."""

    def test_write_action_exists(self):
        """write_action function can be imported from composite module."""
        from wetwire_github.composite import write_action

        assert write_action is not None

    def test_write_minimal_action(self, tmp_path):
        """write_action generates action.yml for minimal composite action."""
        from wetwire_github.composite import (
            CompositeAction,
            CompositeRuns,
            write_action,
        )
        from wetwire_github.workflow import Step

        action = CompositeAction(
            name="Test Action",
            description="A test composite action",
            runs=CompositeRuns(steps=[Step(run="echo 'test'", shell="bash")]),
        )

        output_file = tmp_path / "action.yml"
        write_action(action, str(output_file))

        assert output_file.exists()
        content = output_file.read_text()
        data = yaml.safe_load(content)

        assert data["name"] == "Test Action"
        assert data["description"] == "A test composite action"
        assert data["runs"]["using"] == "composite"

    def test_write_action_with_inputs(self, tmp_path):
        """write_action generates action.yml with inputs."""
        from wetwire_github.composite import (
            ActionInput,
            CompositeAction,
            CompositeRuns,
            write_action,
        )
        from wetwire_github.workflow import Step

        action = CompositeAction(
            name="Action With Inputs",
            description="An action with inputs",
            inputs={
                "version": ActionInput(description="Version to use", required=True),
                "config": ActionInput(description="Config file", default="config.yml"),
            },
            runs=CompositeRuns(steps=[Step(run="echo test", shell="bash")]),
        )

        output_file = tmp_path / "action.yml"
        write_action(action, str(output_file))

        assert output_file.exists()
        data = yaml.safe_load(output_file.read_text())

        assert "inputs" in data
        assert "version" in data["inputs"]
        assert data["inputs"]["version"]["required"] is True
        assert "config" in data["inputs"]
        assert data["inputs"]["config"]["default"] == "config.yml"

    def test_write_action_with_outputs(self, tmp_path):
        """write_action generates action.yml with outputs."""
        from wetwire_github.composite import (
            ActionOutput,
            CompositeAction,
            CompositeRuns,
            write_action,
        )
        from wetwire_github.workflow import Step

        action = CompositeAction(
            name="Action With Outputs",
            description="An action with outputs",
            outputs={
                "result": ActionOutput(
                    description="Build result",
                    value="${{ steps.build.outputs.result }}",
                ),
            },
            runs=CompositeRuns(
                steps=[
                    Step(
                        id="build",
                        run="echo 'result=success' >> $GITHUB_OUTPUT",
                        shell="bash",
                    )
                ]
            ),
        )

        output_file = tmp_path / "action.yml"
        write_action(action, str(output_file))

        assert output_file.exists()
        data = yaml.safe_load(output_file.read_text())

        assert "outputs" in data
        assert "result" in data["outputs"]
        assert data["outputs"]["result"]["description"] == "Build result"

    def test_write_complete_action(self, tmp_path):
        """write_action generates complete action.yml with all fields."""
        from wetwire_github.composite import (
            ActionInput,
            ActionOutput,
            CompositeAction,
            CompositeRuns,
            write_action,
        )
        from wetwire_github.workflow import Step

        action = CompositeAction(
            name="Complete Action",
            description="A complete composite action",
            inputs={
                "version": ActionInput(description="Version", required=True),
            },
            outputs={
                "result": ActionOutput(
                    description="Result", value="${{ steps.test.outputs.result }}"
                ),
            },
            runs=CompositeRuns(
                steps=[
                    Step(uses="actions/checkout@v4"),
                    Step(id="test", run="echo 'result=pass' >> $GITHUB_OUTPUT", shell="bash"),
                ]
            ),
        )

        output_file = tmp_path / "action.yml"
        write_action(action, str(output_file))

        assert output_file.exists()
        data = yaml.safe_load(output_file.read_text())

        assert data["name"] == "Complete Action"
        assert "inputs" in data
        assert "outputs" in data
        assert len(data["runs"]["steps"]) == 2

    def test_write_action_creates_parent_directory(self, tmp_path):
        """write_action creates parent directories if they don't exist."""
        from wetwire_github.composite import (
            CompositeAction,
            CompositeRuns,
            write_action,
        )
        from wetwire_github.workflow import Step

        action = CompositeAction(
            name="Test",
            description="Test",
            runs=CompositeRuns(steps=[Step(run="echo test", shell="bash")]),
        )

        output_file = tmp_path / "nested" / "dir" / "action.yml"
        write_action(action, str(output_file))

        assert output_file.exists()

    def test_write_action_default_filename(self, tmp_path):
        """write_action uses action.yml as default filename when path is directory."""
        from wetwire_github.composite import (
            CompositeAction,
            CompositeRuns,
            write_action,
        )
        from wetwire_github.workflow import Step

        action = CompositeAction(
            name="Test",
            description="Test",
            runs=CompositeRuns(steps=[Step(run="echo test", shell="bash")]),
        )

        output_dir = tmp_path / "my-action"
        output_dir.mkdir()
        write_action(action, str(output_dir))

        expected_file = output_dir / "action.yml"
        assert expected_file.exists()


class TestDiscoverActions:
    """Tests for discover_actions() function."""

    def test_discover_actions_exists(self):
        """discover_actions function can be imported from discover module."""
        from wetwire_github.discover import discover_actions

        assert discover_actions is not None

    def test_discover_single_action(self, tmp_path):
        """discover_actions finds a single CompositeAction in a file."""
        from wetwire_github.discover import discover_actions

        action_file = tmp_path / "my_action.py"
        action_file.write_text('''
from wetwire_github.composite import CompositeAction, CompositeRuns
from wetwire_github.workflow import Step

test_action = CompositeAction(
    name="Test Action",
    description="A test action",
    runs=CompositeRuns(steps=[Step(run="echo test", shell="bash")]),
)
''')

        actions = discover_actions(str(tmp_path))
        assert len(actions) == 1
        assert actions[0].name == "test_action"
        assert actions[0].type == "CompositeAction"

    def test_discover_multiple_actions(self, tmp_path):
        """discover_actions finds multiple CompositeActions."""
        from wetwire_github.discover import discover_actions

        (tmp_path / "action1.py").write_text('''
from wetwire_github.composite import CompositeAction, CompositeRuns
from wetwire_github.workflow import Step

setup_action = CompositeAction(
    name="Setup",
    description="Setup action",
    runs=CompositeRuns(steps=[Step(run="echo setup", shell="bash")]),
)
''')

        (tmp_path / "action2.py").write_text('''
from wetwire_github.composite import CompositeAction, CompositeRuns
from wetwire_github.workflow import Step

deploy_action = CompositeAction(
    name="Deploy",
    description="Deploy action",
    runs=CompositeRuns(steps=[Step(run="echo deploy", shell="bash")]),
)
''')

        actions = discover_actions(str(tmp_path))
        assert len(actions) == 2
        action_names = {a.name for a in actions}
        assert action_names == {"setup_action", "deploy_action"}

    def test_discover_actions_ignores_workflows(self, tmp_path):
        """discover_actions ignores Workflow definitions."""
        from wetwire_github.discover import discover_actions

        (tmp_path / "mixed.py").write_text('''
from wetwire_github.workflow import Workflow, Job, Step, PushTrigger, Triggers
from wetwire_github.composite import CompositeAction, CompositeRuns

action = CompositeAction(
    name="Action",
    description="Action",
    runs=CompositeRuns(steps=[Step(run="echo action", shell="bash")]),
)

workflow = Workflow(
    name="Workflow",
    on=Triggers(push=PushTrigger()),
    jobs={"build": Job(runs_on="ubuntu-latest", steps=[Step(run="echo workflow")])},
)
''')

        actions = discover_actions(str(tmp_path))
        assert len(actions) == 1
        assert actions[0].name == "action"

    def test_discover_actions_in_subdirectories(self, tmp_path):
        """discover_actions recursively finds actions in subdirectories."""
        from wetwire_github.discover import discover_actions

        subdir = tmp_path / "actions"
        subdir.mkdir()

        (subdir / "action.py").write_text('''
from wetwire_github.composite import CompositeAction, CompositeRuns
from wetwire_github.workflow import Step

nested_action = CompositeAction(
    name="Nested",
    description="Nested action",
    runs=CompositeRuns(steps=[Step(run="echo nested", shell="bash")]),
)
''')

        actions = discover_actions(str(tmp_path))
        assert len(actions) == 1
        assert actions[0].name == "nested_action"

    def test_discover_actions_handles_syntax_errors(self, tmp_path):
        """discover_actions handles files with syntax errors gracefully."""
        from wetwire_github.discover import discover_actions

        (tmp_path / "broken.py").write_text('''
def incomplete(
''')

        (tmp_path / "valid.py").write_text('''
from wetwire_github.composite import CompositeAction, CompositeRuns
from wetwire_github.workflow import Step

valid_action = CompositeAction(
    name="Valid",
    description="Valid action",
    runs=CompositeRuns(steps=[Step(run="echo valid", shell="bash")]),
)
''')

        actions = discover_actions(str(tmp_path))
        assert len(actions) == 1
        assert actions[0].name == "valid_action"


class TestActionBuildCommand:
    """Tests for CLI 'action build' command."""

    def test_action_build_command_exists(self, tmp_path):
        """action build command can be invoked via CLI."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "action", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        # Should show help for action command
        assert result.returncode == 0
        assert "action" in result.stdout.lower() or "build" in result.stdout.lower()

    def test_action_build_generates_action_yml(self, tmp_path):
        """action build generates action.yml from CompositeAction definition."""
        actions_dir = tmp_path / "actions"
        actions_dir.mkdir()
        (actions_dir / "__init__.py").write_text("")

        action_file = actions_dir / "setup.py"
        action_file.write_text('''
from wetwire_github.composite import CompositeAction, CompositeRuns, ActionInput
from wetwire_github.workflow import Step

setup_action = CompositeAction(
    name="Setup Tool",
    description="Sets up a tool",
    inputs={
        "version": ActionInput(description="Tool version", required=True),
    },
    runs=CompositeRuns(
        steps=[
            Step(run="echo Setting up version ${{ inputs.version }}", shell="bash"),
        ]
    ),
)
''')

        output_dir = tmp_path / "output"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_github.cli",
                "action",
                "build",
                str(actions_dir),
                "-o",
                str(output_dir),
            ],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}\nstdout: {result.stdout}"
        assert output_dir.exists()

        # Should create action.yml
        action_files = list(output_dir.glob("**/action.yml")) + list(
            output_dir.glob("**/action.yaml")
        )
        assert len(action_files) >= 1

        # Verify content
        data = yaml.safe_load(action_files[0].read_text())
        assert data["name"] == "Setup Tool"
        assert "inputs" in data

    def test_action_build_multiple_actions(self, tmp_path):
        """action build generates multiple action.yml files."""
        actions_dir = tmp_path / "actions"
        actions_dir.mkdir()
        (actions_dir / "__init__.py").write_text("")

        (actions_dir / "setup.py").write_text('''
from wetwire_github.composite import CompositeAction, CompositeRuns
from wetwire_github.workflow import Step

setup = CompositeAction(
    name="Setup",
    description="Setup action",
    runs=CompositeRuns(steps=[Step(run="echo setup", shell="bash")]),
)
''')

        (actions_dir / "deploy.py").write_text('''
from wetwire_github.composite import CompositeAction, CompositeRuns
from wetwire_github.workflow import Step

deploy = CompositeAction(
    name="Deploy",
    description="Deploy action",
    runs=CompositeRuns(steps=[Step(run="echo deploy", shell="bash")]),
)
''')

        output_dir = tmp_path / "output"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_github.cli",
                "action",
                "build",
                str(actions_dir),
                "-o",
                str(output_dir),
            ],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}\nstdout: {result.stdout}"

        # Should create multiple action files
        action_files = list(output_dir.glob("**/action.yml")) + list(
            output_dir.glob("**/action.yaml")
        )
        assert len(action_files) >= 2

    def test_action_build_creates_output_directory(self, tmp_path):
        """action build creates output directory if it doesn't exist."""
        actions_dir = tmp_path / "actions"
        actions_dir.mkdir()
        (actions_dir / "__init__.py").write_text("")

        (actions_dir / "action.py").write_text('''
from wetwire_github.composite import CompositeAction, CompositeRuns
from wetwire_github.workflow import Step

test_action = CompositeAction(
    name="Test",
    description="Test",
    runs=CompositeRuns(steps=[Step(run="echo test", shell="bash")]),
)
''')

        output_dir = tmp_path / "does" / "not" / "exist"
        assert not output_dir.exists()

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_github.cli",
                "action",
                "build",
                str(actions_dir),
                "-o",
                str(output_dir),
            ],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert output_dir.exists()

    def test_action_build_error_no_actions_found(self, tmp_path):
        """action build reports error when no actions found."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        (empty_dir / "__init__.py").write_text("")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_github.cli",
                "action",
                "build",
                str(empty_dir),
            ],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        # Should indicate no actions found
        assert (
            result.returncode != 0
            or "no action" in result.stdout.lower()
            or "no action" in result.stderr.lower()
        )

    def test_action_build_organizes_by_action_name(self, tmp_path):
        """action build organizes output into subdirectories by action name."""
        actions_dir = tmp_path / "actions"
        actions_dir.mkdir()
        (actions_dir / "__init__.py").write_text("")

        (actions_dir / "actions.py").write_text('''
from wetwire_github.composite import CompositeAction, CompositeRuns
from wetwire_github.workflow import Step

setup_tool = CompositeAction(
    name="Setup Tool",
    description="Setup",
    runs=CompositeRuns(steps=[Step(run="echo setup", shell="bash")]),
)

deploy_app = CompositeAction(
    name="Deploy App",
    description="Deploy",
    runs=CompositeRuns(steps=[Step(run="echo deploy", shell="bash")]),
)
''')

        output_dir = tmp_path / "output"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_github.cli",
                "action",
                "build",
                str(actions_dir),
                "-o",
                str(output_dir),
            ],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"

        # Should create subdirectories for each action
        # e.g., output/setup_tool/action.yml and output/deploy_app/action.yml
        setup_dir = output_dir / "setup_tool"
        deploy_dir = output_dir / "deploy_app"

        assert setup_dir.exists() or (output_dir / "setup-tool").exists()
        assert deploy_dir.exists() or (output_dir / "deploy-app").exists()

    def test_action_build_default_output_directory(self, tmp_path):
        """action build uses current directory as default output."""
        actions_dir = tmp_path / "actions"
        actions_dir.mkdir()
        (actions_dir / "__init__.py").write_text("")

        (actions_dir / "action.py").write_text('''
from wetwire_github.composite import CompositeAction, CompositeRuns
from wetwire_github.workflow import Step

test = CompositeAction(
    name="Test",
    description="Test",
    runs=CompositeRuns(steps=[Step(run="echo test", shell="bash")]),
)
''')

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_github.cli",
                "action",
                "build",
                str(actions_dir),
            ],
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"

        # Should create action.yml in default location (current dir or organized structure)
        action_files = list(tmp_path.glob("**/action.yml")) + list(
            tmp_path.glob("**/action.yaml")
        )
        assert len(action_files) >= 1
