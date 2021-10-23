from collections import deque
import html
import logging
import time
import random
import sys

import mpv

from bot import errors, vars
from bot.player.enums import Mode, State, TrackType
from bot.player.track import Track
from bot.sound_devices import SoundDevice, SoundDeviceType


class Player:
    def __init__(self, config, cache):
        self.config = config
        mpv_options = {
            'demuxer_max_back_bytes': 1048576,
            'demuxer_max_bytes': 2097152,
            'video': False,
            'ytdl': False,
        }
        mpv_options.update(config['player_options'])
        try:
            self._player = mpv.MPV(**mpv_options, log_handler=self.log_handler)
        except AttributeError:
            del mpv_options['demuxer_max_back_bytes']
            self._player = mpv.MPV(**mpv_options, log_handler=self.log_handler)
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

    def initialize(self):
        logging.debug('Initializing player')
        logging.debug('Player initialized')

    def run(self):
        logging.debug('Registering callbacks')
        self.register_event_callback("end-file", self.on_end_file)
        self.register_event_callback("metadata-update", self.on_metadata_update)
        logging.debug('Callbacks registered')

    def close(self):
        logging.debug('Closing player')
        if self.state != State.Stopped:
            self.stop()
        self._player.terminate()
        logging.debug('Player closed')

    def play(self, tracks=None, start_track_index=None):
        if tracks != None:
            self.track_list = tracks
            if not start_track_index and self.mode == Mode.Random:
                self.shuffle(True)
                self.track_index = self._index_list[0]
                self.track = self.track_list[self.track_index]
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
                    self.cache.recents.append(self.track_list[self.track_index].get_raw())
            except:
                self.cache.recents.append(self.track_list[self.track_index].get_raw())
            self.cache.save()
        self._player.pause = False
        self._player.play(arg)

    def next(self):
        track_index = self.track_index
        if len(self.track_list) > 0:
            if self.mode == Mode.Random:
                try:
                    track_index = self._index_list[self._index_list.index(self.track_index) + 1]
                except IndexError:
                    track_index = 0
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
                try:
                    track_index = self._index_list[self._index_list.index(self.track_index) - 1]
                except IndexError:
                    track_index = len(self.track_list) - 1
            else:
                if track_index == 0 and self.mode != Mode.RepeatTrackList:
                    raise errors.NoPreviousTrackError
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

    def shuffle(self, enable):
        if enable:
            self._index_list = [i for i in range(0, len(self.track_list))]
            random.shuffle(self._index_list)
        else:
            del self._index_list

    def register_event_callback(self, callback_name, callback_func):
        self._player.event_callback(callback_name)(callback_func)

    def log_handler(self, level, component, message):
        level = logging.getLevelName(self._log_level)
        logging.log(level, "{}: {}: {}".format(level, component, message))

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

    def on_end_file(self, event):
            if self.state == State.Playing and self._player.idle_active:
                if self.mode == Mode.SingleTrack or self.track.type == TrackType.Direct:
                    self.stop()
                elif self.mode == Mode.RepeatTrack:
                    self.play_by_index(self.track_index)
                else:
                    try:
                        self.next()
                    except errors.NoNextTrackError:
                        self.stop()

    def on_metadata_update(self, event):
            if self.state == State.Playing and (self.track.type == TrackType.Direct or self.track.type == TrackType.Local):
                metadata = self._player.metadata
                try:
                    new_name = self._parse_metadata(metadata)
                    if not new_name:
                        new_name = html.unescape(self._player.media_title)
                except TypeError:
                    new_name = html.unescape(self._player.media_title)
                if self.track.name != new_name and new_name:
                    self.track.name = new_name
