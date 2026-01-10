"""Example: Configuring secret scanning with custom patterns using wetwire-github.

This example demonstrates how to define custom secret patterns for detecting
organization-specific secrets and credentials that GitHub's built-in patterns
might not catch.
"""

from wetwire_github.secret_scanning import (
    AlertSettings,
    CustomPattern,
    SecretScanningConfig,
)
from wetwire_github.serialize import to_yaml

# Example 1: Basic secret scanning with push protection
# Enable secret scanning with GitHub's built-in patterns
basic_config = SecretScanningConfig(
    enabled=True,
    push_protection=True,
    alert_settings=AlertSettings(
        push_protection=True,
        alert_notifications=True,
    ),
)


# Example 2: Internal API key patterns
# Custom patterns for detecting organization-specific API keys
internal_api_patterns = [
    CustomPattern(
        name="Internal API Key",
        pattern=r"ACME_API_[a-zA-Z0-9]{32}",
        secret_type="acme_api_key",
    ),
    CustomPattern(
        name="Service Account Token",
        pattern=r"svc_[a-zA-Z0-9]{40}",
        secret_type="service_account_token",
    ),
    CustomPattern(
        name="Internal OAuth Token",
        pattern=r"acme_oauth_[a-zA-Z0-9]{64}",
        secret_type="internal_oauth",
    ),
]

internal_api_config = SecretScanningConfig(
    enabled=True,
    push_protection=True,
    patterns=internal_api_patterns,
    alert_settings=AlertSettings(
        push_protection=True,
        alert_notifications=True,
    ),
)


# Example 3: Database and infrastructure secrets
# Patterns for detecting database connection strings and infrastructure credentials
infrastructure_patterns = [
    CustomPattern(
        name="PostgreSQL Connection String",
        pattern=r"postgres://[^:]+:[^@]+@[^/]+/\w+",
        secret_type="database_url",
    ),
    CustomPattern(
        name="MySQL Connection String",
        pattern=r"mysql://[^:]+:[^@]+@[^/]+/\w+",
        secret_type="database_url",
    ),
    CustomPattern(
        name="MongoDB Connection String",
        pattern=r"mongodb(\+srv)?://[^:]+:[^@]+@[^/]+",
        secret_type="database_url",
    ),
    CustomPattern(
        name="Redis URL",
        pattern=r"redis://:[^@]+@[^:]+:\d+",
        secret_type="redis_url",
    ),
    CustomPattern(
        name="SSH Private Key Header",
        pattern=r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----",
        secret_type="ssh_private_key",
    ),
]

infrastructure_config = SecretScanningConfig(
    enabled=True,
    push_protection=True,
    patterns=infrastructure_patterns,
    alert_settings=AlertSettings(
        push_protection=True,
        alert_notifications=True,
    ),
)


# Example 4: Cloud provider credentials
# Patterns for detecting various cloud provider credentials
cloud_patterns = [
    # AWS
    CustomPattern(
        name="AWS Access Key ID",
        pattern=r"AKIA[0-9A-Z]{16}",
        secret_type="aws_access_key",
    ),
    CustomPattern(
        name="AWS Secret Access Key",
        pattern=r"aws_secret_access_key[=:]\s*['\"]?[A-Za-z0-9/+=]{40}['\"]?",
        secret_type="aws_secret_key",
    ),
    # Google Cloud
    CustomPattern(
        name="GCP Service Account Key",
        pattern=r'"type":\s*"service_account"',
        secret_type="gcp_service_account",
    ),
    # Azure
    CustomPattern(
        name="Azure Storage Key",
        pattern=r"DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[^;]+",
        secret_type="azure_storage_key",
    ),
]

cloud_config = SecretScanningConfig(
    enabled=True,
    push_protection=True,
    patterns=cloud_patterns,
    alert_settings=AlertSettings(
        push_protection=True,
        alert_notifications=True,
    ),
)


# Example 5: Common application secrets
# Patterns for JWT secrets, encryption keys, and other application secrets
application_patterns = [
    CustomPattern(
        name="JWT Secret Assignment",
        pattern=r"(jwt|JWT)_?(secret|SECRET)[=:]\s*['\"][^'\"]{16,}['\"]",
        secret_type="jwt_secret",
    ),
    CustomPattern(
        name="Encryption Key",
        pattern=r"(encryption|ENCRYPTION)_?(key|KEY)[=:]\s*['\"][A-Za-z0-9+/=]{24,}['\"]",
        secret_type="encryption_key",
    ),
    CustomPattern(
        name="API Key in Config",
        pattern=r"api[_-]?key[=:]\s*['\"][a-zA-Z0-9]{20,}['\"]",
        secret_type="generic_api_key",
    ),
    CustomPattern(
        name="Password in Config",
        pattern=r"password[=:]\s*['\"][^'\"]+['\"]",
        secret_type="password",
    ),
    CustomPattern(
        name="Bearer Token",
        pattern=r"Bearer\s+[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",
        secret_type="bearer_token",
    ),
]

application_config = SecretScanningConfig(
    enabled=True,
    push_protection=True,
    patterns=application_patterns,
    alert_settings=AlertSettings(
        push_protection=True,
        alert_notifications=True,
    ),
)


# Example 6: Third-party service tokens
# Patterns for detecting tokens from common third-party services
third_party_patterns = [
    # Slack
    CustomPattern(
        name="Slack Bot Token",
        pattern=r"xoxb-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24}",
        secret_type="slack_bot_token",
    ),
    CustomPattern(
        name="Slack Webhook URL",
        pattern=r"https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[a-zA-Z0-9]+",
        secret_type="slack_webhook",
    ),
    # Stripe
    CustomPattern(
        name="Stripe Secret Key",
        pattern=r"sk_(live|test)_[a-zA-Z0-9]{24,}",
        secret_type="stripe_secret_key",
    ),
    # Twilio
    CustomPattern(
        name="Twilio Auth Token",
        pattern=r"twilio_auth_token[=:]\s*['\"]?[a-f0-9]{32}['\"]?",
        secret_type="twilio_auth_token",
    ),
    # SendGrid
    CustomPattern(
        name="SendGrid API Key",
        pattern=r"SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}",
        secret_type="sendgrid_api_key",
    ),
]

third_party_config = SecretScanningConfig(
    enabled=True,
    push_protection=True,
    patterns=third_party_patterns,
    alert_settings=AlertSettings(
        push_protection=True,
        alert_notifications=True,
    ),
)


# Example 7: Comprehensive configuration combining multiple pattern sets
# A complete configuration for enterprise use
comprehensive_config = SecretScanningConfig(
    enabled=True,
    push_protection=True,
    patterns=[
        # Internal patterns
        CustomPattern(
            name="Internal API Key",
            pattern=r"ACME_API_[a-zA-Z0-9]{32}",
            secret_type="acme_api_key",
        ),
        CustomPattern(
            name="Service Token",
            pattern=r"svc_[a-zA-Z0-9]{40}",
            secret_type="service_token",
        ),
        # Database patterns
        CustomPattern(
            name="Database URL",
            pattern=r"(postgres|mysql|mongodb)://[^:]+:[^@]+@[^/]+",
            secret_type="database_url",
        ),
        # Cloud patterns
        CustomPattern(
            name="AWS Access Key",
            pattern=r"AKIA[0-9A-Z]{16}",
            secret_type="aws_access_key",
        ),
        # Application patterns
        CustomPattern(
            name="JWT Secret",
            pattern=r"(jwt|JWT)_?(secret|SECRET)[=:]\s*['\"][^'\"]{16,}['\"]",
            secret_type="jwt_secret",
        ),
        # Third-party patterns
        CustomPattern(
            name="Stripe Key",
            pattern=r"sk_(live|test)_[a-zA-Z0-9]{24,}",
            secret_type="stripe_key",
        ),
    ],
    alert_settings=AlertSettings(
        push_protection=True,
        alert_notifications=True,
    ),
)


# Print example configurations
if __name__ == "__main__":
    print("=== Basic Secret Scanning Config ===")
    print(to_yaml(basic_config))
    print()

    print("=== Internal API Patterns Config ===")
    print(to_yaml(internal_api_config))
    print()

    print("=== Comprehensive Enterprise Config ===")
    print(to_yaml(comprehensive_config))
