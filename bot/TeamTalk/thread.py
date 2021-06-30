import logging
import os
from threading import Thread
import types
import sys

import TeamTalkPy

class TeamTalkThread(Thread):
    def __init__(self, bot, ttclient):
        Thread.__init__(self, daemon=True)
        self.name = 'TeamTalkThread'
        self.bot = bot
        self.ttclient = ttclient
        self.event_names = {
            TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_USER_LOGGEDIN: "user_logged_in",
            TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_USER_LOGGEDOUT: "user_logged_out",
            TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_USER_JOINED: "user_joined_channel",
            TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_USER_LEFT: "user_left_channel",
            TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_USER_TEXTMSG: "message_sent",
            TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_CHANNEL_NEW: "channel_created",
            TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_CHANNEL_UPDATE: "channel_updated",
            TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_CHANNEL_REMOVE: "channel_removed",
            TeamTalkPy.ClientEvent.CLIENTEVENT_USER_STATECHANGE: "user_state_changed",
            TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_FILE_NEW: "file_uploaded",
            TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_FILE_REMOVE: "file_removed",
        }

    def run(self):
        from . import _str
        if self.ttclient.load_event_handlers:
            self.event_handlers = self.import_event_handlers()
        self._close = False
        while True:
            if self._close:
                break
            msg = self.ttclient.tt.getMessage()
            if msg.nClientEvent == TeamTalkPy.ClientEvent.CLIENTEVENT_NONE:
                continue
            elif msg.nClientEvent == TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_USER_TEXTMSG and msg.textmessage.nMsgType == 1:
                self.ttclient.message_queue.put(self.ttclient.get_message(msg.textmessage))
            elif msg.nClientEvent == TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_FILE_NEW and _str(msg.remotefile.szUsername) == self.ttclient.config["username"] and msg.remotefile.nChannelID == self.ttclient.get_my_channel_id():
                self.ttclient.uploaded_files_queue.put(self.ttclient.get_file(msg.remotefile))
            elif msg.nClientEvent == TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_MYSELF_KICKED:
                logging.warning('Kicked')
                self.ttclient.reconnect()
            elif msg.nClientEvent == TeamTalkPy.ClientEvent.CLIENTEVENT_CON_LOST:
                logging.warning('Server lost')
                self.ttclient.reconnect()
            elif msg.nClientEvent in self.event_names and self.ttclient.load_event_handlers:
                self.run_event_handler(msg)

    def close(self):
        self._close = True

    def import_event_handlers(self):
        try:
            if os.path.isfile(self.ttclient.event_handlers_file_name) and os.path.splitext(self.ttclient.event_handlers_file_name)[1] == ".py":
                module = __import__(os.path.splitext(self.ttclient.event_handlers_file_name)[0])
            elif os.path.isdir(self.ttclient.event_handlers_file_name) and "__init__.py" in os.listdir(self.ttclient.event_handlers_file_name):
                module = __import__(self.ttclient.event_handlers_file_name)
            else:
                logging.error("Incorrect path to event handlers. An empty module will be used")
                module = types.ModuleType("event_handlers")
        except Exception as e:
            logging.error("Can't load specified event handlers. Error: {}. An empty module will be used.".format(e))
            module = types.ModuleType("event_handlers")
        return module

    def parse_event(self, msg):
        if msg.nClientEvent in (TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_USER_UPDATE, TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_USER_JOINED, TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_USER_LOGGEDIN, TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_USER_LOGGEDOUT):
            return (self.ttclient.get_user(msg.user.nUserID),)
        elif msg.nClientEvent == TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_USER_LEFT:
            return (msg.nSource, self.ttclient.get_user(msg.user.nUserID))
        elif msg.nClientEvent == TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_USER_TEXTMSG:
            return (self.ttclient.get_message(msg.textmessage),)
        elif msg.nClientEvent in (TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_CHANNEL_NEW, TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_CHANNEL_UPDATE, TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_CHANNEL_REMOVE):
            return (self.ttclient.get_channel(msg.nChannelID),)
        elif msg.nClientEvent in (TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_FILE_NEW, TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_FILE_REMOVE):
            return (self.ttclient.get_file(msg.remotefile),)

    def run_event_handler(self, msg):
        try:
            event_handler = getattr(self.event_handlers, self.event_names[msg.nClientEvent], False)
            if not event_handler:
                return
            try:
                event_handler(*self.parse_event(msg), self.bot)
            except Exception as e:
                print("Error in event handling {}".format(e))
        except AttributeError:
            self.event_handlers = self.import_event_handlers()
            self.run_event_handler(msg)
