from __future__ import annotations
import html
import logging
import time
from typing import Any, Dict, Callable, List, Optional, TYPE_CHECKING
import random

import mpv

from bot import errors
from bot.player.enums import Mode, State, TrackType
from bot.player.track import Track
from bot.sound_devices import SoundDevice, SoundDeviceType


if TYPE_CHECKING:
    from bot import Bot


MAX_TRACK_LIST_SIZE = 1000


class Player:
    def __init__(self, bot: Bot):
        self.config = bot.config.player
        self.general_config = bot.config.general
        self.cache = bot.cache
        self.cache_manager = bot.cache_manager
        mpv_options = {
            "demuxer_lavf_o": "http_persistent=false",
            "demuxer_max_back_bytes": 1048576,
            "demuxer_max_bytes": 2097152,
            "video": False,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
            "ytdl": False,
        }
        mpv_options.update(self.config.player_options)
        try:
            self._player = mpv.MPV(**mpv_options, log_handler=self.log_handler)
        except AttributeError:
            del mpv_options["demuxer_max_back_bytes"]
            self._player = mpv.MPV(**mpv_options, log_handler=self.log_handler)
        self._log_level = 5
        self.track_list: List[Track] = []
        self.track: Track = Track()
        self.track_index: int = -1
        self.state = State.Stopped
        self.mode = Mode.TrackList
        self.volume = self.config.default_volume
        self._queue_active_track = False
        self.bass_boost_level = 0
        self._position_saved_for_track: Optional[str] = None
        self._suppress_position_clear = False
        try:
            self.set_bass_boost(self.config.bass_boost_level)
        except Exception:
            logging.error("Failed to apply initial bass boost", exc_info=True)

    def initialize(self) -> None:
        logging.debug("Initializing player")
        logging.debug("Player initialized")

    def run(self) -> None:
        logging.debug("Registering player callbacks")
        self.register_event_callback("end-file", self.on_end_file)
        self._player.observe_property("metadata", self.on_metadata_update)
        self._player.observe_property("media-title", self.on_metadata_update)
        logging.debug("Player callbacks registered")

    def close(self) -> None:
        logging.debug("Closing player")
        if self.state != State.Stopped:
            self.stop()
        self._player.terminate()
        logging.debug("Player closed")

    def play(
        self,
        tracks: Optional[List[Track]] = None,
        start_track_index: Optional[int] = None,
    ) -> None:
        if (
            self.general_config.enable_positions
            and self.state != State.Stopped
            and self.track
            and self.track.url
            and self.track.type != TrackType.Live
        ):
            self._save_position_marker()
        self._queue_active_track = False
        if tracks != None:
            # Limitar track_list para evitar consumo excessivo de RAM
            if len(tracks) > MAX_TRACK_LIST_SIZE:
                tracks = tracks[:MAX_TRACK_LIST_SIZE]
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

    def pause(self) -> None:
        self.state = State.Paused
        self._player.pause = True
        self._save_position_marker()

    def stop(self) -> None:
        self._save_position_marker()
        self.state = State.Stopped
        self._suppress_position_clear = True
        self._player.stop()
        self.track_list = []
        self.track = Track()
        self.track_index = -1
        self._queue_active_track = False

    def _play(self, arg: str, save_to_recents: bool = True) -> None:
        if save_to_recents:
            try:
                if self.cache.recents[-1] != self.track_list[self.track_index]:
                    self.cache.recents.append(
                        self.track_list[self.track_index].get_raw()
                    )
            except:
                self.cache.recents.append(self.track_list[self.track_index].get_raw())
            self.cache_manager.save()
        self._position_saved_for_track = None
        self._player.pause = False
        self._player.play(arg)

    def _play_queue_from_start(self) -> None:
        if not self.cache.queue:
            raise errors.NoNextTrackError()
        self.track_list = list(self.cache.queue)
        self.track_index = 0
        self.track = self.track_list[self.track_index]
        self._queue_active_track = True
        self._play(self.track.url)

    def _consume_current_queue_track(self) -> None:
        if self.cache.queue and self.cache.queue[0].url == self.track.url:
            self.cache.queue.pop(0)
            self.cache_manager.save()
        self._queue_active_track = False

    def play_queue(self) -> None:
        if not self.cache.queue:
            raise errors.NothingIsPlayingError()
        self._play_queue_from_start()
        self._player.volume = self.volume
        self.state = State.Playing
        self._position_saved_for_track = None

    def _save_position_marker(self) -> None:
        if not self.general_config.enable_positions:
            return
        if not self.track or not self.track.url:
            return
        if self.track.type == TrackType.Live:
            return
        try:
            position = float(self._player.time_pos or 0)
            duration_value = self._player.duration
            duration = float(duration_value) if duration_value else None
        except Exception:
            return
        self.track.resume_position = position
        self.track.resume_duration = duration if duration else 0
        try:
            for recent_track in reversed(self.cache.recents):
                if recent_track.url == self.track.url:
                    recent_track.resume_position = position
                    recent_track.resume_duration = duration if duration else 0
                    break
        except Exception:
            ...
        try:
            self.cache_manager.save()
        except Exception:
            logging.error("Failed to save positions", exc_info=True)

    def _clear_position_entry(self) -> None:
        pass

    def next(self) -> None:
        if self.mode == Mode.Queue:
            if self.cache.queue and self._queue_active_track:
                self._consume_current_queue_track()
            if self.cache.queue:
                self._play_queue_from_start()
                self._player.volume = self.volume
                self.state = State.Playing
                return
            else:
                self.stop()
                raise errors.NoNextTrackError()
        track_index = self.track_index
        if len(self.track_list) > 0:
            if self.mode == Mode.Random:
                try:
                    track_index = self._index_list[
                        self._index_list.index(self.track_index) + 1
                    ]
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

    def previous(self) -> None:
        if self.mode == Mode.Queue:
            raise errors.NoPreviousTrackError
        track_index = self.track_index
        if len(self.track_list) > 0:
            if self.mode == Mode.Random:
                try:
                    track_index = self._index_list[
                        self._index_list.index(self.track_index) - 1
                    ]
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

    def play_by_index(self, index: int) -> None:
        if index < len(self.track_list) and index >= (0 - len(self.track_list)):
            self.track = self.track_list[index]
            self.track_index = self.track_list.index(self.track)
            self._play(self.track.url)
            self.state = State.Playing
        else:
            raise errors.IncorrectTrackIndexError()

    def set_volume(self, volume: int) -> None:
        volume = volume if volume <= self.config.max_volume else self.config.max_volume
        self.volume = volume
        if self.config.volume_fading:
            n = 1 if self._player.volume < volume else -1
            for i in range(int(self._player.volume), volume, n):
                self._player.volume = i
                time.sleep(self.config.volume_fading_interval)
        else:
            self._player.volume = volume

    def _clear_bass_boost(self) -> None:
        try:
            self._player.command("af", "clr")
        except Exception:
            ...

    def _update_audio_filters(self) -> None:
        """Combine bass_boost and pitch filters into a single af string"""
        filters = []
        # Add bass boost filter if active
        if self.bass_boost_level > 0:
            gain = (self.bass_boost_level * 60) // 100 - 30
            filters.append(f"bass=g={gain}")
        # Add pitch filter if active
        pitch = self.get_pitch()
        if pitch != 0:
            sample_rate = 48000
            pitch_factor = 2.0 ** (pitch / 12.0)
            filters.append(f"lavfi=[asetrate={sample_rate}*{pitch_factor},aresample={sample_rate}]")
        # Set combined filters
        if filters:
            self._player.af = ",".join(filters)
        else:
            self._player.af = ""

    def set_bass_boost(self, level: int) -> None:
        if level < 0 or level > 100:
            raise ValueError()
        self.bass_boost_level = level
        self._update_audio_filters()
        try:
            self.config.bass_boost_level = level
        except Exception:
            ...

    def get_speed(self) -> float:
        return self._player.speed

    def set_speed(self, arg: float) -> None:
        if arg < 0.25 or arg > 4:
            raise ValueError()
        self._player.speed = arg

    def get_pitch(self) -> int:
        return getattr(self, '_pitch', 0)

    def set_pitch(self, semitons: int) -> None:
        if semitons < -12 or semitons > 12:
            raise ValueError()
        self._pitch = semitons
        self._update_audio_filters()

    def seek_back(self, step: Optional[float] = None) -> None:
        step = step if step else self.config.seek_step
        if step <= 0:
            raise ValueError()
        try:
            self._player.seek(-step, reference="relative")
        except SystemError:
            self.stop()

    def seek_forward(self, step: Optional[float] = None) -> None:
        step = step if step else self.config.seek_step
        if step <= 0:
            raise ValueError()
        try:
            self._player.seek(step, reference="relative")
        except SystemError:
            self.stop()

    def get_duration(self) -> float:
        return self._player.duration

    def seek_absolute(self, position: float) -> None:
        if position < 0:
            raise errors.IncorrectPositionError()
        try:
            self._player.command("seek", position, "absolute", "exact")
        except SystemError:
            self.stop()

    """def get_position(self) -> float:
        return self._player.time_pos

    def set_position(self, arg: float) -> None:
        if arg < 0:
            raise errors.IncorrectPositionError()
        self._player.seek(arg, reference="absolute")"""

    def get_output_devices(self) -> List[SoundDevice]:
        devices: List[SoundDevice] = []
        for device in self._player.audio_device_list:
            devices.append(
                SoundDevice(
                    device["description"], device["name"], SoundDeviceType.Output
                )
            )
        return devices

    def set_output_device(self, id: str) -> None:
        self._player.audio_device = id

    def shuffle(self, enable: bool) -> None:
        if enable:
            self._index_list = [i for i in range(0, len(self.track_list))]
            random.shuffle(self._index_list)
        else:
            del self._index_list

    def register_event_callback(
        self, callback_name: str, callback_func: Callable[[mpv.MpvEvent], None]
    ) -> None:
        self._player.event_callback(callback_name)(callback_func)

    def log_handler(self, level: str, component: str, message: str) -> None:
        logging.log(self._log_level, "{}: {}: {}".format(level, component, message))

    def _parse_metadata(self, metadata: Dict[str, Any]) -> str:
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
        chunks: List[str] = []
        chunks.append(artist) if artist else ...
        chunks.append(title) if title else ...
        chunks.append(stream_name) if stream_name else ...
        return " - ".join(chunks)

    def on_end_file(self, event: mpv.MpvEvent) -> None:
        if self.state == State.Playing and self._player.idle_active:
            if self._suppress_position_clear:
                self._suppress_position_clear = False
                return
            self._clear_position_entry()
            if self.mode == Mode.Queue:
                if self._queue_active_track:
                    self._consume_current_queue_track()
                if self.cache.queue:
                    try:
                        self._play_queue_from_start()
                        self._player.volume = self.volume
                        self.state = State.Playing
                    except errors.NoNextTrackError:
                        self.stop()
                else:
                    self.stop()
                return
            if self.mode == Mode.SingleTrack or self.track.type == TrackType.Direct:
                self.stop()
            elif self.mode == Mode.RepeatTrack:
                self.play_by_index(self.track_index)
            else:
                try:
                    self.next()
                except errors.NoNextTrackError:
                    self.stop()

    def on_metadata_update(self, name: str, value: Any) -> None:
        if self.state == State.Playing and (
            self.track.type == TrackType.Direct or self.track.type == TrackType.Local
        ):
            metadata = self._player.metadata
            try:
                new_name = self._parse_metadata(metadata)
                if not new_name:
                    new_name = html.unescape(self._player.media_title)
            except TypeError:
                new_name = html.unescape(self._player.media_title)
            if self.track.name != new_name and new_name:
                self.track.name = new_name
