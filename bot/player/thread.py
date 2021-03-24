from threading import Thread
import time

import vlc

from bot.player.enums import Mode, State
from bot import errors, vars


class PlayerThread(Thread):
    def __init__(self, player):
        Thread.__init__(self)
        self.player = player

    def run(self):
        while True:
            if self.player.state == State.Playing and self.player._vlc_player.get_state() == vlc.State.Ended:
                if self.player.mode == Mode.Single:
                    self.player.stop()
                elif self.player.mode == Mode.TrackList or self.player.mode == Mode.Random:
                    try:
                        self.player.next()
                    except errors.NoNextTrackError:
                        self.player.stop()
            if self.player.state == State.Playing and self.player.track.from_url:
                media = self.player._vlc_player.get_media()
                media.parse_with_options(vlc.MediaParseFlag.do_interact, 0)
                new_name = media.get_meta(12)
                if not new_name:
                    new_name = "{} - {}".format(media.get_meta(vlc.Meta.Title), media.get_meta(vlc.Meta.Artist))
                if self.player.track.name != new_name:
                    self.player.track.name = new_name
            time.sleep(vars.loop_timeout)
