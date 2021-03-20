import TeamTalkPy
from TeamTalkPy import TTMessage, ClientEvent
import time
import sys

def _str(data):
    if isinstance(data, str):
        if sys.platform != 'win32':
            return bytes(data, 'utf-8')
        else:
            return data
    elif isinstance(data, bytes):
        return str(data, 'utf-8')





class TeamTalk(TeamTalkPy.TeamTalk):
    def __init__(self, config):
        TeamTalkPy.setLicense(_str(config['license_name']), _str(config['license_key']))
        TeamTalkPy.TeamTalk.__init__(self)
        self.connect(_str(config['hostname']), int(config['tcp']), int(config['udp']))
        result, msg = self.waitForEvent(ClientEvent.CLIENTEVENT_CON_SUCCESS)
        if not result:
            sys.exit('Failed to connect')
        cmdid = self.doLogin(_str(config['nickname']), _str(config['username']), _str(config['password']), _str(config['client_name']))
        result, msg = self.waitForEvent(ClientEvent.CLIENTEVENT_CMD_MYSELF_LOGGEDIN)
        if not result:
            sys.exit('Failed to log in')
        result, msg = self.waitForEvent(ClientEvent.CLIENTEVENT_CMD_SERVER_UPDATE)
        if not result:
            sys.exit('Failed to log in')
        result, msg = self.waitForCmdSuccess(cmdid, 2000)
        if config['channel'].isdigit():
            channel_id = int(config['channel'])
        else:
            channel_id = self.getChannelIDFromPath(_str(config['channel']))
            if channel_id == 0:
                channel_id = 1
        cmdid = self.doJoinChannelByID(channel_id, _str(config['channel_password']))
        result, msg = self.waitForCmdSuccess(cmdid, 2000)
        if not result:
            sys.exit('Failed to join channel')

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

    def send_message(self, text, user=None, type=1):
        if len(text) > 512:
            print(len(text))
            return
        message = TeamTalkPy.TextMessage()
        message.nFromUserID = self.getMyUserID()
        message.nMsgType = type
        message.szMessage = text
        if type == 1:
            message.nToUserID = user.id
        elif type == 2:
            message.nChannelID = self.getMyChannelID()
        self.doTextMessage(message)

    def change_nickname(self, nickname):
        self.doChangeNickname(_str(nickname))

    def change_status_text(self, text):
        self.doChangeStatus(0, _str(text))





    def get_user(self, id):
        user = self.getUser(id)
        return User(user.nUserID, _str(user.szNickname), _str(user.szUsername), user.nChannelID)


class User:
    def __init__(self, id, nickname, username, channel_id):
        self.id = id
        self.nickname = nickname
        self.username = username
        self.channel_id = channel_id



