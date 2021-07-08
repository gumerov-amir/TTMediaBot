import _thread
import logging
import os
import time
import re
import sys
import queue

from bot.sound_devices import SoundDevice, SoundDeviceType
from bot import errors, vars

if sys.platform == "win32":
    if (sys.version_info.major == 3 and sys.version_info.minor >= 8):
        os.add_dll_directory(vars.directory)
    else:
        os.chdir(vars.directory)

from bot.TeamTalk import thread
from bot.TeamTalk.structs import *

import TeamTalkPy
from TeamTalkPy import TTMessage, ClientEvent, ClientFlags

re_line_endings = re.compile('[\\r\\n]')
genders = {'m': 0, 'f': 256, 'n': 4096}


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
            if len(line) <= max_length:
                if len(lines[-1]) > 0 and len(lines[-1]) + len(line) + 1 <= max_length:
                    lines[-1] += '\n' + line
                elif len(lines) == 1 and len(lines[0]) == 0:
                    lines[0] = line
                else:
                    lines.append(line)
            else:
                words = ['']
                for word in line.split(' '):
                    if len(word) <= max_length:
                        if len(words[-1]) > 0 and len(words[-1]) + len(word) + 1 <= max_length:
                            words[-1] += ' ' + word
                        elif len(words) == 1 and len(words[0]) == 0:
                            words[0] == word
                        else:
                            words.append(word)
                    else:
                        chunk = word
                        for i in range(0, int(len(chunk) / max_length) + 1):
                            words.append(chunk[0:max_length])
                            chunk = chunk[max_length::]
                lines += words
    return lines


class TeamTalk:
    def __init__(self, bot, config):
        self.config = config["teamtalk"]
        TeamTalkPy.setLicense(_str(self.config['license_name']), _str(self.config['license_key']))
        self.tt = TeamTalkPy.TeamTalk()
        self.is_voice_transmission_enabled = False
        self.nickname = self.config['nickname']
        self.gender = genders[self.config['gender']]
        self.status = self.default_status
        self.admins = self.config['users']['admins']
        self.banned_users = self.config['users']['banned_users']
        self.load_event_handlers = config["general"]["load_event_handlers"]
        self.event_handlers_file_name = config["general"]["event_handlers_file_name"]
        self.teamtalk_thread = thread.TeamTalkThread(bot, self)
        self.errors_queue = queue.Queue()
        self.message_queue = queue.Queue()
        self.uploaded_files_queue = queue.Queue()

    def initialize(self):
        logging.debug('Initializing TeamTalk')
        self.connect()
        self.change_status_text(self.status)
        logging.debug('TeamTalk initialized')

    def run(self):
        logging.debug('Starting TeamTalk')
        self.teamtalk_thread.start()
        logging.debug('TeamTalk started')

    def close(self):
        logging.debug('Closing teamtalk')
        self.tt.disconnect()
        self.teamtalk_thread.close()
        logging.debug('Teamtalk closed')

    def connect(self, reconnect=False):
        if reconnect:
            logging.info('Reconnecting')
            if self.tt.getFlags() < ClientFlags.CLIENT_CONNECTED | ClientFlags.CLIENT_AUTHORIZED:
                self.tt.disconnect()
        if self.tt.getFlags() < ClientFlags.CLIENT_CONNECTING:
            connection_attempt = 0
            while connection_attempt != self.config['reconnection_attempts']:
                try:
                    self._connect()
                    logging.debug("connected")
                    break
                except errors.ConnectionError:
                    if not reconnect:
                        logging.error("Cannot connect")
                        sys.exit(1)
                    else:
                        time.sleep(self.config['reconnection_timeout'])
                        connection_attempt += 1
                        self.tt.disconnect()
        if self.tt.getFlags() < ClientFlags.CLIENT_CONNECTED:
            logging.error("ConnectionError")
            sys.exit(1)
        if self.tt.getFlags() < ClientFlags.CLIENT_CONNECTED | ClientFlags.CLIENT_AUTHORIZED:
            login_attempt = 0
            while login_attempt != self.config['reconnection_attempts']:
                try:
                    self._login()
                    logging.debug("Logged in")
                    break
                except errors.LoginError as e:
                    if not reconnect:
                        logging.error("Cannot log in: {}".format(e))
                        sys.exit(1)
                    else:
                        time.sleep(self.config['reconnection_timeout'])
                        login_attempt += 1
        if self.tt.getFlags() < ClientFlags.CLIENT_CONNECTED | ClientFlags.CLIENT_AUTHORIZED:
            logging.error("LoginError")
            sys.exit(1)
        if self.tt.getMyChannelID() == 0:
            join_attempt = 0
            while join_attempt != self.config['reconnection_attempts']:
                try:
                    self._join()
                    logging.debug("Joined channel")
                    break
                except errors.JoinChannelError:
                    if not reconnect:
                        logging.error("Cannot joined channel")
                        sys.exit(1)
                    else:
                        time.sleep(self.config['reconnection_timeout'])
                        join_attempt += 1
        if self.tt.getMyChannelID() == 0:
                logging.error("Cannot joined channel")
                sys.exit(1)

    def _connect(self):
        self.tt.connect(_str(self.config['hostname']), self.config['tcp_port'], self.config['udp_port'], self.config['encrypted'])
        try:
            self.wait_for_event(ClientEvent.CLIENTEVENT_CON_SUCCESS, error_events=[ClientEvent.CLIENTEVENT_CON_FAILED])
        except errors.TTEventError as e:
            raise errors.ConnectionError(e)

    def _login(self):
        cmdid = self.tt.doLogin(_str(self.config['nickname']), _str(self.config['username']), _str(self.config['password']), _str(vars.client_name))
        try:
            msg = self.wait_for_event(ClientEvent.CLIENTEVENT_CMD_MYSELF_LOGGEDIN, error_events=[ClientEvent.CLIENTEVENT_CMD_ERROR])
            self._user_account = self.get_user_account_by_tt_obj(msg.useraccount)
        except errors.TTEventError as e:
            raise errors.LoginError(e)
        try:
            self.wait_for_event(ClientEvent.CLIENTEVENT_CMD_SERVER_UPDATE)
        except errors.TTEventError as e:
            raise errors.LoginError(e)
        self.wait_for_cmd_success(cmdid)

    def _join(self):
        if isinstance(self.config['channel'], int):
            channel_id = int(self.config['channel'])
        else:
            channel_id = self.tt.getChannelIDFromPath(_str(self.config['channel']))
            if channel_id == 0:
                channel_id = 1
        cmdid = self.tt.doJoinChannelByID(channel_id, _str(self.config['channel_password']))
        try:
            msg = self.wait_for_cmd_success(cmdid)
        except errors.TTEventError:
            cmdid = self.tt.doJoinChannelByID(0, _str(''))
            try:
                msg = self.wait_for_cmd_success(cmdid)
            except errors.TTEventError:
                raise errors.JoinChannelError()

    def wait_for_event(self, event, error_events=[]):
        get_time = lambda: int(round(time.time()))
        end = get_time() + vars.tt_event_timeout
        msg = self.tt.getMessage(vars.tt_event_timeout * 1000)
        while msg.nClientEvent != event:
            if get_time() >= end:
                raise errors.TTEventError()
            if msg.nClientEvent in error_events:
                raise errors.TTEventError(_str(msg.clienterrormsg.szErrorMsg))
            msg = self.tt.getMessage(vars.tt_event_timeout * 1000)
        return msg

    def wait_for_cmd_success(self, cmdid):
        while True:
            msg = self.wait_for_event(ClientEvent.CLIENTEVENT_CMD_SUCCESS)
            if msg.nSource == cmdid:
                return

    @property
    def default_status(self):
        if self.config['status']:
            return self.config['status']
        else:
            return _('Send "h" for help')

    def send_message(self, text, user=None, type=1):
        for string in split(text):
            message = TeamTalkPy.TextMessage()
            message.nFromUserID = self.tt.getMyUserID()
            message.nMsgType = type
            message.szMessage = _str(string)
            if type == 1:
                if isinstance(user, int):
                    message.nToUserID = user
                else:
                    message.nToUserID = user.id
            elif type == 2:
                message.nChannelID = self.tt.getMyChannelID()
            self.tt.doTextMessage(message)

    def send_file(self, channel, file_path):
        if isinstance(channel, int):
            channel_id = channel
        else:
            channel_id = self.tt.getChannelIDFromPath(_str(channel))
            if channel_id == 0:
                raise ValueError()
        return self.tt.doSendFile(channel_id, _str(file_path))

    def delete_file(self, channel, file_id):
        if isinstance(channel, int):
            channel_id = channel
        else:
            channel_id = self.tt.getChannelIDFromPath(_str(channel))
            if channel_id == 0 or not isinstance(file_id, int) or file_id == 0:
                raise ValueError()
        self.tt.doDeleteFile(channel_id, file_id)

    def join_channel(self, channel, password):
        if isinstance(channel, int):
            channel_id = channel
        else:
            channel_id = self.tt.getChannelIDFromPath(_str(channel))
            if channel_id == 0:
                raise ValueError()
        cmdid = self.tt.doJoinChannelByID(channel_id, _str(password))

    def change_nickname(self, nickname):
        self.nickname = nickname
        self.tt.doChangeNickname(_str(self.nickname))

    def change_status_text(self, text):
        if text:
            self.status = split(text)[0]
        else:
            self.status = self.default_status
        self.tt.doChangeStatus(self.gender, _str(self.status))

    def change_gender(self, gender):
        self.gender = genders[gender]
        self.tt.doChangeStatus(self.gender, _str(self.status))

    def get_channel(self, channel_id):
        channel = self.tt.getChannel(channel_id)
        return Channel(channel.nChannelID, channel.szName, channel.szTopic, channel.nMaxUsers, ChannelType(channel.uChannelType))

    def get_error(self, error_no, cmdid):
        return Error(_str(self.tt.getErrorMessage(error_no)), ErrorType(error_no), cmdid)

    def get_message(self, msg):
        return Message(re.sub(re_line_endings, '', _str(msg.szMessage)), self.get_user(msg.nFromUserID), self.get_channel(msg.nChannelID), MessageType(msg.nMsgType))

    def get_file(self, file):
        return File(file.nFileID, _str(file.szFileName), self.get_channel(file.nChannelID), file.nFileSize, _str(file.szUsername))

    @property
    def user(self):
        user = self.get_user(self.tt.getMyUserID())
        user.user_account = self._user_account
        return user

    @property
    def channel(self):
        return self.get_channel(self.tt.getMyChannelID())

    def get_user(self, id):
        user = self.tt.getUser(id)
        gender = list(genders.keys())[list(genders.values()).index(user.nStatusMode)]
        return User(
            user.nUserID, _str(user.szNickname), _str(user.szUsername),
            _str(user.szStatusMsg), gender, UserState(user.uUserState),
            self.get_channel(user.nChannelID), _str(user.szClientName), user.uVersion,
            self.get_user_account(_str(user.szUsername)), UserType(user.uUserType),
            _str(user.szUsername) in self.admins, _str(user.szUsername) in self.banned_users
        )

    def get_user_account(self, username):
        return UserAccount(username, "", "", "", "", "")

    def get_user_account_by_tt_obj(self, obj):
        return UserAccount(_str(obj.szUsername), _str(obj.szPassword), _str(obj.szNote), UserType(obj.uUserType), UserRight(obj.uUserRights), _str(obj.szInitChannel))

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
        self.is_voice_transmission_enabled = True

    def disable_voice_transmission(self):
        self.tt.enableVoiceTransmission(False)
        self.is_voice_transmission_enabled = False
