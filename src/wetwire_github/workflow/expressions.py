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

    @staticmethod
    def push(prop: str) -> Expression:
        """Get a property from the push event payload."""
        return Expression(f"github.event.{prop}")

    @staticmethod
    def workflow_run(prop: str) -> Expression:
        """Get a property from the workflow_run event payload."""
        return Expression(f"github.event.workflow_run.{prop}")

    @staticmethod
    def sender(prop: str) -> Expression:
        """Get a property from the event sender."""
        return Expression(f"github.event.sender.{prop}")

    @staticmethod
    def repository(prop: str) -> Expression:
        """Get a property from the event repository."""
        return Expression(f"github.event.repository.{prop}")

    # Convenience properties for common event payload fields
    pr_title = Expression("github.event.pull_request.title")
    pr_body = Expression("github.event.pull_request.body")
    pr_number = Expression("github.event.pull_request.number")
    issue_title = Expression("github.event.issue.title")
    issue_body = Expression("github.event.issue.body")
    issue_number = Expression("github.event.issue.number")
    release_tag_name = Expression("github.event.release.tag_name")
    release_body = Expression("github.event.release.body")

    # Additional convenience properties
    head_commit_message = Expression("github.event.head_commit.message")
    head_commit_id = Expression("github.event.head_commit.id")
    sender_login = Expression("github.event.sender.login")
    repo_full_name = Expression("github.event.repository.full_name")
    repo_name = Expression("github.event.repository.name")


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


# Expression function helpers
def contains(text: str | Expression, search: str) -> Expression:
    """Check if text contains a substring.

    Args:
        text: The text to search in (string or expression)
        search: The substring to search for

    Returns:
        Expression that evaluates to boolean

    Example:
        >>> contains(Event.pr_title, "bug")
        ${{ contains(github.event.pull_request.title, 'bug') }}
    """
    text_str = str(text).strip("${{ }}").strip() if isinstance(text, Expression) else f"'{text}'"
    return Expression(f"contains({text_str}, '{search}')")


def startsWith(text: str | Expression, prefix: str) -> Expression:  # noqa: N802
    """Check if text starts with a prefix.

    Args:
        text: The text to check (string or expression)
        prefix: The prefix to check for

    Returns:
        Expression that evaluates to boolean

    Example:
        >>> startsWith(Event.pr_title, "feat:")
        ${{ startsWith(github.event.pull_request.title, 'feat:') }}
    """
    text_str = str(text).strip("${{ }}").strip() if isinstance(text, Expression) else f"'{text}'"
    return Expression(f"startsWith({text_str}, '{prefix}')")


def endsWith(text: str | Expression, suffix: str) -> Expression:  # noqa: N802
    """Check if text ends with a suffix.

    Args:
        text: The text to check (string or expression)
        suffix: The suffix to check for

    Returns:
        Expression that evaluates to boolean

    Example:
        >>> endsWith(Event.pr_title, ".md")
        ${{ endsWith(github.event.pull_request.title, '.md') }}
    """
    text_str = str(text).strip("${{ }}").strip() if isinstance(text, Expression) else f"'{text}'"
    return Expression(f"endsWith({text_str}, '{suffix}')")


def format(template: str, *args: str | Expression) -> Expression:
    """Format a string with placeholders.

    Args:
        template: Format string with {0}, {1}, etc. placeholders
        *args: Values to substitute (strings or expressions)

    Returns:
        Expression containing formatted string

    Example:
        >>> format("cache-{0}-{1}", Runner.os, hashFiles("*.lock"))
        ${{ format('cache-{0}-{1}', runner.os, hashFiles('*.lock')) }}
    """
    arg_strs = []
    for arg in args:
        if isinstance(arg, Expression):
            arg_strs.append(str(arg).strip("${{ }}").strip())
        else:
            arg_strs.append(f"'{arg}'")

    all_args = ", ".join([f"'{template}'"] + arg_strs)
    return Expression(f"format({all_args})")


def hashFiles(patterns: str) -> Expression:  # noqa: N802
    """Generate a hash of files matching patterns for cache keys.

    Args:
        patterns: Glob pattern(s) to match files

    Returns:
        Expression containing hash of matched files

    Example:
        >>> hashFiles("requirements.txt")
        ${{ hashFiles('requirements.txt') }}
        >>> hashFiles("**/requirements*.txt")
        ${{ hashFiles('**/requirements*.txt') }}
    """
    return Expression(f"hashFiles('{patterns}')")


def join(array: str | Expression, separator: str = ",") -> Expression:
    """Join an array into a string.

    Args:
        array: Array to join (string or expression)
        separator: Separator to use (default: ",")

    Returns:
        Expression containing joined string

    Example:
        >>> join(Matrix.get("versions"), ", ")
        ${{ join(matrix.versions, ', ') }}
    """
    array_str = str(array).strip("${{ }}").strip() if isinstance(array, Expression) else array
    return Expression(f"join({array_str}, '{separator}')")


def toJson(value: str | Expression) -> Expression:  # noqa: N802
    """Convert a value to JSON string.

    Args:
        value: Value to convert (string or expression)

    Returns:
        Expression containing JSON string

    Example:
        >>> toJson(Expression("matrix"))
        ${{ toJSON(matrix) }}
    """
    value_str = str(value).strip("${{ }}").strip() if isinstance(value, Expression) else value
    return Expression(f"toJSON({value_str})")


def fromJson(value: str | Expression) -> Expression:  # noqa: N802
    """Parse a JSON string.

    Args:
        value: JSON string to parse (string or expression)

    Returns:
        Expression containing parsed value

    Example:
        >>> fromJson(Env.get("JSON_DATA"))
        ${{ fromJSON(env.JSON_DATA) }}
    """
    value_str = str(value).strip("${{ }}").strip() if isinstance(value, Expression) else value
    return Expression(f"fromJSON({value_str})")


def lower(text: str | Expression) -> Expression:  # noqa: N802
    """Convert string to lowercase.

    Args:
        text: The text to convert (string or expression)

    Returns:
        Expression containing lowercased string

    Example:
        >>> lower("HELLO")
        ${{ lower('HELLO') }}
        >>> lower(GitHub.ref)
        ${{ lower(github.ref) }}
    """
    text_str = str(text).strip("${{ }}").strip() if isinstance(text, Expression) else f"'{text}'"
    return Expression(f"lower({text_str})")


def upper(text: str | Expression) -> Expression:  # noqa: N802
    """Convert string to uppercase.

    Args:
        text: The text to convert (string or expression)

    Returns:
        Expression containing uppercased string

    Example:
        >>> upper("hello")
        ${{ upper('hello') }}
        >>> upper(GitHub.ref)
        ${{ upper(github.ref) }}
    """
    text_str = str(text).strip("${{ }}").strip() if isinstance(text, Expression) else f"'{text}'"
    return Expression(f"upper({text_str})")


def trim(text: str | Expression) -> Expression:  # noqa: A001
    """Remove leading and trailing whitespace from a string.

    Args:
        text: The text to trim (string or expression)

    Returns:
        Expression containing trimmed string

    Example:
        >>> trim("  hello  ")
        ${{ trim('  hello  ') }}
        >>> trim(GitHub.ref)
        ${{ trim(github.ref) }}
    """
    text_str = str(text).strip("${{ }}").strip() if isinstance(text, Expression) else f"'{text}'"
    return Expression(f"trim({text_str})")
