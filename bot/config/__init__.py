import json
import sys
from typing import Optional

import portalocker

from bot import utils
from bot.config.models import ConfigModel


def save_default_file() -> None:
    with open(utils.get_abs_path("config_default.json"), "w") as f:
        json.dump(ConfigModel().dict(), f, indent=4, ensure_ascii=False)


class ConfigManager:
    def __init__(self, file_name: Optional[str]) -> None:
        if file_name:
            if utils.check_file_path(file_name):
                self.file_name = file_name
                with open(self.file_name, "r", encoding="UTF-8") as f:
                    try:
                        config_dict = json.load(f)
                    except json.decoder.JSONDecodeError as e:
                        sys.exit("Syntax error in configuration file: " + str(e))
                self.file_locker = portalocker.Lock(
                    self.file_name,
                    timeout=0,
                    flags=portalocker.LOCK_EX | portalocker.LOCK_NB,
                )
                try:
                    self.file_locker.acquire()
                except portalocker.exceptions.LockException:
                    raise PermissionError()
            else:
                sys.exit("Incorrect configuration file path")
        else:
            config_dict = {}
        self.config: ConfigModel = ConfigModel(**config_dict)

    def close(self):
        self.file_locker.release()

    def save(self):
        self.file_locker.release()
        with open(self.file_name, "w", encoding="UTF-8") as f:
            json.dump(self.config.dict(), f, indent=4, ensure_ascii=False)
        self.file_locker.acquire()
