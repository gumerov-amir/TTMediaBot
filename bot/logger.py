import logging
from logging.handlers import RotatingFileHandler


def initialize_logger(config):
    level = logging.getLevelName(config['level'])
    formatter = logging.Formatter(config['format'])
    handler = RotatingFileHandler(filename=config['file_name'], mode='a', maxBytes=config['max_file_size'] * 1024, backupCount=config['backup_count'])
    handler.setFormatter(formatter)
    handler.setLevel(level)
    root_logger = logging.getLogger('root')
    root_logger.setLevel(level)
    root_logger.addHandler(handler)
