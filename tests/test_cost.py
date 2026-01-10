"""Tests for workflow cost estimation module."""

import pytest

from wetwire_github.cost import CostCalculator, CostEstimate, RunnerCost
from wetwire_github.workflow import Job, Matrix, Strategy, Workflow


class TestRunnerCost:
    """Tests for RunnerCost dataclass."""

    def test_default_pricing(self):
        """RunnerCost has default GitHub Actions pricing."""
        cost = RunnerCost()
        assert cost.linux_per_minute == 0.008
        assert cost.windows_per_minute == 0.016
        assert cost.macos_per_minute == 0.08

    def test_custom_pricing(self):
        """RunnerCost accepts custom pricing."""
        cost = RunnerCost(
            linux_per_minute=0.01, windows_per_minute=0.02, macos_per_minute=0.10
        )
        assert cost.linux_per_minute == 0.01
        assert cost.windows_per_minute == 0.02
        assert cost.macos_per_minute == 0.10


class TestCostEstimate:
    """Tests for CostEstimate dataclass."""

    def test_cost_estimate_creation(self):
        """CostEstimate can be created with basic fields."""
        estimate = CostEstimate(
            total_cost=1.0,
            linux_minutes=100,
            windows_minutes=50,
            macos_minutes=10,
        )
        assert estimate.total_cost == 1.0
        assert estimate.linux_minutes == 100
        assert estimate.windows_minutes == 50
        assert estimate.macos_minutes == 10

    def test_cost_estimate_with_job_estimates(self):
        """CostEstimate can include per-job breakdown."""
        estimate = CostEstimate(
            total_cost=1.0, job_estimates={"build": 0.5, "test": 0.5}
        )
        assert estimate.job_estimates == {"build": 0.5, "test": 0.5}

    def test_cost_estimate_defaults(self):
        """CostEstimate has zero defaults for minute counts."""
        estimate = CostEstimate(total_cost=0.0)
        assert estimate.linux_minutes == 0
        assert estimate.windows_minutes == 0
        assert estimate.macos_minutes == 0
        assert estimate.job_estimates == {}


class TestCostCalculator:
    """Tests for CostCalculator class."""

    def test_calculator_with_default_runner_cost(self):
        """CostCalculator uses default RunnerCost if not provided."""
        calc = CostCalculator()
        assert calc.runner_cost.linux_per_minute == 0.008

    def test_calculator_with_custom_runner_cost(self):
        """CostCalculator accepts custom RunnerCost."""
        custom_cost = RunnerCost(linux_per_minute=0.01)
        calc = CostCalculator(runner_cost=custom_cost)
        assert calc.runner_cost.linux_per_minute == 0.01

    def test_estimate_single_linux_job(self):
        """CostCalculator estimates cost for single Linux job."""
        workflow = Workflow(
            name="CI",
            jobs={
                "build": Job(name="build", runs_on="ubuntu-latest", timeout_minutes=10)
            },
        )
        calc = CostCalculator()
        estimate = calc.estimate(workflow)

        assert estimate.linux_minutes == 10
        assert estimate.windows_minutes == 0
        assert estimate.macos_minutes == 0
        assert estimate.total_cost == 10 * 0.008  # 0.08
        assert estimate.job_estimates["build"] == 10 * 0.008

    def test_estimate_windows_job(self):
        """CostCalculator estimates cost for Windows job."""
        workflow = Workflow(
            name="CI",
            jobs={
                "build": Job(name="build", runs_on="windows-latest", timeout_minutes=20)
            },
        )
        calc = CostCalculator()
        estimate = calc.estimate(workflow)

        assert estimate.linux_minutes == 0
        assert estimate.windows_minutes == 20
        assert estimate.macos_minutes == 0
        assert estimate.total_cost == 20 * 0.016  # 0.32
        assert estimate.job_estimates["build"] == 20 * 0.016

    def test_estimate_macos_job(self):
        """CostCalculator estimates cost for macOS job."""
        workflow = Workflow(
            name="CI",
            jobs={
                "build": Job(name="build", runs_on="macos-latest", timeout_minutes=5)
            },
        )
        calc = CostCalculator()
        estimate = calc.estimate(workflow)

        assert estimate.linux_minutes == 0
        assert estimate.windows_minutes == 0
        assert estimate.macos_minutes == 5
        assert estimate.total_cost == 5 * 0.08  # 0.40
        assert estimate.job_estimates["build"] == 5 * 0.08

    def test_estimate_multiple_jobs(self):
        """CostCalculator estimates cost for multiple jobs."""
        workflow = Workflow(
            name="CI",
            jobs={
                "build": Job(name="build", runs_on="ubuntu-latest", timeout_minutes=10),
                "test": Job(name="test", runs_on="windows-latest", timeout_minutes=15),
                "deploy": Job(name="deploy", runs_on="macos-latest", timeout_minutes=5),
            },
        )
        calc = CostCalculator()
        estimate = calc.estimate(workflow)

        assert estimate.linux_minutes == 10
        assert estimate.windows_minutes == 15
        assert estimate.macos_minutes == 5
        expected_total = (10 * 0.008) + (15 * 0.016) + (5 * 0.08)
        assert estimate.total_cost == pytest.approx(expected_total)
        assert estimate.job_estimates["build"] == 10 * 0.008
        assert estimate.job_estimates["test"] == 15 * 0.016
        assert estimate.job_estimates["deploy"] == 5 * 0.08

    def test_estimate_with_default_timeout(self):
        """CostCalculator uses default timeout when job has no timeout."""
        workflow = Workflow(
            name="CI",
            jobs={"build": Job(name="build", runs_on="ubuntu-latest")},
        )
        calc = CostCalculator()
        estimate = calc.estimate(workflow, default_timeout=30)

        assert estimate.linux_minutes == 30
        assert estimate.total_cost == 30 * 0.008

    def test_estimate_matrix_build(self):
        """CostCalculator estimates cost for matrix builds."""
        matrix = Matrix(
            values={"os": ["ubuntu-latest", "windows-latest", "macos-latest"]}
        )
        strategy = Strategy(matrix=matrix)
        workflow = Workflow(
            name="CI",
            jobs={
                "test": Job(
                    name="test",
                    runs_on="${{ matrix.os }}",
                    strategy=strategy,
                    timeout_minutes=10,
                )
            },
        )
        calc = CostCalculator()
        estimate = calc.estimate(workflow)

        # Each OS runs once: 1x Linux, 1x Windows, 1x macOS
        assert estimate.linux_minutes == 10
        assert estimate.windows_minutes == 10
        assert estimate.macos_minutes == 10
        expected_total = (10 * 0.008) + (10 * 0.016) + (10 * 0.08)
        assert estimate.total_cost == pytest.approx(expected_total)

    def test_estimate_matrix_build_multiple_dimensions(self):
        """CostCalculator estimates cost for multi-dimensional matrix."""
        matrix = Matrix(
            values={
                "os": ["ubuntu-latest", "windows-latest"],
                "python": ["3.10", "3.11", "3.12"],
            }
        )
        strategy = Strategy(matrix=matrix)
        workflow = Workflow(
            name="CI",
            jobs={
                "test": Job(
                    name="test",
                    runs_on="${{ matrix.os }}",
                    strategy=strategy,
                    timeout_minutes=5,
                )
            },
        )
        calc = CostCalculator()
        estimate = calc.estimate(workflow)

        # 2 OSes × 3 Python versions = 6 jobs
        # 3 runs on ubuntu-latest, 3 runs on windows-latest
        assert estimate.linux_minutes == 15  # 3 runs × 5 minutes
        assert estimate.windows_minutes == 15  # 3 runs × 5 minutes
        assert estimate.macos_minutes == 0
        expected_total = (15 * 0.008) + (15 * 0.016)
        assert estimate.total_cost == pytest.approx(expected_total)

    def test_estimate_empty_workflow(self):
        """CostCalculator handles empty workflow."""
        workflow = Workflow(name="CI")
        calc = CostCalculator()
        estimate = calc.estimate(workflow)

        assert estimate.total_cost == 0.0
        assert estimate.linux_minutes == 0
        assert estimate.windows_minutes == 0
        assert estimate.macos_minutes == 0
        assert estimate.job_estimates == {}

    def test_estimate_ubuntu_variations(self):
        """CostCalculator recognizes ubuntu runner variations."""
        workflow = Workflow(
            name="CI",
            jobs={
                "ubuntu_20": Job(
                    name="ubuntu_20", runs_on="ubuntu-20.04", timeout_minutes=5
                ),
                "ubuntu_22": Job(
                    name="ubuntu_22", runs_on="ubuntu-22.04", timeout_minutes=5
                ),
                "ubuntu_24": Job(
                    name="ubuntu_24", runs_on="ubuntu-24.04", timeout_minutes=5
                ),
            },
        )
        calc = CostCalculator()
        estimate = calc.estimate(workflow)

        assert estimate.linux_minutes == 15
        assert estimate.total_cost == 15 * 0.008

    def test_estimate_windows_variations(self):
        """CostCalculator recognizes Windows runner variations."""
        workflow = Workflow(
            name="CI",
            jobs={
                "win_2019": Job(
                    name="win_2019", runs_on="windows-2019", timeout_minutes=10
                ),
                "win_2022": Job(
                    name="win_2022", runs_on="windows-2022", timeout_minutes=10
                ),
            },
        )
        calc = CostCalculator()
        estimate = calc.estimate(workflow)

        assert estimate.windows_minutes == 20
        assert estimate.total_cost == 20 * 0.016

    def test_estimate_macos_variations(self):
        """CostCalculator recognizes macOS runner variations."""
        workflow = Workflow(
            name="CI",
            jobs={
                "macos_12": Job(
                    name="macos_12", runs_on="macos-12", timeout_minutes=10
                ),
                "macos_13": Job(
                    name="macos_13", runs_on="macos-13", timeout_minutes=10
                ),
                "macos_14": Job(
                    name="macos_14", runs_on="macos-14", timeout_minutes=10
                ),
            },
        )
        calc = CostCalculator()
        estimate = calc.estimate(workflow)

        assert estimate.macos_minutes == 30
        assert estimate.total_cost == 30 * 0.08

    def test_estimate_with_matrix_exclude(self):
        """CostCalculator accounts for matrix excludes."""
        matrix = Matrix(
            values={
                "os": ["ubuntu-latest", "windows-latest", "macos-latest"],
                "python": ["3.10", "3.11"],
            },
            exclude=[{"os": "macos-latest", "python": "3.10"}],
        )
        strategy = Strategy(matrix=matrix)
        workflow = Workflow(
            name="CI",
            jobs={
                "test": Job(
                    name="test",
                    runs_on="${{ matrix.os }}",
                    strategy=strategy,
                    timeout_minutes=10,
                )
            },
        )
        calc = CostCalculator()
        estimate = calc.estimate(workflow)

        # 3 OSes × 2 Python versions = 6 total
        # Minus 1 exclude (macos-latest + python 3.10) = 5 jobs
        # ubuntu: 2 runs, windows: 2 runs, macos: 1 run
        assert estimate.linux_minutes == 20
        assert estimate.windows_minutes == 20
        assert estimate.macos_minutes == 10
        expected_total = (20 * 0.008) + (20 * 0.016) + (10 * 0.08)
        assert estimate.total_cost == pytest.approx(expected_total)

    def test_estimate_with_matrix_include(self):
        """CostCalculator accounts for matrix includes."""
        matrix = Matrix(
            values={"os": ["ubuntu-latest"], "python": ["3.10", "3.11"]},
            include=[{"os": "windows-latest", "python": "3.12"}],
        )
        strategy = Strategy(matrix=matrix)
        workflow = Workflow(
            name="CI",
            jobs={
                "test": Job(
                    name="test",
                    runs_on="${{ matrix.os }}",
                    strategy=strategy,
                    timeout_minutes=10,
                )
            },
        )
        calc = CostCalculator()
        estimate = calc.estimate(workflow)

        # Base: ubuntu × 2 python = 2 jobs
        # Include: windows × 1 = 1 job
        # Total: 2 ubuntu + 1 windows
        assert estimate.linux_minutes == 20
        assert estimate.windows_minutes == 10
        expected_total = (20 * 0.008) + (10 * 0.016)
        assert estimate.total_cost == pytest.approx(expected_total)
