"""Generated wrapper for Checkout."""

from wetwire_github.workflow import Step


def checkout(
    repository: str | None = None,
    ref: str | None = None,
    token: str | None = None,
    ssh_key: str | None = None,
    ssh_known_hosts: str | None = None,
    ssh_strict: str | None = None,
    ssh_user: str | None = None,
    persist_credentials: str | None = None,
    path: str | None = None,
    clean: str | None = None,
    filter: str | None = None,
    sparse_checkout: str | None = None,
    sparse_checkout_cone_mode: str | None = None,
    fetch_depth: str | None = None,
    fetch_tags: str | None = None,
    show_progress: str | None = None,
    lfs: str | None = None,
    submodules: str | None = None,
    set_safe_directory: str | None = None,
    github_server_url: str | None = None,
) -> Step:
    """Checkout a Git repository at a particular version

        Args:
            repository: Repository name with owner. For example, actions/checkout
            ref: The branch, tag or SHA to checkout. When checking out the repository that triggered a workflow, this defaults to the reference or SHA for that event.  Otherwise, uses the default branch.

            token: Personal access token (PAT) used to fetch the repository. The PAT is configured with the local git config, which enables your scripts to run authenticated git commands. The post-job step removes the PAT.

    We recommend using a service account with the least permissions necessary. Also when generating a new PAT, select the least scopes necessary.

    [Learn more about creating and using encrypted secrets](https://help.github.com/en/actions/automating-your-workflow-with-github-actions/creating-and-using-encrypted-secrets)

            ssh_key: SSH key used to fetch the repository. The SSH key is configured with the local git config, which enables your scripts to run authenticated git commands. The post-job step removes the SSH key.

    We recommend using a service account with the least permissions necessary.

    [Learn more about creating and using encrypted secrets](https://help.github.com/en/actions/automating-your-workflow-with-github-actions/creating-and-using-encrypted-secrets)

            ssh_known_hosts: Known hosts in addition to the user and global host key database. The public SSH keys for a host may be obtained using the utility `ssh-keyscan`. For example, `ssh-keyscan github.com`. The public key for github.com is always implicitly added.

            ssh_strict: Whether to perform strict host key checking. When true, adds the options `StrictHostKeyChecking=yes` and `CheckHostIP=no` to the SSH command line. Use the input `ssh-known-hosts` to configure additional hosts.

            ssh_user: The user to use when connecting to the remote SSH host. By default 'git' is used.

            persist_credentials: Whether to configure the token or SSH key with the local git config
            path: Relative path under $GITHUB_WORKSPACE to place the repository
            clean: Whether to execute `git clean -ffdx && git reset --hard HEAD` before fetching
            filter: Partially clone against a given filter. Overrides sparse-checkout if set.

            sparse_checkout: Do a sparse checkout on given patterns. Each pattern should be separated with new lines.

            sparse_checkout_cone_mode: Specifies whether to use cone-mode when doing a sparse checkout.

            fetch_depth: Number of commits to fetch. 0 indicates all history for all branches and tags.
            fetch_tags: Whether to fetch tags, even if fetch-depth > 0.
            show_progress: Whether to show progress status output when fetching.
            lfs: Whether to download Git-LFS files
            submodules: Whether to checkout submodules: `true` to checkout submodules or `recursive` to recursively checkout submodules.

    When the `ssh-key` input is not provided, SSH URLs beginning with `git@github.com:` are converted to HTTPS.

            set_safe_directory: Add repository path as safe.directory for Git global config by running `git config --global --add safe.directory <path>`
            github_server_url: The base URL for the GitHub instance that you are trying to clone from, will use environment defaults to fetch from the same instance that the workflow is running from unless specified. Example URLs are https://github.com or https://my-ghes-server.example.com

        Returns:
            Step configured to use this action
    """
    with_dict = {
        "repository": repository,
        "ref": ref,
        "token": token,
        "ssh-key": ssh_key,
        "ssh-known-hosts": ssh_known_hosts,
        "ssh-strict": ssh_strict,
        "ssh-user": ssh_user,
        "persist-credentials": persist_credentials,
        "path": path,
        "clean": clean,
        "filter": filter,
        "sparse-checkout": sparse_checkout,
        "sparse-checkout-cone-mode": sparse_checkout_cone_mode,
        "fetch-depth": fetch_depth,
        "fetch-tags": fetch_tags,
        "show-progress": show_progress,
        "lfs": lfs,
        "submodules": submodules,
        "set-safe-directory": set_safe_directory,
        "github-server-url": github_server_url,
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="actions/checkout@v4",
        with_=with_dict if with_dict else None,
    )
