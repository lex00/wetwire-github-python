"""Generated wrapper for Configure GitHub Pages."""

from wetwire_github.workflow import Step


def configure_pages(
    static_site_generator: str | None = None,
    generator_config_file: str | None = None,
    token: str | None = None,
    enablement: str | None = None,
) -> Step:
    """Configure GitHub Pages and extract metadata.

    Args:
        static_site_generator: Optional static site generator to configure: "nuxt", "next", "gatsby", or "sveltekit"
        generator_config_file: Optional file path to static site generator configuration file
        token: GitHub token
        enablement: Try to enable Pages for the repository if not already enabled. Requires a token with repo scope or Pages write permission. Default is false.

    Returns:
        Step configured to use this action
    """
    with_dict = {
        "static_site_generator": static_site_generator,
        "generator_config_file": generator_config_file,
        "token": token,
        "enablement": enablement,
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="actions/configure-pages@v5",
        with_=with_dict if with_dict else None,
    )
