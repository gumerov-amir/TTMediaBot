from __future__ import annotations

import platform
import sys
import time
from typing import TYPE_CHECKING, List, Optional
from bot.commands.command import Command
from bot.player.enums import Mode, State, TrackType
from bot.TeamTalk.structs import User, UserRight
from bot import errors, app_vars

if TYPE_CHECKING:
    from bot.TeamTalk.structs import User


class HelpCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate("Shows command help")

    def __call__(self, arg: str, user: User) -> Optional[str]:
        return self.command_processor.help(arg, user)

class TimeCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate(
            "Shows the elapsed and total time of the playing stream"
        )

    def __call__(self, arg: str, user: User) -> Optional[str]:

        if self.player.state.name != "Playing" and self.player.state.name != "Paused":
            self.ttclient.send_message(self.translator.translate("Nothing is being played."), user)
            return None

        current = self.player._player.time_pos or 0
        total = self.player._player.duration or 0

        def format_seconds(seconds):
            h = int(seconds) // 3600
            m = (int(seconds) % 3600) // 60
            s = int(seconds) % 60
            return f"{h:02}:{m:02}:{s:02}"

        message = self.translator.translate(
            "{current}" if total <= 0 else "{current} de {total}"
        ).format(
            current=format_seconds(current),
            total=format_seconds(total),
        )

        self.ttclient.send_message(message, user)
        return None


class TimeRemainingCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate(
            "Shows the remaining time of the playing stream"
        )

    def __call__(self, arg: str, user: User) -> Optional[str]:

        if self.player.state.name != "Playing" and self.player.state.name != "Paused":
            self.ttclient.send_message(
                self.translator.translate("Nothing is being played."), user
            )
            return None

        current = self.player._player.time_pos or 0
        total = self.player._player.duration or 0
        remaining = max(total - current, 0) if total > 0 else 0

        def format_seconds(seconds):
            h = int(seconds) // 3600
            m = (int(seconds) % 3600) // 60
            s = int(seconds) % 60
            return f"{h:02}:{m:02}:{s:02}"

        message = format_seconds(remaining)

        self.ttclient.send_message(message, user)
        return None

class EnablePositionsCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate("Toggles saving playback position on pause/stop for resumable tracks")

    def __call__(self, arg: str, user: User) -> Optional[str]:
        self.config.general.enable_positions = not self.config.general.enable_positions
        return (
            self.translator.translate("Position saving enabled")
            if self.config.general.enable_positions
            else self.translator.translate("Position saving disabled")
        )

class AboutCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate("Shows information about the bot")

    def __call__(self, arg: str, user: User) -> Optional[str]:
        return app_vars.client_name + "\n" + app_vars.about_text(self.translator)


class PlayPauseCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate(
            "QUERY Plays tracks found for the query. If no query is given, plays or pauses current track"
        )

    def __call__(self, arg: str, user: User) -> Optional[str]:
        if arg:
            if self.player.mode == Mode.Queue:
                self.run_async(
                    self.ttclient.send_message,
                    self.translator.translate("Searching..."),
                    user,
                )
                try:
                    track_list = self.service_manager.service.search(arg)
                    if not track_list:
                        raise errors.NothingFoundError()
                    track = track_list[0].get_raw()
                    self.cache.add_to_queue(track)
                    self.cache_manager.save()
                    if self.config.general.send_channel_messages:
                        self.run_async(
                            self.ttclient.send_message,
                            self.translator.translate(
                                "{nickname} added to the queue: {request}"
                            ).format(nickname=user.nickname, request=arg),
                            type=2,
                        )
                    if self.player.state == State.Stopped:
                        self.player.play_queue()
                        return self.translator.translate("Playing {}").format(
                            track.name if track.name else track.url
                        )
                    return self.translator.translate("Added to queue")
                except errors.NothingFoundError:
                    return self.translator.translate("Nothing is found for your query")
                except errors.ServiceError:
                    return self.translator.translate(
                        "The selected service is currently unavailable"
                    )
            self.run_async(
                self.ttclient.send_message,
                self.translator.translate("Searching..."),
                user,
            )
            try:
                track_list = self.service_manager.service.search(arg)
                if self.config.general.send_channel_messages:
                    self.run_async(
                        self.ttclient.send_message,
                        self.translator.translate(
                            "{nickname} requested {request}"
                        ).format(nickname=user.nickname, request=arg),
                        type=2,
                    )
                self.run_async(self.player.play, track_list)
                return self.translator.translate("Playing {}").format(
                    track_list[0].name
                )
            except errors.NothingFoundError:
                return self.translator.translate("Nothing is found for your query")
            except errors.ServiceError:
                return self.translator.translate(
                    "The selected service is currently unavailable"
                )
        else:
            if self.player.state == State.Playing:
                self._save_current_position()
                self.run_async(self.player.pause)
            elif self.player.state == State.Paused:
                self.run_async(self.player.play)


class PlayUrlCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate("URL Plays a stream from a given URL")

    def __call__(self, arg: str, user: User) -> Optional[str]:
        if arg:
            try:
                tracks = self.module_manager.streamer.get(arg, user.is_admin)
                if self.player.mode == Mode.Queue:
                    # Converter tracks para raw e adicionar de uma vez
                    raw_tracks = [track.get_raw() for track in tracks]
                    self.cache.extend_queue(raw_tracks)
                    self.cache_manager.save()
                    if self.config.general.send_channel_messages:
                        self.run_async(
                            self.ttclient.send_message,
                            self.translator.translate(
                                "{nickname} added to the queue: {request}"
                            ).format(nickname=user.nickname, request=arg),
                            type=2,
                        )
                    if self.player.state == State.Stopped:
                        self.player.play_queue()
                        return self.translator.translate("Playing {}").format(
                            tracks[0].name if tracks[0].name else tracks[0].url
                        )
                    return self.translator.translate("Added to queue")
                if self.config.general.send_channel_messages:
                    self.run_async(
                        self.ttclient.send_message,
                        self.translator.translate(
                            "{nickname} requested playing from a URL"
                        ).format(nickname=user.nickname),
                        type=2,
                    )
                self.run_async(self.player.play, tracks)
            except errors.IncorrectProtocolError:
                return self.translator.translate("Incorrect protocol")
            except errors.ServiceError:
                return self.translator.translate("Cannot process stream URL")
            except errors.PathNotFoundError:
                return self.translator.translate("The path cannot be found")
        else:
            raise errors.InvalidArgumentError


class StopCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate("Stops playback")

    def __call__(self, arg: str, user: User) -> Optional[str]:
        if self.player.state != State.Stopped:
            self._save_current_position()
            self.player.stop()
            if self.config.general.send_channel_messages:
                self.ttclient.send_message(
                    self.translator.translate("{nickname} stopped playback").format(
                        nickname=user.nickname
                    ),
                    type=2,
                )
        else:
            return self.translator.translate("Nothing is playing")


class VolumeCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate(
            "VOLUME Sets the volume to a value between 0 and {max_volume}. If no volume is specified, the current volume level is displayed"
        ).format(max_volume=self.config.player.max_volume)

    def __call__(self, arg: str, user: User) -> Optional[str]:
        if arg:
            try:
                volume = int(arg)
                if 0 <= volume <= self.config.player.max_volume:
                    self.player.set_volume(int(arg))
                else:
                    raise ValueError
            except ValueError:
                raise errors.InvalidArgumentError
        else:
            return str(self.player.volume)


class MuteCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate("Toggles mute")

    def __call__(self, arg: str, user: User) -> Optional[str]:
        try:
            self.player._player.mute = not bool(self.player._player.mute)
        except Exception:
            self.player._player.mute = True
        return (
            self.translator.translate("Muted")
            if self.player._player.mute
            else self.translator.translate("Unmuted")
        )


class SeekBackCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate(
            "STEP Seeks current track backward. the default step is {seek_step} seconds"
        ).format(seek_step=self.config.player.seek_step)

    def __call__(self, arg: str, user: User) -> Optional[str]:
        if self.player.state == State.Stopped:
            return self.translator.translate("Nothing is playing")
        if arg:
            try:
                self.player.seek_back(float(arg))
            except ValueError:
                raise errors.InvalidArgumentError
        else:
            self.player.seek_back()


class SeekForwardCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate(
            "STEP Seeks current track forward. the default step is {seek_step} seconds"
        ).format(seek_step=self.config.player.seek_step)

    def __call__(self, arg: str, user: User) -> Optional[str]:
        if self.player.state == State.Stopped:
            return self.translator.translate("Nothing is playing")
        if arg:
            try:
                self.player.seek_forward(float(arg))
            except ValueError:
                raise errors.InvalidArgumentError
        else:
            self.player.seek_forward()


class NextTrackCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate("Plays next track")

    def __call__(self, arg: str, user: User) -> Optional[str]:
        try:
            self.player.next()
            return self.translator.translate("Playing {}").format(
                self.player.track.name
            )
        except errors.NoNextTrackError:
            return self.translator.translate("No next track")
        except errors.NothingIsPlayingError:
            return self.translator.translate("Nothing is playing")


class PreviousTrackCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate("Plays previous track")

    def __call__(self, arg: str, user: User) -> Optional[str]:
        try:
            self.player.previous()
            return self.translator.translate("Playing {}").format(
                self.player.track.name
            )
        except errors.NoPreviousTrackError:
            return self.translator.translate("No previous track")
        except errors.NothingIsPlayingError:
            return self.translator.translate("Nothing is playing")


class ModeCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate(
            "MODE Sets the playback mode. If no mode is specified, the current mode and a list of modes are displayed"
        )

    def __call__(self, arg: str, user: User) -> Optional[str]:
        self.mode_names = {
            Mode.SingleTrack: self.translator.translate("Single Track"),
            Mode.RepeatTrack: self.translator.translate("Repeat Track"),
            Mode.TrackList: self.translator.translate("Track list"),
            Mode.RepeatTrackList: self.translator.translate("Repeat track list"),
            Mode.Random: self.translator.translate("Random"),
            Mode.Queue: self.translator.translate("Queue"),
        }
        mode_help = self.translator.translate(
            "Current mode: {current_mode}\n{modes}"
        ).format(
            current_mode=self.mode_names[self.player.mode],
            modes="\n".join(
                [
                    "{value} {name}".format(name=self.mode_names[i], value=i.value)
                    for i in Mode.__members__.values()
                ]
            ),
        )
        if arg:
            try:
                mode = Mode(arg.lower())
                if mode == Mode.Random:
                    self.player.shuffle(True)
                if self.player.mode == Mode.Random and mode != Mode.Random:
                    self.player.shuffle(False)
                if self.player.mode == Mode.Queue and mode != Mode.Queue:
                    self.player._queue_active_track = False
                self.player.mode = Mode(mode)
                if (
                    self.player.mode == Mode.Queue
                    and self.player.state == State.Stopped
                    and self.cache.queue
                ):
                    self.player.play_queue()
                return self.translator.translate("Current mode: {mode}").format(
                    mode=self.mode_names[self.player.mode]
                )
            except ValueError:
                return "Incorrect mode\n" + mode_help
        else:
            return mode_help


class ServiceCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate(
            "SERVICE Selects the service to play from, sv SERVICE h returns additional help. If no service is specified, the current service and a list of available services are displayed"
        )

    def __call__(self, arg: str, user: User) -> Optional[str]:
        args = arg.split(" ")
        if args[0]:
            service_name = args[0].lower()
            if service_name not in self.service_manager.services:
                return self.translator.translate("Unknown service.\n{}").format(
                    self.service_help
                )
            service = self.service_manager.services[service_name]
            if len(args) == 1:
                if not service.hidden and service.is_enabled:
                    self.service_manager.service = service
                    if service.warning_message:
                        return self.translator.translate(
                            "Current service: {}\nWarning: {}"
                        ).format(service.name, service.warning_message)
                    return self.translator.translate("Current service: {}").format(
                        service.name
                    )
                elif not service.is_enabled:
                    if service.error_message:
                        return self.translator.translate(
                            "Error: {error}\n{service} is disabled".format(
                                error=service.error_message,
                                service=service.name,
                            )
                        )
                    else:
                        return self.translator.translate(
                            "{service} is disabled".format(service=service.name)
                        )
            elif len(args) >= 1:
                if service.help:
                    return service.help
                else:
                    return self.translator.translate(
                        "This service has no additional help"
                    )
        else:
            return self.service_help

    @property
    def service_help(self):
        services: List[str] = []
        for i in self.service_manager.services:
            service = self.service_manager.services[i]
            if not service.is_enabled:
                if service.error_message:
                    services.append(
                        "{} (Error: {})".format(service.name, service.error_message)
                    )
                else:
                    services.append("{} (Error)".format(service.name))
            elif service.warning_message:
                services.append(
                    self.translator.translate("{} (Warning: {})").format(
                        service.name, service.warning_message
                    )
                )
            else:
                services.append(service.name)
        help = self.translator.translate(
            "Current service: {current_service}\nAvailable:\n{available_services}\nsend sv SERVICE h for additional help"
        ).format(
            current_service=self.service_manager.service.name,
            available_services="\n".join(services),
        )
        return help


class SelectTrackCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate(
            "NUMBER Selects track by number from the list of current results"
        )

    def __call__(self, arg: str, user: User) -> Optional[str]:
        if arg:
            try:
                number = int(arg)
                if number > 0:
                    index = number - 1
                elif number < 0:
                    index = number
                else:
                    return self.translator.translate("Incorrect number")
                self.player.play_by_index(index)
                return self.translator.translate("Playing {} {}").format(
                    arg, self.player.track.name
                )
            except errors.IncorrectTrackIndexError:
                return self.translator.translate("Out of list")
            except errors.NothingIsPlayingError:
                return self.translator.translate("Nothing is playing")
            except ValueError:
                raise errors.InvalidArgumentError
        else:
            if self.player.state != State.Stopped:
                return self.translator.translate("Playing {} {}").format(
                    self.player.track_index + 1, self.player.track.name
                )
            else:
                return self.translator.translate("Nothing is playing")


class SpeedCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate(
            "SPEED Sets playback speed from 0.25 to 4. If no speed is given, shows current speed"
        )

    def __call__(self, arg: str, user: User) -> Optional[str]:
        if not arg:
            return self.translator.translate("Current rate: {}").format(
                str(self.player.get_speed())
            )
        else:
            try:
                self.player.set_speed(float(arg))
            except ValueError:
                raise errors.InvalidArgumentError()


class BassBoostCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate(
            "LEVEL Sets bass boost level from 0 (disabled) to 100"
        )

    def __call__(self, arg: str, user: User) -> Optional[str]:
        if not arg:
            return self.translator.translate("Current bass boost: {level}").format(
                level=self.player.bass_boost_level
            )
        try:
            level = int(arg)
            self.player.set_bass_boost(level)
            return self.translator.translate("Bass boost set to {level}").format(
                level=level
            )
        except ValueError:
            raise errors.InvalidArgumentError()
        except errors.ServiceError:
            return self.translator.translate("Cannot set bass boost")


class PitchCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate(
            "SEMITONES Sets pitch from -12 to +12 semitones (one octave). 0 disables pitch shift"
        )

    def __call__(self, arg: str, user: User) -> Optional[str]:
        if not arg:
            return self.translator.translate("Current pitch: {semitons} semitones").format(
                semitons=self.player.get_pitch()
            )
        try:
            semitons = int(arg)
            self.player.set_pitch(semitons)
            if semitons == 0:
                return self.translator.translate("Pitch shift disabled")
            else:
                return self.translator.translate("Pitch set to {semitons} semitones").format(
                    semitons=semitons
                )
        except ValueError:
            raise errors.InvalidArgumentError()


class FavoritesCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate(
            "+/-NUMBER Manages favorite tracks. + adds the current track to favorites. - removes a track requested from favorites. If a number is specified after +/-, adds/removes a track with that number"
        )

    def __call__(self, arg: str, user: User) -> Optional[str]:
        if user.username == "":
            return self.translator.translate(
                "This command is not available for guest users"
            )
        if arg:
            if arg[0] == "+":
                return self._add(user)
            elif arg[0] == "-":
                return self._del(arg, user)
            else:
                return self._play(arg, user)
        else:
            return self._list(user)

    def _add(self, user: User) -> str:
        if self.player.state != State.Stopped:
            if user.username in self.cache.favorites:
                self.cache.favorites[user.username].append(self.player.track.get_raw())
            else:
                self.cache.favorites[user.username] = [self.player.track.get_raw()]
            self.cache_manager.save()
            return self.translator.translate("Added")
        else:
            return self.translator.translate("Nothing is playing")

    def _del(self, arg: str, user: User) -> str:
        if (self.player.state != State.Stopped and len(arg) == 1) or len(arg) > 1:
            try:
                if len(arg) == 1:
                    self.cache.favorites[user.username].remove(self.player.track)
                else:
                    del self.cache.favorites[user.username][int(arg[1::]) - 1]
                self.cache_manager.save()
                return self.translator.translate("Deleted")
            except IndexError:
                return self.translator.translate("Out of list")
            except ValueError:
                if not arg[1::].isdigit:
                    return self.help
                return self.translator.translate("This track is not in favorites")
        else:
            return self.translator.translate("Nothing is playing")

    def _list(self, user: User) -> str:
        track_names: List[str] = []
        try:
            for number, track in enumerate(self.cache.favorites[user.username]):
                track_names.append(
                    "{number}: {track_name}".format(
                        number=number + 1,
                        track_name=track.name if track.name else track.url,
                    )
                )
        except KeyError:
            pass
        if len(track_names) > 0:
            return "\n".join(track_names)
        else:
            return self.translator.translate("The list is empty")

    def _play(self, arg: str, user: User) -> Optional[str]:
        try:
            self.player.play(
                self.cache.favorites[user.username], start_track_index=int(arg) - 1
            )
        except ValueError:
            raise errors.InvalidArgumentError()
        except IndexError:
            return self.translator.translate("Out of list")
        except KeyError:
            return self.translator.translate("The list is empty")


class QueueCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate(
            "Manages the playback queue. q + adds the current track, q -NUMBER removes by number, q c clears the queue, without arguments shows the queue"
        )

    def __call__(self, arg: str, user: User) -> Optional[str]:
        if arg:
            if arg == "c":
                self.cache.queue.clear()
                self.cache_manager.save()
                self.player._queue_active_track = False
                return self.translator.translate("Queue cleared")
            if arg[0] == "+":
                return self._add_current()
            elif arg[0] == "-":
                return self._remove(arg)
            else:
                raise errors.InvalidArgumentError
        else:
            return self._list()

    def _auto_start_queue(self) -> None:
        if self.player.mode == Mode.Queue and self.player.state == State.Stopped:
            try:
                self.player.play_queue()
            except (errors.NothingIsPlayingError, errors.NoNextTrackError):
                pass

    def _add_current(self) -> str:
        if self.player.state == State.Stopped:
            return self.translator.translate("Nothing is playing")
        self.cache.queue.append(self.player.track.get_raw())
        self.cache_manager.save()
        self._auto_start_queue()
        return self.translator.translate("Added to queue")

    def _remove(self, arg: str) -> str:
        if len(arg) == 1:
            if self.cache.queue:
                if (
                    self.player.mode == Mode.Queue
                    and self.player.state != State.Stopped
                    and self.player._queue_active_track
                ):
                    try:
                        self.player.next()
                    except errors.NoNextTrackError:
                        self.player.stop()
                else:
                    del self.cache.queue[0]
                    self.cache_manager.save()
                return self.translator.translate("Deleted")
            else:
                return self.translator.translate("The list is empty")
        try:
            index = int(arg[1::]) - 1
            del self.cache.queue[index]
            self.cache_manager.save()
            return self.translator.translate("Deleted")
        except (ValueError, IndexError):
            return self.translator.translate("Out of list")

    def _list(self) -> str:
        track_names: List[str] = []
        for number, track in enumerate(self.cache.queue):
            track_names.append(
                "{number}: {track_name}".format(
                    number=number + 1, track_name=track.name if track.name else track.url
                )
            )
        if len(track_names) > 0:
            return "\n".join(track_names)
        else:
            return self.translator.translate("The list is empty")


class GetLinkCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate("Gets a direct link to the current track")

    def __call__(self, arg: str, user: User) -> Optional[str]:
        if self.player.state != State.Stopped:
            url = self.player.track.url
            if url:
                shortener = self.module_manager.shortener
                return shortener.get(url) if shortener else url
            else:
                return self.translator.translate("URL is not available")
        else:
            return self.translator.translate("Nothing is playing")

class MoveUsersCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate(
            'Move the bot in your channel.'
        )

    def __call__(self, arg: str, user: User) -> Optional[str]:
        if not self.config.general.back_to_root_channel: return self.translator.translate("Option disabled for this bot.")
        if user.channel.id == self.ttclient.channel.id:return self.translator.translate("I'm already on this channel.")
        users = self.ttclient.tt.getChannelUsers(user.channel.id)
        can_move = True
        for user_entry in users:
            if sys.version_info < (3, 11):
                if "TTMediaBot" in user_entry.szClientName:
                    can_move = False
                    break
            else:
                if bytes("TTMediaBot", 'utf-8') in user_entry.szClientName:
                    can_move = False
                    break
        if not can_move:
            return self.translator.translate("There is already a bot on this channel.")
        if self.ttclient.channel.id != self.config.general.root_channel_id:
            return self.translator.translate("I'm not on the root channel.")
        self.ttclient.DoMoveUser(self.ttclient.user.id, user.channel.id)
        return self.translator.translate("Ready, I'm at your disposal. But remember. If there are no users in the channel other than me, I'll go back to the home channel.")

class RecentsCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate(
            "NUMBER Plays a track with  the given number from a list of recent tracks. Without a number shows recent tracks"
        )

    def __call__(self, arg: str, user: User) -> Optional[str]:
        if arg:
            try:
                recents_list = list(reversed(list(self.cache.recents)))
                start_index = int(arg) - 1
                self.player.play(recents_list, start_track_index=start_index)
                if (
                    self.config.general.enable_positions
                    and 0 <= start_index < len(recents_list)
                ):
                    track = recents_list[start_index]
                    if (
                        track.resume_position
                        and track.type not in (TrackType.Live,)
                        and track.resume_position > 0
                        and (
                            not track.resume_duration
                            or track.resume_position < track.resume_duration
                        )
                    ):
                        seek_pos = track.resume_position
                        self.run_async(self._seek_with_delay, seek_pos)
            except ValueError:
                raise errors.InvalidArgumentError()
            except IndexError:
                return self.translator.translate("Out of list")
        else:
            track_names: List[str] = []
            for number, track in enumerate(reversed(self.cache.recents)):
                if track.name:
                    track_names.append(f"{number + 1}: {track.name}")
                else:
                    track_names.append(f"{number + 1}: {track.url}")
            return (
                "\n".join(track_names)
                if track_names
                else self.translator.translate("The list is empty")
            )

    def _seek_with_delay(self, position: float) -> None:
        # Ensure playback actually starts before seeking
        for _ in range(10):
            if self.player.state == State.Playing and self.player._player.time_pos is not None:
                break
            time.sleep(0.2)
        try:
            self.player.seek_absolute(position)
        except Exception:
            pass


class DownloadCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate(
            "Downloads the current track and uploads it to the channel."
        )

    def __call__(self, arg: str, user: User) -> Optional[str]:
        if not (
            self.ttclient.user.user_account.rights & UserRight.UploadFiles
            == UserRight.UploadFiles
        ):
            raise PermissionError(
                self.translator.translate("Cannot upload file to channel")
            )
        if self.player.state != State.Stopped:
            track = self.player.track
            if track.url and (
                track.type == TrackType.Default or track.type == TrackType.Local
            ):
                self.module_manager.uploader(self.player.track, user)
                return self.translator.translate("Downloading...")
            else:
                return self.translator.translate("Live streams cannot be downloaded")
        else:
            return self.translator.translate("Nothing is playing")
