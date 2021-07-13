from enum import Flag
import logging
from logging.handlers import RotatingFileHandler
import os
import sys

from bot import vars

class Mode(Flag):
    Stdout = 1
    File = 2
    StdoutFile = Stdout|File

def initialize_logger(config, file_name):
    logging.addLevelName(5, "PLAYER_DEBUG")
    level = logging.getLevelName(config.level)
    formatter = logging.Formatter(config.format)
    handlers = []
    try:
        mode = Mode(config.mode) if isinstance(config.mode, int) else Mode.__members__[config.mode]
    except KeyError:
        sys.exit("Invalid log mode name")
    if mode & Mode.File == Mode.File:
        if file_name:
            file_name = file_name
        else:
            file_name = config.file_name
        if os.path.isdir(os.path.join(*os.path.split(file_name)[0:-1])):
            file = file_name
        else:
            file = os.path.join(vars.directory, file_name)
        rotating_file_handler = RotatingFileHandler(filename=file, mode='a', maxBytes=config.max_file_size * 1024, backupCount=config.backup_count, encoding='UTF-8')
        rotating_file_handler.setFormatter(formatter)
        rotating_file_handler.setLevel(level)
        handlers.append(rotating_file_handler)
    if mode & Mode.Stdout == Mode.Stdout:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(level)
        handlers.append(stream_handler)
    logging.basicConfig(level=level, format=config.format, handlers=handlers)
