class NotFoundError(Exception):
    pass


class NoNextTrackError(Exception):
    pass


class NoPreviousTrackError(Exception):
    pass


class IncorrectProtocolError(Exception):
    pass


class PathNotFoundError(Exception):
    pass


class IncorrectTrackIndexError(Exception):
    pass


class NothingIsPlayingError(Exception):
    pass


class IncorrectPositionError:
    pass


class ConnectionError(Exception):
    pass


class LoginError(Exception):
    pass


class JoinChannelError(Exception):
    pass
