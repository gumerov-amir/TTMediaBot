from collections import deque
import logging
import time
import random
import sys

import mpv

from bot import errors, vars
from bot.player.enums import Mode, State
from bot.player.track import Track
from bot.player.thread import PlayerThread
from bot.sound_devices import SoundDevice, SoundDeviceType
import ctypes

if sys.platform == 'win32':
    from ctypes import windll
    windll.ole32.CoInitializeEx(None, 0)

if sys.platform == 'win32':
    vsnprintf = ctypes.cdll.msvcrt.vsnprintf
else:
    libc = ctypes.cdll.LoadLibrary(ctypes.util.find_library('c'))
    vsnprintf = libc.vsnprintf

vsnprintf.restype = ctypes.c_int
vsnprintf.argtypes = (ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p, ctypes.c_void_p)

class Player:
    def __init__(self, config, cache):
        self.config = config
        self._player = mpv.MPV(**self.config["player_options"], log_handler=self.log_handler, loglevel=None)
        self.volume = self.config['default_volume']
        self.max_volume = self.config['max_volume']
        self.volume_fading = self.config['volume_fading']
        self.volume_fading_interval = self.config['volume_fading_interval']
        self.seek_step = config['seek_step']
        self.track_list = []
        self.track = Track()
        self.track_index = -1
        self.state = State.Stopped
        self.mode = Mode.TrackList
        self.cache = cache
        self.player_thread = PlayerThread(self)

    def initialize(self):
        logging.debug('Initializing player')
        logging.debug('Player initialized')

    def run(self):
        logging.debug('Starting player thread')
        self.player_thread.start()
        logging.debug('Player thread started')

    def close(self):
        logging.debug('Closing player thread')
        self.player_thread.close()
        self._player.terminate()
        logging.debug('Player thread closed')

    def play(self, tracks=None, start_track_index=None):
        if tracks != None:
            self.track_list = tracks
            if not start_track_index and self.mode == Mode.Random:
                self.track = random.choice(self.track_list)
                self.track_index = self.track_list.index(self.track)
            else:
                self.track_index = start_track_index if start_track_index else 0
                self.track = tracks[self.track_index]
            self._play(self.track.url)
        else:
            self._player.pause = False
        self._player.volume = self.volume
        self.state = State.Playing

    def pause(self):
        self.state = State.Paused
        self._player.pause = True

    def stop(self):
        self.state = State.Stopped
        self._player.stop()
        self.track_list = []
        self.track = Track()
        self.track_index = -1

    def _play(self, arg, save_to_history=True):
        self._player.pause = False
        if save_to_history:
            try:
                if self.cache.recents[-1] != self.track_list[self.track_index]:
                    self.cache.recents.append(self.track_list[self.track_index])
            except:
                self.cache.recents.append(self.track_list[self.track_index])
            self.cache.save()
        self._player.play(arg)

    def next(self):
        track_index = self.track_index
        if len(self.track_list) > 0:
            if self.mode == Mode.Random:
                track_index = random.randrange(0, len(self.track_list))
            else:
                track_index += 1
        else:
            track_index = 0
        try:
            self.play_by_index(track_index)
        except errors.IncorrectTrackIndexError:
            if self.mode == Mode.RepeatTrackList:
                self.play_by_index(0)
            else:
                raise errors.NoNextTrackError()

    def previous(self):
        track_index = self.track_index
        if len(self.track_list) > 0:
            if self.mode == Mode.Random:
                track_index = random.randrange(0, len(self.track_list))
            else:
                track_index -= 1
        else:
            track_index = 0
        try:
            self.play_by_index(track_index)
        except errors.IncorrectTrackIndexError:
            if self.mode == Mode.RepeatTrackList:
                self.play_by_index(len(self.track_list) - 1)
            else:
                raise errors.NoPreviousTrackError

    def play_by_index(self, index):
        if self.state == State.Stopped:
            raise errors.NothingIsPlayingError()
        if index < len(self.track_list) and index >= (0 - len(self.track_list)):
            self.track = self.track_list[index]
            self.track_index = self.track_list.index(self.track)
            self._play(self.track.url)
            self.state = State.Playing
        else:
            raise errors.IncorrectTrackIndexError()

    def set_volume(self, volume):
        volume = volume if volume <= self.max_volume else self.max_volume
        self.volume = volume
        if self.volume_fading:
            n = 1 if self._player.volume < volume else -1
            for i in range(int(self._player.volume), volume, n):
                self._player.volume = i
                time.sleep(self.volume_fading_interval)
        else:
            self._player.volume = volume

    def get_speed(self):
        return self._player.speed

    def set_speed(self, arg):
        self._player.speed = arg

    def seek_back(self, time_step=None):
        time_step = time_step if time_step else self.seek_step
        self._player.seek(-time_step)

    def seek_forward(self, time_step=None):
        time_step = time_step if time_step else self.seek_step
        self._player.seek(time_step)

    def get_position(self):
        if self.state != State.Stopped:
            return self._vlc_player.get_position() * 100
        else:
            raise errors.NothingIsPlayingError()

    def set_position(self, arg):
        if arg >= 0 and arg <= 100:
            self._vlc_player.set_position(arg)
        else:
            raise errors.IncorrectPositionError()

    def get_output_devices(self):
        devices = []
        for device in self._player.audio_device_list:
                devices.append(SoundDevice(device["description"], device["name"], SoundDeviceType.Output))
        return devices

    def set_output_device(self, id):
        self._player.audio_device = id

    def log_handler(self, level, component, message):
        logging.log(5, "{}: {}: {}".format(level, component, message))
