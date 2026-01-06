"""Generated wrapper for Setup Java JDK."""

from wetwire_github.workflow import Step


def setup_java(
    distribution: str,
    java_version: str | None = None,
    java_version_file: str | None = None,
    java_package: str | None = None,
    architecture: str | None = None,
    jdk_file: str | None = None,
    check_latest: str | None = None,
    server_id: str | None = None,
    server_username: str | None = None,
    server_password: str | None = None,
    settings_path: str | None = None,
    overwrite_settings: str | None = None,
    gpg_private_key: str | None = None,
    gpg_passphrase: str | None = None,
    cache: str | None = None,
    cache_dependency_path: str | None = None,
    job_status: str | None = None,
    token: str | None = None,
    mvn_toolchain_id: str | None = None,
    mvn_toolchain_vendor: str | None = None,
) -> Step:
    """Set up a specific version of the Java JDK and add the command-line tools to the PATH

    Args:
        distribution: Java distribution. See the list of supported distributions in README file
        java_version: The Java version to set up. Takes a whole or semver Java version. See examples of supported syntax in README file
        java_version_file: The path to the `.java-version` file. See examples of supported syntax in README file
        java_package: The package type (jdk, jre, jdk+fx, jre+fx)
        architecture: The architecture of the package (defaults to the action runner's architecture)
        jdk_file: Path to where the compressed JDK is located
        check_latest: Set this option if you want the action to check for the latest available version that satisfies the version spec
        server_id: ID of the distributionManagement repository in the pom.xml file. Default is `github`
        server_username: Environment variable name for the username for authentication to the Apache Maven repository. Default is $GITHUB_ACTOR
        server_password: Environment variable name for password or token for authentication to the Apache Maven repository. Default is $GITHUB_TOKEN
        settings_path: Path to where the settings.xml file will be written. Default is ~/.m2.
        overwrite_settings: Overwrite the settings.xml file if it exists. Default is "true".
        gpg_private_key: GPG private key to import. Default is empty string.
        gpg_passphrase: Environment variable name for the GPG private key passphrase. Default is $GPG_PASSPHRASE.
        cache: Name of the build platform to cache dependencies. It can be "maven", "gradle" or "sbt".
        cache_dependency_path: The path to a dependency file: pom.xml, build.gradle, build.sbt, etc. This option can be used with the `cache` option. If this option is omitted, the action searches for the dependency file in the entire repository. This option supports wildcards and a list of file names for caching multiple dependencies.
        job_status: Workaround to pass job status to post job step. This variable is not intended for manual setting
        token: The token used to authenticate when fetching version manifests hosted on github.com, such as for the Microsoft Build of OpenJDK. When running this action on github.com, the default value is sufficient. When running on GHES, you can pass a personal access token for github.com if you are experiencing rate limiting.
        mvn_toolchain_id: Name of Maven Toolchain ID if the default name of "${distribution}_${java-version}" is not wanted. See examples of supported syntax in Advanced Usage file
        mvn_toolchain_vendor: Name of Maven Toolchain Vendor if the default name of "${distribution}" is not wanted. See examples of supported syntax in Advanced Usage file

    Returns:
        Step configured to use this action
    """
    with_dict = {
        "distribution": distribution,
        "java-version": java_version,
        "java-version-file": java_version_file,
        "java-package": java_package,
        "architecture": architecture,
        "jdkFile": jdk_file,
        "check-latest": check_latest,
        "server-id": server_id,
        "server-username": server_username,
        "server-password": server_password,
        "settings-path": settings_path,
        "overwrite-settings": overwrite_settings,
        "gpg-private-key": gpg_private_key,
        "gpg-passphrase": gpg_passphrase,
        "cache": cache,
        "cache-dependency-path": cache_dependency_path,
        "job-status": job_status,
        "token": token,
        "mvn-toolchain-id": mvn_toolchain_id,
        "mvn-toolchain-vendor": mvn_toolchain_vendor,
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="actions/setup-java@v4",
        with_=with_dict if with_dict else None,
    )
