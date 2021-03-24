import logging
import TeamTalkPy
from TeamTalkPy import TTMessage, ClientEvent
import time
import sys
import queue

from bot.TeamTalk.thread import TeamTalkThread
from bot.sound_devices import SoundDevice, SoundDeviceType
from bot import vars


def _str(data):
    if isinstance(data, str):
        if sys.platform != 'win32':
            return bytes(data, 'utf-8')
        else:
            return data
    elif isinstance(data, bytes):
        return str(data, 'utf-8')


def split(text, max_length=vars.max_message_length):
    if len(text) <= max_length:
        lines = [text]
    else:
        lines = ['']
        for line in text.split('\n'):
            if len(line) < max_length:
                if len(lines[-1]) + len(line) + 1 <= max_length:
                    lines[-1] += '\n' + line
                else:
                    lines.append(line)
            else:
                words = ['']
                for word in line.split(' '):
                    if len(word) <= max_length:
                        if len(words[-1]) + len(word) + 1 <= max_length:
                            words[-1] += ' ' + word
                        else:
                            words.append(word)
                    else:
                        chunc = word
                        for i in range(0, int(len(word) / max_length) + 1):
                            words.append(chunc[0:max_length])
                            chunc = chunc[max_length::]
                lines += words
    return lines


class TeamTalk(TeamTalkPy.TeamTalk):
    def __init__(self, tt_config, user_config):
        TeamTalkPy.setLicense(_str(tt_config['license_name']), _str(tt_config['license_key']))
        TeamTalkPy.TeamTalk.__init__(self)
        self.config = tt_config
        self.user_config = user_config
        self.admins = self.user_config['admins']
        self.banned_users = self.user_config['banned_users']
        self.teamtalk_thread = TeamTalkThread(self)
        self.message_queue = queue.SimpleQueue()

    def initialize(self):
        logging.debug('Initializing TeamTalk')
        self.connect(_str(self.config['hostname']), self.config['tcp'], self.config['udp'], self.config['encrypted'])
        result, msg = self.waitForEvent(ClientEvent.CLIENTEVENT_CON_SUCCESS)
        if not result:
            sys.exit('Failed to connect')
        cmdid = self.doLogin(_str(self.config['nickname']), _str(self.config['username']), _str(self.config['password']), _str(self.config['client_name']))
        result, msg = self.waitForEvent(ClientEvent.CLIENTEVENT_CMD_MYSELF_LOGGEDIN)
        if not result:
            sys.exit('Failed to log in')
        result, msg = self.waitForEvent(ClientEvent.CLIENTEVENT_CMD_SERVER_UPDATE)
        if not result:
            sys.exit('Failed to log in')
        result, msg = self.waitForCmdSuccess(cmdid, 2000)
        if isinstance(self.config['channel'], int):
            channel_id = int(self.config['channel'])
        else:
            channel_id = self.getChannelIDFromPath(_str(self.config['channel']))
            if channel_id == 0:
                channel_id = 1
        cmdid = self.doJoinChannelByID(channel_id, _str(self.config['channel_password']))
        result, msg = self.waitForCmdSuccess(cmdid, 2000)
        if not result:
            sys.exit('Failed to join channel')
        logging.debug('TeamTalk initialized')

    def run(self):
        logging.debug('Starting TeamTalk')
        self.teamtalk_thread.start()
        logging.debug('TeamTalk started')

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

    def get_message(self, msg):
        return Message(_str(msg.szMessage), self.get_user(msg.nFromUserID))

    def get_my_channel_id(self):
        return self.getMyChannelID()

    def get_input_devices(self):
        devices = []
        device_list = [i for i in self.getSoundDevices()]
        for device in device_list:
            devices.append(SoundDevice(_str(device.szDeviceName), device.nDeviceID, SoundDeviceType.Input))
        return devices

    def set_input_device(self, id):
        self.initSoundInputDevice(id)


class Message:
    def __init__(self, text, user):
        self.text = text
        self.user = user


class User:
    def __init__(self, id, nickname, username, channel_id, is_admin, is_banned):
        self.id = id
        self.nickname = nickname
        self.username = username
        self.channel_id = channel_id
        self.is_admin = is_admin
        self.is_banned = is_banned
