"""Generated wrapper for peaceiris/actions-gh-pages."""

from wetwire_github.workflow import Step


def gh_pages(
    *,
    github_token: str | None = None,
    deploy_key: str | None = None,
    personal_token: str | None = None,
    publish_dir: str = "./public",
    publish_branch: str | None = None,
    cname: str | None = None,
    keep_files: bool | None = None,
    external_repository: str | None = None,
    force_orphan: bool | None = None,
    commit_message: str | None = None,
    user_name: str | None = None,
    user_email: str | None = None,
) -> Step:
    """Create a step to deploy to GitHub Pages.

    Args:
        github_token: GITHUB_TOKEN for deployment
        deploy_key: SSH deploy key (alternative to token)
        personal_token: Personal access token (alternative)
        publish_dir: Directory to publish (default: "./public")
        publish_branch: Target branch (default: "gh-pages")
        cname: Custom domain for CNAME file
        keep_files: Keep existing files in branch
        external_repository: Deploy to external repo
        force_orphan: Create orphan branch
        commit_message: Custom commit message
        user_name: Git user name for commits
        user_email: Git user email for commits

    Returns:
        Step configured for GitHub Pages deployment
    """
    with_dict = {
        "github_token": github_token,
        "deploy_key": deploy_key,
        "personal_token": personal_token,
        "publish_dir": publish_dir,
        "publish_branch": publish_branch,
        "cname": cname,
        "keep_files": "true" if keep_files is True else ("false" if keep_files is False else None),
        "external_repository": external_repository,
        "force_orphan": "true" if force_orphan is True else ("false" if force_orphan is False else None),
        "commit_message": commit_message,
        "user_name": user_name,
        "user_email": user_email,
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="peaceiris/actions-gh-pages@v4",
        with_=with_dict if with_dict else None,
    )
