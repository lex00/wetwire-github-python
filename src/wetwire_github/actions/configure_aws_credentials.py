"""Generated wrapper for aws-actions/configure-aws-credentials."""

from wetwire_github.workflow import Step


def configure_aws_credentials(
    aws_region: str | None = None,
    role_to_assume: str | None = None,
    role_duration_seconds: str | None = None,
    role_session_name: str | None = None,
    role_external_id: str | None = None,
    role_skip_session_tagging: bool | None = None,
    aws_access_key_id: str | None = None,
    aws_secret_access_key: str | None = None,
    aws_session_token: str | None = None,
    web_identity_token_file: str | None = None,
    audience: str | None = None,
    http_proxy: str | None = None,
    mask_aws_account_id: bool | None = None,
    output_credentials: bool | None = None,
    unset_current_credentials: bool | None = None,
    disable_retry: bool | None = None,
    retry_max_attempts: str | None = None,
    special_characters_workaround: bool | None = None,
) -> Step:
    """Configure AWS credentials for use in GitHub Actions.

    This action configures AWS credentials and region environment variables
    for use with the AWS CLI and AWS SDKs.

    Args:
        aws_region: The AWS region to configure.
        role_to_assume: IAM role ARN to assume using OIDC or STS.
        role_duration_seconds: Duration of the role session in seconds.
        role_session_name: Name for the role session.
        role_external_id: External ID for the role assumption.
        role_skip_session_tagging: Skip session tagging.
        aws_access_key_id: AWS access key ID.
        aws_secret_access_key: AWS secret access key.
        aws_session_token: AWS session token.
        web_identity_token_file: Path to web identity token file.
        audience: Audience for OIDC provider.
        http_proxy: HTTP proxy for AWS API calls.
        mask_aws_account_id: Mask AWS account ID in logs.
        output_credentials: Output credentials to action output.
        unset_current_credentials: Unset existing credentials before configuring.
        disable_retry: Disable retry logic.
        retry_max_attempts: Maximum number of retry attempts.
        special_characters_workaround: Enable workaround for special characters.

    Returns:
        Step configured to use aws-actions/configure-aws-credentials
    """
    with_dict = {
        "aws-region": aws_region,
        "role-to-assume": role_to_assume,
        "role-duration-seconds": role_duration_seconds,
        "role-session-name": role_session_name,
        "role-external-id": role_external_id,
        "role-skip-session-tagging": "true" if role_skip_session_tagging else ("false" if role_skip_session_tagging is False else None),
        "aws-access-key-id": aws_access_key_id,
        "aws-secret-access-key": aws_secret_access_key,
        "aws-session-token": aws_session_token,
        "web-identity-token-file": web_identity_token_file,
        "audience": audience,
        "http-proxy": http_proxy,
        "mask-aws-account-id": "true" if mask_aws_account_id else ("false" if mask_aws_account_id is False else None),
        "output-credentials": "true" if output_credentials else ("false" if output_credentials is False else None),
        "unset-current-credentials": "true" if unset_current_credentials else ("false" if unset_current_credentials is False else None),
        "disable-retry": "true" if disable_retry else ("false" if disable_retry is False else None),
        "retry-max-attempts": retry_max_attempts,
        "special-characters-workaround": "true" if special_characters_workaround else ("false" if special_characters_workaround is False else None),
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="aws-actions/configure-aws-credentials@v4",
        with_=with_dict if with_dict else None,
    )
