import logging
from threading import Thread

import TeamTalkPy

class TeamTalkThread(Thread):
    def __init__(self, bot, config, ttclient):
        Thread.__init__(self, daemon=True)
        self.name = 'TeamTalkThread'
        self.bot = bot
        self.load_event_handlers = config["general"]["load_event_handlers"]
        self.event_handlers_file_name = config["general"]["event_handlers_file_name"]
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
        if self.load_event_handlers:
            try:
                event_handlers = __import__(".".join(self.event_handlers_file_name.split(".")[0:-1]))
            except Exception as e:
                logging.error("Can't load specified event handlers." + e)
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
            if msg.nClientEvent == TeamTalkPy.ClientEvent.CLIENTEVENT_CON_LOST:
                logging.warning('Server lost')
                self.ttclient.reconnect()
            elif msg.nClientEvent in self.event_names and self.load_event_handlers:
                try:
                    event_handler = getattr(event_handlers, self.event_names[msg.nClientEvent])
                    try:
                        event_handler(*self.parse_event(msg), self.bot)
                    except KeyError:
                        pass
                    except Exception as e:
                        logging.error(e)
                except AttributeError:
                    pass

    def close(self):
        self._close = True

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
