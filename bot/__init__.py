import sys
from . import commands, event_handler, player, services, tt
import json
import gettext
import sys
from utils import Logger



class Bot(object):
    def __init__(self, config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        if self.config['general']['log']:
            sys.stdout = Logger(sys.stdout, self.config['general']['log_file_name'])
            sys.stderr = Logger(sys.stderr, self.config['general']['log_file_name'])
        self.translation = gettext.translation('TTMediaBot', 'locale', languages=[self.config['general']['language']])
        self.translation.install()
        self.ttclient = tt.TeamTalk(self.config['teamtalk'], self.config['users'])
        self.player = player.Player(self.ttclient, self.config['player'])
        self.service_manager = services.ServiceManager(self.config['services'])
        self.command_processor = commands.CommandProcessor(self.player, self.ttclient, self.service_manager)
        self.event_handler = event_handler.EventHandler(self.player, self.ttclient)

    def run(self):
        self.event_handler.start()
        while True:
            result, request_text, user = self.ttclient.get_private_message()
            if result:
                reply_text = self.command_processor(request_text, user)
                print("{text} from ({username}) replied: {reply_text}".format(text=request_text, username=user.username, reply_text=reply_text))
                if reply_text:
                    self.ttclient.send_message(reply_text, user)
