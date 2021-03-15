from threading import Thread
import time
from .player import State

class EventHandler(Thread):
    def __init__(self, player, ttclient):
        Thread.__init__(self)
        self.player = player
        self.ttclient = ttclient

    def run(self):
        last_player_state = State.Stopped
        last_track_meta = {"name": None, "url": None}
        while True:
            if self.player.state != last_player_state:
                last_player_state = self.player.state
                if self.player.state == State.Playing:
                    self.ttclient.enableVoiceTransmission(True)
                    last_track_meta = self.player.track.get_meta()
                    self.ttclient.doChangeStatus(0, "{state}: {name}".format(state=self.player.state.value, name=self.player.track.name))
                elif self.player.state == State.Stopped:
                    self.ttclient.enableVoiceTransmission(False)
                    self.ttclient.doChangeStatus(0, "")
                elif self.player.state == State.Paused:
                    self.ttclient.enableVoiceTransmission(False)
                    self.ttclient.doChangeStatus(0, "{state}: {name}".format(state=self.player.state.value, name=self.player.track.name))
            if self.player.track.get_meta() != last_track_meta and last_player_state != State.Stopped:
                last_track_meta = self.player.track.get_meta()
                self.ttclient.doChangeStatus(0, "{state}: {name}".format(state=self.player.state.value, name=self.player.track.name))
