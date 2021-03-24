from enum import Enum
import logging


class SoundDeviceManager:
    def __init__(self, config, player, ttclient):
        self.output_device_index = config['output']
        self.input_device_index = config['input']
        self.player = player
        self.ttclient = ttclient
        self.output_devices = self.player.get_output_devices()
        self.input_devices = self.ttclient.get_input_devices()

    def initialize(self):
        logging.debug('Initializing sound devices')
        self.player.set_output_device(self.output_devices[self.output_device_index].id)
        self.ttclient.set_input_device(self.input_devices[self.input_device_index].id)
        logging.debug('Sound devices initialized')


class SoundDevice:
    def __init__(self, name, id, type):
        self.name = name
        self.id = id
        self.type = type


class SoundDeviceType(Enum):
    Output = 0
    Input = 1
