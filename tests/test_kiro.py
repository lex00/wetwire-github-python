"""Tests for Kiro CLI integration."""

from pathlib import Path


class TestKiroModuleImports:
    """Tests for Kiro module imports."""

    def test_kiro_module_exists(self):
        """Test that kiro module can be imported."""
        from wetwire_github import kiro

        assert kiro is not None

    def test_install_kiro_configs_exists(self):
        """Test that install_kiro_configs function exists."""
        from wetwire_github.kiro import install_kiro_configs

        assert callable(install_kiro_configs)

    def test_launch_kiro_exists(self):
        """Test that launch_kiro function exists."""
        from wetwire_github.kiro import launch_kiro

        assert callable(launch_kiro)

    def test_check_kiro_installed_exists(self):
        """Test that check_kiro_installed function exists."""
        from wetwire_github.kiro import check_kiro_installed

        assert callable(check_kiro_installed)

    def test_run_kiro_scenario_exists(self):
        """Test that run_kiro_scenario function exists."""
        from wetwire_github.kiro import run_kiro_scenario

        assert callable(run_kiro_scenario)


class TestKiroInstaller:
    """Tests for Kiro installer functions."""

    def test_get_agent_config_path(self):
        """Test agent config path is in home directory."""
        from wetwire_github.kiro.installer import get_agent_config_path

        path = get_agent_config_path()
        assert path.name == "wetwire-github-runner.json"
        assert ".kiro" in str(path)
        assert "agents" in str(path)

    def test_get_mcp_config_path_default(self):
        """Test MCP config path defaults to current directory."""
        from wetwire_github.kiro.installer import get_mcp_config_path

        path = get_mcp_config_path()
        assert path.name == "mcp.json"
        assert ".kiro" in str(path)

    def test_get_mcp_config_path_with_project(self, tmp_path: Path):
        """Test MCP config path with project directory."""
        from wetwire_github.kiro.installer import get_mcp_config_path

        path = get_mcp_config_path(tmp_path)
        assert path == tmp_path / ".kiro" / "mcp.json"

    def test_check_kiro_installed_returns_bool(self):
        """Test check_kiro_installed returns a boolean."""
        from wetwire_github.kiro.installer import check_kiro_installed

        result = check_kiro_installed()
        assert isinstance(result, bool)

    def test_install_agent_config_creates_file(self, tmp_path: Path, monkeypatch):
        """Test install_agent_config creates the config file."""
        from wetwire_github.kiro.installer import install_agent_config

        # Patch home directory to temp path
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        result = install_agent_config(force=True)

        assert result is True
        config_path = fake_home / ".kiro" / "agents" / "wetwire-github-runner.json"
        assert config_path.exists()

    def test_install_mcp_config_creates_file(self, tmp_path: Path):
        """Test install_mcp_config creates the config file."""
        from wetwire_github.kiro.installer import install_mcp_config

        result = install_mcp_config(project_dir=tmp_path, force=True)

        assert result is True
        config_path = tmp_path / ".kiro" / "mcp.json"
        assert config_path.exists()

    def test_install_mcp_config_skips_existing(self, tmp_path: Path):
        """Test install_mcp_config skips if already configured."""
        import json

        from wetwire_github.kiro.installer import install_mcp_config

        # Pre-create config with wetwire-github-mcp
        kiro_dir = tmp_path / ".kiro"
        kiro_dir.mkdir()
        config_path = kiro_dir / "mcp.json"
        config_path.write_text(json.dumps({
            "mcpServers": {"wetwire-github-mcp": {"command": "test"}}
        }))

        result = install_mcp_config(project_dir=tmp_path, force=False)

        assert result is False

    def test_install_kiro_configs_returns_dict(self, tmp_path: Path, monkeypatch):
        """Test install_kiro_configs returns status dict."""
        from wetwire_github.kiro.installer import install_kiro_configs

        # Patch home directory
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        result = install_kiro_configs(project_dir=tmp_path, force=True)

        assert isinstance(result, dict)
        assert "agent" in result
        assert "mcp" in result
        assert result["agent"] is True
        assert result["mcp"] is True


class TestAgentConfig:
    """Tests for agent configuration."""

    def test_agent_config_has_required_fields(self):
        """Test AGENT_CONFIG has required fields."""
        from wetwire_github.kiro.installer import AGENT_CONFIG

        assert "name" in AGENT_CONFIG
        assert "description" in AGENT_CONFIG
        assert "prompt" in AGENT_CONFIG
        assert AGENT_CONFIG["name"] == "wetwire-github-runner"

    def test_agent_config_prompt_mentions_github(self):
        """Test agent prompt mentions GitHub Actions."""
        from wetwire_github.kiro.installer import AGENT_CONFIG

        prompt = AGENT_CONFIG["prompt"]
        assert "GitHub" in prompt or "github" in prompt.lower()

    def test_agent_config_mentions_lint_rules(self):
        """Test agent prompt mentions lint rules."""
        from wetwire_github.kiro.installer import AGENT_CONFIG

        prompt = AGENT_CONFIG["prompt"]
        assert "WAG001" in prompt or "lint" in prompt.lower()


class TestLaunchKiro:
    """Tests for launch_kiro function."""

    def test_launch_kiro_returns_error_if_not_installed(self, capsys):
        """Test launch_kiro returns error if Kiro not installed."""
        import wetwire_github.kiro.installer as installer
        from wetwire_github.kiro.installer import launch_kiro

        # Mock check to return False
        original_check = installer.check_kiro_installed
        installer.check_kiro_installed = lambda: False

        try:
            result = launch_kiro()
            assert result == 1
            captured = capsys.readouterr()
            assert "not found" in captured.err.lower()
        finally:
            installer.check_kiro_installed = original_check


class TestRunKiroScenario:
    """Tests for run_kiro_scenario function."""

    def test_run_kiro_scenario_returns_error_if_not_installed(self):
        """Test run_kiro_scenario returns error if Kiro not installed."""
        import wetwire_github.kiro.installer as installer
        from wetwire_github.kiro.installer import run_kiro_scenario

        # Mock check to return False
        original_check = installer.check_kiro_installed
        installer.check_kiro_installed = lambda: False

        try:
            result = run_kiro_scenario("Create a CI workflow")
            assert result["success"] is False
            assert "not found" in result["stderr"].lower()
        finally:
            installer.check_kiro_installed = original_check

    def test_run_kiro_scenario_returns_dict(self):
        """Test run_kiro_scenario returns expected dict structure."""
        import wetwire_github.kiro.installer as installer
        from wetwire_github.kiro.installer import run_kiro_scenario

        # Mock to avoid actual execution
        original_check = installer.check_kiro_installed
        installer.check_kiro_installed = lambda: False

        try:
            result = run_kiro_scenario("test")
            assert isinstance(result, dict)
            assert "success" in result
            assert "exit_code" in result
            assert "stdout" in result
            assert "stderr" in result
            assert "workflow_valid" in result
        finally:
            installer.check_kiro_installed = original_check


class TestKiroCLI:
    """Tests for Kiro CLI command."""

    def test_kiro_command_exists(self):
        """Test kiro command is registered in CLI."""
        from wetwire_github.cli.main import create_parser

        parser = create_parser()
        # Check that kiro is a valid subcommand
        args = parser.parse_args(["kiro", "--install-only"])
        assert args.command == "kiro"
        assert args.install_only is True

    def test_kiro_install_only_option(self, tmp_path: Path, monkeypatch):
        """Test --install-only installs configs without launching."""
        from wetwire_github.cli.main import main

        # Patch home directory
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        monkeypatch.setattr(Path, "home", lambda: fake_home)
        monkeypatch.chdir(tmp_path)

        # Run with --install-only
        exit_code = main(["kiro", "--install-only", "--force"])

        assert exit_code == 0
        # Check that configs were created
        agent_path = fake_home / ".kiro" / "agents" / "wetwire-github-runner.json"
        assert agent_path.exists()

    def test_kiro_force_option(self, tmp_path: Path, monkeypatch):
        """Test --force reinstalls existing configs."""
        import json

        from wetwire_github.cli.main import main

        # Patch home directory
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        monkeypatch.setattr(Path, "home", lambda: fake_home)
        monkeypatch.chdir(tmp_path)

        # Pre-create a config
        agent_dir = fake_home / ".kiro" / "agents"
        agent_dir.mkdir(parents=True)
        agent_path = agent_dir / "wetwire-github-runner.json"
        agent_path.write_text(json.dumps({"old": "config"}))

        # Run with --force
        exit_code = main(["kiro", "--install-only", "--force"])

        assert exit_code == 0
        # Check that config was updated
        new_config = json.loads(agent_path.read_text())
        assert "name" in new_config
        assert new_config["name"] == "wetwire-github-runner"
