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

def split(text):
    strings = []
    for i in range(0, int(len(text) / 512) + 1):
        strings.append(text[0:512])
        text = text[512::]
    return strings

class TeamTalk(TeamTalkPy.TeamTalk):
    def __init__(self, tt_config, user_config):
        TeamTalkPy.setLicense(_str(tt_config['license_name']), _str(tt_config['license_key']))
        TeamTalkPy.TeamTalk.__init__(self)
        self.connect(_str(tt_config['hostname']), tt_config['tcp'], tt_config['udp'], tt_config['encrypted'])
        result, msg = self.waitForEvent(ClientEvent.CLIENTEVENT_CON_SUCCESS)
        if not result:
            sys.exit('Failed to connect')
        cmdid = self.doLogin(_str(tt_config['nickname']), _str(tt_config['username']), _str(tt_config['password']), _str(tt_config['client_name']))
        result, msg = self.waitForEvent(ClientEvent.CLIENTEVENT_CMD_MYSELF_LOGGEDIN)
        if not result:
            sys.exit('Failed to log in')
        result, msg = self.waitForEvent(ClientEvent.CLIENTEVENT_CMD_SERVER_UPDATE)
        if not result:
            sys.exit('Failed to log in')
        result, msg = self.waitForCmdSuccess(cmdid, 2000)
        if isinstance(tt_config['channel'], int):
            channel_id = int(tt_config['channel'])
        else:
            channel_id = self.getChannelIDFromPath(_str(tt_config['channel']))
            if channel_id == 0:
                channel_id = 1
        cmdid = self.doJoinChannelByID(channel_id, _str(tt_config['channel_password']))
        result, msg = self.waitForCmdSuccess(cmdid, 2000)
        if not result:
            sys.exit('Failed to join channel')
        self.admins = user_config['admins']
        self.banned_users = user_config['banned_users']

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

    def get_private_message(self):
        result, msg = self.waitForEvent(ClientEvent.CLIENTEVENT_CMD_USER_TEXTMSG)
        if result:
            if msg.textmessage.nMsgType == 1:
                return True, _str(msg.textmessage.szMessage), self.get_user(msg.textmessage.nFromUserID)
            else:
                return False, None, None
        else:
            return False, None, None




    def send_message(self, text, user=None, type=1):
        for string in split(text):
            message = TeamTalkPy.TextMessage()
            message.nFromUserID = self.getMyUserID()
            message.nMsgType = type
            message.szMessage = _str(string)
            if type == 1:
                message.nToUserID = user.id
            elif type == 2:
                message.nChannelID = self.getMyChannelID()
            self.doTextMessage(message)

    def change_nickname(self, nickname):
        self.doChangeNickname(_str(nickname))

    def change_status_text(self, text):
        self.doChangeStatus(0, _str(split(text)[0][0:256]))





    def get_user(self, id):
        user = self.getUser(id)
        return User(user.nUserID, _str(user.szNickname), _str(user.szUsername), user.nChannelID, _str(user.szUsername) in self.admins, _str(user.szUsername) in self.banned_users)

    def get_my_channel_id(self):
        return self.getMyChannelID()



class User:
    def __init__(self, id, nickname, username, channel_id, is_admin, is_banned):
        self.id = id
        self.nickname = nickname
        self.username = username
        self.channel_id = channel_id
        self.is_admin = is_admin
        self.is_banned = is_banned



