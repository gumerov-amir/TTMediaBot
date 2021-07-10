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

class Player:
    def __init__(self, config, cache):
        self.config = config
        self._player = mpv.MPV(**self.config["player_options"], log_handler=self.log_handler)
        self._log_level = 'PLAYER_DEBUG'
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

    def _play(self, arg, save_to_recents=True):
        if save_to_recents:
            try:
                if self.cache.recents[-1] != self.track_list[self.track_index]:
                    self.cache.recents.append(self.track_list[self.track_index])
            except:
                self.cache.recents.append(self.track_list[self.track_index])
            self.cache.save()
        self._player.pause = False
        self._player.play(arg)
        while self._player.playlist_pos == -1 or self._player.idle_active:
            time.sleep(vars.loop_timeout)

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
        if arg < 0.25 or arg > 4:
            raise ValueError()
        self._player.speed = arg

    def seek_back(self, step=None):
        step = step if step else self.seek_step
        if step <= 0:
            raise ValueError()
        if self.state == State.Stopped:
            raise errors.NothingIsPlayingError()
        self._player.seek(-step, reference='relative')

    def seek_forward(self, step=None):
        step = step if step else self.seek_step
        if step <= 0:
            raise ValueError()
        if self.state == State.Stopped:
            raise errors.NothingIsPlayingError()
        self._player.seek(step, reference='relative')

    def get_duration(self):
        if self.state == State.Stopped:
            raise errors.NothingIsPlayingError()
        return self._player.duration

    def get_position(self):
        if self.state == State.Stopped:
            raise errors.NothingIsPlayingError()
        pos = self._player.time_pos
        return self._player.time_pos

    def set_position(self, arg):
        if arg < 0:
            raise errors.IncorrectPositionError()
        self._player.seek(arg, reference='absolute')

    def get_output_devices(self):
        devices = []
        for device in self._player.audio_device_list:
                devices.append(SoundDevice(device["description"], device["name"], SoundDeviceType.Output))
        return devices

    def set_output_device(self, id):
        self._player.audio_device = id

    def log_handler(self, level, component, message):
        level = logging.getLevelName(self._log_level)
        logging.log(level, "{}: {}: {}".format(level, component, message))
