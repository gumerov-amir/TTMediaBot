from . import commands, event_handler, player, services, tt
import configparser
import gettext
import sys
from TeamTalkPy import ClientEvent



class Bot(object):
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        with open(config_file, "r", encoding="utf-8") as f:
            self.config.readfp(f)
        self.translation = gettext.translation("TTMediaBot", "local", languages=[self.config["general"]["language"]])
        self.translation.install()
        self.ttclient = tt.TeamTalk(self.config["teamtalk"])
        self.player = player.Player(self.ttclient, self.config["player"])
        self.services = {}
        for service_name in self.config["general"]["services"].split(","):
            self.services[service_name] = getattr(services, service_name).Service(self.config[service_name])
        self.process_command = commands.ProcessCommand(self.player, self.services, self.services[self.config['general']['default_service']])
        self.event_handler = event_handler.EventHandler(self.player, self.ttclient)

    def run(self):
        self.event_handler.start()
        while True:
            result, msg = self.ttclient.waitForEvent(ClientEvent.CLIENTEVENT_CMD_USER_TEXTMSG)
            if result:
                if msg.textmessage.nMsgType == 1:
                    print(msg.textmessage.szMessage)
                    reply_text = self.process_command(msg.textmessage.szMessage)
                    print(reply_text)
                    if reply_text:
                        self.ttclient.reply_to_message(msg.textmessage, reply_text)
