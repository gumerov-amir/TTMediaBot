from typing import Callable, Dict
from version import Version

from bot import app_vars
from bot.config import ConfigManager
from bot.cache import Cache


class Migrator:
    def __init__(self, config_manager: ConfigManager, cache: Cache):
        self.current_version = Version(app_vars.app_version)
        self.config_manager = config_manager
        self.cache = cache
        self.migrate_functions: Dict[str, Callable[..., None]] = {"2.3.0": self.V2_3_0}

    def migrate(self):
        config_version = Version(self.config_manager.config.version)
        if config_version == self.current_version:
            return
        for version in self.migrate_functions:
            if Version(version) > config_version:
                self.migrate_functions[version]()
        self.config_manager.config.version = app_vars.app_version
        self.config_manager.save()
        self.cache.save()

    def V2_3_0(self):
        self.config_manager.config.version = "2.3.0"
