from __future__ import annotations
from enum import Enum
import logging
import sys
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from bot import Bot


class SoundDevice:
    def __init__(self, name: str, id: Union[int, str], type: SoundDeviceType) -> None:
        self.name = name
        self.id = id
        self.type = type


class SoundDeviceType(Enum):
    Output = 0
    Input = 1


class SoundDeviceManager:
    def __init__(self, bot: Bot) -> None:
        self.config = bot.config
        self.output_device_index = self.config.sound_devices.output_device
        self.input_device_index = self.config.sound_devices.input_device
        self.player = bot.player
        self.ttclient = bot.ttclient
        self.output_devices = self.player.get_output_devices()
        self.input_devices = self.ttclient.get_input_devices()

    def initialize(self) -> None:
        logging.debug("Initializing sound devices")
        try:
            self.player.set_output_device(
                str(self.output_devices[self.output_device_index].id)
            )
        except IndexError:
            error = "Incorrect output device index: " + str(self.output_device_index)
            logging.error(error)
            sys.exit(error)
        try:
            self.ttclient.set_input_device(
                int(self.input_devices[self.input_device_index].id)
            )
        except IndexError:
            error = "Incorrect input device index: " + str(self.input_device_index)
            logging.error(error)
            sys.exit(error)
        logging.debug("Sound devices initialized")
