import logging
from threading import Thread

import TeamTalkPy


class TeamTalkThread(Thread):
    def __init__(self, ttclient):
        Thread.__init__(self, daemon=True)
        self.name = 'TeamTalkThread'
        self.ttclient = ttclient

    def run(self):
        empty_msg = TeamTalkPy.TTMessage()
        while True:
            msg = self.ttclient.getMessage()
            if msg == empty_msg:
                continue
            elif msg.nClientEvent == TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_USER_TEXTMSG and msg.textmessage.nMsgType == 1:
                logging.info('Got a message from user')
                self.ttclient.message_queue.put(self.ttclient.get_message(msg.textmessage))
            elif msg.nClientEvent == TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_MYSELF_KICKED:
                logging.warning('Kicked')
                self.ttclient.disconnect()
                self.ttclient.initialize()
            if msg.nClientEvent == TeamTalkPy.ClientEvent.CLIENTEVENT_CON_LOST:
                logging.warning('Server lost')
                self.ttclient.initialize()
