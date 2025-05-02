from enum import Enum, Flag

import TeamTalkPy

major, minor, patch, build = TeamTalkPy.ttstr(TeamTalkPy.getVersion()).split(".")


class State(Enum):
    NOT_CONNECTED = 0
    CONNECTING = 1
    RECONNECTING = 2
    CONNECTED = 3


class Flags(Flag):
    CLOSED = TeamTalkPy.ClientFlags.CLIENT_CLOSED
    SND_INPUT_READY = TeamTalkPy.ClientFlags.CLIENT_SNDINPUT_READY
    SND_OUTPUT_READY = TeamTalkPy.ClientFlags.CLIENT_SNDOUTPUT_READY
    SND_INOUTPUT_DUPLEX = TeamTalkPy.ClientFlags.CLIENT_SNDINOUTPUT_DUPLEX
    SND_INPUT_VOICE_ACTIVATED = TeamTalkPy.ClientFlags.CLIENT_SNDINPUT_VOICEACTIVATED
    SND_INPUT_VOICE_ACTIVE = TeamTalkPy.ClientFlags.CLIENT_SNDINPUT_VOICEACTIVE
    SND_OUTPUT_MUTE = TeamTalkPy.ClientFlags.CLIENT_SNDOUTPUT_MUTE
    SND_OUTPUT_AUTO_3D_POSITION = TeamTalkPy.ClientFlags.CLIENT_SNDOUTPUT_AUTO3DPOSITION
    VIDEO_CAPTURE_READY = TeamTalkPy.ClientFlags.CLIENT_VIDEOCAPTURE_READY
    TX_VOICE = TeamTalkPy.ClientFlags.CLIENT_TX_VOICE
    TX_VIDEO_CAPTURE = TeamTalkPy.ClientFlags.CLIENT_TX_VIDEOCAPTURE
    TX_DESKTOP = TeamTalkPy.ClientFlags.CLIENT_TX_DESKTOP
    DESKTOP_ACTIVE = TeamTalkPy.ClientFlags.CLIENT_DESKTOP_ACTIVE
    MUX_AUDIO_FILE = TeamTalkPy.ClientFlags.CLIENT_MUX_AUDIOFILE
    CONNECTING = TeamTalkPy.ClientFlags.CLIENT_CONNECTING
    CONNECTED = TeamTalkPy.ClientFlags.CLIENT_CONNECTED
    CONNECTION = TeamTalkPy.ClientFlags.CLIENT_CONNECTION = (
        TeamTalkPy.ClientFlags.CLIENT_CONNECTING
        or TeamTalkPy.ClientFlags.CLIENT_CONNECTED
    )
    AUTHORIZED = TeamTalkPy.ClientFlags.CLIENT_AUTHORIZED
    STREAM_AUDIO = TeamTalkPy.ClientFlags.CLIENT_STREAM_AUDIO
    STREAM_VIDEO = TeamTalkPy.ClientFlags.CLIENT_STREAM_VIDEO


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
    def __init__(
        self, id: int, name: str, topic: str, max_users: int, type: ChannelType
    ) -> None:
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
    AudioCodecBitrateLimitExceeded = (
        TeamTalkPy.ClientError.CMDERR_AUDIOCODEC_BITRATE_LIMIT_EXCEEDED
    )
    MaxLoginsPerIpAddressExceeded = (
        TeamTalkPy.ClientError.CMDERR_MAX_LOGINS_PER_IPADDRESS_EXCEEDED
    )
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


class UserRightPre15(Flag):
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


if major == "5" and minor >= "15":
    class UserRight15(Flag):
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
        textMessageUser = TeamTalkPy.UserRight.USERRIGHT_TEXTMESSAGE_USER
        textMessageChannel = TeamTalkPy.UserRight.USERRIGHT_TEXTMESSAGE_CHANNEL

    UserRight = UserRight15
else:
    UserRight = UserRightPre15


class UserRight15(Flag):
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
    textMessageUser = TeamTalkPy.UserRight.USERRIGHT_TEXTMESSAGE_USER
    textMessageChannel = TeamTalkPy.UserRight.USERRIGHT_TEXTMESSAGE_CHANNEL


if major == "5" and minor >= "15":
    UserRight = UserRight15
else:
    UserRight = UserRightPre15


class UserAccount:
    def __init__(
        self,
        username: str,
        password: str,
        note: str,
        type: UserType,
        rights: UserRight,
        init_channel: str,
    ) -> None:
        self.username = username
        self.password = password
        self.note = note
        self.type = type
        self.rights = rights
        self.init_channel = init_channel


class User:
    def __init__(
        self,
        id: int,
        nickname: str,
        username: str,
        status: str,
        gender: UserStatusMode,
        state: UserState,
        channel: Channel,
        client_name: str,
        version: int,
        user_account: UserAccount,
        type: UserType,
        is_admin: bool,
        is_banned: bool,
    ) -> None:
        self.id = id
        self.nickname = nickname
        self.username = username
        self.channel = channel
        self.status = status
        self.gender = gender
        self.state = state
        self.client_name = client_name
        self.version = version
        self.user_account = user_account
        self.type = type
        self.is_admin = is_admin
        self.is_banned = is_banned


class MessageType(Enum):
    NONE = 0
    User = TeamTalkPy.TextMsgType.MSGTYPE_USER
    Channel = TeamTalkPy.TextMsgType.MSGTYPE_CHANNEL
    Broadcast = TeamTalkPy.TextMsgType.MSGTYPE_BROADCAST
    Custom = TeamTalkPy.TextMsgType.MSGTYPE_CUSTOM


class Message:
    def __init__(
        self, text: str, user: User, channel: Channel, type: MessageType
    ) -> None:
        self.text = text
        self.channel = channel
        self.user = user
        self.type = type


class File:
    def __init__(
        self, id: int, name: str, channel: Channel, size: int, username: str
    ) -> None:
        self.id = id
        self.name = name
        self.channel = channel
        self.size = size
        self.username = username


class EventType(Enum):
    NONE = TeamTalkPy.ClientEvent.CLIENTEVENT_NONE
    CON_SUCCESS = TeamTalkPy.ClientEvent.CLIENTEVENT_CON_SUCCESS
    CON_FAILED = TeamTalkPy.ClientEvent.CLIENTEVENT_CON_FAILED
    CON_LOST = TeamTalkPy.ClientEvent.CLIENTEVENT_CON_LOST
    CON_MAX_PAYLOAD_UPDATED = TeamTalkPy.ClientEvent.CLIENTEVENT_CON_MAX_PAYLOAD_UPDATED
    PROCESSING = TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_PROCESSING
    ERROR = TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_ERROR
    SUCCESS = TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_SUCCESS
    MYSELF_LOGGEDIN = TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_MYSELF_LOGGEDIN
    MYSELF_LOGGEDOUT = TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_MYSELF_LOGGEDOUT
    MYSELF_KICKED = TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_MYSELF_KICKED
    USER_LOGGEDIN = TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_USER_LOGGEDIN
    USER_LOGGEDOUT = TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_USER_LOGGEDOUT
    USER_UPDATE = TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_USER_UPDATE
    USER_JOINED = TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_USER_JOINED
    USER_LEFT = TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_USER_LEFT
    USER_TEXT_MESSAGE = TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_USER_TEXTMSG
    CHANNEL_NEW = TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_CHANNEL_NEW
    CHANNEL_UPDATE = TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_CHANNEL_UPDATE
    CHANNEL_REMOVE = TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_CHANNEL_REMOVE
    SERVER_UPDATE = TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_SERVER_UPDATE
    SERVER_STATISTICS = TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_SERVERSTATISTICS
    FILE_NEW = TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_FILE_NEW
    FILE_REMOVE = TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_FILE_REMOVE
    USER_ACCOUNT = TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_USERACCOUNT
    BANNED_USER = TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_BANNEDUSER
    USERACCOUNT_NEW = TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_USERACCOUNT_NEW
    USERACCOUNT_REMOVE = TeamTalkPy.ClientEvent.CLIENTEVENT_CMD_USERACCOUNT_REMOVE
    STATE_CHANGE = TeamTalkPy.ClientEvent.CLIENTEVENT_USER_STATECHANGE
    USER_VIDEO_CAPTURE = TeamTalkPy.ClientEvent.CLIENTEVENT_USER_VIDEOCAPTURE
    USER_MEDIAFILE_VIDEO = TeamTalkPy.ClientEvent.CLIENTEVENT_USER_MEDIAFILE_VIDEO
    USER_DESKTOP_WINDOW = TeamTalkPy.ClientEvent.CLIENTEVENT_USER_DESKTOPWINDOW
    USER_DESKTOP_CURSOR = TeamTalkPy.ClientEvent.CLIENTEVENT_USER_DESKTOPCURSOR
    USER_DESKTOP_INPUT = TeamTalkPy.ClientEvent.CLIENTEVENT_USER_DESKTOPINPUT
    USER_RECORD_MEDIAFILE = TeamTalkPy.ClientEvent.CLIENTEVENT_USER_RECORD_MEDIAFILE
    USER_AUDIO_BLOCK = TeamTalkPy.ClientEvent.CLIENTEVENT_USER_AUDIOBLOCK
    INTERNAL_ERROR = TeamTalkPy.ClientEvent.CLIENTEVENT_INTERNAL_ERROR
    VOICE_ACTIVATION = TeamTalkPy.ClientEvent.CLIENTEVENT_VOICE_ACTIVATION
    HOTKEY = TeamTalkPy.ClientEvent.CLIENTEVENT_HOTKEY
    HOTKEY_TEST = TeamTalkPy.ClientEvent.CLIENTEVENT_HOTKEY_TEST
    FILE_TRANSFER = TeamTalkPy.ClientEvent.CLIENTEVENT_FILETRANSFER
    DESKTOP_WINDOW_TRANSFER = TeamTalkPy.ClientEvent.CLIENTEVENT_DESKTOPWINDOW_TRANSFER
    STREAM_MEDIAFILE = TeamTalkPy.ClientEvent.CLIENTEVENT_STREAM_MEDIAFILE
    LOCAL_MEDIAFILE = TeamTalkPy.ClientEvent.CLIENTEVENT_LOCAL_MEDIAFILE
    AUDIO_INPUT = TeamTalkPy.ClientEvent.CLIENTEVENT_AUDIOINPUT
    USER_FIRST_STREAM_VOICE_PACKET = (
        TeamTalkPy.ClientEvent.CLIENTEVENT_USER_FIRSTVOICESTREAMPACKET
    )


class Event:
    def __init__(
        self,
        event_type: EventType,
        source: int,
        channel: Channel,
        error: Error,
        file: File,
        message: Message,
        user: User,
        user_account: UserAccount,
    ):
        self.event_type = event_type
        self.source = source
        # ("ttType", INT32),
        # ("uReserved", UINT32),
        self.channel = channel
        self.error = error
        # desktop_input
        # ("filetransfer", FileTransfer),
        # ("mediafileinfo", MediaFileInfo),
        self.file = file
        # ("serverproperties", ServerProperties),
        # ("serverstatistics", ServerStatistics),
        self.message: Message = message
        self.user = user
        self.user_account = user_account
        # ("banneduser", BannedUser),
        # ("bActive", BOOL),
        # ("nBytesRemain", INT32),
        # ("nStreamID", INT32),
        # ("nPayloadSize", INT32),
        # ("nStreamType", INT32),
        # ("audioinputprogress", AudioInputProgress),
