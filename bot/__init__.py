import logging
import os
import queue
import sys
import time
from pathlib import Path

from pydantic import ValidationError

from bot import (
    TeamTalk,
    app_vars,
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
)
from bot.TeamTalk.structs import (
    Message,
    MessageType,
    User,
    UserState,
    UserStatusMode,
    UserType,
)


class Bot:
    def __init__(
        self,
        config_file_name: str | None,
        cache_file_name: str | None = None,
        log_file_name: str | None = None,
    ) -> None:
        try:
            self.config_manager = config.ConfigManager(config_file_name)
        except ValidationError as e:
            for _error in e.errors():
                pass
            sys.exit(1)
        except PermissionError:
            sys.exit(
                "The configuration file cannot be accessed due to a permission error or is already used by another instance of the bot",
            )
        self.config = self.config_manager.config
        self.translator = translator.Translator(self.config.general.language)
        try:
            if cache_file_name:
                self.cache_manager = cache.CacheManager(cache_file_name)
            else:
                cache_file_name = self.config.general.cache_file_name
                if not Path().joinpath(*os.path.split(cache_file_name)[0:-1]).is_dir():
                    cache_file_name = str(
                        Path(self.config_manager.config_dir) / cache_file_name
                    )
                self.cache_manager = cache.CacheManager(cache_file_name)
        except PermissionError:
            sys.exit(
                "The cache file cannot be accessed due to a permission error or is already used by another instance of the bot",
            )
        self.cache = self.cache_manager.cache
        self.log_file_name = log_file_name
        self.player = player.Player(self)
        self.ttclient = TeamTalk.TeamTalk(self)
        self.tt_player_connector = connectors.TTPlayerConnector(self)
        self.sound_device_manager = sound_devices.SoundDeviceManager(self)
        self.service_manager = services.ServiceManager(self)
        self.module_manager = modules.ModuleManager(self)
        self.command_processor = commands.CommandProcessor(self)

    def initialize(self) -> None:
        if self.config.logger.log:
            logger.initialize_logger(self)
        logging.debug("Initializing")
        self.sound_device_manager.initialize()
        self.ttclient.initialize()
        self.player.initialize()
        self.service_manager.initialize()
        logging.debug("Initialized")

    def run(self) -> None:
        logging.debug("Starting")
        self.player.run()
        self.tt_player_connector.start()
        self.command_processor.run()
        logging.info("Started")
        logging.info(
            f"Processing {len(self.config.general.start_commands)} startup command(s)...",
        )
        startup_context_user = User(
            user_id=-1,
            nickname="Startup",
            username="",
            channel=self.ttclient.channel,
            user_type=UserType.Admin,
            is_admin=True,
            status="",
            gender=UserStatusMode.N,
            state=UserState.Null,
            client_name="",
            version=0,
            user_account=None,
            is_banned=False,
        )
        for command in self.config.general.start_commands:
            message = Message(
                text=command,
                user=startup_context_user,
                channel=self.ttclient.channel,
                message_type=MessageType.User,
            )
            self.command_processor(message)
        self._close = False
        while not self._close:
            try:
                message = self.ttclient.message_queue.get_nowait()
                logging.info(
                    f"New message {message.text} from {message.user.username}",
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
        self.cache_manager.close()
        self._close = True
        logging.info("Bot closed")
