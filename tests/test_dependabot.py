"""Tests for Dependabot configuration support."""

import yaml


class TestDependabotTypes:
    """Tests for Dependabot dataclass types."""

    def test_dependabot_dataclass_exists(self):
        """Dependabot dataclass can be imported."""
        from wetwire_github.dependabot import Dependabot

        assert Dependabot is not None

    def test_update_dataclass_exists(self):
        """Update dataclass can be imported."""
        from wetwire_github.dependabot import Update

        assert Update is not None

    def test_schedule_dataclass_exists(self):
        """Schedule dataclass can be imported."""
        from wetwire_github.dependabot import Schedule

        assert Schedule is not None

    def test_package_ecosystem_enum_exists(self):
        """PackageEcosystem enum can be imported."""
        from wetwire_github.dependabot import PackageEcosystem

        assert PackageEcosystem is not None

    def test_registries_dataclass_exists(self):
        """Registries dataclass can be imported."""
        from wetwire_github.dependabot import Registry

        assert Registry is not None

    def test_groups_dataclass_exists(self):
        """Groups dataclass can be imported."""
        from wetwire_github.dependabot import Group

        assert Group is not None


class TestPackageEcosystem:
    """Tests for PackageEcosystem enum."""

    def test_npm_ecosystem(self):
        """npm ecosystem is defined."""
        from wetwire_github.dependabot import PackageEcosystem

        assert PackageEcosystem.NPM.value == "npm"

    def test_pip_ecosystem(self):
        """pip ecosystem is defined."""
        from wetwire_github.dependabot import PackageEcosystem

        assert PackageEcosystem.PIP.value == "pip"

    def test_bundler_ecosystem(self):
        """bundler ecosystem is defined."""
        from wetwire_github.dependabot import PackageEcosystem

        assert PackageEcosystem.BUNDLER.value == "bundler"

    def test_docker_ecosystem(self):
        """docker ecosystem is defined."""
        from wetwire_github.dependabot import PackageEcosystem

        assert PackageEcosystem.DOCKER.value == "docker"

    def test_github_actions_ecosystem(self):
        """github-actions ecosystem is defined."""
        from wetwire_github.dependabot import PackageEcosystem

        assert PackageEcosystem.GITHUB_ACTIONS.value == "github-actions"

    def test_cargo_ecosystem(self):
        """cargo ecosystem is defined."""
        from wetwire_github.dependabot import PackageEcosystem

        assert PackageEcosystem.CARGO.value == "cargo"

    def test_gomod_ecosystem(self):
        """gomod ecosystem is defined."""
        from wetwire_github.dependabot import PackageEcosystem

        assert PackageEcosystem.GOMOD.value == "gomod"


class TestSchedule:
    """Tests for Schedule dataclass."""

    def test_daily_schedule(self):
        """Daily schedule can be created."""
        from wetwire_github.dependabot import Schedule

        schedule = Schedule(interval="daily")
        assert schedule.interval == "daily"

    def test_weekly_schedule(self):
        """Weekly schedule can be created."""
        from wetwire_github.dependabot import Schedule

        schedule = Schedule(interval="weekly", day="monday")
        assert schedule.interval == "weekly"
        assert schedule.day == "monday"

    def test_monthly_schedule(self):
        """Monthly schedule can be created."""
        from wetwire_github.dependabot import Schedule

        schedule = Schedule(interval="monthly")
        assert schedule.interval == "monthly"

    def test_schedule_with_time(self):
        """Schedule with time can be created."""
        from wetwire_github.dependabot import Schedule

        schedule = Schedule(interval="daily", time="09:00")
        assert schedule.time == "09:00"

    def test_schedule_with_timezone(self):
        """Schedule with timezone can be created."""
        from wetwire_github.dependabot import Schedule

        schedule = Schedule(interval="daily", timezone="America/New_York")
        assert schedule.timezone == "America/New_York"


class TestUpdate:
    """Tests for Update dataclass."""

    def test_basic_update(self):
        """Basic update can be created."""
        from wetwire_github.dependabot import PackageEcosystem, Schedule, Update

        update = Update(
            package_ecosystem=PackageEcosystem.NPM,
            directory="/",
            schedule=Schedule(interval="daily"),
        )
        assert update.package_ecosystem == PackageEcosystem.NPM
        assert update.directory == "/"

    def test_update_with_open_pull_requests_limit(self):
        """Update with open-pull-requests-limit can be created."""
        from wetwire_github.dependabot import PackageEcosystem, Schedule, Update

        update = Update(
            package_ecosystem=PackageEcosystem.PIP,
            directory="/",
            schedule=Schedule(interval="weekly"),
            open_pull_requests_limit=5,
        )
        assert update.open_pull_requests_limit == 5

    def test_update_with_reviewers(self):
        """Update with reviewers can be created."""
        from wetwire_github.dependabot import PackageEcosystem, Schedule, Update

        update = Update(
            package_ecosystem=PackageEcosystem.NPM,
            directory="/",
            schedule=Schedule(interval="daily"),
            reviewers=["@user1", "@user2"],
        )
        assert update.reviewers == ["@user1", "@user2"]

    def test_update_with_assignees(self):
        """Update with assignees can be created."""
        from wetwire_github.dependabot import PackageEcosystem, Schedule, Update

        update = Update(
            package_ecosystem=PackageEcosystem.NPM,
            directory="/",
            schedule=Schedule(interval="daily"),
            assignees=["user1"],
        )
        assert update.assignees == ["user1"]

    def test_update_with_labels(self):
        """Update with labels can be created."""
        from wetwire_github.dependabot import PackageEcosystem, Schedule, Update

        update = Update(
            package_ecosystem=PackageEcosystem.NPM,
            directory="/",
            schedule=Schedule(interval="daily"),
            labels=["dependencies", "automerge"],
        )
        assert "dependencies" in update.labels

    def test_update_with_ignore(self):
        """Update with ignore patterns can be created."""
        from wetwire_github.dependabot import PackageEcosystem, Schedule, Update

        update = Update(
            package_ecosystem=PackageEcosystem.NPM,
            directory="/",
            schedule=Schedule(interval="daily"),
            ignore=[{"dependency_name": "lodash", "versions": [">= 5"]}],
        )
        assert len(update.ignore) == 1


class TestDependabot:
    """Tests for Dependabot dataclass."""

    def test_basic_dependabot(self):
        """Basic Dependabot config can be created."""
        from wetwire_github.dependabot import (
            Dependabot,
            PackageEcosystem,
            Schedule,
            Update,
        )

        config = Dependabot(
            version=2,
            updates=[
                Update(
                    package_ecosystem=PackageEcosystem.NPM,
                    directory="/",
                    schedule=Schedule(interval="daily"),
                )
            ],
        )
        assert config.version == 2
        assert len(config.updates) == 1

    def test_dependabot_with_registries(self):
        """Dependabot with registries can be created."""
        from wetwire_github.dependabot import (
            Dependabot,
            PackageEcosystem,
            Registry,
            Schedule,
            Update,
        )

        config = Dependabot(
            version=2,
            registries={
                "npm-private": Registry(
                    type="npm-registry",
                    url="https://npm.pkg.github.com",
                    token="${{ secrets.NPM_TOKEN }}",
                )
            },
            updates=[
                Update(
                    package_ecosystem=PackageEcosystem.NPM,
                    directory="/",
                    schedule=Schedule(interval="daily"),
                    registries=["npm-private"],
                )
            ],
        )
        assert "npm-private" in config.registries


class TestDependabotSerialization:
    """Tests for Dependabot YAML serialization."""

    def test_serialize_basic_dependabot(self):
        """Basic Dependabot config serializes to valid YAML."""
        from wetwire_github.dependabot import (
            Dependabot,
            PackageEcosystem,
            Schedule,
            Update,
        )
        from wetwire_github.serialize import to_dict

        config = Dependabot(
            version=2,
            updates=[
                Update(
                    package_ecosystem=PackageEcosystem.NPM,
                    directory="/",
                    schedule=Schedule(interval="daily"),
                )
            ],
        )

        result = to_dict(config)
        assert result["version"] == 2
        assert len(result["updates"]) == 1
        assert result["updates"][0]["package-ecosystem"] == "npm"

    def test_serialize_to_yaml_string(self):
        """Dependabot config can be converted to YAML string."""
        from wetwire_github.dependabot import (
            Dependabot,
            PackageEcosystem,
            Schedule,
            Update,
        )
        from wetwire_github.serialize import to_dict

        config = Dependabot(
            version=2,
            updates=[
                Update(
                    package_ecosystem=PackageEcosystem.NPM,
                    directory="/",
                    schedule=Schedule(interval="daily"),
                )
            ],
        )

        result = to_dict(config)
        yaml_str = yaml.dump(result, sort_keys=False)
        assert "version: 2" in yaml_str
        assert "package-ecosystem: npm" in yaml_str

    def test_serialize_schedule_with_day(self):
        """Schedule with day serializes correctly."""
        from wetwire_github.dependabot import (
            Dependabot,
            PackageEcosystem,
            Schedule,
            Update,
        )
        from wetwire_github.serialize import to_dict

        config = Dependabot(
            version=2,
            updates=[
                Update(
                    package_ecosystem=PackageEcosystem.NPM,
                    directory="/",
                    schedule=Schedule(interval="weekly", day="monday"),
                )
            ],
        )

        result = to_dict(config)
        schedule = result["updates"][0]["schedule"]
        assert schedule["interval"] == "weekly"
        assert schedule["day"] == "monday"


class TestDependabotCLIIntegration:
    """Tests for Dependabot CLI integration."""

    def test_build_type_dependabot_accepted(self):
        """Build command accepts --type dependabot."""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "build", "--help"],
            capture_output=True,
            text=True,
        )

        assert "dependabot" in result.stdout

    def test_import_type_dependabot_accepted(self):
        """Import command accepts --type dependabot."""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-m", "wetwire_github.cli", "import", "--help"],
            capture_output=True,
            text=True,
        )

        assert "dependabot" in result.stdout
