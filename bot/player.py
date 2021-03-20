from enum import Enum
import vlc
from threading import Thread
import time
import random

from .track import Track

class Player:
    def __init__(self, ttclient, config):
        self._ttclient = ttclient
        self.config = config
        self._vlc_instance = vlc.Instance()
        self._vlc_player = self._vlc_instance.media_player_new()
        if self.config:
            self._vlc_player.audio_set_volume(int(self.config['default_volume']))
            self.max_volume = int(self.config['max_volume'])
            self.faded_volume = {'True': True, 'False': False}[self.config['faded_volume']]
            self.faded_volume_timestamp = float(self.config['faded_volume_timestamp'])
            self.seek_step = float(config['seek_step'])
            self.output_device = int(self.config['output_device'])
            self.input_device = int(self.config['input_device'])
        self.output_devices = self.get_output_devices()
        self.input_devices = self.get_input_devices()
        self.initialize_devices()
        self.track_list = []
        self.track = Track()
        self.track_index = 0
        self.state = State.Stopped
        self.mode = Mode.Single
        self.playing_thread = PlayingThread(self)
        self.playing_thread.start()

    def play(self, tracks=None):
        if tracks:
            self.track_list = tracks
            if self.mode == Mode.Random:
                self.track = random.choice(self.track_list)
                self.track_index = self.track_list.index(self.track)
            else:
                self.track_index = 0
                self.track = tracks[self.track_index]
            self._play_with_vlc(self.track.url)
        else:
            self._vlc_player.play()
        while self._vlc_player.get_state() != vlc.State.Playing and self._vlc_player.get_state() != vlc.State.Ended:
            pass    
        self.state = State.Playing


    def pause(self):
        self.state = State.Paused
        self._vlc_player.pause()

    def stop(self):
        self.state = State.Stopped
        self._vlc_player.pause()
        self.track_index = None
        self.track = Track()


    def _play_with_vlc(self, arg):
        self._vlc_player.set_media(self._vlc_instance.media_new(arg))
        self._vlc_player.play()

    def next(self):
        if self.mode == Mode.Random:
            self.track = random.choice(self.track_list)
            self.track_index = self.track_list.index(self.track)
        else:
            try:
                self.track = self.track_list[self.track_index + 1]
                self.track_index += 1
            except IndexError:
                raise errors.NoNextTrackError()
        self._play_with_vlc(self.track.url)

    def previous(self):
        if self.mode == Mode.Random:
            self.track = random.choice(self.track_list)
            self.track_index = self.track_list.index(self.track)
        else:
            try:
                track_index = self.track_index - 1
                if track_index < 0:
                    raise errors.NoPreviousTrackError()
                self.track = self.track_list[track_index]
                self.track_index -= 1
            except IndexError:
                raise errors.NoPreviousTrackError()
        self._play_with_vlc(self.track.url)

    def play_by_index(self, index):
        if index >= 0 and index < len(self.track_list):
            self.track_index = index
            self.track = self.track_list[self.track_index]
            self._play_with_vlc(self.track.url)
        else:
            raise errors.IncorrectTrackIndexError()

    def set_volume(self, volume):
        volume = volume if volume <= self.max_volume else self.max_volume
        if self.faded_volume:
            n = 1 if self._vlc_player.audio_get_volume() < volume else -1
            for i in range(self._vlc_player.audio_get_volume(), volume, n):
                self._vlc_player.audio_set_volume(i)
                time.sleep(self.faded_volume_timestamp)
        else:
            self._vlc_player.audio_set_volume(volume)

    def seek_back(self, time_step=None):
        time_step = float(time_step) / 100 if time_step else self.seek_step / 100
        pos = self._vlc_player.get_position() - time_step
        if pos < 0:
            pos = 0
        elif pos > 1:
            pos = 1
        self._vlc_player.set_position(pos)

    def seek_forward(self, time_step=None):
        time_step = float(time_step) / 100 if time_step else self.seek_step / 100
        pos = self._vlc_player.get_position() + time_step
        if pos < 0:
            pos = 0
        elif pos > 1:
            pos = 1
        self._vlc_player.set_position(pos)

    def get_output_devices(self):
        devices = {}
        mods = self._vlc_player.audio_output_device_enum()
        if mods:
            mod = mods
            while mod:
                mod = mod.contents
                devices[str(mod.description, 'utf-8')] = mod.device
                mod = mod.next
        vlc.libvlc_audio_output_device_list_release(mods)
        return devices

    def get_input_devices(self):
        devices = {}
        device_list = [i for i in self._ttclient.getSoundDevices()]
        for device in device_list:
            devices[device.szDeviceName] = device.nDeviceID
        return devices

    def initialize_devices(self):
        self._vlc_player.audio_output_device_set(None, self.output_devices[list(self.output_devices)[self.output_device]])
        self._ttclient.initSoundInputDevice(self.input_devices[list(self.input_devices)[self.input_device]])

class State(Enum):
    Stopped = 'Stopped'
    Playing = 'Playing'
    Paused = 'Paused'

class Mode(Enum):
    Single = 0
    TrackList = 1
    Random = 2

class PlayingThread(Thread):
    def __init__(self, player):
        Thread.__init__(self)
        self.player = player

    def run(self):
        while True:
            if self.player.state == State.Playing and self.player._vlc_player.get_state() == vlc.State.Ended:
                if self.player.mode == Mode.Single:
                    self.player.state = State.Stopped
                elif self.player.mode == Mode.TrackList or self.player.mode == Mode.Random:
                    self.player.next()
            if self.player.state == State.Playing and self.player.track.from_url:
                media = self.player._vlc_player.get_media()
                media.parse_with_options(vlc.MediaParseFlag.do_interact, 0)
                new_name = media.get_meta(12)
                if not new_name:
                    new_name = "{} - {}".format(media.get_meta(vlc.Meta.Title), media.get_meta(vlc.Meta.Artist))
                if self.player.track.name != new_name:
                    self.player.track.name = new_name
            time.sleep(1)
