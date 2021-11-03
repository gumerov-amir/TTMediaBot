from __future__ import annotations
import logging
import os
import time
import re
import sys
from typing import List, TYPE_CHECKING, Optional, Union
from queue import Queue

from bot import errors, app_vars
from bot.sound_devices import SoundDevice, SoundDeviceType


if sys.platform == "win32":
    if sys.version_info.major == 3 and sys.version_info.minor >= 8:
        os.add_dll_directory(app_vars.directory)
    else:
        os.chdir(app_vars.directory)

from bot.TeamTalk.thread import TeamTalkThread
from bot.TeamTalk.structs import *

import TeamTalkPy
from TeamTalkPy import ClientEvent, ClientFlags, TTMessage

re_line_endings = re.compile("[\\r\\n]")

if TYPE_CHECKING:
    from bot import Bot


def _str(data: Union[str, bytes]) -> Union[str, bytes]:
    if isinstance(data, str):
        if os.supports_bytes_environ:
            return bytes(data, "utf-8")
        else:
            return data
    else:
        return str(data, "utf-8")


def split(text: str, max_length: int = app_vars.max_message_length) -> List[str]:
    if len(text) <= max_length:
        lines = [text]
    else:
        lines = [""]
        for line in text.split("\n"):
            if len(line) <= max_length:
                if len(lines[-1]) > 0 and len(lines[-1]) + len(line) + 1 <= max_length:
                    lines[-1] += "\n" + line
                elif len(lines) == 1 and len(lines[0]) == 0:
                    lines[0] = line
                else:
                    lines.append(line)
            else:
                words = [""]
                for word in line.split(" "):
                    if len(word) <= max_length:
                        if (
                            len(words[-1]) > 0
                            and len(words[-1]) + len(word) + 1 <= max_length
                        ):
                            words[-1] += " " + word
                        elif len(words) == 1 and len(words[0]) == 0:
                            words[0] == word
                        else:
                            words.append(word)
                    else:
                        chunk = word
                        for _ in range(0, int(len(chunk) / max_length) + 1):
                            words.append(chunk[0:max_length])
                            chunk = chunk[max_length::]
                lines += words
    return lines


class TeamTalk:
    def __init__(self, bot: Bot) -> None:
        self.config = bot.config.teamtalk
        self.translator = bot.translator
        TeamTalkPy.setLicense(
            _str(self.config.license_name), _str(self.config.license_key)
        )
        self.tt = TeamTalkPy.TeamTalk()
        self.is_voice_transmission_enabled = False
        self.nickname = self.config.nickname
        self.gender = UserStatusMode.__members__[self.config.gender.upper()]
        self.status = self.default_status
        self.errors_queue: Queue[Error] = Queue()
        self.message_queue: Queue[Message] = Queue()
        self.uploaded_files_queue: Queue[File] = Queue()
        self.thread = TeamTalkThread(bot, self)

    def initialize(self) -> None:
        logging.debug("Initializing TeamTalk")
        self.connect()
        self.change_status_text(self.status)
        logging.debug("TeamTalk initialized")

    def run(self) -> None:
        logging.debug("Starting TeamTalk event thread")
        self.thread.start()
        logging.debug("TeamTalk event thread started")

    def close(self) -> None:
        logging.debug("Closing teamtalk")
        self.thread.close()
        self.tt.disconnect()
        self.tt.closeTeamTalk()
        logging.debug("Teamtalk closed")

    def connect(self, reconnect: bool = False) -> None:
        if reconnect:
            logging.info("Reconnecting")
            if (
                self.tt.getFlags()
                < ClientFlags.CLIENT_CONNECTED | ClientFlags.CLIENT_AUTHORIZED
            ):
                self.tt.disconnect()
        if self.tt.getFlags() < ClientFlags.CLIENT_CONNECTING:
            connection_attempt = 0
            while connection_attempt != self.config.reconnection_attempts:
                try:
                    self._connect()
                    logging.debug("connected")
                    break
                except errors.ConnectionError:
                    if not reconnect:
                        error = "Cannot connect"
                        logging.error(error)
                        sys.exit(error)
                    else:
                        time.sleep(self.config.reconnection_timeout)
                        connection_attempt += 1
                        self.tt.disconnect()
        if self.tt.getFlags() < ClientFlags.CLIENT_CONNECTED:
            error = "Connection error"
            logging.error(error)
            sys.exit(error)
        if (
            self.tt.getFlags()
            < ClientFlags.CLIENT_CONNECTED | ClientFlags.CLIENT_AUTHORIZED
        ):
            login_attempt = 0
            while login_attempt != self.config.reconnection_attempts:
                try:
                    self._login()
                    logging.debug("Logged in")
                    break
                except errors.LoginError as e:
                    if not reconnect:
                        error = "Cannot log in: {}".format(e)
                        logging.error(error)
                        sys.exit(error)
                    else:
                        time.sleep(self.config.reconnection_timeout)
                        login_attempt += 1
        if (
            self.tt.getFlags()
            < ClientFlags.CLIENT_CONNECTED | ClientFlags.CLIENT_AUTHORIZED
        ):
            error = "Login error"
            logging.error(error)
            sys.exit(error)
        if self.tt.getMyChannelID() == 0:
            join_attempt = 0
            while join_attempt != self.config.reconnection_attempts:
                try:
                    self._join()
                    logging.debug("Joined channel")
                    break
                except errors.JoinChannelError:
                    if not reconnect:
                        error = "Cannot join channel"
                        logging.error(error)
                        sys.exit(error)
                    else:
                        time.sleep(self.config.reconnection_timeout)
                        join_attempt += 1
        if self.tt.getMyChannelID() == 0:
            error = "Cannot join channel"
            logging.error(error)
            sys.exit(error)

    def _connect(self) -> None:
        self.tt.connect(
            _str(self.config.hostname),
            self.config.tcp_port,
            self.config.udp_port,
            self.config.encrypted,
        )
        try:
            self.wait_for_event(
                ClientEvent.CLIENTEVENT_CON_SUCCESS,
                error_events=[ClientEvent.CLIENTEVENT_CON_FAILED],
            )
        except errors.TTEventError as e:
            raise errors.ConnectionError(e)

    def _login(self) -> None:
        cmdid = self.tt.doLogin(
            _str(self.config.nickname),
            _str(self.config.username),
            _str(self.config.password),
            _str(app_vars.client_name),
        )
        try:
            msg = self.wait_for_event(
                ClientEvent.CLIENTEVENT_CMD_MYSELF_LOGGEDIN,
                error_events=[ClientEvent.CLIENTEVENT_CMD_ERROR],
            )
            self._user_account = self.get_user_account_by_tt_obj(msg.useraccount)
        except errors.TTEventError as e:
            raise errors.LoginError(e)
        try:
            self.wait_for_event(ClientEvent.CLIENTEVENT_CMD_SERVER_UPDATE)
        except errors.TTEventError as e:
            raise errors.LoginError(e)
        self.wait_for_cmd_success(cmdid)

    def _join(self) -> None:
        if isinstance(self.config.channel, int):
            channel_id = int(self.config.channel)
        else:
            channel_id = self.tt.getChannelIDFromPath(_str(self.config.channel))
            if channel_id == 0:
                channel_id = 1
        cmdid = self.tt.doJoinChannelByID(
            channel_id, _str(self.config.channel_password)
        )
        try:
            msg = self.wait_for_cmd_success(cmdid)
        except errors.TTEventError:
            cmdid = self.tt.doJoinChannelByID(0, _str(""))
            try:
                msg = self.wait_for_cmd_success(cmdid)
            except errors.TTEventError:
                raise errors.JoinChannelError()

    def wait_for_event(self, event, error_events=[]):
        get_time = lambda: int(round(time.time()))
        end = get_time() + app_vars.tt_event_timeout
        msg = self.tt.getMessage(app_vars.tt_event_timeout * 1000)
        while msg.nClientEvent != event:
            if get_time() >= end:
                raise errors.TTEventError()
            if msg.nClientEvent in error_events:
                raise errors.TTEventError(_str(msg.clienterrormsg.szErrorMsg))
            msg = self.tt.getMessage(app_vars.tt_event_timeout * 1000)
        return msg

    def wait_for_cmd_success(self, cmdid):
        while True:
            msg = self.wait_for_event(ClientEvent.CLIENTEVENT_CMD_SUCCESS)
            if msg.nSource == cmdid:
                return

    @property
    def default_status(self):
        if self.config.status:
            return self.config.status
        else:
            return self.translator.translate('Send "h" for help')

    def send_message(
        self, text: str, user: Optional[User] = None, type: int = 1
    ) -> None:
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

    def send_file(self, channel: Union[int, str], file_path: str):
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

    def join_channel(self, channel: Union[str, int], password: str) -> None:
        if isinstance(channel, int):
            channel_id = channel
        else:
            channel_id = self.tt.getChannelIDFromPath(_str(channel))
            if channel_id == 0:
                raise ValueError()
        cmdid = self.tt.doJoinChannelByID(channel_id, _str(password))

    def change_nickname(self, nickname: str) -> None:
        self.tt.doChangeNickname(_str(nickname))

    def change_status_text(self, text: str) -> None:
        if text:
            self.status = split(text)[0]
        else:
            self.status = split(self.default_status)[0]
        self.tt.doChangeStatus(self.gender.value, _str(self.status))

    def change_gender(self, gender: str) -> None:
        self.gender = UserStatusMode.__members__[gender.upper()]
        self.tt.doChangeStatus(self.gender.value, _str(self.status))

    def get_channel(self, channel_id: int) -> Channel:
        channel = self.tt.getChannel(channel_id)
        return Channel(
            channel.nChannelID,
            channel.szName,
            channel.szTopic,
            channel.nMaxUsers,
            ChannelType(channel.uChannelType),
        )

    def get_error(self, error_no, cmdid):
        return Error(
            _str(self.tt.getErrorMessage(error_no)), ErrorType(error_no), cmdid
        )

    def get_message(self, msg: TTMessage) -> None:
        return Message(
            re.sub(re_line_endings, "", _str(msg.szMessage)),
            self.get_user(msg.nFromUserID),
            self.get_channel(msg.nChannelID),
            MessageType(msg.nMsgType),
        )

    def get_file(self, file):
        return File(
            file.nFileID,
            _str(file.szFileName),
            self.get_channel(file.nChannelID),
            file.nFileSize,
            _str(file.szUsername),
        )

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
        gender = UserStatusMode(user.nStatusMode)
        return User(
            user.nUserID,
            _str(user.szNickname),
            _str(user.szUsername),
            _str(user.szStatusMsg),
            gender,
            UserState(user.uUserState),
            self.get_channel(user.nChannelID),
            _str(user.szClientName),
            user.uVersion,
            self.get_user_account(_str(user.szUsername)),
            UserType(user.uUserType),
            True
            if _str(user.szUsername) in self.config.users.admins or user.uUserType == 2
            else False,
            _str(user.szUsername) in self.config.users.banned_users,
        )

    def get_user_account(self, username):
        return UserAccount(username, "", "", "", "", "")

    def get_user_account_by_tt_obj(self, obj):
        return UserAccount(
            _str(obj.szUsername),
            _str(obj.szPassword),
            _str(obj.szNote),
            UserType(obj.uUserType),
            UserRight(obj.uUserRights),
            _str(obj.szInitChannel),
        )

    def get_input_devices(self) -> List[SoundDevice]:
        devices = []
        device_list = [i for i in self.tt.getSoundDevices()]
        for device in device_list:
            if sys.platform == "win32":
                if device.nSoundSystem == TeamTalkPy.SoundSystem.SOUNDSYSTEM_WASAPI:
                    devices.append(
                        SoundDevice(
                            _str(device.szDeviceName),
                            device.nDeviceID,
                            SoundDeviceType.Input,
                        )
                    )
            else:
                devices.append(
                    SoundDevice(
                        _str(device.szDeviceName),
                        device.nDeviceID,
                        SoundDeviceType.Input,
                    )
                )
        return devices

    def set_input_device(self, id: str) -> None:
        self.tt.initSoundInputDevice(id)

    def enable_voice_transmission(self) -> None:
        self.tt.enableVoiceTransmission(True)
        self.is_voice_transmission_enabled = True

    def disable_voice_transmission(self) -> None:
        self.tt.enableVoiceTransmission(False)
        self.is_voice_transmission_enabled = False
