import sys
from . import commands, event_handler, player, services, tt
import configparser
import gettext
import sys
from utils import Logger



class Bot(object):
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config.readfp(f)
        if self.config.getboolean('general', 'log'):
            sys.stdout = Logger(sys.stdout, self.config['general']['log_file_name'])
            sys.stderr = Logger(sys.stderr, self.config['general']['log_file_name'])
        self.translation = gettext.translation('TTMediaBot', 'locale', languages=[self.config['general']['language']])
        self.translation.install()
        self.ttclient = tt.TeamTalk(self.config['teamtalk'])
        self.player = player.Player(self.ttclient, self.config['player'])
        self.services = {}
        for service_name in self.config['general']['services'].split(','):
            Service = getattr(services, service_name).Service
            if self.config.has_section(service_name):
                config = self.config[service_name]
            else:
                None
            self.services[service_name] = Service(config)
        self.process_command = commands.ProcessCommand(self.player, self.ttclient, self.services, self.services[self.config['general']['default_service']], self.config['general']['admins'], self.config['general']['banned_users'])
        self.event_handler = event_handler.EventHandler(self.player, self.ttclient)

    def run(self):
        self.event_handler.start()
        while True:
            result, request_text, user = self.ttclient.get_private_message()
            if result:
                reply_text = self.process_command(request_text, user)
                print("{text} from ({username}) replied: {reply_text}".format(text=request_text, username=user.username, reply_text=reply_text))
                if reply_text:
                    self.ttclient.send_message(reply_text, user)
