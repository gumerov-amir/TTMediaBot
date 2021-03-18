import sys
from . import commands, event_handler, player, services, tt
import configparser
import gettext
import sys
from TeamTalkPy import ClientEvent
from utils import Logger



class Bot(object):
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config.readfp(f)
        if self.config.getboolean('general', 'log'):
            sys.stdout = Logger(self.config['general']['log_file_name'])
        self.translation = gettext.translation('TTMediaBot', 'local', languages=[self.config['general']['language']])
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
        self.process_command = commands.ProcessCommand(self.player, self.ttclient, self.services, self.services[self.config['general']['default_service']])
        self.event_handler = event_handler.EventHandler(self.player, self.ttclient)
        self.admins = self.config['general']['admins'].split(',')
        self.banned_users = self.config['general']['banned_users'].split(',')

    def run(self):
        self.event_handler.start()
        while True:
            result, msg = self.ttclient.waitForEvent(ClientEvent.CLIENTEVENT_CMD_USER_TEXTMSG)
            if result:
                if msg.textmessage.nMsgType == 1:
                    print(msg.textmessage.szMessage)
                    print(msg.textmessage.szFromUsername)
                    if not msg.textmessage.szFromUsername in self.banned_users:
                        reply_text = self.process_command(msg.textmessage.szMessage, is_admin=msg.textmessage.szFromUsername in self.admins)
                    else:
                        reply_text = _('You are a banned user.')
                    print(reply_text)
                    if reply_text:
                        self.ttclient.reply_to_message(msg.textmessage, reply_text)
