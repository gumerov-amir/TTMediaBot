from enum import Enum


class State(Enum):
    Stopped = "Stopped"
    Playing = "Playing"
    Paused = "Paused"


class Mode(Enum):
    SingleTrack = "st"
    RepeatTrack = "rt"
    TrackList = "tl"
    RepeatTrackList = "rtl"
    Random = "rnd"


class TrackType(Enum):
    Default = 0
    Live = 1
    Local = 2
    Direct = 3
    Dynamic = 4
