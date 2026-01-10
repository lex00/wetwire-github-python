"""Expression types and context accessors for GitHub Actions."""


class Expression(str):
    """Wraps a GitHub Actions expression string.

    When converted to string, wraps the value in ${{ }}.
    """

    def __str__(self) -> str:
        return f"${{{{ {super().__str__()} }}}}"

    def and_(self, other: "Expression") -> "Expression":
        """Combine expressions with &&."""
        return Expression(f"({super().__str__()}) && ({str.__str__(other)})")

    def or_(self, other: "Expression") -> "Expression":
        """Combine expressions with ||."""
        return Expression(f"({super().__str__()}) || ({str.__str__(other)})")

    def not_(self) -> "Expression":
        """Negate the expression."""
        return Expression(f"!({super().__str__()})")


class SecretsContext:
    """Accessor for secrets context."""

    @staticmethod
    def get(name: str) -> Expression:
        """Get a secret by name."""
        return Expression(f"secrets.{name}")


class MatrixContext:
    """Accessor for matrix context."""

    @staticmethod
    def get(name: str) -> Expression:
        """Get a matrix value by name."""
        return Expression(f"matrix.{name}")


class GitHubContext:
    """Accessor for github context."""

    ref = Expression("github.ref")
    sha = Expression("github.sha")
    actor = Expression("github.actor")
    event_name = Expression("github.event_name")
    repository = Expression("github.repository")
    run_id = Expression("github.run_id")
    run_number = Expression("github.run_number")
    workflow = Expression("github.workflow")
    job = Expression("github.job")
    head_ref = Expression("github.head_ref")
    base_ref = Expression("github.base_ref")
    event_path = Expression("github.event_path")
    workspace = Expression("github.workspace")
    action = Expression("github.action")
    token = Expression("github.token")
    server_url = Expression("github.server_url")
    api_url = Expression("github.api_url")
    graphql_url = Expression("github.graphql_url")
    ref_name = Expression("github.ref_name")
    ref_type = Expression("github.ref_type")
    triggering_actor = Expression("github.triggering_actor")


class EnvContext:
    """Accessor for env context."""

    @staticmethod
    def get(name: str) -> Expression:
        """Get an environment variable by name."""
        return Expression(f"env.{name}")


class RunnerContext:
    """Accessor for runner context."""

    os = Expression("runner.os")
    arch = Expression("runner.arch")
    name = Expression("runner.name")
    temp = Expression("runner.temp")
    tool_cache = Expression("runner.tool_cache")
    debug = Expression("runner.debug")

    @staticmethod
    def is_linux() -> Expression:
        """Check if runner OS is Linux."""
        return Expression("runner.os == 'Linux'")

    @staticmethod
    def is_windows() -> Expression:
        """Check if runner OS is Windows."""
        return Expression("runner.os == 'Windows'")

    @staticmethod
    def is_macos() -> Expression:
        """Check if runner OS is macOS."""
        return Expression("runner.os == 'macOS'")


class NeedsContext:
    """Accessor for needs context (job dependencies)."""

    @staticmethod
    def output(job: str, output: str) -> Expression:
        """Get an output from a dependent job."""
        return Expression(f"needs.{job}.outputs.{output}")

    @staticmethod
    def result(job: str) -> Expression:
        """Get the result of a dependent job."""
        return Expression(f"needs.{job}.result")


class InputsContext:
    """Accessor for inputs context."""

    @staticmethod
    def get(name: str) -> Expression:
        """Get an input by name."""
        return Expression(f"inputs.{name}")


class StepsContext:
    """Accessor for steps context."""

    @staticmethod
    def output(step_id: str, output: str) -> Expression:
        """Get an output from a step."""
        return Expression(f"steps.{step_id}.outputs.{output}")

    @staticmethod
    def outcome(step_id: str) -> Expression:
        """Get the outcome of a step."""
        return Expression(f"steps.{step_id}.outcome")

    @staticmethod
    def conclusion(step_id: str) -> Expression:
        """Get the conclusion of a step."""
        return Expression(f"steps.{step_id}.conclusion")


class EventContext:
    """Accessor for github.event context (event payload)."""

    @staticmethod
    def pull_request(prop: str) -> Expression:
        """Get a property from the pull_request event payload."""
        return Expression(f"github.event.pull_request.{prop}")

    @staticmethod
    def issue(prop: str) -> Expression:
        """Get a property from the issue event payload."""
        return Expression(f"github.event.issue.{prop}")

    @staticmethod
    def release(prop: str) -> Expression:
        """Get a property from the release event payload."""
        return Expression(f"github.event.release.{prop}")

    @staticmethod
    def discussion(prop: str) -> Expression:
        """Get a property from the discussion event payload."""
        return Expression(f"github.event.discussion.{prop}")

    # Convenience properties for common event payload fields
    pr_title = Expression("github.event.pull_request.title")
    pr_body = Expression("github.event.pull_request.body")
    pr_number = Expression("github.event.pull_request.number")
    issue_title = Expression("github.event.issue.title")
    issue_body = Expression("github.event.issue.body")
    issue_number = Expression("github.event.issue.number")
    release_tag_name = Expression("github.event.release.tag_name")
    release_body = Expression("github.event.release.body")


# Module-level context instances
Secrets = SecretsContext()
Matrix = MatrixContext()
GitHub = GitHubContext()
Env = EnvContext()
Runner = RunnerContext()
Needs = NeedsContext()
Inputs = InputsContext()
Steps = StepsContext()
Event = EventContext()


# Condition builder functions
def always() -> Expression:
    """Always run, regardless of status."""
    return Expression("always()")


def failure() -> Expression:
    """Run if any previous step failed."""
    return Expression("failure()")


def success() -> Expression:
    """Run if all previous steps succeeded."""
    return Expression("success()")


def cancelled() -> Expression:
    """Run if the workflow was cancelled."""
    return Expression("cancelled()")


def branch(name: str) -> Expression:
    """Check if the ref matches a branch."""
    return Expression(f"github.ref == 'refs/heads/{name}'")


def tag(name: str) -> Expression:
    """Check if the ref matches a tag."""
    return Expression(f"github.ref == 'refs/tags/{name}'")
