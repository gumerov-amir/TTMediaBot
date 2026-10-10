import os
import logging
import queue
import sys
import time
from typing import Optional
from bot.TeamTalk.structs import Message, MessageType, User, UserType, UserStatusMode, UserState
from bot import errors

from pydantic import ValidationError

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

from bot.player.enums import State
from bot.player.enums import Mode

class Bot:
    def __init__(
        self,
        config_file_name: Optional[str],
        cache_file_name: Optional[str] = None,
        log_file_name: Optional[str] = None,
    ) -> None:
        try:
            self.config_manager = config.ConfigManager(config_file_name)
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
        self.config = self.config_manager.config
        self.translator = translator.Translator(self.config.general.language)
        try:
            if cache_file_name:
                self.cache_manager = cache.CacheManager(cache_file_name)
            else:
                cache_file_name = self.config.general.cache_file_name
                if not os.path.isdir(
                    os.path.join(*os.path.split(cache_file_name)[0:-1])
                ):
                    cache_file_name = os.path.join(
                        self.config_manager.config_dir, cache_file_name
                    )
                self.cache_manager = cache.CacheManager(cache_file_name)
        except PermissionError:
            sys.exit(
                "The cache file cannot be accessed due to a permission error or is already used by another instance of the bot"
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

        # Esperar estar conectado E no canal antes de processar comandos de startup
        logging.info("Waiting to join channel...")
        max_wait = 30  # segundos máximos de espera
        waited = 0
        while not self.ttclient._joined_channel and waited < max_wait:
            time.sleep(1)
            waited += 1
            if waited % 5 == 0:
                logging.debug(f"Still waiting to join channel... ({waited}/{max_wait}s)")

        if not self.ttclient._joined_channel:
            logging.error("Timed out waiting to join channel!")
        else:
            logging.info(f"Successfully joined channel after {waited} seconds")

        logging.info(f"Processing {len(self.config.general.start_commands)} startup command(s)...")
        startup_context_user = User(
            id=-1, nickname="Startup", username="",
            channel=self.ttclient.channel,
            type=UserType.Admin, is_admin=True,
            status="", gender=UserStatusMode.N, state=UserState.Null,
            client_name="", version=0, user_account=None, is_banned=False
        )
        for command in self.config.general.start_commands:
            message = Message(text=command, user=startup_context_user, channel=self.ttclient.channel, type=MessageType.User)
            self.command_processor(message)
        if (
            self.player.mode == Mode.Queue
            and self.cache.queue
            and self.player.state == State.Stopped
        ):
            try:
                self.player.play_queue()
            except (errors.NothingIsPlayingError, errors.NoNextTrackError):
                pass
        self._close = False
        while not self._close:
            root_channel_id = self.config.general.root_channel_id
            if self.config.general.back_to_root_channel and len(self.ttclient.tt.getChannelUsers(self.ttclient.channel.id))==1 and self.ttclient.channel.id != root_channel_id:
                if self.player.state != State.Stopped:
                    self.player.stop()
                self.ttclient.DoMoveUser(self.ttclient.user.id, root_channel_id)
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
        self.cache_manager.close()
        self._close = True
        logging.info("Bot closed")
