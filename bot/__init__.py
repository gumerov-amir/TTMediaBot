import gettext
import json
import logging

from bot import commands, connectors, modules, player, services, sound_devices, TeamTalk


class Bot(object):
    def __init__(self, config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        if self.config['logger']['log']:
            logging.basicConfig(format=self.config['logger']['format'], level=logging.getLevelName(self.config['logger']['level_name']), filename=self.config['logger']['file_name'])
        self.translation = gettext.translation('TTMediaBot', 'locale', languages=[self.config['general']['language']])
        self.translation.install()
        self.player = player.Player(self.config['player'])
        self.ttclient = TeamTalk.TeamTalk(self.config['teamtalk'], self.config['users'])
        self.tt_player_connector = connectors.TTPlayerConnector(self.player, self.ttclient)
        self.sound_device_manager = sound_devices.SoundDeviceManager(self.config['sound_devices'], self. player, self.ttclient)
        self.service_manager = services.ServiceManager(self.config['services'])
        self.module_manager = modules.ModuleManager(self.player, self.ttclient, self.service_manager)
        self.command_processor = commands.CommandProcessor(self.player, self.ttclient, self.module_manager, self.service_manager)

    def initialize(self):
        logging.debug('Initializing')
        self.ttclient.initialize()
        self.sound_device_manager.initialize()
        self.service_manager.initialize()
        logging.debug('Initialized')

    def run(self):
        logging.debug('Starting')
        self.ttclient.run()
        self.player.run()
        self.tt_player_connector.start()
        logging.debug('Started')
        while True:
            message = self.ttclient.message_queue.get()
            reply_text = self.command_processor(message)
            logging.info("{text} from ({username}) replied: {reply_text}".format(text=message.text, username=message.user.username, reply_text=reply_text))
            if reply_text:
                self.ttclient.send_message(reply_text, message.user)
