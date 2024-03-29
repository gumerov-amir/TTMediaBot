from __future__ import annotations
import logging
from threading import Thread
import time
from typing import TYPE_CHECKING

from bot.player import State
from bot import app_vars

if TYPE_CHECKING:
    from bot import Bot


class TTPlayerConnector(Thread):
    def __init__(self, bot: Bot):
        super().__init__(daemon=True)
        self.name = "TTPlayerConnector"
        self.player = bot.player
        self.ttclient = bot.ttclient
        self.translator = bot.translator

    def run(self):
        last_player_state = State.Stopped
        last_track_meta = {"name": None, "url": None}
        self._close = False
        while not self._close:
            try:
                if self.player.state != last_player_state:
                    last_player_state = self.player.state
                    if self.player.state == State.Playing:
                        self.ttclient.enable_voice_transmission()
                        last_track_meta = self.player.track.get_meta()
                        if self.player.track.name:
                            self.ttclient.change_status_text(
                                self.translator.translate(
                                    "Playing: {track_name}"
                                ).format(track_name=self.player.track.name)
                            )
                        else:
                            self.ttclient.change_status_text(
                                self.translator.translate(
                                    "Playing: {stream_url}"
                                ).format(stream_url=self.player.track.url)
                            )
                    elif self.player.state == State.Stopped:
                        self.ttclient.disable_voice_transmission()
                        self.ttclient.change_status_text("")
                    elif self.player.state == State.Paused:
                        self.ttclient.disable_voice_transmission()
                        if self.player.track.name:
                            self.ttclient.change_status_text(
                                self.translator.translate(
                                    "Paused: {track_name}"
                                ).format(track_name=self.player.track.name)
                            )
                        else:
                            self.ttclient.change_status_text(
                                self.translator.translate(
                                    "Paused: {stream_url}"
                                ).format(stream_url=self.player.track.url)
                            )
                if (
                    self.player.track.get_meta() != last_track_meta
                    and last_player_state != State.Stopped
                ):
                    last_track_meta = self.player.track.get_meta()
                    self.ttclient.change_status_text(
                        "{state}: {name}".format(
                            state=self.ttclient.status.split(":")[0],
                            name=self.player.track.name,
                        )
                    )
            except Exception:
                logging.error("", exc_info=True)
            time.sleep(app_vars.loop_timeout)

    def close(self):
        self._close = True
