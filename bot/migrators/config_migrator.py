import sys

from bot.config import ConfigManager, config_data_type


def to_v1(config_data: config_data_type) -> config_data_type:
    return update_version(config_data, 1)


def to_v2(config_data: config_data_type) -> config_data_type:
    if "player" in config_data and "bass_boost_level" not in config_data["player"]:
        config_data["player"]["bass_boost_level"] = 0
    return update_version(config_data, 2)

def to_v3(config_data: config_data_type) -> config_data_type:
    if "general" in config_data and "enable_positions" not in config_data["general"]:
        config_data["general"]["enable_positions"] = False
    return update_version(config_data, 3)

migrate_functs = {1: to_v1, 2: to_v2, 3: to_v3}


def migrate(
    config_manager: ConfigManager,
    config_data: config_data_type,
) -> config_data_type:
    if "config_version" not in config_data:
        config_data = update_version(config_data, 0)
    elif (
        not isinstance(config_data["config_version"], int)
        or config_data["config_version"] > config_manager.version
    ):
        sys.exit("Error: invalid config_version value")
    elif config_data["config_version"] == config_manager.version:
        return config_data
    else:
        for ver in sorted(migrate_functs):
            if ver > config_data["config_version"]:
                config_data = migrate_functs[ver](config_data)
        config_manager._dump(config_data)
    return config_data


def update_version(config_data: config_data_type, version: int) -> config_data_type:
    _config_data = {"config_version": version}
    _config_data.update(config_data)
    return _config_data
