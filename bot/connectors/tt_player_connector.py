from threading import Thread
import time

from bot.player import State
from bot import vars


class TTPlayerConnector(Thread):
    def __init__(self, player, ttclient):
        Thread.__init__(self, daemon=True)
        self.name = 'TTPlayerConnector'
        self.player = player
        self.ttclient = ttclient

    def run(self):
        last_player_state = State.Stopped
        last_track_meta = {'name': None, 'url': None}
        while True:
            if self.player.state != last_player_state:
                last_player_state = self.player.state
                if self.player.state == State.Playing:
                    self.ttclient.enable_voice_transmission()
                    last_track_meta = self.player.track.get_meta()
                    if self.player.track.name:
                        self.ttclient.change_status_text('{state}: {name}'.format(state=self.player.state.value, name=self.player.track.name))
                    else:
                        self.ttclient.change_status_text('{state}: {url}'.format(state=self.player.state.value, url=self.player.track.url))
                elif self.player.state == State.Stopped:
                    self.ttclient.disable_voice_transmission()
                    self.ttclient.change_status_text('')
                elif self.player.state == State.Paused:
                    self.ttclient.disable_voice_transmission()
                    self.ttclient.change_status_text('{state}: {name}'.format(state=self.player.state.value, name=self.player.track.name))
            if self.player.track.get_meta() != last_track_meta and last_player_state != State.Stopped:
                last_track_meta = self.player.track.get_meta()
                self.ttclient.change_status_text('{state}: {name}'.format(state=self.player.state.value, name=self.player.track.name))
            time.sleep(vars.loop_timeout)
