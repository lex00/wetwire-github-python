"""Generated wrapper for ruby/setup-ruby."""

from wetwire_github.workflow import Step


def setup_ruby(
    ruby_version: str | None = None,
    rubygems: str | None = None,
    bundler: str | None = None,
    bundler_cache: bool | None = None,
    working_directory: str | None = None,
    cache_version: str | None = None,
) -> Step:
    """Set up a Ruby environment.

    This action downloads a prebuilt Ruby and adds it to PATH. It also
    optionally installs gems and caches dependencies.

    Args:
        ruby_version: Ruby version to use. Examples: 3.2, 3.3, jruby, truffleruby.
            Also supports .ruby-version file.
        rubygems: RubyGems version to install (default, latest, or version).
        bundler: Bundler version to install (default, latest, Gemfile.lock, or version).
        bundler_cache: Run bundle install and cache the result.
        working_directory: Working directory for bundler operations.
        cache_version: An arbitrary string to add to the cache key.

    Returns:
        Step configured to use ruby/setup-ruby
    """
    with_dict = {
        "ruby-version": ruby_version,
        "rubygems": rubygems,
        "bundler": bundler,
        "bundler-cache": "true" if bundler_cache else ("false" if bundler_cache is False else None),
        "working-directory": working_directory,
        "cache-version": cache_version,
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="ruby/setup-ruby@v1",
        with_=with_dict if with_dict else None,
    )
