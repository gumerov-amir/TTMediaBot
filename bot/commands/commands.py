import _thread

from bot.player.enums import Mode, State
from bot import errors


class Command:
    def __init__(self, command_processor):
        self.player = command_processor.player
        self.ttclient = command_processor.ttclient
        self.service_manager = command_processor.service_manager
        self.module_manager = command_processor.module_manager


class HelpCommand(Command):
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.command_processor = command_processor
        self.help = _('Shows command help')

    def __call__(self, arg, user):
        return self.command_processor.help(arg, user)


class AboutCommand(Command):
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.help = _('Shows information about this bot')

    def __call__(self, arg, user):
        about_text = _('')
        return about_text


class PlayPauseCommand(Command):
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.help = _('QUERY Plays tracks found for the query. If no query is given plays or pauses current track')

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
            except errors.SearchError:
                return _('Unable to perform a search. Please try again')
        else:
            if self.player.state == State.Playing:
                self.player.pause()
            elif self.player.state == State.Paused:
                self.player.play()


class RateCommand(Command):
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.help = _('RATE Sets rate to a value from 0.25 to 4. If no rate is given shows current rate')

    def __call__(self, arg, user):
        if arg:
            try:
                rate_number = abs(float(arg))
                if rate_number >= 0.25 and rate_number <= 4:
                    self.player.set_rate(rate_number)
                else:
                    raise ValueError
            except ValueError:
                raise errors.InvalidArgumentError
        else:
            return str(self.player.get_rate())


class PlayUrlCommand(Command):
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.help = _('URL Plays a stream from a given URL')

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
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.help = _('Stops playback')

    def __call__(self, arg, user):
        if self.player.state != State.Stopped:
            self.player.stop()
            self.ttclient.send_message(_("{nickname} stopped playback").format(nickname=user.nickname), type=2)
        else:
            return _('Nothing is playing')


class VolumeCommand(Command):
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.help = _('VOLUME Sets volume to a value from 0 to {max_volume}').format(max_volume=self.player.max_volume)

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
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.help = _('[STEP] Seeks current track back. the optional step is specified in percents from 1 to 100')

    def __call__(self, arg, user):
        if arg:
            try:
                self.player.seek_back(float(arg))
            except ValueError:
                raise errors.InvalidArgumentError
        else:
            self.player.seek_back()


class SeekForwardCommand(Command):
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.help = _('[STEP] Seeks current track forward. the optional step is specified in percents from 1 to 100')

    def __call__(self, arg, user):
        if arg:
            try:
                self.player.seek_forward(float(arg))
            except ValueError:
                raise errors.InvalidArgumentError
        else:
            self.player.seek_forward()


class NextTrackCommand(Command):
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.help = _('Plays next track')

    def __call__(self, arg, user):
        try:
            self.player.next()
            return _('Playing {}').format(self.player.track.name)
        except errors.NoNextTrackError:
            return _('No next track')
        except errors.NothingIsPlayingError:
            return _('Nothing is currently playing')


class PreviousTrackCommand(Command):
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.help = _('Plays previous track')

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
        self.help = ('MODE Sets playback mode. If no MODE is given shows a list of modes')
        self.mode_names = {Mode.SingleTrack: _('Single Track'), Mode.RepeatTrack: _('Repeat Track'), Mode.TrackList: _('Track list'), Mode.RepeatTrackList: _('Repeat track list'), Mode.Random: _('Random')}

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
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.help = _('SERVICE Selects a service to play from. If no service is given shows current service and a list of available ones')

    def __call__(self, arg, user):
        service_help = 'Current service: {current_service}\nAvailable: {available_services}'.format(current_service=self.service_manager.service.name, available_services=', '.join([i for i in self.service_manager.available_services]))
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
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.help = _('NUMBER Selects track by number from the list of current results')

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
            if self.player.state == State.Playing:
                return _('Playing {} {}').format(self.player.track_index + 1, self.player.track.name)
            else:
                return _('Nothing is currently playing')


class GetLinkCommand(Command):
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.help = _('Gets a direct link to the current track')

    def __call__(self, arg, user):
        if self.player.state != State.Stopped:
            url = self.player.track.url
            if url:
                return url
            else:
                return _('URL is not available')
        else:
            return _('Nothing is currently playing')


class ChangeNicknameCommand(Command):
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.help = _('NICKNAME Sets the bot\'s nickname')

    def __call__(self, arg, user):
        self.ttclient.change_nickname(arg)


class PositionCommand(Command):
    def __init__(self, command_processor):
        super().__init__(command_processor)

    def __call__(self, arg, user):
        if arg:
            try:
                self.player.set_position(float(arg))
            except errors.IncorrectPositionError:
                return _('Incorrect position')
            except ValueError:
                return _('Must be integer')
        else:
            try:
                return str(round(self.player.get_position(), 2))
            except errors.NothingIsPlayingError:
                return _('Nothing is currently playing')

class VoiceTransmissionCommand(Command):
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.help = _('Enables or disables voice transmission')

    def __call__(self, arg, user):
        if not self.ttclient.is_voice_transmission_enabled:
            self.ttclient.enable_voice_transmission()
            if self.player.state == State.Stopped:
                self.ttclient.change_status_text(_('Voice transmission enabled'))
            return _('Voice transmission enabled')
        else:
            self.ttclient.disable_voice_transmission()
            if self.player.state == State.Stopped:
                self.ttclient.change_status_text('')
            return _('Voice transmission disabled')


class LockCommand(Command):
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.command_processor = command_processor
        self.help = _('Locks or unlocks the bot')

    def __call__(self, arg, user):
        return self.command_processor.lock(arg, user)



class ChangeStatusCommand(Command):
    def __init__(self, command_processor):
        super().__init__(command_processor)

    def __call__(self, arg, user):
        self.ttclient.change_status_text(arg)

class QuitCommand(Command):
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.help = _('Quits the bot')

    def __call__(self, arg, user):
        _thread.interrupt_main()
