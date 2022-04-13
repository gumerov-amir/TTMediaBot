import sys

from bot.config import ConfigManager, config_data_type


def to_v1(config_data: config_data_type) -> config_data_type:
    return update_version(config_data, 1)


migrate_functs = {1: to_v1}


def migrate(
    config_manager: ConfigManager,
    config_data: config_data_type,
) -> config_data_type:
    if "config_version" not in config_data:
        update_version(config_data, 0)
    elif (
        not isinstance(config_data["config_version"], int)
        or config_data["config_version"] > config_manager.version
    ):
        sys.exit("Error: invalid config_version value")
    elif config_data["config_version"] == config_manager.version:
        return config_data
    else:
        for ver in migrate_functs:
            if ver > config_data["config_version"]:
                config_data = migrate_functs[ver](config_data)
        config_manager._dump(config_data)
    return config_data


def update_version(config_data: config_data_type, version: int) -> config_data_type:
    _config_data = {"config_version": version}
    _config_data.update(config_data)
    return _config_data
