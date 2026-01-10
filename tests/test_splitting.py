"""Tests for file splitting utilities."""


from wetwire_github.linter.splitting import (
    JOB_CATEGORIES,
    MAX_JOBS_PER_FILE,
    JobInfo,
    categorize_job,
    suggest_workflow_splits,
)


class TestJobCategories:
    """Tests for job categorization."""

    def test_build_job_categorized_as_ci(self):
        """Build jobs go to ci category."""
        assert categorize_job("build") == "ci"
        assert categorize_job("build_linux") == "ci"
        assert categorize_job("Build") == "ci"

    def test_test_job_categorized_as_ci(self):
        """Test jobs go to ci category."""
        assert categorize_job("test") == "ci"
        assert categorize_job("unit_tests") == "ci"
        assert categorize_job("integration-test") == "ci"

    def test_lint_job_categorized_as_ci(self):
        """Lint jobs go to ci category."""
        assert categorize_job("lint") == "ci"
        assert categorize_job("lint_check") == "ci"
        assert categorize_job("type-check") == "ci"

    def test_deploy_job_categorized_as_deploy(self):
        """Deploy jobs go to deploy category."""
        assert categorize_job("deploy") == "deploy"
        assert categorize_job("deploy_production") == "deploy"
        assert categorize_job("deploy-staging") == "deploy"

    def test_release_job_categorized_as_release(self):
        """Release jobs go to release category."""
        assert categorize_job("release") == "release"
        assert categorize_job("publish") == "release"
        assert categorize_job("publish_npm") == "release"

    def test_security_job_categorized_as_security(self):
        """Security jobs go to security category."""
        assert categorize_job("security_scan") == "security"
        assert categorize_job("codeql") == "security"
        assert categorize_job("dependabot") == "security"
        assert categorize_job("vulnerability_check") == "security"

    def test_maintenance_job_categorized_as_maintenance(self):
        """Maintenance jobs go to maintenance category."""
        assert categorize_job("cleanup") == "maintenance"
        assert categorize_job("stale") == "maintenance"
        assert categorize_job("prune_cache") == "maintenance"

    def test_unknown_job_categorized_as_main(self):
        """Unknown jobs go to main category."""
        assert categorize_job("custom_job") == "main"
        assert categorize_job("workflow_xyz") == "main"


class TestJobCategoriesWithSteps:
    """Tests for job categorization based on step content."""

    def test_job_with_checkout_and_run_tests_is_ci(self):
        """Jobs that run tests should be categorized as ci."""
        job = JobInfo(
            name="custom",
            steps=["actions/checkout@v4", "pytest", "npm test"],
            dependencies=set(),
        )
        assert categorize_job(job.name, job.steps) == "ci"

    def test_job_with_deploy_action_is_deploy(self):
        """Jobs that deploy should be categorized as deploy."""
        job = JobInfo(
            name="custom",
            steps=["actions/checkout@v4", "aws-actions/configure-aws-credentials", "cdk deploy"],
            dependencies=set(),
        )
        assert categorize_job(job.name, job.steps) == "deploy"

    def test_job_with_publish_action_is_release(self):
        """Jobs that publish packages should be categorized as release."""
        job = JobInfo(
            name="custom",
            steps=["actions/checkout@v4", "npm publish", "twine upload"],
            dependencies=set(),
        )
        assert categorize_job(job.name, job.steps) == "release"


class TestSuggestWorkflowSplits:
    """Tests for workflow splitting suggestions."""

    def test_small_workflow_no_split(self):
        """Small workflows don't need splitting."""
        jobs = [
            JobInfo("build", "AWS::S3::Bucket", set()),
            JobInfo("test", "AWS::S3::Bucket", set()),
        ]
        splits = suggest_workflow_splits(jobs, max_per_file=15)

        # Should have fewer entries than job count (jobs grouped)
        assert len(splits) <= len(jobs)

    def test_large_workflow_splits_by_category(self):
        """Large workflows split by category."""
        jobs = [
            JobInfo("build", "", set()),
            JobInfo("test", "", set()),
            JobInfo("lint", "", set()),
            JobInfo("deploy_staging", "", set()),
            JobInfo("deploy_prod", "", set()),
            JobInfo("publish", "", set()),
            JobInfo("security_scan", "", set()),
            JobInfo("cleanup", "", set()),
        ]
        splits = suggest_workflow_splits(jobs, max_per_file=3)

        # Should split into multiple categories
        assert len(splits) > 1
        # CI jobs should be together
        assert any("ci" in k.lower() for k in splits.keys())

    def test_splits_contain_all_jobs(self):
        """All jobs should appear in splits exactly once."""
        jobs = [
            JobInfo("build", "", set()),
            JobInfo("test", "", set()),
            JobInfo("deploy", "", set()),
            JobInfo("release", "", set()),
        ]
        splits = suggest_workflow_splits(jobs)

        all_assigned = []
        for job_list in splits.values():
            all_assigned.extend(job_list)

        assert sorted(all_assigned) == sorted([j.name for j in jobs])

    def test_respects_max_per_file(self):
        """Each file should have at most max_per_file jobs."""
        jobs = [JobInfo(f"job_{i}", "", set()) for i in range(20)]
        splits = suggest_workflow_splits(jobs, max_per_file=5)

        for job_list in splits.values():
            assert len(job_list) <= 5


class TestJobInfo:
    """Tests for JobInfo dataclass."""

    def test_job_info_creation(self):
        """JobInfo can be created."""
        job = JobInfo("build", "run tests", {"checkout"})

        assert job.name == "build"
        assert job.steps == "run tests"
        assert job.dependencies == {"checkout"}


class TestConstants:
    """Tests for module constants."""

    def test_max_jobs_per_file_is_reasonable(self):
        """MAX_JOBS_PER_FILE should be a reasonable value."""
        assert MAX_JOBS_PER_FILE >= 5
        assert MAX_JOBS_PER_FILE <= 20

    def test_job_categories_exists(self):
        """JOB_CATEGORIES module constant should exist."""
        # JOB_CATEGORIES may be empty if using keyword patterns
        # Just verify it's a dict (or dict-like)
        assert isinstance(JOB_CATEGORIES, dict)


class TestWAG007Integration:
    """Tests for WAG007 integration with splitting utilities."""

    def test_wag007_provides_split_suggestions(self):
        """WAG007 should provide split suggestions for large files."""
        from wetwire_github.linter.rules import WAG007FileTooLarge

        rule = WAG007FileTooLarge(max_jobs=3)

        source = '''
from wetwire_github.workflow import Job, Step

build_job = Job(runs_on="ubuntu-latest", steps=[])
test_job = Job(runs_on="ubuntu-latest", steps=[])
lint_job = Job(runs_on="ubuntu-latest", steps=[])
deploy_staging = Job(runs_on="ubuntu-latest", steps=[])
deploy_production = Job(runs_on="ubuntu-latest", steps=[])
'''

        errors = rule.check(source, "test.py")

        assert len(errors) == 1
        error = errors[0]
        assert "WAG007" in error.rule_id
        assert "5" in error.message  # 5 jobs
        assert "ci" in error.message.lower()  # Should suggest ci.py
        assert "deploy" in error.message.lower()  # Should suggest deploy.py
