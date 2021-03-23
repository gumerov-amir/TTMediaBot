import logging
from threading import Thread
import time

from TeamTalkPy import ClientEvent

from bot import vars


class TeamTalkThread(Thread):
    def __init__(self, ttclient):
        Thread.__init__(self)
        self.ttclient = ttclient

    def run(self):
        print('text')
        while True:
            result, msg = self.ttclient.waitForEvent(ClientEvent.CLIENTEVENT_CMD_MYSELF_KICKED)
            print(result, msg)
            if result:
                logging.warning('Kicked')
                self.ttclient.initialize()
            result, msg = self.ttclient.waitForEvent(ClientEvent.CLIENTEVENT_CON_LOST)
            print(result, msg)
            if result:
                logging.warning('Server lost')
                self.ttclient.initialize()
            time.sleep(vars.loop_timeout)
