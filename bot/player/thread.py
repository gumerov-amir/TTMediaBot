import html
from threading import Thread
import time

import mpv

from bot.player.enums import Mode, State, TrackType
from bot import errors, vars


class PlayerThread(Thread):
    def __init__(self, player):
        super().__init__(daemon=True)
        self.name = 'PlayerThread'
        self.player = player

    def run(self):
        self._close = False
        while not self._close:
            if self.player.state == State.Playing and self.player._player.idle_active:
                if self.player.mode == Mode.SingleTrack or self.player.track.type == TrackType.Direct:
                    self.player.stop()
                elif self.player.mode == Mode.RepeatTrack:
                    self.player.play_by_index(self.player.track_index)
                else:
                    try:
                        self.player.next()
                    except errors.NoNextTrackError:
                        self.player.stop()
            if self.player.state == State.Playing and (self.player.track.type == TrackType.Direct or self.player.track.type == TrackType.Local):
                metadata = self.player._player.metadata
                try:
                    new_name = self._parse_metadata(metadata)
                    if not new_name:
                        new_name = html.unescape(self.player._player.media_title)
                except TypeError:
                    new_name = html.unescape(self.player._player.media_title)
                if self.player.track.name != new_name and new_name:
                    self.player.track.name = new_name
            time.sleep(vars.loop_timeout)

    def close(self):
        self.__close = True

    def _parse_metadata(self, metadata):
        stream_names = ["icy-name"]
        stream_name = None
        title = None
        artist = None
        for i in metadata:
            if i in stream_names:
                stream_name = html.unescape(metadata[i])
            if "title" in i:
                title = html.unescape(metadata[i])
            if "artist" in i:
                artist = html.unescape(metadata[i])
        chunks = []
        chunks.append(artist) if artist else ...
        chunks.append(title) if title else ...
        chunks.append(stream_name) if stream_name else ...
        return " - ".join(chunks)
