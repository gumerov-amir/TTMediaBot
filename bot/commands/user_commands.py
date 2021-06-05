from bot.commands.command import Command
from bot.player.enums import Mode, State
from bot import errors


class HelpCommand(Command):
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.command_processor = command_processor

    @property
    def help(self):
        return _('Shows command help')

    def __call__(self, arg, user):
        return self.command_processor.help(arg, user)


class AboutCommand(Command):
    @property
    def help(self):
        return _('Shows information about this bot')

    def __call__(self, arg, user):
        about_text = _('')
        return about_text


class PlayPauseCommand(Command):
    @property
    def help(self):
        return _('QUERY Plays tracks found for the query. If no query is given plays or pauses current track')

    def __call__(self, arg, user):
        if arg:
            self.ttclient.send_message(_('Searching...'), user)
            try:
                track_list = self.service_manager.service.search(arg)
                self.ttclient.send_message(_("{nickname} requested {request}").format(nickname=user.nickname, request=arg), type=2)
                self.player.play(track_list)
                return _('Playing {}').format(self.player.track.name)
            except errors.NothingFoundError:
                return _('Nothing is found for your query')
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
                self.ttclient.send_message(_('{nickname} requested playing from a URL').format(nickname=user.nickname), type=2)
                self.player.play(tracks)
            except errors.IncorrectProtocolError:
                return _('Incorrect protocol')
            except errors.ServiceError:
                return _('Cannot get stream URL')
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
            self.ttclient.send_message(_("{nickname} stopped playback").format(nickname=user.nickname), type=2)
        else:
            return _('Nothing is playing')


class VolumeCommand(Command):
    @property
    def help(self):
        return _('VOLUME Sets volume to a value from 0 to {max_volume}').format(max_volume=self.player.max_volume)

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
        return _('[STEP] Seeks current track back. the optional step is specified in percents from 1 to 100')

    def __call__(self, arg, user):
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
        return _('[STEP] Seeks current track forward. the optional step is specified in percents from 1 to 100')

    def __call__(self, arg, user):
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
            return _('Nothing is currently playing')


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
        return _('MODE Sets playback mode. If no MODE is given shows a list of modes')

    def __call__(self, arg, user):
        mode_help = 'current_ mode: {current_mode}\n{modes}'.format(current_mode=self.mode_names[self.player.mode], modes='\n'.join(['{value} {name}'.format(name=self.mode_names[i], value=i.value) for i in Mode.__members__.values()]))
        if arg:
            try:
                mode = Mode(arg.lower())
                self.player.mode = Mode(mode)
                return 'Current mode: {mode}'.format(mode=self.mode_names[self.player.mode])
            except ValueError:
                return 'Incorrect mode\n' + mode_help
        else:
            return mode_help


class ServiceCommand(Command):
    @property
    def help(self):
        return _('SERVICE Selects a service to play from. If no service is given shows current service and a list of available ones')

    def __call__(self, arg, user):
        service_help = _('Current service: {current_service}\nAvailable: {available_services}').format(current_service=self.service_manager.service.name, available_services=', '.join([i for i in self.service_manager.available_services]))
        if arg:
            arg = arg.lower()
            if arg in self.service_manager.available_services:
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
                return _('Nothing is currently playing')
            except ValueError:
                raise errors.InvalidArgumentError
        else:
            if self.player.state != State.Stopped:
                return _('Playing {} {}').format(self.player.track_index + 1, self.player.track.name)
            else:
                return _('Nothing is currently playing')


class FavoritesCommand(Command):
    @property
    def help(self):
        return _('returns list of favorites tracks, number is given plays from track under this number in favorites')

    def __call__(self, arg, user):
        if user.username == '':
            return _('Sorry, guest users can not use this command')
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
                self.cache.favorites[user.username].append(self.player.track)
            else:
                self.cache.favorites[user.username] = [self.player.track]
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
            return _('List is empty')


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
            return _('Nothing is currently playing')


class HistoryCommand(Command):
    @property
    def help(self):
        return _('shows history of playing (64 last tracks)')

    def __call__(self, arg, user):
        if arg:
            try:
                self.player.play(list(reversed(list(self.cache.history))), start_track_index=int(arg) - 1)
            except ValueError:
                return _('must be integer')
            except IndexError:
                return _('Out of list')
        else:
            track_names = []
            for number, track in enumerate(reversed(self.cache.history)):
                if track.name:
                    track_names.append(f'{number + 1}: {track.name}')
                else:
                    track_names.append(f'{number + 1}: {track.url}')
            return '\n'.join(track_names) if track_names else _('List is empty')
