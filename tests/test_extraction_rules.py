"""Tests for inline extraction lint rules (WAG013-WAG015)."""


class TestWAG013InlineEnvVariables:
    """Tests for WAG013: Inline Environment Variables."""

    def test_detects_large_inline_env_in_step(self) -> None:
        """Should detect when Step has >3 inline env variables."""
        from wetwire_github.linter.rules import WAG013InlineEnvVariables

        rule = WAG013InlineEnvVariables()
        source = '''
Step(
    run="make build",
    env={
        "CI": "true",
        "NODE_ENV": "production",
        "DEBUG": "false",
        "VERBOSE": "1",
    },
)
'''
        errors = rule.check(source, "test.py")
        assert len(errors) == 1
        assert errors[0].rule_id == "WAG013"
        assert "inline env" in errors[0].message.lower()

    def test_allows_small_inline_env(self) -> None:
        """Should allow Step with <=3 inline env variables."""
        from wetwire_github.linter.rules import WAG013InlineEnvVariables

        rule = WAG013InlineEnvVariables()
        source = '''
Step(run="make build", env={"CI": "true", "DEBUG": "false"})
'''
        errors = rule.check(source, "test.py")
        assert len(errors) == 0

    def test_allows_extracted_env(self) -> None:
        """Should not flag when env is a variable reference."""
        from wetwire_github.linter.rules import WAG013InlineEnvVariables

        rule = WAG013InlineEnvVariables()
        source = '''
build_env = {"CI": "true", "NODE_ENV": "production", "DEBUG": "false", "VERBOSE": "1"}
Step(run="make build", env=build_env)
'''
        errors = rule.check(source, "test.py")
        assert len(errors) == 0

    def test_custom_threshold(self) -> None:
        """Should support custom threshold for max inline env vars."""
        from wetwire_github.linter.rules import WAG013InlineEnvVariables

        rule = WAG013InlineEnvVariables(max_inline=2)
        source = '''
Step(run="make build", env={"CI": "true", "DEBUG": "false", "VERBOSE": "1"})
'''
        errors = rule.check(source, "test.py")
        assert len(errors) == 1


class TestWAG014InlineMatrixConfig:
    """Tests for WAG014: Inline Matrix Configuration."""

    def test_detects_complex_inline_matrix(self) -> None:
        """Should detect complex inline Matrix in Job."""
        from wetwire_github.linter.rules import WAG014InlineMatrixConfig

        rule = WAG014InlineMatrixConfig()
        source = '''
Job(
    runs_on="ubuntu-latest",
    strategy=Strategy(
        matrix=Matrix(
            values={
                "python": ["3.9", "3.10", "3.11", "3.12"],
                "os": ["ubuntu-latest", "macos-latest", "windows-latest"],
            }
        )
    ),
    steps=[Step(run="echo test")],
)
'''
        errors = rule.check(source, "test.py")
        assert len(errors) == 1
        assert errors[0].rule_id == "WAG014"
        assert "matrix" in errors[0].message.lower()

    def test_allows_simple_inline_matrix(self) -> None:
        """Should allow simple inline Matrix (<=2 keys, <=2 values each)."""
        from wetwire_github.linter.rules import WAG014InlineMatrixConfig

        rule = WAG014InlineMatrixConfig()
        source = '''
Job(
    runs_on="ubuntu-latest",
    strategy=Strategy(matrix=Matrix(values={"python": ["3.11", "3.12"]})),
    steps=[Step(run="echo test")],
)
'''
        errors = rule.check(source, "test.py")
        assert len(errors) == 0

    def test_allows_extracted_matrix(self) -> None:
        """Should not flag when matrix is a variable reference."""
        from wetwire_github.linter.rules import WAG014InlineMatrixConfig

        rule = WAG014InlineMatrixConfig()
        source = '''
version_matrix = Matrix(values={"python": ["3.9", "3.10", "3.11", "3.12"], "os": ["ubuntu", "macos", "windows"]})
Job(
    runs_on="ubuntu-latest",
    strategy=Strategy(matrix=version_matrix),
    steps=[Step(run="echo test")],
)
'''
        errors = rule.check(source, "test.py")
        assert len(errors) == 0


class TestWAG015InlineOutputs:
    """Tests for WAG015: Inline Outputs."""

    def test_detects_large_inline_outputs(self) -> None:
        """Should detect when Job has >2 inline outputs."""
        from wetwire_github.linter.rules import WAG015InlineOutputs

        rule = WAG015InlineOutputs()
        source = '''
Job(
    runs_on="ubuntu-latest",
    outputs={
        "version": "${{ steps.get_version.outputs.version }}",
        "tag": "${{ steps.get_tag.outputs.tag }}",
        "sha": "${{ steps.get_sha.outputs.sha }}",
    },
    steps=[Step(run="echo test")],
)
'''
        errors = rule.check(source, "test.py")
        assert len(errors) == 1
        assert errors[0].rule_id == "WAG015"
        assert "output" in errors[0].message.lower()

    def test_allows_small_inline_outputs(self) -> None:
        """Should allow Job with <=2 inline outputs."""
        from wetwire_github.linter.rules import WAG015InlineOutputs

        rule = WAG015InlineOutputs()
        source = '''
Job(
    runs_on="ubuntu-latest",
    outputs={"version": "${{ steps.get_version.outputs.version }}"},
    steps=[Step(run="echo test")],
)
'''
        errors = rule.check(source, "test.py")
        assert len(errors) == 0

    def test_allows_extracted_outputs(self) -> None:
        """Should not flag when outputs is a variable reference."""
        from wetwire_github.linter.rules import WAG015InlineOutputs

        rule = WAG015InlineOutputs()
        source = '''
job_outputs = {
    "version": "${{ steps.get_version.outputs.version }}",
    "tag": "${{ steps.get_tag.outputs.tag }}",
    "sha": "${{ steps.get_sha.outputs.sha }}",
}
Job(runs_on="ubuntu-latest", outputs=job_outputs, steps=[Step(run="echo")])
'''
        errors = rule.check(source, "test.py")
        assert len(errors) == 0


class TestExtractionRulesAutoFix:
    """Tests for auto-fix support in extraction rules."""

    def test_wag013_autofix_extracts_env(self) -> None:
        """WAG013 should auto-fix by extracting inline env to variable."""
        from wetwire_github.linter.rules import WAG013InlineEnvVariables

        rule = WAG013InlineEnvVariables()
        source = '''step = Step(
    run="make build",
    env={
        "CI": "true",
        "NODE_ENV": "production",
        "DEBUG": "false",
        "VERBOSE": "1",
    },
)
'''
        fixed, count, remaining = rule.fix(source, "test.py")
        assert count == 1
        assert "step_env" in fixed
        assert "env=step_env" in fixed

    def test_wag014_autofix_extracts_matrix(self) -> None:
        """WAG014 should auto-fix by extracting inline matrix to variable."""
        from wetwire_github.linter.rules import WAG014InlineMatrixConfig

        rule = WAG014InlineMatrixConfig()
        source = '''job = Job(
    runs_on="ubuntu-latest",
    strategy=Strategy(
        matrix=Matrix(
            values={
                "python": ["3.9", "3.10", "3.11", "3.12"],
                "os": ["ubuntu-latest", "macos-latest"],
            }
        )
    ),
    steps=[Step(run="echo test")],
)
'''
        fixed, count, remaining = rule.fix(source, "test.py")
        assert count == 1
        assert "job_matrix" in fixed
        assert "matrix=job_matrix" in fixed

    def test_wag015_autofix_extracts_outputs(self) -> None:
        """WAG015 should auto-fix by extracting inline outputs to variable."""
        from wetwire_github.linter.rules import WAG015InlineOutputs

        rule = WAG015InlineOutputs()
        source = '''job = Job(
    runs_on="ubuntu-latest",
    outputs={
        "version": "${{ steps.get_version.outputs.version }}",
        "tag": "${{ steps.get_tag.outputs.tag }}",
        "sha": "${{ steps.get_sha.outputs.sha }}",
    },
    steps=[Step(run="echo test")],
)
'''
        fixed, count, remaining = rule.fix(source, "test.py")
        assert count == 1
        assert "job_outputs" in fixed
        assert "outputs=job_outputs" in fixed


class TestExtractionRulesInDefaultSet:
    """Tests that extraction rules are included in default rule set."""

    def test_rules_in_get_default_rules(self) -> None:
        """Extraction rules should be in the default set."""
        from wetwire_github.linter.rules import get_default_rules

        rules = get_default_rules()
        rule_ids = [r.id for r in rules]
        assert "WAG013" in rule_ids
        assert "WAG014" in rule_ids
        assert "WAG015" in rule_ids
