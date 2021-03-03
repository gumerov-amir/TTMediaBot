import TeamTalkPy
from TeamTalkPy import TTMessage, ClientEvent
import time
import sys


class TeamTalk(TeamTalkPy.TeamTalk):
    def __init__(self, config):
        TeamTalkPy.setLicense(config["license_name"], config["license_key"])
        TeamTalkPy.TeamTalk.__init__(self)
        self.connect(config["hostname"], int(config["tcp"]), int(config["udp"]))
        result, msg = self.waitForEvent(ClientEvent.CLIENTEVENT_CON_SUCCESS)
        if not result:
            sys.exit("Failed to connect")
        cmdid = self.doLogin(config["nickname"], config["username"], config["password"], config["client_name"])
        result, msg = self.waitForEvent(ClientEvent.CLIENTEVENT_CMD_MYSELF_LOGGEDIN)
        if not result:
            sys.exit("Failed to log in")
        result, msg = self.waitForEvent(ClientEvent.CLIENTEVENT_CMD_SERVER_UPDATE)
        if not result:
            sys.exit("Failed to log in")
        result, msg = self.waitForCmdSuccess(cmdid, 2000)
        if config["channel"].isdigit():
            channel_id = int(config["channel"])
        else:
            channel_id = self.getChannelIDFromPath(config["channel"])
            if channel_id == 0:
                channel_id = 1
        cmdid = self.doJoinChannelByID(channel_id, config["channel_password"])
        result, msg = self.waitForCmdSuccess(cmdid, 2000)
        if not result:
            sys.exit("Failed to join channel")

    def waitForEvent(self, event, timeout=2000):
        msg = self.getMessage(timeout)
        timestamp = lambda: int(round(time.time() * 1000))
        end = timestamp() + timeout
        while msg.nClientEvent != event:
            if timestamp() >= end:
                return False, TTMessage()
            msg = self.getMessage(timeout)
        return True, msg

    def waitForCmdSuccess(self, cmdid, timeout):
        result = True
        while result:
            result, msg = self.waitForEvent(ClientEvent.CLIENTEVENT_CMD_SUCCESS, timeout)
            if result and msg.nSource == cmdid:
                return result, msg
        return False, TTMessage()

    def reply_to_message(self, msg, text):
        if len(text) > 512:
            return
        message = TeamTalkPy.TextMessage()
        message.nFromUserID = self.getMyUserID()
        message.nMsgType = 1
        message.szMessage = text
        message.nToUserID = msg.nFromUserID
        self.doTextMessage(message)







