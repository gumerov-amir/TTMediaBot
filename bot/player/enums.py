from enum import Enum


class State(Enum):
    Stopped = 'Stopped'
    Playing = 'Playing'
    Paused = 'Paused'


class Mode(Enum):
    SingleTrack = 'st'
    RepeatTrack = 'rt'
    TrackList = 'tl'
    RepeatTrackList = 'rtl'
    Random = 'rnd'
