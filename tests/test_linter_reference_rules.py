"""Tests for reference graph tracking lint rules (WAG050-WAG053)."""

from wetwire_github.linter.rules import (
    WAG050UnusedJobOutputs,
    WAG051CircularJobDependencies,
    WAG052OrphanSecrets,
    WAG053StepOutputReferences,
)


class TestWAG050UnusedJobOutputs:
    """Tests for WAG050: Unused job outputs."""

    def test_detect_unused_job_output(self):
        """Detect job outputs that are never referenced by downstream jobs."""
        rule = WAG050UnusedJobOutputs()
        errors = rule.check(
            """
from wetwire_github.workflow import Workflow, Job, Step

build_job = Job(
    runs_on="ubuntu-latest",
    outputs={
        "version": "${{ steps.get_version.outputs.version }}",
        "unused_output": "${{ steps.other.outputs.value }}",
    },
    steps=[Step(run="echo test")],
)

deploy_job = Job(
    runs_on="ubuntu-latest",
    needs=["build"],
    steps=[
        Step(run="echo ${{ needs.build.outputs.version }}"),
    ],
)

workflow = Workflow(
    name="CI",
    on={"push": {}},
    jobs={"build": build_job, "deploy": deploy_job},
)
""",
            "test.py",
        )
        assert len(errors) == 1
        assert "unused_output" in errors[0].message
        assert "WAG050" == errors[0].rule_id

    def test_allow_all_outputs_referenced(self):
        """Allow when all job outputs are referenced."""
        rule = WAG050UnusedJobOutputs()
        errors = rule.check(
            """
from wetwire_github.workflow import Workflow, Job, Step

build_job = Job(
    runs_on="ubuntu-latest",
    outputs={
        "version": "${{ steps.get_version.outputs.version }}",
    },
    steps=[Step(run="echo test")],
)

deploy_job = Job(
    runs_on="ubuntu-latest",
    needs=["build"],
    steps=[
        Step(run="echo ${{ needs.build.outputs.version }}"),
    ],
)

workflow = Workflow(
    name="CI",
    on={"push": {}},
    jobs={"build": build_job, "deploy": deploy_job},
)
""",
            "test.py",
        )
        assert len(errors) == 0

    def test_allow_jobs_without_outputs(self):
        """Allow jobs that don't define outputs."""
        rule = WAG050UnusedJobOutputs()
        errors = rule.check(
            """
from wetwire_github.workflow import Workflow, Job, Step

build_job = Job(
    runs_on="ubuntu-latest",
    steps=[Step(run="make build")],
)

workflow = Workflow(
    name="CI",
    on={"push": {}},
    jobs={"build": build_job},
)
""",
            "test.py",
        )
        assert len(errors) == 0

    def test_detect_multiple_unused_outputs(self):
        """Detect multiple unused outputs across jobs."""
        rule = WAG050UnusedJobOutputs()
        errors = rule.check(
            """
from wetwire_github.workflow import Workflow, Job, Step

build_job = Job(
    runs_on="ubuntu-latest",
    outputs={
        "version": "${{ steps.ver.outputs.version }}",
        "sha": "${{ steps.sha.outputs.sha }}",
    },
    steps=[Step(run="echo test")],
)

test_job = Job(
    runs_on="ubuntu-latest",
    outputs={
        "coverage": "${{ steps.cov.outputs.coverage }}",
    },
    steps=[Step(run="pytest")],
)

workflow = Workflow(
    name="CI",
    on={"push": {}},
    jobs={"build": build_job, "test": test_job},
)
""",
            "test.py",
        )
        # All outputs are unused since no downstream job references them
        assert len(errors) >= 1


class TestWAG051CircularJobDependencies:
    """Tests for WAG051: Circular job dependencies."""

    def test_detect_direct_circular_dependency(self):
        """Detect direct circular dependency (A -> B -> A)."""
        rule = WAG051CircularJobDependencies()
        errors = rule.check(
            """
from wetwire_github.workflow import Workflow, Job, Step

job_a = Job(
    runs_on="ubuntu-latest",
    needs=["job_b"],
    steps=[Step(run="echo A")],
)

job_b = Job(
    runs_on="ubuntu-latest",
    needs=["job_a"],
    steps=[Step(run="echo B")],
)

workflow = Workflow(
    name="CI",
    on={"push": {}},
    jobs={"job_a": job_a, "job_b": job_b},
)
""",
            "test.py",
        )
        assert len(errors) >= 1
        assert "circular" in errors[0].message.lower()
        assert "WAG051" == errors[0].rule_id

    def test_detect_indirect_circular_dependency(self):
        """Detect indirect circular dependency (A -> B -> C -> A)."""
        rule = WAG051CircularJobDependencies()
        errors = rule.check(
            """
from wetwire_github.workflow import Workflow, Job, Step

job_a = Job(
    runs_on="ubuntu-latest",
    needs=["job_c"],
    steps=[Step(run="echo A")],
)

job_b = Job(
    runs_on="ubuntu-latest",
    needs=["job_a"],
    steps=[Step(run="echo B")],
)

job_c = Job(
    runs_on="ubuntu-latest",
    needs=["job_b"],
    steps=[Step(run="echo C")],
)

workflow = Workflow(
    name="CI",
    on={"push": {}},
    jobs={"job_a": job_a, "job_b": job_b, "job_c": job_c},
)
""",
            "test.py",
        )
        assert len(errors) >= 1
        assert "circular" in errors[0].message.lower()

    def test_allow_valid_dependency_chain(self):
        """Allow valid dependency chain without cycles."""
        rule = WAG051CircularJobDependencies()
        errors = rule.check(
            """
from wetwire_github.workflow import Workflow, Job, Step

build_job = Job(
    runs_on="ubuntu-latest",
    steps=[Step(run="make build")],
)

test_job = Job(
    runs_on="ubuntu-latest",
    needs=["build"],
    steps=[Step(run="make test")],
)

deploy_job = Job(
    runs_on="ubuntu-latest",
    needs=["test"],
    steps=[Step(run="make deploy")],
)

workflow = Workflow(
    name="CI",
    on={"push": {}},
    jobs={"build": build_job, "test": test_job, "deploy": deploy_job},
)
""",
            "test.py",
        )
        assert len(errors) == 0

    def test_allow_jobs_without_dependencies(self):
        """Allow independent jobs without dependencies."""
        rule = WAG051CircularJobDependencies()
        errors = rule.check(
            """
from wetwire_github.workflow import Workflow, Job, Step

job_a = Job(
    runs_on="ubuntu-latest",
    steps=[Step(run="echo A")],
)

job_b = Job(
    runs_on="ubuntu-latest",
    steps=[Step(run="echo B")],
)

workflow = Workflow(
    name="CI",
    on={"push": {}},
    jobs={"job_a": job_a, "job_b": job_b},
)
""",
            "test.py",
        )
        assert len(errors) == 0

    def test_detect_self_reference(self):
        """Detect job that depends on itself."""
        rule = WAG051CircularJobDependencies()
        errors = rule.check(
            """
from wetwire_github.workflow import Workflow, Job, Step

build_job = Job(
    runs_on="ubuntu-latest",
    needs=["build"],
    steps=[Step(run="make build")],
)

workflow = Workflow(
    name="CI",
    on={"push": {}},
    jobs={"build": build_job},
)
""",
            "test.py",
        )
        assert len(errors) >= 1
        assert "circular" in errors[0].message.lower()


class TestWAG052OrphanSecrets:
    """Tests for WAG052: Orphan secrets."""

    def test_detect_orphan_secret(self):
        """Detect secrets that are referenced but not used in any step."""
        rule = WAG052OrphanSecrets()
        errors = rule.check(
            """
from wetwire_github.workflow import Workflow, Job, Step
from wetwire_github.workflow.expressions import Secrets

# Secret referenced in job env but not used by any step
deploy_job = Job(
    runs_on="ubuntu-latest",
    env={
        "DEPLOY_TOKEN": Secrets.get("DEPLOY_TOKEN"),
        "UNUSED_SECRET": Secrets.get("UNUSED_SECRET"),
    },
    steps=[
        Step(run="echo $DEPLOY_TOKEN"),  # Only uses DEPLOY_TOKEN
    ],
)

workflow = Workflow(
    name="Deploy",
    on={"push": {}},
    jobs={"deploy": deploy_job},
)
""",
            "test.py",
        )
        assert len(errors) == 1
        assert "UNUSED_SECRET" in errors[0].message
        assert "WAG052" == errors[0].rule_id

    def test_allow_all_secrets_used(self):
        """Allow when all secrets are used in steps."""
        rule = WAG052OrphanSecrets()
        errors = rule.check(
            """
from wetwire_github.workflow import Workflow, Job, Step
from wetwire_github.workflow.expressions import Secrets

deploy_job = Job(
    runs_on="ubuntu-latest",
    steps=[
        Step(
            run="deploy.sh",
            env={"TOKEN": Secrets.get("DEPLOY_TOKEN")},
        ),
    ],
)

workflow = Workflow(
    name="Deploy",
    on={"push": {}},
    jobs={"deploy": deploy_job},
)
""",
            "test.py",
        )
        assert len(errors) == 0

    def test_detect_secret_in_workflow_env_not_used(self):
        """Detect secret defined in workflow env but not used by any job."""
        rule = WAG052OrphanSecrets()
        errors = rule.check(
            """
from wetwire_github.workflow import Workflow, Job, Step
from wetwire_github.workflow.expressions import Secrets

workflow = Workflow(
    name="CI",
    on={"push": {}},
    env={
        "GLOBAL_TOKEN": Secrets.get("GLOBAL_TOKEN"),
    },
    jobs={
        "build": Job(
            runs_on="ubuntu-latest",
            steps=[Step(run="make build")],  # Doesn't use GLOBAL_TOKEN
        ),
    },
)
""",
            "test.py",
        )
        assert len(errors) == 1
        assert "GLOBAL_TOKEN" in errors[0].message


class TestWAG053StepOutputReferences:
    """Tests for WAG053: Step output references."""

    def test_detect_invalid_step_id_reference(self):
        """Detect references to non-existent step IDs."""
        rule = WAG053StepOutputReferences()
        errors = rule.check(
            """
from wetwire_github.workflow import Job, Step

build_job = Job(
    runs_on="ubuntu-latest",
    outputs={
        "version": "${{ steps.nonexistent_step.outputs.version }}",
    },
    steps=[
        Step(id="get_version", run="echo version=1.0.0"),
    ],
)
""",
            "test.py",
        )
        assert len(errors) == 1
        assert "nonexistent_step" in errors[0].message
        assert "WAG053" == errors[0].rule_id

    def test_allow_valid_step_id_reference(self):
        """Allow references to valid step IDs."""
        rule = WAG053StepOutputReferences()
        errors = rule.check(
            """
from wetwire_github.workflow import Job, Step

build_job = Job(
    runs_on="ubuntu-latest",
    outputs={
        "version": "${{ steps.get_version.outputs.version }}",
    },
    steps=[
        Step(id="get_version", run="echo version=1.0.0"),
    ],
)
""",
            "test.py",
        )
        assert len(errors) == 0

    def test_detect_step_reference_in_env(self):
        """Detect invalid step references in env values."""
        rule = WAG053StepOutputReferences()
        errors = rule.check(
            """
from wetwire_github.workflow import Job, Step

build_job = Job(
    runs_on="ubuntu-latest",
    steps=[
        Step(id="step1", run="echo 'hello'"),
        Step(
            run="echo $VERSION",
            env={"VERSION": "${{ steps.wrong_id.outputs.version }}"},
        ),
    ],
)
""",
            "test.py",
        )
        assert len(errors) == 1
        assert "wrong_id" in errors[0].message

    def test_detect_step_reference_in_if_condition(self):
        """Detect invalid step references in if conditions."""
        rule = WAG053StepOutputReferences()
        errors = rule.check(
            """
from wetwire_github.workflow import Job, Step

build_job = Job(
    runs_on="ubuntu-latest",
    steps=[
        Step(id="check", run="echo result=true"),
        Step(
            run="echo 'deploying'",
            if_="${{ steps.invalid_check.outputs.result == 'true' }}",
        ),
    ],
)
""",
            "test.py",
        )
        assert len(errors) == 1
        assert "invalid_check" in errors[0].message

    def test_allow_step_reference_later_in_list(self):
        """Allow referencing step defined earlier in steps list."""
        rule = WAG053StepOutputReferences()
        errors = rule.check(
            """
from wetwire_github.workflow import Job, Step

build_job = Job(
    runs_on="ubuntu-latest",
    steps=[
        Step(id="first", run="echo 'first'"),
        Step(id="second", run="echo ${{ steps.first.outputs.value }}"),
    ],
)
""",
            "test.py",
        )
        assert len(errors) == 0

    def test_detect_reference_to_later_step(self):
        """Detect reference to step defined later (forward reference)."""
        rule = WAG053StepOutputReferences()
        errors = rule.check(
            """
from wetwire_github.workflow import Job, Step

build_job = Job(
    runs_on="ubuntu-latest",
    steps=[
        Step(id="first", run="echo ${{ steps.second.outputs.value }}"),
        Step(id="second", run="echo 'second'"),
    ],
)
""",
            "test.py",
        )
        # Forward references are invalid - step hasn't run yet
        assert len(errors) == 1
        assert "second" in errors[0].message

    def test_multiple_jobs_independent_step_ids(self):
        """Step IDs are scoped to their job."""
        rule = WAG053StepOutputReferences()
        errors = rule.check(
            """
from wetwire_github.workflow import Job, Step

job_a = Job(
    runs_on="ubuntu-latest",
    steps=[
        Step(id="my_step", run="echo A"),
    ],
)

job_b = Job(
    runs_on="ubuntu-latest",
    steps=[
        # This references step in same job, not job_a
        Step(run="echo ${{ steps.my_step.outputs.value }}"),
    ],
)
""",
            "test.py",
        )
        # job_b references my_step but doesn't have it defined
        assert len(errors) == 1
        assert "my_step" in errors[0].message


class TestDefaultRulesIncludeReferenceRules:
    """Test that get_default_rules includes reference rules."""

    def test_default_rules_include_wag050(self):
        """WAG050 is in default rules."""
        from wetwire_github.linter.rules import get_default_rules

        rules = get_default_rules()
        rule_ids = [r.id for r in rules]
        assert "WAG050" in rule_ids

    def test_default_rules_include_wag051(self):
        """WAG051 is in default rules."""
        from wetwire_github.linter.rules import get_default_rules

        rules = get_default_rules()
        rule_ids = [r.id for r in rules]
        assert "WAG051" in rule_ids

    def test_default_rules_include_wag052(self):
        """WAG052 is in default rules."""
        from wetwire_github.linter.rules import get_default_rules

        rules = get_default_rules()
        rule_ids = [r.id for r in rules]
        assert "WAG052" in rule_ids

    def test_default_rules_include_wag053(self):
        """WAG053 is in default rules."""
        from wetwire_github.linter.rules import get_default_rules

        rules = get_default_rules()
        rule_ids = [r.id for r in rules]
        assert "WAG053" in rule_ids
