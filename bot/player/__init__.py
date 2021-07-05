from collections import deque
import logging
import time
import random
import sys

import vlc

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
        self._vlc_instance = vlc.Instance(self.config['vlc_options'])
        self._vlc_player = self._vlc_instance.media_player_new()
        self.volume = self.config['default_volume']
        self.max_volume = self.config['max_volume']
        self.faded_volume = self.config['faded_volume']
        self.faded_volume_timestamp = self.config['faded_volume_timestamp']
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
        self._vlc_instance.log_set(self.log_callback, None)
        logging.debug('Player initialized')

    def run(self):
        logging.debug('Starting player thread')
        self.player_thread.start()
        logging.debug('Player thread started')

    def close(self):
        logging.debug('Closing player thread')
        self.player_thread.close()
        self._vlc_player.release()
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
            self._play_with_vlc(self.track.url)
        else:
            self._vlc_player.play()
        while self._vlc_player.get_state() != vlc.State.Playing and self._vlc_player.get_state() != vlc.State.Ended:
            time.sleep(vars.loop_timeout)
        while self._vlc_player.audio_set_volume(self.volume) == -1:
            time.sleep(vars.loop_timeout)
        self._vlc_player.audio_set_volume(self.volume)
        self.state = State.Playing

    def pause(self):
        self.state = State.Paused
        self._vlc_player.pause()

    def stop(self):
        self.state = State.Stopped
        self._vlc_player.pause()
        self.track_list = []
        self.track = Track()
        self.track_index = -1

    def _play_with_vlc(self, arg, save_to_history=True):
        if save_to_history:
            try:
                if self.cache.history[-1] != self.track_list[self.track_index]:
                    self.cache.history.append(self.track_list[self.track_index])
            except:
                self.cache.history.append(self.track_list[self.track_index])
        self.cache.save()
        self._vlc_player.set_media(self._vlc_instance.media_new(arg))
        self._vlc_player.play()

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
            self._play_with_vlc(self.track.url)
            if self.state == State.Paused:
                while self._vlc_player.get_state() != vlc.State.Playing and self._vlc_player.get_state() != vlc.State.Ended:
                    pass
                self.state = State.Playing
        else:
            raise errors.IncorrectTrackIndexError()

    def set_volume(self, volume):
        volume = volume if volume <= self.max_volume else self.max_volume
        self.volume = volume
        if volume == 0:
            self._vlc_player.audio_set_mute(True)
        else:
            if self._vlc_player.audio_get_mute():
                self._vlc_player.audio_set_mute(False)
        if self.faded_volume:
            n = 1 if self._vlc_player.audio_get_volume() < volume else -1
            for i in range(self._vlc_player.audio_get_volume(), volume, n):
                self._vlc_player.audio_set_volume(i)
                time.sleep(self.faded_volume_timestamp)
        else:
            self._vlc_player.audio_set_volume(volume)

    def get_rate(self):
        return self._vlc_player.get_rate()

    def set_rate(self, arg):
        self._vlc_player.set_rate(arg)

    def seek_back(self, time_step=None):
        time_step = time_step / 100 if time_step else self.seek_step / 100
        pos = self._vlc_player.get_position() - time_step
        if pos < 0:
            pos = 0
        elif pos > 1:
            pos = 1
        self._vlc_player.set_position(pos)

    def seek_forward(self, time_step=None):
        time_step = time_step / 100 if time_step else self.seek_step / 100
        pos = self._vlc_player.get_position() + time_step
        if pos < 0:
            pos = 0
        elif pos > 1:
            pos = 1
        self._vlc_player.set_position(pos)

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
        if sys.platform == 'win32':
            self._vlc_player.audio_output_set('waveout')
        devices = []
        mods = self._vlc_player.audio_output_device_enum()
        if mods:
            mod = mods
            while mod:
                mod = mod.contents
                try:
                    devices.append(SoundDevice(mod.psz_description.decode('UTF-8'), mod.psz_device, SoundDeviceType.Output))
                except:
                    devices.append(SoundDevice(mod.description.decode('UTF-8'), mod.device, SoundDeviceType.Output))
                try:
                    mod = mod.p_next
                except:
                    mod = mod.next

        vlc.libvlc_audio_output_device_list_release(mods)
        return devices

    def set_output_device(self, id):
        self._vlc_player.audio_output_device_set(None, id)

    @vlc.CallbackDecorators.LogCb
    def log_callback(data, level, ctx, fmt, args):
        levels = {0: 5, 2: 20, 3: 30, 4: 40}
        BUF_LEN = 1024
        outBuf = ctypes.create_string_buffer(BUF_LEN)
        vsnprintf(outBuf, BUF_LEN, fmt, args)
        logging.log(levels.get(level), str(outBuf.value.decode()))

