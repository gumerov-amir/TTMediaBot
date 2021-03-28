from enum import Enum


class State(Enum):
    Stopped = 'Stopped'
    Playing = 'Playing'
    Paused = 'Paused'


class Mode(Enum):
    SingleTrack = 0
    RepeatTrack = 1
    TrackList = 2
    RepeatTrackList = 3
    Random = 4
