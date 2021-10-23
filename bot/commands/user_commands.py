from bot.commands.command import Command
from bot.player.enums import Mode, State, TrackType
from bot.TeamTalk.structs import UserRight
from bot import errors, vars


class HelpCommand(Command):
    @property
    def help(self):
        return _('Shows command help')

    def __call__(self, arg, user):
        return self.command_processor.help(arg, user)


class AboutCommand(Command):
    @property
    def help(self):
        return _('Shows information about the bot')

    def __call__(self, arg, user):
        return vars.client_name + '\n' + vars.about_text()


class PlayPauseCommand(Command):
    @property
    def help(self):
        return _('QUERY Plays tracks found for the query. If no query is given, plays or pauses current track')

    def __call__(self, arg, user):
        if arg:
            self.ttclient.send_message(_('Searching...'), user)
            try:
                track_list = self.service_manager.service.search(arg)
                if self.command_processor.send_channel_messages:
                    self.ttclient.send_message(_("{nickname} requested {request}").format(nickname=user.nickname, request=arg), type=2)
                self.player.play(track_list)
                return _('Playing {}').format(self.player.track.name)
            except errors.NothingFoundError:
                return _('Nothing is found for your query')
            except errors.ServiceError:
                return _('The selected service is currently unavailable')
        else:
            if self.player.state == State.Playing:
                self.player.pause()
            elif self.player.state == State.Paused:
                self.player.play()


class PlayUrlCommand(Command):
    @property
    def help(self):
        return _('URL Plays a stream from a given URL')

    def __call__(self, arg, user):
        if arg:
            try:
                tracks = self.module_manager.streamer.get(arg, user.is_admin)
                if self.command_processor.send_channel_messages:
                    self.ttclient.send_message(_('{nickname} requested playing from a URL').format(nickname=user.nickname), type=2)
                self.player.play(tracks)
            except errors.IncorrectProtocolError:
                return _('Incorrect protocol')
            except errors.ServiceError:
                return _('Cannot process stream URL')
            except errors.PathNotFoundError:
                return _('The path cannot be found')
        else:
            raise errors.InvalidArgumentError


class StopCommand(Command):
    @property
    def help(self):
        return _('Stops playback')

    def __call__(self, arg, user):
        if self.player.state != State.Stopped:
            self.player.stop()
            if self.command_processor.send_channel_messages:
                self.ttclient.send_message(_("{nickname} stopped playback").format(nickname=user.nickname), type=2)
        else:
            return _('Nothing is playing')


class VolumeCommand(Command):
    @property
    def help(self):
        return _('VOLUME Sets the volume to a value between 0 and {max_volume}. If no volume is specified, the current volume level is displayed').format(max_volume=self.player.max_volume)

    def __call__(self, arg, user):
        if arg:
            try:
                volume = int(arg)
                if 0 <= volume <= self.player.max_volume:
                    self.player.set_volume(int(arg))
                else:
                    raise ValueError
            except ValueError:
                raise errors.InvalidArgumentError
        else:
            return str(self.player.volume)


class SeekBackCommand(Command):
    @property
    def help(self):
        return _('STEP Seeks current track backward. the default step is {seek_step} seconds').format(seek_step=self.player.seek_step)

    def __call__(self, arg, user):
        if self.player.state == State.Stopped:
            return _('Nothing is playing')
        if arg:
            try:
                self.player.seek_back(float(arg))
            except ValueError:
                raise errors.InvalidArgumentError
        else:
            self.player.seek_back()


class SeekForwardCommand(Command):
    @property
    def help(self):
        return _('STEP Seeks current track forward. the default step is {seek_step} seconds').format(seek_step=self.player.seek_step)

    def __call__(self, arg, user):
        if self.player.state == State.Stopped:
            return _('Nothing is playing')
        if arg:
            try:
                self.player.seek_forward(float(arg))
            except ValueError:
                raise errors.InvalidArgumentError
        else:
            self.player.seek_forward()


class NextTrackCommand(Command):
    @property
    def help(self):
        return _('Plays next track')

    def __call__(self, arg, user):
        try:
            self.player.next()
            return _('Playing {}').format(self.player.track.name)
        except errors.NoNextTrackError:
            return _('No next track')
        except errors.NothingIsPlayingError:
            return _('Nothing is playing')


class PreviousTrackCommand(Command):
    @property
    def help(self):
        return _('Plays previous track')

    def __call__(self, arg, user):
        try:
            self.player.previous()
            return _('Playing {}').format(self.player.track.name)
        except errors.NoPreviousTrackError:
            return _('No previous track')
        except errors.NothingIsPlayingError:
            return _('Nothing is playing')


class ModeCommand(Command):
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.mode_names = {Mode.SingleTrack: _('Single Track'), Mode.RepeatTrack: _('Repeat Track'), Mode.TrackList: _('Track list'), Mode.RepeatTrackList: _('Repeat track list'), Mode.Random: _('Random')}

    @property
    def help(self):
        return _('MODE Sets the playback mode. If no mode is specified, the current mode and a list of modes are displayed')

    def __call__(self, arg, user):
        mode_help = _("Current_ mode: {current_mode}\n{modes}").format(current_mode=self.mode_names[self.player.mode], modes='\n'.join(['{value} {name}'.format(name=self.mode_names[i], value=i.value) for i in Mode.__members__.values()]))
        if arg:
            try:
                mode = Mode(arg.lower())
                if mode == Mode .Random:
                    self.player.shuffle(True)
                if self.player.mode == Mode.Random and mode != Mode.Random:
                    self.player.shuffle(False)
                self.player.mode = Mode(mode)
                return _("Current mode: {mode}").format(mode=self.mode_names[self.player.mode])
            except ValueError:
                return 'Incorrect mode\n' + mode_help
        else:
            return mode_help


class ServiceCommand(Command):
    @property
    def help(self):
        return _('SERVICE Selects the service to play from. If no service is specified, the current service and a list of available services are displayed')

    def __call__(self, arg, user):
        service_help = _('Current service: {current_service}\nAvailable: {available_services}').format(current_service=self.service_manager.service.name, available_services=', '.join([i for i in self.service_manager.available_services if not self.service_manager.available_services[i].hidden]))
        if arg:
            arg = arg.lower()
            if arg in self.service_manager.available_services and not self.service_manager.available_services[arg].hidden:
                self.service_manager.service = self.service_manager.available_services[arg]
                return _('Current service: {}').format(self.service_manager.service.name)
            else:
                return _('Unknown service.\n{}').format(service_help)
        else:
            return service_help


class SelectTrackCommand(Command):
    @property
    def help(self):
        return _('NUMBER Selects track by number from the list of current results')

    def __call__(self, arg, user):
        if arg:
            try:
                number = int(arg)
                if number > 0:
                    index = number - 1
                elif number < 0:
                    index = number
                else:
                    return _('Incorrect number')
                self.player.play_by_index(index)
                return _('Playing {} {}').format(arg, self.player.track.name)
            except errors.IncorrectTrackIndexError:
                return _('Out of list')
            except errors.NothingIsPlayingError:
                return _('Nothing is playing')
            except ValueError:
                raise errors.InvalidArgumentError
        else:
            if self.player.state != State.Stopped:
                return _('Playing {} {}').format(self.player.track_index + 1, self.player.track.name)
            else:
                return _('Nothing is playing')


class SpeedCommand(Command):
    @property
    def help(self):
        return _("SPEED Sets playback speed from 0.25 to 4. If no speed is given, shows current speed")

    def __call__(self, arg, user):
        if not arg:
            return _("Current rate: {}").format(str(self.player.get_speed()))
        else:
            try:
                self.player.set_speed(float(arg))
            except ValueError:
                raise errors.InvalidArgumentError()


class FavoritesCommand(Command):
    @property
    def help(self):
        return _('+/-NUMBER Manages favorite tracks. + adds the current track to favorites. - removes a track requested from favorites. If a number is specified after +/-, adds/removes a track with that number')

    def __call__(self, arg, user):
        if user.username == '':
            return _('This command is not available for guest users')
        if arg:
            if arg[0] == '+':
                return self._add(user)
            elif arg[0] == '-':
                return self._del(arg, user)
            else:
                return self._play(arg, user)
        else:
            return self._list(user)

    def _add(self, user):
        if self.player.state != State.Stopped:
            if user.username in self.cache.favorites:
                self.cache.favorites[user.username].append(self.player.track.get_raw())
            else:
                self.cache.favorites[user.username] = [self.player.track.get_raw()]
            self.cache.save()
            return _('Added')
        else:
            return _('Nothing is playing')

    def _del(self, arg, user):
        if (self.player.state != State.Stopped and len(arg) == 1) or len(arg) > 1:
            try:
                if len(arg) == 1:
                    self.cache.favorites[user.username].remove(self.player.track)
                else:
                    del self.cache.favorites[user.username][int(arg[1::]) - 1]
                self.cache.save()
                return _('Deleted')
            except IndexError:
                return _('Out of list')
            except ValueError:
                if not arg[1::].isdigit:
                    return self.help
                return _('This track is not in favorites')
        else:
            return _('Nothing is playing')

    def _list(self, user):
        track_names = []
        try:
            for number, track in enumerate(self.cache.favorites[user.username]):
                track_names.append('{number}: {track_name}'.format(number=number + 1, track_name=track.name if track.name else track.url))
        except KeyError:
            pass
        if len(track_names) > 0:
            return '\n'.join(track_names)
        else:
            return _('List is empty')

    def _play(self, arg, user):
        try:
            self.player.play(self.cache.favorites[user.username], start_track_index=int(arg) - 1)
        except ValueError:
            return self.help
        except IndexError:
            return _('Out of list')
        except KeyError:
            return _('The list is is empty')


class GetLinkCommand(Command):
    @property
    def help(self):
        return _('Gets a direct link to the current track')

    def __call__(self, arg, user):
        if self.player.state != State.Stopped:
            url = self.player.track.url
            if url:
                return url
            else:
                return _('URL is not available')
        else:
            return _('Nothing is playing')


class RecentsCommand(Command):
    @property
    def help(self):
        return _('NUMBER Plays a track with  the given number from a list of recent tracks. Without a number shows recent tracks')

    def __call__(self, arg, user):
        if arg:
            try:
                self.player.play(list(reversed(list(self.cache.recents))), start_track_index=int(arg) - 1)
            except ValueError:
                raise errors.InvalidArgumentError()
            except IndexError:
                return _('Out of list')
        else:
            track_names = []
            for number, track in enumerate(reversed(self.cache.recents)):
                if track.name:
                    track_names.append(f'{number + 1}: {track.name}')
                else:
                    track_names.append(f'{number + 1}: {track.url}')
            return '\n'.join(track_names) if track_names else _('The list is empty')


class DownloadCommand(Command):
    @property
    def help(self):
        return _("Downloads the current track and uploads it to the channel")

    def __call__(self, arg, user):
        if not (self.ttclient.user.user_account.rights & UserRight.UploadFiles == UserRight.UploadFiles):
            raise PermissionError(_("Cannot upload file to channel"))
        if self.player.state != State.Stopped:
            track = self.player.track
            if track.url and (track.type == TrackType.Default or track.type == TrackType.Local):
                self.module_manager.downloader(self.player.track, user)
                return _("Downloading...")
            else:
                return _('Live streams cannot be downloaded')
        else:
            return _('Nothing is playing')
