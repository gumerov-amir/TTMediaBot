import _thread
import logging
import TeamTalkPy
from TeamTalkPy import TTMessage, ClientEvent
import time
import sys
import queue

from bot.TeamTalk import thread
from bot.sound_devices import SoundDevice, SoundDeviceType
from bot import errors, vars


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
                        for i in range(0, int(len(chunc) / max_length) + 1):
                            words.append(chunc[0:max_length])
                            chunc = chunc[max_length::]
                lines += words
    return lines


class TeamTalk:
    def __init__(self, config):
        TeamTalkPy.setLicense(_str(config['license_name']), _str(config['license_key']))
        self.config = config
        self.tt = TeamTalkPy.TeamTalk()
        self.admins = self.config['users']['admins']
        self.banned_users = self.config['users']['banned_users']
        self.teamtalk_thread = thread.TeamTalkThread(self)
        self.message_queue = queue.SimpleQueue()

    def initialize(self):
        logging.debug('Initializing TeamTalk')
        self.connect()
        logging.debug('TeamTalk initialized')

    def run(self):
        logging.debug('Starting TeamTalk')
        self.teamtalk_thread.start()
        logging.debug('TeamTalk started')

    def connect(self):
        self.tt.connect(_str(self.config['hostname']), self.config['tcp'], self.config['udp'], self.config['encrypted'])
        result, msg = self.waitForEvent(ClientEvent.CLIENTEVENT_CON_SUCCESS)
        if not result:
            raise errors.ConnectionError()
        cmdid = self.tt.doLogin(_str(self.config['nickname']), _str(self.config['username']), _str(self.config['password']), _str('TTMediaBot-V{ver}'.format(ver=vars.version)))
        result, msg = self.waitForEvent(ClientEvent.CLIENTEVENT_CMD_MYSELF_LOGGEDIN)
        if not result:
            raise errors.LoginError()
        result, msg = self.waitForEvent(ClientEvent.CLIENTEVENT_CMD_SERVER_UPDATE)
        if not result:
            raise errors.LoginError()
        result, msg = self.waitForCmdSuccess(cmdid, 2000)
        if isinstance(self.config['channel'], int):
            channel_id = int(self.config['channel'])
        else:
            channel_id = self.tt.getChannelIDFromPath(_str(self.config['channel']))
            if channel_id == 0:
                channel_id = 1
        cmdid = self.tt.doJoinChannelByID(channel_id, _str(self.config['channel_password']))
        result, msg = self.waitForCmdSuccess(cmdid, 2000)
        if not result:
            cmdid = self.tt.doJoinChannelByID(0, _str(''))
            result, msg = self.waitForCmdSuccess(cmdid, 2000)
            if not result:
                raise errors.JoinChannelError()

    def reconnect(self):
        logging.info('Reconnecting')
        self.tt.disconnect()
        attempt = 0
        while attempt != self.config['reconnection_attempts']:
            try:
                self.connect()
                logging.info('Reconnected')
                return
            except errors.ConnectionError:
                time.sleep(self.config['reconnection_timeout'])
                attempt += 1
        logging.error('Not reconnected')
        _thread.interrupt_main()

    def waitForEvent(self, event, timeout=2000):
        msg = self.tt.getMessage(timeout)
        timestamp = lambda: int(round(time.time() * 1000))
        end = timestamp() + timeout
        while msg.nClientEvent != event:
            if timestamp() >= end:
                return False, TTMessage()
            msg = self.tt.getMessage(timeout)
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
            message.nFromUserID = self.tt.getMyUserID()
            message.nMsgType = type
            message.szMessage = _str(string)
            if type == 1:
                message.nToUserID = user.id
            elif type == 2:
                message.nChannelID = self.tt.getMyChannelID()
            self.tt.doTextMessage(message)

    def change_nickname(self, nickname):
        self.tt.doChangeNickname(_str(nickname))

    def change_status_text(self, text):
        self.tt.doChangeStatus(0, _str(split(text)[0][0:256]))

    def get_user(self, id):
        user = self.tt.getUser(id)
        return User(user.nUserID, _str(user.szNickname), _str(user.szUsername), user.nChannelID, _str(user.szUsername) in self.admins, _str(user.szUsername) in self.banned_users)

    def get_message(self, msg):
        return Message(_str(msg.szMessage), self.get_user(msg.nFromUserID))

    def get_my_channel_id(self):
        return self.tt.getMyChannelID()

    def get_input_devices(self):
        devices = []
        device_list = [i for i in self.tt.getSoundDevices()]
        for device in device_list:
            if sys.platform == 'win32':
                if device.nSoundSystem == TeamTalkPy.SoundSystem.SOUNDSYSTEM_WASAPI:
                    devices.append(SoundDevice(_str(device.szDeviceName), device.nDeviceID, SoundDeviceType.Input))
            else:
                devices.append(SoundDevice(_str(device.szDeviceName), device.nDeviceID, SoundDeviceType.Input))
        return devices

    def set_input_device(self, id):
        self.tt.initSoundInputDevice(id)

    def enable_voice_transmission(self):
        self.tt.enableVoiceTransmission(True)

    def disable_voice_transmission(self):
        self.tt.enableVoiceTransmission(False)


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
