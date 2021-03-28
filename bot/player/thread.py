from threading import Thread
import time

import vlc

from bot.player.enums import Mode, State
from bot import errors, vars


class PlayerThread(Thread):
    def __init__(self, player):
        Thread.__init__(self, daemon=True)
        self.name = 'PlayerThread'
        self.player = player

    def run(self):
        while True:
            if self.player.state == State.Playing and self.player._vlc_player.get_state() == vlc.State.Ended:
                if self.player.mode == Mode.SingleTrack:
                    self.player.stop()
                elif self.player.mode == Mode.RepeatTrack:
                    self.player.play_by_index(self.player.track_index)
                else:
                    try:
                        self.player.next()
                    except errors.NoNextTrackError:
                        self.player.stop()
            if self.player.state == State.Playing and self.player.track.from_url:
                media = self.player._vlc_player.get_media()
                media.parse_with_options(vlc.MediaParseFlag.fetch_network, 0)
                new_name = media.get_meta(vlc.Meta.Title)
                if media.get_meta(12):
                    new_name += ' - ' + media.get_meta(12)
                if self.player.track.name != new_name and new_name:
                    self.player.track.name = new_name
            time.sleep(vars.loop_timeout)
