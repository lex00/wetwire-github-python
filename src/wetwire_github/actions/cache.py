"""Generated wrapper for Cache."""

from wetwire_github.workflow import Step


def cache(
    path: str,
    key: str,
    restore_keys: str | None = None,
    upload_chunk_size: str | None = None,
    enable_cross_os_archive: str | None = None,
    fail_on_cache_miss: str | None = None,
    lookup_only: str | None = None,
    save_always: str | None = None,
) -> Step:
    """Cache artifacts like dependencies and build outputs to improve workflow execution time

    Args:
        path: A list of files, directories, and wildcard patterns to cache and restore
        key: An explicit key for restoring and saving the cache
        restore_keys: An ordered multiline string listing the prefix-matched keys, that are used for restoring stale cache if no cache hit occurred for key. Note `cache-hit` returns false in this case.
        upload_chunk_size: The chunk size used to split up large files during upload, in bytes
        enable_cross_os_archive: An optional boolean when enabled, allows windows runners to save or restore caches that can be restored or saved respectively on other platforms
        fail_on_cache_miss: Fail the workflow if cache entry is not found
        lookup_only: Check if a cache entry exists for the given input(s) (key, restore-keys) without downloading the cache
        save_always: Run the post step to save the cache even if another step before fails

    Returns:
        Step configured to use this action
    """
    with_dict = {
        "path": path,
        "key": key,
        "restore-keys": restore_keys,
        "upload-chunk-size": upload_chunk_size,
        "enableCrossOsArchive": enable_cross_os_archive,
        "fail-on-cache-miss": fail_on_cache_miss,
        "lookup-only": lookup_only,
        "save-always": save_always,
    }
    # Filter out None values
    with_dict = {k: v for k, v in with_dict.items() if v is not None}

    return Step(
        uses="actions/cache@v4",
        with_=with_dict if with_dict else None,
    )
