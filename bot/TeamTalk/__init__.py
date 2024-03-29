from __future__ import annotations
import logging
import os
import re
import sys
from typing import AnyStr, List, TYPE_CHECKING, Optional, Union
from queue import Queue

from bot import app_vars
from bot.sound_devices import SoundDevice, SoundDeviceType

if sys.platform == "win32":
    if sys.version_info.major == 3 and sys.version_info.minor >= 8:
        os.add_dll_directory(app_vars.directory)
        os.add_dll_directory(os.path.join(app_vars.directory, "TeamTalk_DLL"))
    else:
        os.chdir(app_vars.directory)

from bot.TeamTalk.thread import TeamTalkThread
from bot.TeamTalk.structs import *

import TeamTalkPy


re_line_endings = re.compile("[\\r\\n]")

if TYPE_CHECKING:
    from bot import Bot


def _str(data: AnyStr) -> AnyStr:
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
        self.state = State.NOT_CONNECTED
        self.is_voice_transmission_enabled = False
        self.nickname = self.config.nickname
        self.gender = UserStatusMode.__members__[self.config.gender.upper()]
        self.status = self.default_status
        self.errors_queue: Queue[Error] = Queue()
        self.event_success_queue: Queue[Event] = Queue()
        self.message_queue: Queue[Message] = Queue()
        self.myself_event_queue: Queue[Event] = Queue()
        self.uploaded_files_queue: Queue[File] = Queue()
        self.thread = TeamTalkThread(bot, self)
        self.reconnect = False
        self.reconnect_attempt = 0
        self.user_account: UserAccount

    def initialize(self) -> None:
        logging.debug("Initializing TeamTalk")
        self.thread.start()
        self.connect()
        logging.debug("TeamTalk initialized")

    def close(self) -> None:
        logging.debug("Closing teamtalk")
        self.thread.close()
        self.disconnect()
        self.state = State.NOT_CONNECTED
        self.tt.closeTeamTalk()
        logging.debug("Teamtalk closed")

    def connect(self) -> None:
        self.state = State.CONNECTING
        self.tt.connect(
            _str(self.config.hostname),
            self.config.tcp_port,
            self.config.udp_port,
            0,
            0,
            self.config.encrypted,
        )

    def disconnect(self) -> None:
        self.tt.disconnect()
        self.state = State.NOT_CONNECTED

    def login(self) -> None:
        self.tt.doLogin(
            _str(self.config.nickname),
            _str(self.config.username),
            _str(self.config.password),
            _str(app_vars.client_name),
        )

    def join(self) -> None:
        if isinstance(self.config.channel, int):
            channel_id = int(self.config.channel)
        else:
            channel_id = self.tt.getChannelIDFromPath(_str(self.config.channel))
            if channel_id == 0:
                channel_id = 1
        self.tt.doJoinChannelByID(channel_id, _str(self.config.channel_password))

    @property
    def default_status(self) -> str:
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

    def delete_file(self, channel: Union[int, str], file_id: int) -> int:
        if isinstance(channel, int):
            channel_id = channel
        else:
            channel_id = self.tt.getChannelIDFromPath(_str(channel))
            if channel_id == 0 or file_id == 0:
                raise ValueError()
        return self.tt.doDeleteFile(channel_id, file_id)

    def join_channel(self, channel: Union[str, int], password: str) -> int:
        if isinstance(channel, int):
            channel_id = channel
        else:
            channel_id = self.tt.getChannelIDFromPath(_str(channel))
            if channel_id == 0:
                raise ValueError()
        return self.tt.doJoinChannelByID(channel_id, _str(password))

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
        return self.get_channel_from_obj(channel)

    def get_channel_from_obj(self, obj: TeamTalkPy.Channel) -> Channel:
        try:
            return Channel(
                obj.nChannelID,
                obj.szName,
                obj.szTopic,
                obj.nMaxUsers,
                ChannelType(obj.uChannelType),
            )
        except ValueError:
            return Channel(0, "", "", 0, ChannelType.Default)

    @property
    def flags(self) -> Flags:
        return Flags(self.tt.getFlags())

    def get_error(self, error_no: int, cmdid: int) -> Error:
        try:
            error_type = ErrorType(error_no)
        except ValueError:
            error_type = ErrorType(0)
        return Error(_str(self.tt.getErrorMessage(error_no)), error_type, cmdid)

    def get_message(self, msg: TeamTalkPy.TextMessage) -> Message:
        try:
            return Message(
                re.sub(re_line_endings, "", _str(msg.szMessage)),
                self.get_user(msg.nFromUserID),
                self.get_channel(msg.nChannelID),
                MessageType(msg.nMsgType),
            )
        except ValueError:
            return Message("", self.get_user(1), self.get_channel(1), MessageType.User)

    def get_file(self, file: TeamTalkPy.RemoteFile) -> File:
        return File(
            file.nFileID,
            _str(file.szFileName),
            self.get_channel(file.nChannelID),
            file.nFileSize,
            _str(file.szUsername),
        )

    @property
    def user(self) -> User:
        user = self.get_user(self.tt.getMyUserID())
        user.user_account = self.user_account
        return user

    @property
    def channel(self) -> Channel:
        return self.get_channel(self.tt.getMyChannelID())

    def get_user(self, id: int) -> User:
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

    def get_user_account(self, username: str) -> UserAccount:
        return UserAccount(username, "", "", UserType.Null, UserRight.Null, "/")

    def get_user_account_by_tt_obj(self, obj: TeamTalkPy.UserAccount) -> UserAccount:
        return UserAccount(
            _str(obj.szUsername),
            _str(obj.szPassword),
            _str(obj.szNote),
            UserType(obj.uUserType),
            UserRight(obj.uUserRights),
            _str(obj.szInitChannel),
        )

    def get_event(self, obj: TeamTalkPy.TTMessage) -> Event:
        try:
            channel = self.get_channel_from_obj(obj.channel)
        except (UnicodeDecodeError, ValueError):
            channel = Channel(1, "", "", 0, ChannelType.Default)
        try:
            error = self.get_error(obj.clienterrormsg.nErrorNo, obj.nSource)
        except (UnicodeDecodeError, ValueError):
            error = Error("", ErrorType.Success, 1)
        try:
            file = self.get_file(obj.remotefile)
        except (UnicodeDecodeError, ValueError):
            file = File(1, "", channel, 0, "")
        try:
            user_account = self.get_user_account_by_tt_obj(obj.useraccount)
        except (UnicodeDecodeError, ValueError):
            user_account = UserAccount("", "", "", UserType.Null, UserRight.Null, "")
        try:
            user = self.get_user(obj.user.nUserID)
        except (UnicodeDecodeError, ValueError):
            user = User(
                1,
                "",
                "",
                "",
                UserStatusMode.M,
                UserState.Null,
                channel,
                "",
                1,
                user_account,
                UserType.Null,
                False,
                False,
            )
        try:
            message = self.get_message(obj.textmessage)
        except (UnicodeDecodeError, ValueError):
            message = Message("", user, channel, MessageType.NONE)
        return Event(
            EventType(obj.nClientEvent),
            obj.nSource,
            channel,
            error,
            file,
            message,
            user,
            user_account,
        )

    def get_input_devices(self) -> List[SoundDevice]:
        devices: List[SoundDevice] = []
        device_list = [i for i in self.tt.getSoundDevices()]
        for device in device_list:
            if sys.platform == "win32":
                if (
                    device.nSoundSystem == TeamTalkPy.SoundSystem.SOUNDSYSTEM_WASAPI
                    and device.nMaxOutputChannels == 0
                ):
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

    def set_input_device(self, id: int) -> None:
        self.tt.initSoundInputDevice(id)

    def enable_voice_transmission(self) -> None:
        self.tt.enableVoiceTransmission(True)
        self.is_voice_transmission_enabled = True

    def disable_voice_transmission(self) -> None:
        self.tt.enableVoiceTransmission(False)
        self.is_voice_transmission_enabled = False
