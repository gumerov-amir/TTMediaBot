from __future__ import annotations

import logging
import os
import sys
from enum import Flag
from logging.handlers import RotatingFileHandler
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from bot import Bot


class Mode(Flag):
    STDOUT = 1
    FILE = 2
    STDOUT_AND_FILE = STDOUT | FILE


def initialize_logger(bot: Bot) -> None:
    config = bot.config.logger
    logging.addLevelName(5, "PLAYER_DEBUG")
    level = logging.getLevelName(config.level)
    formatter = logging.Formatter(config.format)
    handlers: list[Any] = []
    try:
        mode = (
            Mode(config.mode)
            if isinstance(config.mode, int)
            else Mode.__members__[config.mode]
        )
    except KeyError:
        sys.exit("Invalid log mode name")
    if mode & Mode.FILE == Mode.FILE:
        file_name = bot.log_file_name if bot.log_file_name else config.file_name
        if os.path.isdir(os.path.join(*os.path.split(file_name)[0:-1])):
            file = file_name
        else:
            file = os.path.join(bot.config_manager.config_dir, file_name)
        rotating_file_handler = RotatingFileHandler(
            filename=file,
            mode="a",
            maxBytes=config.max_file_size * 1024,
            backupCount=config.backup_count,
            encoding="UTF-8",
        )
        rotating_file_handler.setFormatter(formatter)
        rotating_file_handler.setLevel(level)
        handlers.append(rotating_file_handler)
    if mode & Mode.STDOUT == Mode.STDOUT:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(level)
        handlers.append(stream_handler)
    logging.basicConfig(level=level, format=config.format, handlers=handlers)
