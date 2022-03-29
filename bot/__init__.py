import os
import logging
import queue
import sys
import time
from typing import Optional

from pydantic.error_wrappers import ValidationError

from bot import (
    TeamTalk,
    cache,
    commands,
    config,
    connectors,
    logger,
    modules,
    player,
    services,
    sound_devices,
    translator,
    app_vars,
)


class Bot:
    def __init__(
        self,
        config_file_name: Optional[str],
        cache_file_name: Optional[str] = None,
        log_file_name: Optional[str] = None,
    ) -> None:
        try:
            self.config_manager = config.ConfigManager(config_file_name)
            self.config = self.config_manager.config
        except ValidationError as e:
            for error in e.errors():
                print(
                    "Error in config:",
                    ".".join([str(i) for i in error["loc"]]),
                    error["msg"],
                )
            sys.exit(1)
        except PermissionError:
            sys.exit(
                "The configuration file cannot be accessed due to a permission error or is already used by another instance of the bot"
            )
        self.translator = translator.Translator(self.config.general.language)
        try:
            if cache_file_name:
                self.cache = cache.Cache(cache_file_name)
            else:
                cache_file_name = self.config.general.cache_file_name
                if not os.path.isdir(
                    os.path.join(*os.path.split(cache_file_name)[0:-1])
                ):
                    cache_file_name = os.path.join(
                        self.config_manager.config_dir, cache_file_name
                    )
                self.cache = cache.Cache(cache_file_name)
        except PermissionError:
            sys.exit(
                "The cache file cannot be accessed due to a permission error or is already used by another instance of the bot"
            )
        self.log_file_name = log_file_name
        self.player = player.Player(self)
        self.ttclient = TeamTalk.TeamTalk(self)
        self.tt_player_connector = connectors.TTPlayerConnector(self)
        self.sound_device_manager = sound_devices.SoundDeviceManager(self)
        self.service_manager = services.ServiceManager(self)
        self.module_manager = modules.ModuleManager(self)
        self.command_processor = commands.CommandProcessor(self)

    def initialize(self):
        if self.config.logger.log:
            logger.initialize_logger(self)
        logging.debug("Initializing")
        self.sound_device_manager.initialize()
        self.ttclient.initialize()
        self.player.initialize()
        self.service_manager.initialize()
        logging.debug("Initialized")

    def run(self):
        logging.debug("Starting")
        self.player.run()
        self.tt_player_connector.start()
        self.command_processor.run()
        logging.info("Started")
        self._close = False
        while not self._close:
            try:
                message = self.ttclient.message_queue.get_nowait()
                logging.info(
                    "New message {text} from {username}".format(
                        text=message.text, username=message.user.username
                    )
                )
                self.command_processor(message)
            except queue.Empty:
                pass
            time.sleep(app_vars.loop_timeout)

    def close(self) -> None:
        logging.debug("Closing bot")
        self.player.close()
        self.ttclient.close()
        self.tt_player_connector.close()
        self.config_manager.close()
        self.cache.close()
        self._close = True
        logging.info("Bot closed")
