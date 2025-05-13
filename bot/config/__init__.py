import json
import sys
from pathlib import Path
from typing import Any

import portalocker

from bot import app_vars, utils
from bot.config.models import ConfigModel
from bot.migrators import config_migrator

config_data_type = dict[str, Any]


def save_default_file() -> None:
    with Path(utils.get_abs_path("config_default.json")).open("w") as f:
        json.dump(ConfigModel().dict(), f, indent=4, ensure_ascii=False)


class ConfigManager:
    version = 1

    def __init__(self, file_name: str | None) -> None:
        if file_name:
            if Path(file_name).is_file():
                self.file_name = Path(file_name).resolve()
                config_dict = config_migrator.migrate(self, self._load())
                self.config_dir = Path(self.file_name).parent
                self._lock()
            else:
                sys.exit("Incorrect configuration file path")
        else:
            self.config_dir = app_vars.directory
            config_dict = {}
        self.config: ConfigModel = ConfigModel(**config_dict)

    def dump(self, data: config_data_type) -> None:
        with Path(self.file_name).open("w", encoding="UTF-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _load(self) -> config_data_type:
        with Path(self.file_name).open(encoding="UTF-8") as f:
            try:
                return json.load(f)
            except json.decoder.JSONDecodeError as e:
                sys.exit("Syntax error in configuration file: " + str(e))

    def _lock(self) -> None:
        self.file_locker = portalocker.Lock(
            self.file_name,
            timeout=0,
            flags=portalocker.LOCK_EX | portalocker.LOCK_NB,
        )
        try:
            self.file_locker.acquire()
        except portalocker.exceptions.LockException as e:
            raise PermissionError from e

    def close(self) -> None:
        self.file_locker.release()

    def save(self) -> None:
        self.file_locker.release()
        self.dump(self.config.dict())
        self.file_locker.acquire()
