from enum import Enum

class State(Enum):
    Stopped = 'Stopped'
    Playing = 'Playing'
    Paused = 'Paused'

class Mode(Enum):
    Single = 0
    TrackList = 1
    Random = 2
