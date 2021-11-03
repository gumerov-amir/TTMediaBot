from ctypes import *
from ctypes.util import find_library as find_library
from enum import IntEnum as IntEnum
from time import sleep as sleep
from typing import Any, Tuple, Union

dll: Any
TTCHAR = c_wchar
TTCHAR_P = c_wchar_p
INT32 = c_int
INT64 = c_longlong
UINT32 = c_uint
FLOAT = c_float
TT_STRLEN: int
TT_VIDEOFORMATS_MAX: int
TT_TRANSMITUSERS_MAX: int
TT_CHANNELS_OPERATOR_MAX: int
TT_TRANSMITQUEUE_MAX: int
TT_SAMPLERATES_MAX: int

class SoundSystem(INT32):
    SOUNDSYSTEM_NONE: int
    SOUNDSYSTEM_WINMM: int
    SOUNDSYSTEM_DSOUND: int
    SOUNDSYSTEM_ALSA: int
    SOUNDSYSTEM_COREAUDIO: int
    SOUNDSYSTEM_WASAPI: int
    SOUNDSYSTEM_OPENSLES_ANDROID: int
    SOUNDSYSTEM_AUDIOUNIT: int

class SoundDeviceFeature(UINT32):
    SOUNDDEVICEFEATURE_NONE: int
    SOUNDDEVICEFEATURE_AEC: int
    SOUNDDEVICEFEATURE_AGC: int
    SOUNDDEVICEFEATURE_DENOISE: int
    SOUNDDEVICEFEATURE_3DPOSITION: int
    SOUNDDEVICEFEATURE_DUPLEXMODE: int
    SOUNDDEVICEFEATURE_DEFAULTCOMDEVICE: int

class SoundDevice(Structure):
    def __init__(self) -> None: ...

class SoundDeviceEffects(Structure):
    def __init__(self) -> None: ...

class SoundLevel(INT32):
    SOUND_VU_MAX: int
    SOUND_VU_MIN: int
    SOUND_VOLUME_MAX: int
    SOUND_VOLUME_DEFAULT: int
    SOUND_VOLUME_MIN: int
    SOUND_GAIN_MAX: int
    SOUND_GAIN_DEFAULT: int
    SOUND_GAIN_MIN: int

class AudioBlock(Structure):
    def __init__(self) -> None: ...

class MediaFileStatus(INT32):
    MFS_CLOSED: int
    MFS_ERROR: int
    MFS_STARTED: int
    MFS_FINISHED: int
    MFS_ABORTED: int
    MFS_PAUSED: int
    MFS_PLAYING: int

class AudioFileFormat(INT32):
    AFF_NONE: int
    AFF_CHANNELCODEC_FORMAT: int
    AFF_WAVE_FORMAT: int
    AFF_MP3_16KBIT_FORMAT: int
    AFF_MP3_32KBIT_FORMAT: int
    AFF_MP3_64KBIT_FORMAT: int
    AFF_MP3_128KBIT_FORMAT: int
    AFF_MP3_256KBIT_FORMAT: int

class AudioFormat(Structure):
    def __init__(self) -> None: ...

class FourCC(INT32):
    FOURCC_NONE: int
    FOURCC_I420: int
    FOURCC_YUY2: int
    FOURCC_RGB32: int

class VideoFormat(Structure):
    def __init__(self) -> None: ...

class VideoFrame(Structure):
    def __init__(self) -> None: ...

class VideoCaptureDevice(Structure):
    def __init__(self) -> None: ...

class BitmapFormat(INT32):
    BMP_NONE: int
    BMP_RGB8_PALETTE: int
    BMP_RGB16_555: int
    BMP_RGB24: int
    BMP_RGB32: int

class DesktopProtocol(INT32):
    DESKTOPPROTOCOL_ZLIB_1: int

class DesktopWindow(Structure):
    def __init__(self) -> None: ...

class DesktopKeyState(UINT32):
    DESKTOPKEYSTATE_NONE: int
    DESKTOPKEYSTATE_DOWN: int
    DESKTOPKEYSTATE_UP: int

class DesktopInput(Structure):
    def __init__(self) -> None: ...

class SpeexCodec(Structure):
    def __init__(self) -> None: ...

class SpeexVBRCodec(Structure):
    def __init__(self) -> None: ...

SPEEX_NB_MIN_BITRATE: int
SPEEX_NB_MAX_BITRATE: int
SPEEX_WB_MIN_BITRATE: int
SPEEX_WB_MAX_BITRATE: int
SPEEX_UWB_MIN_BITRATE: int
SPEEX_UWB_MAX_BITRATE: int

class OpusCodec(Structure):
    def __init__(self) -> None: ...

OPUS_APPLICATION_VOIP: int
OPUS_APPLICATION_AUDIO: int
OPUS_MIN_BITRATE: int
OPUS_MAX_BITRATE: int
OPUS_MIN_FRAMESIZE: int
OPUS_MAX_FRAMESIZE: int
OPUS_REALMAX_FRAMESIZE: int

class SpeexDSP(Structure):
    def __init__(self) -> None: ...

class WebRTCAudioPreprocessor(Structure):
    def __init__(self) -> None: ...

class TTAudioPreprocessor(Structure):
    def __init__(self) -> None: ...

class AudioPreprocessorType(INT32):
    NO_AUDIOPREPROCESSOR: int
    SPEEXDSP_AUDIOPREPROCESSOR: int
    TEAMTALK_AUDIOPREPROCESSOR: int
    WEBRTC_AUDIOPREPROCESSOR: int

class AudioPreprocessorUnion(Union): ...

class AudioPreprocessor(Structure):
    def __init__(self) -> None: ...

class WebMVP8CodecUnion(Union): ...

class WebMVP8Codec(Structure):
    def __init__(self) -> None: ...

WEBM_VPX_DL_REALTIME: int
WEBM_VPX_DL_GOOD_QUALITY: int
WEBM_VPX_DL_BEST_QUALITY: int

class Codec(INT32):
    NO_CODEC: int
    SPEEX_CODEC: int
    SPEEX_VBR_CODEC: int
    OPUS_CODEC: int
    WEBM_VP8_CODEC: int

class AudioCodecUnion(Union): ...

class AudioCodec(Structure):
    def __init__(self) -> None: ...

class AudioConfig(Structure):
    def __init__(self) -> None: ...

class VideoCodecUnion(Union): ...

class VideoCodec(Structure):
    def __init__(self) -> None: ...

class MediaFileInfo(Structure):
    def __init__(self) -> None: ...

class MediaFilePlayback(Structure):
    def __init__(self) -> None: ...

class AudioInputProgress(Structure):
    def __init__(self) -> None: ...

class StreamType(UINT32):
    STREAMTYPE_NONE: int
    STREAMTYPE_VOICE: int
    STREAMTYPE_VIDEOCAPTURE: int
    STREAMTYPE_MEDIAFILE_AUDIO: int
    STREAMTYPE_MEDIAFILE_VIDEO: int
    STREAMTYPE_DESKTOP: int
    STREAMTYPE_DESKTOPINPUT: int
    STREAMTYPE_MEDIAFILE: Any
    STREAMTYPE_CHANNELMSG: int
    STREAMTYPE_CLASSROOM_ALL: Any

class UserRight(UINT32):
    USERRIGHT_NONE: int
    USERRIGHT_MULTI_LOGIN: int
    USERRIGHT_VIEW_ALL_USERS: int
    USERRIGHT_CREATE_TEMPORARY_CHANNEL: int
    USERRIGHT_MODIFY_CHANNELS: int
    USERRIGHT_TEXTMESSAGE_BROADCAST: int
    USERRIGHT_KICK_USERS: int
    USERRIGHT_BAN_USERS: int
    USERRIGHT_MOVE_USERS: int
    USERRIGHT_OPERATOR_ENABLE: int
    USERRIGHT_UPLOAD_FILES: int
    USERRIGHT_DOWNLOAD_FILES: int
    USERRIGHT_UPDATE_SERVERPROPERTIES: int
    USERRIGHT_TRANSMIT_VOICE: int
    USERRIGHT_TRANSMIT_VIDEOCAPTURE: int
    USERRIGHT_TRANSMIT_DESKTOP: int
    USERRIGHT_TRANSMIT_DESKTOPINPUT: int
    USERRIGHT_TRANSMIT_MEDIAFILE_AUDIO: int
    USERRIGHT_TRANSMIT_MEDIAFILE_VIDEO: int
    USERRIGHT_TRANSMIT_MEDIAFILE: Any
    USERRIGHT_LOCKED_NICKNAME: int
    USERRIGHT_LOCKED_STATUS: int
    USERRIGHT_RECORD_VOICE: int
    USERRIGHT_VIEW_HIDDEN_CHANNELS: int

class ServerProperties(Structure):
    def __init__(self) -> None: ...

class ServerStatistics(Structure):
    def __init__(self) -> None: ...

class BanType(UINT32):
    BANTYPE_NONE: int
    BANTYPE_CHANNEL: int
    BANTYPE_IPADDR: int
    BANTYPE_USERNAME: int

class BannedUser(Structure):
    def __init__(self) -> None: ...

class UserType(UINT32):
    USERTYPE_NONE: int
    USERTYPE_DEFAULT: int
    USERTYPE_ADMIN: int

class AbusePrevention(Structure):
    def __init__(self) -> None: ...

class UserAccount(Structure):
    def __init__(self) -> None: ...

class Subscription(UINT32):
    SUBSCRIBE_NONE: int
    SUBSCRIBE_USER_MSG: int
    SUBSCRIBE_CHANNEL_MSG: int
    SUBSCRIBE_BROADCAST_MSG: int
    SUBSCRIBE_CUSTOM_MSG: int
    SUBSCRIBE_VOICE: int
    SUBSCRIBE_VIDEOCAPTURE: int
    SUBSCRIBE_DESKTOP: int
    SUBSCRIBE_DESKTOPINPUT: int
    SUBSCRIBE_MEDIAFILE: int
    SUBSCRIBE_INTERCEPT_USER_MSG: int
    SUBSCRIBE_INTERCEPT_CHANNEL_MSG: int
    SUBSCRIBE_INTERCEPT_CUSTOM_MSG: int
    SUBSCRIBE_INTERCEPT_VOICE: int
    SUBSCRIBE_INTERCEPT_VIDEOCAPTURE: int
    SUBSCRIBE_INTERCEPT_DESKTOP: int
    SUBSCRIBE_INTERCEPT_MEDIAFILE: int

class UserState(UINT32):
    USERSTATE_NONE: int
    USERSTATE_VOICE: int
    USERSTATE_MUTE_VOICE: int
    USERSTATE_MUTE_MEDIAFILE: int
    USERSTATE_DESKTOP: int
    USERSTATE_VIDEOCAPTURE: int
    USERSTATE_MEDIAFILE_AUDIO: int
    USERSTATE_MEDIAFILE_VIDEO: int
    USERSTATE_MEDIAFILE: Any

class User(Structure):
    def __init__(self) -> None: ...

class UserStatistics(Structure):
    def __init__(self) -> None: ...

class TextMsgType(INT32):
    MSGTYPE_USER: int
    MSGTYPE_CHANNEL: int
    MSGTYPE_BROADCAST: int
    MSGTYPE_CUSTOM: int

class TextMessage(Structure):
    def __init__(self) -> None: ...

class ChannelType(UINT32):
    CHANNEL_DEFAULT: int
    CHANNEL_PERMANENT: int
    CHANNEL_SOLO_TRANSMIT: int
    CHANNEL_CLASSROOM: int
    CHANNEL_OPERATOR_RECVONLY: int
    CHANNEL_NO_VOICEACTIVATION: int
    CHANNEL_NO_RECORDING: int
    CHANNEL_HIDDEN: int

class Channel(Structure):
    def __init__(self) -> None: ...

class FileTransferStatus(INT32):
    FILETRANSFER_CLOSED: int
    FILETRANSFER_ERROR: int
    FILETRANSFER_ACTIVE: int
    FILETRANSFER_FINISHED: int

class FileTransfer(Structure):
    def __init__(self) -> None: ...

class RemoteFile(Structure):
    def __init__(self) -> None: ...

class EncryptionContext(Structure): ...

class ClientKeepAlive(Structure):
    def __init__(self) -> None: ...

class ClientStatistics(Structure):
    def __init__(self) -> None: ...

class JitterConfig(Structure):
    def __init__(self) -> None: ...

class ClientError(INT32):
    CMDERR_SUCCESS: int
    CMDERR_SYNTAX_ERROR: int
    CMDERR_UNKNOWN_COMMAND: int
    CMDERR_MISSING_PARAMETER: int
    CMDERR_INCOMPATIBLE_PROTOCOLS: int
    CMDERR_UNKNOWN_AUDIOCODEC: int
    CMDERR_INVALID_USERNAME: int
    CMDERR_INCORRECT_CHANNEL_PASSWORD: int
    CMDERR_INVALID_ACCOUNT: int
    CMDERR_MAX_SERVER_USERS_EXCEEDED: int
    CMDERR_MAX_CHANNEL_USERS_EXCEEDED: int
    CMDERR_SERVER_BANNED: int
    CMDERR_NOT_AUTHORIZED: int
    CMDERR_MAX_DISKUSAGE_EXCEEDED: int
    CMDERR_INCORRECT_OP_PASSWORD: int
    CMDERR_AUDIOCODEC_BITRATE_LIMIT_EXCEEDED: int
    CMDERR_MAX_LOGINS_PER_IPADDRESS_EXCEEDED: int
    CMDERR_MAX_CHANNELS_EXCEEDED: int
    CMDERR_COMMAND_FLOOD: int
    CMDERR_CHANNEL_BANNED: int
    CMDERR_NOT_LOGGEDIN: int
    CMDERR_ALREADY_LOGGEDIN: int
    CMDERR_NOT_IN_CHANNEL: int
    CMDERR_ALREADY_IN_CHANNEL: int
    CMDERR_CHANNEL_ALREADY_EXISTS: int
    CMDERR_CHANNEL_NOT_FOUND: int
    CMDERR_USER_NOT_FOUND: int
    CMDERR_BAN_NOT_FOUND: int
    CMDERR_FILETRANSFER_NOT_FOUND: int
    CMDERR_OPENFILE_FAILED: int
    CMDERR_ACCOUNT_NOT_FOUND: int
    CMDERR_FILE_NOT_FOUND: int
    CMDERR_FILE_ALREADY_EXISTS: int
    CMDERR_FILESHARING_DISABLED: int
    CMDERR_CHANNEL_HAS_USERS: int
    CMDERR_LOGINSERVICE_UNAVAILABLE: int
    CMDERR_CHANNEL_CANNOT_BE_HIDDEN: int
    INTERR_SNDINPUT_FAILURE: int
    INTERR_SNDOUTPUT_FAILURE: int
    INTERR_AUDIOCODEC_INIT_FAILED: int
    INTERR_SPEEXDSP_INIT_FAILED: int
    INTERR_TTMESSAGE_QUEUE_OVERFLOW: int
    INTERR_SNDEFFECT_FAILURE: int

class ClientErrorMsg(Structure):
    def __init__(self) -> None: ...

class ClientEvent(UINT32):
    CLIENTEVENT_NONE: int
    CLIENTEVENT_CON_SUCCESS: Any
    CLIENTEVENT_CON_FAILED: Any
    CLIENTEVENT_CON_LOST: Any
    CLIENTEVENT_CON_MAX_PAYLOAD_UPDATED: Any
    CLIENTEVENT_CMD_PROCESSING: Any
    CLIENTEVENT_CMD_ERROR: Any
    CLIENTEVENT_CMD_SUCCESS: Any
    CLIENTEVENT_CMD_MYSELF_LOGGEDIN: Any
    CLIENTEVENT_CMD_MYSELF_LOGGEDOUT: Any
    CLIENTEVENT_CMD_MYSELF_KICKED: Any
    CLIENTEVENT_CMD_USER_LOGGEDIN: Any
    CLIENTEVENT_CMD_USER_LOGGEDOUT: Any
    CLIENTEVENT_CMD_USER_UPDATE: Any
    CLIENTEVENT_CMD_USER_JOINED: Any
    CLIENTEVENT_CMD_USER_LEFT: Any
    CLIENTEVENT_CMD_USER_TEXTMSG: Any
    CLIENTEVENT_CMD_CHANNEL_NEW: Any
    CLIENTEVENT_CMD_CHANNEL_UPDATE: Any
    CLIENTEVENT_CMD_CHANNEL_REMOVE: Any
    CLIENTEVENT_CMD_SERVER_UPDATE: Any
    CLIENTEVENT_CMD_SERVERSTATISTICS: Any
    CLIENTEVENT_CMD_FILE_NEW: Any
    CLIENTEVENT_CMD_FILE_REMOVE: Any
    CLIENTEVENT_CMD_USERACCOUNT: Any
    CLIENTEVENT_CMD_BANNEDUSER: Any
    CLIENTEVENT_USER_STATECHANGE: Any
    CLIENTEVENT_USER_VIDEOCAPTURE: Any
    CLIENTEVENT_USER_MEDIAFILE_VIDEO: Any
    CLIENTEVENT_USER_DESKTOPWINDOW: Any
    CLIENTEVENT_USER_DESKTOPCURSOR: Any
    CLIENTEVENT_USER_DESKTOPINPUT: Any
    CLIENTEVENT_USER_RECORD_MEDIAFILE: Any
    CLIENTEVENT_USER_AUDIOBLOCK: Any
    CLIENTEVENT_INTERNAL_ERROR: Any
    CLIENTEVENT_VOICE_ACTIVATION: Any
    CLIENTEVENT_HOTKEY: Any
    CLIENTEVENT_HOTKEY_TEST: Any
    CLIENTEVENT_FILETRANSFER: Any
    CLIENTEVENT_DESKTOPWINDOW_TRANSFER: Any
    CLIENTEVENT_STREAM_MEDIAFILE: Any
    CLIENTEVENT_LOCAL_MEDIAFILE: Any
    CLIENTEVENT_AUDIOINPUT: Any
    CLIENTEVENT_USER_FIRSTVOICESTREAMPACKET: Any

class TTType(INT32):
    NONE: int
    AUDIOCODEC: int
    BANNEDUSER: int
    VIDEOFORMAT: int
    OPUSCODEC: int
    CHANNEL: int
    CLIENTSTATISTICS: int
    REMOTEFILE: int
    FILETRANSFER: int
    MEDIAFILESTATUS: int
    SERVERPROPERTIES: int
    SERVERSTATISTICS: int
    SOUNDDEVICE: int
    SPEEXCODEC: int
    TEXTMESSAGE: int
    WEBMVP8CODEC: int
    TTMESSAGE: int
    USER: int
    USERACCOUNT: int
    USERSTATISTICS: int
    VIDEOCAPTUREDEVICE: int
    VIDEOCODEC: int
    AUDIOCONFIG: int
    SPEEXVBRCODEC: int
    VIDEOFRAME: int
    AUDIOBLOCK: int
    AUDIOFORMAT: int
    MEDIAFILEINFO: int
    CLIENTERRORMSG: int
    TTBOOL: int
    INT32: int
    DESKTOPINPUT: int
    SPEEXDSP: int
    STREAMTYPE: int
    AUDIOPREPROCESSORTYPE: int
    AUDIOPREPROCESSOR: int
    TTAUDIOPREPROCESSOR: int
    MEDIAFILEPLAYBACK: int
    CLIENTKEEPALIVE: int
    UINT32: int
    AUDIOINPUTPROGRESS: int
    JITTERCONFIG: int
    WEBRTCAUDIOPREPROCESSOR: int
    ENCRYPTIONCONTEXT: int

class TTMessageUnion(Union): ...

class TTMessage(Structure):
    def __init__(self) -> None: ...

class ClientFlags(UINT32):
    CLIENT_CLOSED: int
    CLIENT_SNDINPUT_READY: int
    CLIENT_SNDOUTPUT_READY: int
    CLIENT_SNDINOUTPUT_DUPLEX: int
    CLIENT_SNDINPUT_VOICEACTIVATED: int
    CLIENT_SNDINPUT_VOICEACTIVE: int
    CLIENT_SNDOUTPUT_MUTE: int
    CLIENT_SNDOUTPUT_AUTO3DPOSITION: int
    CLIENT_VIDEOCAPTURE_READY: int
    CLIENT_TX_VOICE: int
    CLIENT_TX_VIDEOCAPTURE: int
    CLIENT_TX_DESKTOP: int
    CLIENT_DESKTOP_ACTIVE: int
    CLIENT_MUX_AUDIOFILE: int
    CLIENT_CONNECTING: int
    CLIENT_CONNECTED: int
    CLIENT_CONNECTION: Any
    CLIENT_AUTHORIZED: int
    CLIENT_STREAM_AUDIO: int
    CLIENT_STREAM_VIDEO: int

def getVersion(): ...
def setLicense(name: Union[str, bytes], key: Union[str, bytes]): ...
def DBG_SIZEOF(t): ...

class TeamTalkError(Exception): ...

class TeamTalk:
    def __init__(self) -> None: ...
    def closeTeamTalk(self): ...
    def __del__(self) -> None: ...
    def getMessage(self, nWaitMS: int = ...) -> TTMessage: ...
    def getFlags(self) -> ClientFlags: ...
    def getDefaultSoundDevices(self): ...
    def getSoundDevices(self)-> Tuple[SoundDevice]: ...
    def initSoundInputDevice(self, indev: int) -> bool: ...
    def initSoundOutputDevice(self, outdev): ...
    def enableVoiceTransmission(self, bEnable: bool) -> bool: ...
    def connect(self, szHostAddress: Union[str, bytes], nTcpPort: int, nUdpPort: int, nLocalTcpPort: int = ..., nLocalUdpPort: int = ..., bEncrypted: bool = ...) -> bool: ...
    def disconnect(self) -> bool: ...
    def doPing(self) -> int: ...
    def doLogin(self, szNickname: Union[str, bytes], szUsername: Union[str, bytes], szPassword: Union[str, bytes], szClientname: Union[str, bytes]) -> int: ...
    def doLogout(self) -> int: ...
    def doJoinChannelByID(self, nChannelID: int, szPassword: Union[str, bytes]) -> int: ...
    def doLeaveChannel(self) -> int: ...
    def doSendFile(self, nChannelID: int, szLocalFilePath: Union[str, bytes]) -> int: ...
    def doRecvFile(self, nChannelID: int, nFileID: int, szLocalFilePath: Union[str, bytes]) -> int: ...
    def doDeleteFile(self, nChannelID: int, nFileID: int) -> int: ...
    def doChangeNickname(self, szNewNick: Union[str, bytes]) -> int: ...
    def doChangeStatus(self, nStatusMode: int, szStatusMessage: Union[str, bytes]) -> int: ...
    def doTextMessage(self, msg: TextMessage) -> int: ...
    def getServerProperties(self): ...
    def getServerUsers(self): ...
    def getRootChannelID(self): ...
    def getMyChannelID(self) -> int: ...
    def getChannel(self, nChannelID: int) -> Channel: ...
    def getChannelPath(self, nChannelID): ...
    def getChannelIDFromPath(self, szChannelPath: Union[str, bytes]) -> int: ...
    def getChannelUsers(self, nChannelID): ...
    def getChannelFiles(self, nChannelID): ...
    def getServerChannels(self): ...
    def getMyUserID(self) -> int: ...
    def getMyUserAccount(self): ...
    def getMyUserData(self): ...
    def getUser(self, nUserID: int) -> User: ...
    def getUserStatistics(self, nUserID): ...
    def getUserByUsername(self, szUsername): ...
    def getErrorMessage(self, nError: int) -> Union[str, bytes]: ...
