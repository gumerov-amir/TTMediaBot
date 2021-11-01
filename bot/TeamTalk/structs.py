from enum import Enum, Flag

import TeamTalkPy


class ChannelType(Flag):
    ClassRoom = TeamTalkPy.ChannelType.CHANNEL_CLASSROOM
    Default = TeamTalkPy.ChannelType.CHANNEL_DEFAULT
    Hidden = TeamTalkPy.ChannelType.CHANNEL_HIDDEN
    NoRecording = TeamTalkPy.ChannelType.CHANNEL_NO_RECORDING
    NoVoiceActivation = TeamTalkPy.ChannelType.CHANNEL_NO_VOICEACTIVATION
    OperatorRecnvOnly = TeamTalkPy.ChannelType.CHANNEL_OPERATOR_RECVONLY
    Permanent = TeamTalkPy.ChannelType.CHANNEL_PERMANENT
    SoloTransmit = TeamTalkPy.ChannelType.CHANNEL_SOLO_TRANSMIT


class Channel:
    def __init__(self, id: int, name: str, topic: str, max_users: int, type: ChannelType) -> None:
        self.id = id
        self.name = name
        self.topic = topic
        self.max_users = max_users
        self.type = type

class ErrorType(Enum):
    Success = TeamTalkPy.ClientError.CMDERR_SUCCESS
    SyntaxError = TeamTalkPy.ClientError.CMDERR_SYNTAX_ERROR
    UnknownCommand = TeamTalkPy.ClientError.CMDERR_UNKNOWN_COMMAND
    MissingParameter = TeamTalkPy.ClientError.CMDERR_MISSING_PARAMETER
    IncompatibleProtocols = TeamTalkPy.ClientError.CMDERR_INCOMPATIBLE_PROTOCOLS
    UnknownAudioCodec = TeamTalkPy.ClientError.CMDERR_UNKNOWN_AUDIOCODEC
    InvalidUsername = TeamTalkPy.ClientError.CMDERR_INVALID_USERNAME
    IncorrectChannelPassword = TeamTalkPy.ClientError.CMDERR_INCORRECT_CHANNEL_PASSWORD
    InvalidAccount = TeamTalkPy.ClientError.CMDERR_INVALID_ACCOUNT
    MaxServerUsersExceeded = TeamTalkPy.ClientError.CMDERR_MAX_SERVER_USERS_EXCEEDED
    MaxChannelUsersExceeded = TeamTalkPy.ClientError.CMDERR_MAX_CHANNEL_USERS_EXCEEDED
    ServerBanned = TeamTalkPy.ClientError.CMDERR_SERVER_BANNED
    NotAuthorised = TeamTalkPy.ClientError.CMDERR_NOT_AUTHORIZED
    MaxDiskusageExceeded = TeamTalkPy.ClientError.CMDERR_MAX_DISKUSAGE_EXCEEDED
    IncorrectOperatorPassword = TeamTalkPy.ClientError.CMDERR_INCORRECT_OP_PASSWORD
    AudioCodecBitrateLimitExceeded = TeamTalkPy.ClientError.CMDERR_AUDIOCODEC_BITRATE_LIMIT_EXCEEDED
    MaxLoginsPerIpAddressExceeded = TeamTalkPy.ClientError.CMDERR_MAX_LOGINS_PER_IPADDRESS_EXCEEDED
    MaxChannelsExceeded = TeamTalkPy.ClientError.CMDERR_MAX_CHANNELS_EXCEEDED
    CommandFlood = TeamTalkPy.ClientError.CMDERR_COMMAND_FLOOD
    ChannelBanned = TeamTalkPy.ClientError.CMDERR_CHANNEL_BANNED
    NotLoggedin = TeamTalkPy.ClientError.CMDERR_NOT_LOGGEDIN
    AlreadyLoggedin = TeamTalkPy.ClientError.CMDERR_ALREADY_LOGGEDIN
    NotInChannel = TeamTalkPy.ClientError.CMDERR_NOT_IN_CHANNEL
    AlreadyInChannel = TeamTalkPy.ClientError.CMDERR_ALREADY_IN_CHANNEL
    ChannelAlreadyExists = TeamTalkPy.ClientError.CMDERR_CHANNEL_ALREADY_EXISTS
    ChannelNotFound = TeamTalkPy.ClientError.CMDERR_CHANNEL_NOT_FOUND
    UserNotFound = TeamTalkPy.ClientError.CMDERR_USER_NOT_FOUND
    BanNotFound = TeamTalkPy.ClientError.CMDERR_BAN_NOT_FOUND
    FileTransferNotFound = TeamTalkPy.ClientError.CMDERR_FILETRANSFER_NOT_FOUND
    OpenFileFailed = TeamTalkPy.ClientError.CMDERR_OPENFILE_FAILED
    AccountNotFound = TeamTalkPy.ClientError.CMDERR_ACCOUNT_NOT_FOUND
    FileNotFound = TeamTalkPy.ClientError.CMDERR_FILE_NOT_FOUND
    FileAlreadyExists = TeamTalkPy.ClientError.CMDERR_FILE_ALREADY_EXISTS
    FileSharingDisabled = TeamTalkPy.ClientError.CMDERR_FILESHARING_DISABLED
    ChannelHasUsers = TeamTalkPy.ClientError.CMDERR_CHANNEL_HAS_USERS
    LoginServiceUnavailable = TeamTalkPy.ClientError.CMDERR_LOGINSERVICE_UNAVAILABLE
    ChannelCannotBeHidden = TeamTalkPy.ClientError.CMDERR_CHANNEL_CANNOT_BE_HIDDEN
    SndInputFailure = TeamTalkPy.ClientError.INTERR_SNDINPUT_FAILURE
    SndOutputFailure = TeamTalkPy.ClientError.INTERR_SNDOUTPUT_FAILURE
    AudioCodecInitFailed = TeamTalkPy.ClientError.INTERR_AUDIOCODEC_INIT_FAILED
    SpeexDSPInitFailed = TeamTalkPy.ClientError.INTERR_SPEEXDSP_INIT_FAILED
    TTMesageQueueOverflow = TeamTalkPy.ClientError.INTERR_TTMESSAGE_QUEUE_OVERFLOW
    SndEffectFailure = TeamTalkPy.ClientError.INTERR_SNDEFFECT_FAILURE


class Error:
    def __init__(self, message: str, type: ErrorType, command_id: int) -> None:
        self.message = message
        self.type = type
        self.command_id = command_id

class UserType(Enum):
    Null = 0
    Default = 1
    Admin = 2


class UserState(Flag):
    Null = TeamTalkPy.UserState.USERSTATE_NONE
    Voice = TeamTalkPy.UserState.USERSTATE_VOICE
    MuteVoice = TeamTalkPy.UserState.USERSTATE_MUTE_VOICE
    MuteMediaFile = TeamTalkPy.UserState.USERSTATE_MUTE_MEDIAFILE
    Desktop = TeamTalkPy.UserState.USERSTATE_DESKTOP
    VideoCapture = TeamTalkPy.UserState.USERSTATE_VIDEOCAPTURE
    AudioFile = TeamTalkPy.UserState.USERSTATE_MEDIAFILE_AUDIO
    VideoFile = TeamTalkPy.UserState.USERSTATE_MEDIAFILE_VIDEO
    MediaFile = TeamTalkPy.UserState.USERSTATE_MEDIAFILE


class UserStatusMode(Flag):
    Available = 0
    Away = 1
    Question = 2
    VideoTx = 512
    Desktop = 1024
    StreamMediaFile = 2048
    M = Available
    F = 256
    N = 4096


class UserRight(Flag):
    Null = TeamTalkPy.UserRight.USERRIGHT_NONE
    MultiLogin = TeamTalkPy.UserRight.USERRIGHT_MULTI_LOGIN
    ViewAllUsers = TeamTalkPy.UserRight.USERRIGHT_VIEW_ALL_USERS
    CreateTemporaryChannel = TeamTalkPy.UserRight.USERRIGHT_CREATE_TEMPORARY_CHANNEL
    ModifyChannels = TeamTalkPy.UserRight.USERRIGHT_MODIFY_CHANNELS
    BroadcastTextMessage = TeamTalkPy.UserRight.USERRIGHT_TEXTMESSAGE_BROADCAST
    KickUsers = TeamTalkPy.UserRight.USERRIGHT_KICK_USERS
    BanUsers = TeamTalkPy.UserRight.USERRIGHT_BAN_USERS
    MoveUsers = TeamTalkPy.UserRight.USERRIGHT_MOVE_USERS
    OperatorEnable = TeamTalkPy.UserRight.USERRIGHT_OPERATOR_ENABLE
    UploadFiles = TeamTalkPy.UserRight.USERRIGHT_UPLOAD_FILES
    DownloadFiles = TeamTalkPy.UserRight.USERRIGHT_DOWNLOAD_FILES
    UpdateServerProperties = TeamTalkPy.UserRight.USERRIGHT_UPDATE_SERVERPROPERTIES
    TransmitVoice = TeamTalkPy.UserRight.USERRIGHT_TRANSMIT_VOICE
    TransmitVideoCapture = TeamTalkPy.UserRight.USERRIGHT_TRANSMIT_VIDEOCAPTURE
    TransmitDesktop = TeamTalkPy.UserRight.USERRIGHT_TRANSMIT_DESKTOP
    TransmitDesktopInput = TeamTalkPy.UserRight.USERRIGHT_TRANSMIT_DESKTOPINPUT
    TransmitMediaFileAudio = TeamTalkPy.UserRight.USERRIGHT_TRANSMIT_MEDIAFILE_AUDIO
    TransmitMediaFileVideo = TeamTalkPy.UserRight.USERRIGHT_TRANSMIT_MEDIAFILE_VIDEO
    TransmitMediaFile = TeamTalkPy.UserRight.USERRIGHT_TRANSMIT_MEDIAFILE
    LockedNickname = TeamTalkPy.UserRight.USERRIGHT_LOCKED_NICKNAME
    LockedStatus = TeamTalkPy.UserRight.USERRIGHT_LOCKED_STATUS
    RecordVoice = TeamTalkPy.UserRight.USERRIGHT_RECORD_VOICE
    ViewHiddenChannels = TeamTalkPy.UserRight.USERRIGHT_VIEW_HIDDEN_CHANNELS


class UserAccount:
    def __init__(self, username: str, password: str, note: str, type: UserType, rights: UserRight, init_channel: int) -> None:
        self.username = username
        self.password = password
        self.note = note
        self.type = type
        self.rights = rights
        self.init_channel = init_channel


class User:
    def __init__(self, id: int, nickname: str, username: str, status: str, gender: str, state: UserState, channel: Channel, client_name: str, version: str, account: str, type: UserType, is_admin: bool, is_banned: bool) -> None:
        self.id = id
        self.nickname = nickname
        self.username = username
        self.channel = channel
        self.status = status
        self.gender = gender
        self.state= state
        self.client_name = client_name
        self.version = version
        self.account = account
        self.type = type
        self.is_admin = is_admin
        self.is_banned = is_banned


class MessageType(Enum):
    User = TeamTalkPy.TextMsgType.MSGTYPE_USER
    Channel = TeamTalkPy.TextMsgType.MSGTYPE_CHANNEL
    Broadcast = TeamTalkPy.TextMsgType.MSGTYPE_BROADCAST
    Custom = TeamTalkPy.TextMsgType.MSGTYPE_CUSTOM


class Message:
    def __init__(self, text: str, user: User, channel: Channel, type: MessageType) -> None:
        self.text = text
        self.channel = channel
        self.user = user
        self.type = type


class File:
    def __init__(self, id: int, name: str, channel: Channel, size: int, username: str) -> None:
        self.id = id
        self.name = name
        self.channel = channel
        self.size = size
        self.username = username
