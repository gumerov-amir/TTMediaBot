from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.cache import CacheManager, cache_data_type


def to_v1(cache_data: cache_data_type) -> cache_data_type:
    return update_version(cache_data, 1)


def to_v2(cache_data: cache_data_type) -> cache_data_type:
    if "queue" not in cache_data:
        cache_data["queue"] = []
    cache_data.pop("queue_mode", None)
    return update_version(cache_data, 2)


def to_v3(cache_data: cache_data_type) -> cache_data_type:
    if "positions" not in cache_data:
        cache_data["positions"] = {}
    return update_version(cache_data, 3)

migrate_functs = {1: to_v1, 2: to_v2, 3: to_v3}


def to_v4(cache_data: cache_data_type) -> cache_data_type:
    cache_data.pop("positions", None)
    return update_version(cache_data, 4)

migrate_functs[4] = to_v4


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
        for ver in sorted(migrate_functs):
            if ver > cache_data["cache_version"]:
                cache_data = migrate_functs[ver](cache_data)
        cache_manager._dump(cache_data)
    return cache_data


def update_version(cache_data: cache_data_type, version: int) -> cache_data_type:
    _cache_data = {"cache_version": version}
    _cache_data.update(cache_data)
    return _cache_data
