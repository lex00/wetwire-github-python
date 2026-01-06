"""Trigger types for workflow definitions."""

from dataclasses import dataclass

from .types import WorkflowInput, WorkflowOutput, WorkflowSecret


@dataclass
class PushTrigger:
    """Push event trigger."""

    branches: list[str] | None = None
    branches_ignore: list[str] | None = None
    tags: list[str] | None = None
    tags_ignore: list[str] | None = None
    paths: list[str] | None = None
    paths_ignore: list[str] | None = None


@dataclass
class PullRequestTrigger:
    """Pull request event trigger."""

    branches: list[str] | None = None
    branches_ignore: list[str] | None = None
    paths: list[str] | None = None
    paths_ignore: list[str] | None = None
    types: list[str] | None = None


@dataclass
class PullRequestTargetTrigger:
    """Pull request target event trigger."""

    branches: list[str] | None = None
    branches_ignore: list[str] | None = None
    paths: list[str] | None = None
    paths_ignore: list[str] | None = None
    types: list[str] | None = None


@dataclass
class ScheduleTrigger:
    """Schedule event trigger."""

    cron: str = ""


@dataclass
class WorkflowDispatchTrigger:
    """Manual workflow dispatch trigger."""

    inputs: dict[str, WorkflowInput] | None = None


@dataclass
class WorkflowCallTrigger:
    """Reusable workflow call trigger."""

    inputs: dict[str, WorkflowInput] | None = None
    outputs: dict[str, WorkflowOutput] | None = None
    secrets: dict[str, WorkflowSecret] | None = None


@dataclass
class WorkflowRunTrigger:
    """Workflow run event trigger."""

    workflows: list[str] | None = None
    types: list[str] | None = None
    branches: list[str] | None = None
    branches_ignore: list[str] | None = None


@dataclass
class RepositoryDispatchTrigger:
    """Repository dispatch event trigger."""

    types: list[str] | None = None


@dataclass
class ReleaseTrigger:
    """Release event trigger."""

    types: list[str] | None = None


@dataclass
class IssueTrigger:
    """Issue event trigger."""

    types: list[str] | None = None


@dataclass
class IssueCommentTrigger:
    """Issue comment event trigger."""

    types: list[str] | None = None


@dataclass
class LabelTrigger:
    """Label event trigger."""

    types: list[str] | None = None


@dataclass
class MilestoneTrigger:
    """Milestone event trigger."""

    types: list[str] | None = None


@dataclass
class ProjectTrigger:
    """Project event trigger."""

    types: list[str] | None = None


@dataclass
class ProjectCardTrigger:
    """Project card event trigger."""

    types: list[str] | None = None


@dataclass
class ProjectColumnTrigger:
    """Project column event trigger."""

    types: list[str] | None = None


@dataclass
class DiscussionTrigger:
    """Discussion event trigger."""

    types: list[str] | None = None


@dataclass
class DiscussionCommentTrigger:
    """Discussion comment event trigger."""

    types: list[str] | None = None


@dataclass
class CreateTrigger:
    """Create event trigger (branch/tag creation)."""

    pass


@dataclass
class DeleteTrigger:
    """Delete event trigger (branch/tag deletion)."""

    pass


@dataclass
class DeploymentTrigger:
    """Deployment event trigger."""

    pass


@dataclass
class DeploymentStatusTrigger:
    """Deployment status event trigger."""

    pass


@dataclass
class ForkTrigger:
    """Fork event trigger."""

    pass


@dataclass
class GollumTrigger:
    """Gollum (wiki) event trigger."""

    pass


@dataclass
class PageBuildTrigger:
    """Page build event trigger."""

    pass


@dataclass
class PublicTrigger:
    """Public event trigger (repo made public)."""

    pass


@dataclass
class PullRequestReviewTrigger:
    """Pull request review event trigger."""

    types: list[str] | None = None


@dataclass
class PullRequestReviewCommentTrigger:
    """Pull request review comment event trigger."""

    types: list[str] | None = None


@dataclass
class CheckRunTrigger:
    """Check run event trigger."""

    types: list[str] | None = None


@dataclass
class CheckSuiteTrigger:
    """Check suite event trigger."""

    types: list[str] | None = None


@dataclass
class StatusTrigger:
    """Status event trigger."""

    pass


@dataclass
class WatchTrigger:
    """Watch event trigger."""

    types: list[str] | None = None


@dataclass
class MemberTrigger:
    """Member event trigger."""

    types: list[str] | None = None


@dataclass
class MembershipTrigger:
    """Membership event trigger."""

    types: list[str] | None = None


@dataclass
class OrgBlockTrigger:
    """Org block event trigger."""

    types: list[str] | None = None


@dataclass
class OrganizationTrigger:
    """Organization event trigger."""

    types: list[str] | None = None


@dataclass
class TeamTrigger:
    """Team event trigger."""

    types: list[str] | None = None


@dataclass
class TeamAddTrigger:
    """Team add event trigger."""

    pass


@dataclass
class MergeGroupTrigger:
    """Merge group event trigger."""

    types: list[str] | None = None


@dataclass
class BranchProtectionRuleTrigger:
    """Branch protection rule event trigger."""

    types: list[str] | None = None


@dataclass
class Triggers:
    """Container for all trigger types."""

    # Common triggers
    push: PushTrigger | None = None
    pull_request: PullRequestTrigger | None = None
    pull_request_target: PullRequestTargetTrigger | None = None
    schedule: list[ScheduleTrigger] | None = None
    workflow_dispatch: WorkflowDispatchTrigger | None = None
    workflow_call: WorkflowCallTrigger | None = None
    workflow_run: WorkflowRunTrigger | None = None
    repository_dispatch: RepositoryDispatchTrigger | None = None

    # Release and issue triggers
    release: ReleaseTrigger | None = None
    issues: IssueTrigger | None = None
    issue_comment: IssueCommentTrigger | None = None
    label: LabelTrigger | None = None
    milestone: MilestoneTrigger | None = None

    # Project triggers
    project: ProjectTrigger | None = None
    project_card: ProjectCardTrigger | None = None
    project_column: ProjectColumnTrigger | None = None

    # Discussion triggers
    discussion: DiscussionTrigger | None = None
    discussion_comment: DiscussionCommentTrigger | None = None

    # Branch/tag lifecycle triggers
    create: CreateTrigger | None = None
    delete: DeleteTrigger | None = None

    # Deployment triggers
    deployment: DeploymentTrigger | None = None
    deployment_status: DeploymentStatusTrigger | None = None

    # Misc triggers
    fork: ForkTrigger | None = None
    gollum: GollumTrigger | None = None
    page_build: PageBuildTrigger | None = None
    public: PublicTrigger | None = None
    status: StatusTrigger | None = None
    watch: WatchTrigger | None = None

    # PR review triggers
    pull_request_review: PullRequestReviewTrigger | None = None
    pull_request_review_comment: PullRequestReviewCommentTrigger | None = None

    # Check triggers
    check_run: CheckRunTrigger | None = None
    check_suite: CheckSuiteTrigger | None = None

    # Team/org triggers
    member: MemberTrigger | None = None
    membership: MembershipTrigger | None = None
    org_block: OrgBlockTrigger | None = None
    organization: OrganizationTrigger | None = None
    team: TeamTrigger | None = None
    team_add: TeamAddTrigger | None = None

    # Merge queue triggers
    merge_group: MergeGroupTrigger | None = None

    # Branch protection triggers
    branch_protection_rule: BranchProtectionRuleTrigger | None = None
