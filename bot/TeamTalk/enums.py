from enum import Enum, Flag

import TeamTalkPy

class MessageType(Enum):
    User = TeamTalkPy.TextMsgType.MSGTYPE_USER
    Channel = TeamTalkPy.TextMsgType.MSGTYPE_CHANNEL
    Broadcast = TeamTalkPy.TextMsgType.MSGTYPE_BROADCAST
    Custom = TeamTalkPy.TextMsgType.MSGTYPE_CUSTOM

class ChannelType(Flag):
    ClassRoom = TeamTalkPy.ChannelType.CHANNEL_CLASSROOM
    Default = TeamTalkPy.ChannelType.CHANNEL_DEFAULT
    Hidden = TeamTalkPy.ChannelType.CHANNEL_HIDDEN
    NoRecording = TeamTalkPy.ChannelType.CHANNEL_NO_RECORDING
    NoVoiceActivation = TeamTalkPy.ChannelType.CHANNEL_NO_VOICEACTIVATION
    OperatorRecnvOnly = TeamTalkPy.ChannelType.CHANNEL_OPERATOR_RECVONLY
    Permanent = TeamTalkPy.ChannelType.CHANNEL_PERMANENT
    SoloTransmit = TeamTalkPy.ChannelType.CHANNEL_SOLO_TRANSMIT
