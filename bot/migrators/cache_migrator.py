from __future__ import annotations

import sys
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from bot.cache import CacheManager, cache_data_type


def to_v1(cache_data: cache_data_type) -> cache_data_type:
    return update_version(cache_data, 1)


migrate_functs = {1: to_v1}


def migrate(
    cache_manager: CacheManager,
    cache_data: cache_data_type,
) -> cache_data_type:
    if "cache_version" not in cache_data:
        cache_data = update_version(cache_data, 0)
    elif (
        not isinstance(cache_data["cache_version"], int)
        or cache_data["cache_version"] > cache_manager.version
    ):
        sys.exit("Error: invalid cache_version value")
    elif cache_data["cache_version"] == cache_manager.version:
        return cache_data
    else:
        for ver in migrate_functs:
            if ver > cache_data["cache_version"]:
                cache_data = migrate_functs[ver](cache_data)
        cache_manager._dump(cache_data)
    return cache_data


def update_version(cache_data: cache_data_type, version: int) -> cache_data_type:
    _cache_data = {"cache_version": version}
    _cache_data.update(cache_data)
    return _cache_data
