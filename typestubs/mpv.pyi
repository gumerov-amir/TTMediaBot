from collections.abc import Callable
from ctypes import *
from typing import Any

class MpvEventID(c_int):
    NONE: int
    SHUTDOWN: int
    LOG_MESSAGE: int
    GET_PROPERTY_REPLY: int
    SET_PROPERTY_REPLY: int
    COMMAND_REPLY: int
    START_FILE: int
    END_FILE: int
    FILE_LOADED: int
    TRACKS_CHANGED: int
    TRACK_SWITCHED: int
    IDLE: int
    PAUSE: int
    UNPAUSE: int
    TICK: int
    SCRIPT_INPUT_DISPATCH: int
    CLIENT_MESSAGE: int
    VIDEO_RECONFIG: int
    AUDIO_RECONFIG: int
    METADATA_UPDATE: int
    SEEK: int
    PLAYBACK_RESTART: int
    PROPERTY_CHANGE: int
    CHAPTER_CHANGE: int

class MpvEvent(Structure):
    _fields_ = ...

class MPV:
    def __init__(
        self,
        *extra_mpv_flags: Any,
        log_handler: Callable[[str, str, str], None] | None = ...,
        start_event_thread: bool = ...,
        loglevel: str | None = ...,
        **extra_mpv_opts: Any,
    ) -> None: ...
    audio_device: str
    audio_device_list: list[dict[str, Any]]
    idle_active: bool
    duration: float
    def event_callback(
        self,
        *event_types: str,
    ) -> Callable[[Callable[[MpvEvent], None]], None]: ...
    media_title: str
    metadata: dict[str, Any]
    pause: bool
    def seek(
        self,
        amount: float,
        reference: str = ...,
        precision: str = ...,
    ) -> None: ...
    speed: float
    def stop(self, keep_playlist: bool = ...) -> None: ...
    stream_record: str
    def play(self, filename: str) -> None: ...
    def terminate(self) -> None: ...
    volume: int
