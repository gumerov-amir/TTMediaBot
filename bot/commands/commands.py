from bot.player.enums import Mode, State
from bot import errors


class Command:
    def __init__(self, command_processor):
        self.player = command_processor.player
        self.ttclient = command_processor.ttclient
        self.service_manager = command_processor.service_manager
        self.streamer = command_processor.streamer




class AboutCommand(Command):
    def __init__(self, command_processor):
        Command.__init__(self, command_processor)
        self.help = _('Return information about bot')

    def __call__(self, arg, user):
        return _('It is the best TeamTalk bot of all blind world')

class PlayPauseCommand(Command):
    def __init__(self, command_processor):
        Command.__init__(self, command_processor)
        self.help = _('Play first track from search by argument, if argument is not gived play or pause current track, if it is not stopped')


    def __call__(self, arg, user):
        if arg:
            self.ttclient.send_message(_('it is finding'), user)
            try:
                track_list = self.service_manager.service.search(arg)
                self.player.play(track_list)
                self.ttclient.send_message(_("{} offered {}").format(user.nickname, track_list[0].name), type=2)
                return _('Playing {}').format(track_list[0].name)
            except errors.NotFoundError:
                return _('not found')
        else:
            if self.player.state == State.Playing:
                self.player.pause()
            elif self.player.state == State.Paused:
                self.player.play()


class RateCommand(Command):
    def __init__(self, command_processor):
        Command.__init__(self, command_processor)
        self.help = _('Set rate from argument, if it is not gived, returns current rate')

    def __call__(self, arg, user):
        if arg:
            try:
                rate_number = abs(float(arg))
                if rate_number > 0 and rate_number <= 4:
                    self.player.set_rate(rate_number)
                else:
                    return _('Speed must be from 1 to 4')
            except ValueError:
                return _('Введите число, используйте .')
        else:
            return str(self.player.get_rate())


class PlayUrlCommand:
    def __init__(self, command_processor):
        Command.__init__(self, command_processor)

    def __call__(self, arg, user):
        if arg:
            try:
                tracks = self.streamer.get(arg, user.is_admin)
                self.player.play(tracks)
            except errors.IncorrectProtocolError:
                return _('Неверный протокол')
            except errors.PathNotExistError:
                return _('path not exist')
        else:
            return self.help()


class StopCommand:
    def __init__(self, command_processor):
        Command.__init__(self, command_processor)

    def __call__(self, arg, user):
        self.player.stop()


class VolumeCommand:
    def __init__(self, command_processor):
        Command.__init__(self, command_processor)

    def __call__(self, arg, user):
        if arg:
            try:
                volume = int(arg)
                if volume >= 0 and volume <= 100:
                    self.player.set_volume(int(arg))
                else:
                    return _('Громкость в диапозоне 1 100')
            except ValueError:
                return _('Недопустимое значение. Укажите число от 1 до 100.')
        else:
            return str(self.player.get_volume())


class SeekBackCommand:
    def __init__(self, command_processor):
        Command.__init__(self, command_processor)

    def __call__(self, arg, user):
        if arg:
            try:
                self.player.seek_back(float(arg))
            except ValueError:
                return _('Недопустимое значение. Укажите число от 1 до 100.')
        else:
            self.player.seek_back()


class SeekForwardCommand:
    def __init__(self, command_processor):
        Command.__init__(self, command_processor)

    def __call__(self, arg, user):
        if arg:
            try:
                self.player.seek_forward(float(arg))
            except ValueError:
                return _('Недопустимое значение. Укажите число от 1 до 100.')
        else:
            self.player.seek_forward()


class NextTrackCommand:
    def __init__(self, command_processor):
        Command.__init__(self, command_processor)

    def __call__(self, arg, user):
        try:
            self.player.next()
        except errors.NoNextTrackError:
            return _('это последний трек')
        except errors.NothingIsPlayingError:
            return _('Now nothing is playing')


class PreviousTrackCommand:
    def __init__(self, command_processor):
        Command.__init__(self, command_processor)

    def __call__(self, arg, user):
        try:
            self.player.previous()
        except errors.NoPreviousTrackError:
            return _('Это первый трек')
        except errors.NothingIsPlayingError:
            return _('Nothing is playing')


class ModeCommand:
    def __init__(self, command_processor):
        Command.__init__(self, command_processor)

    def __call__(self, arg, user):
        mode_help = 'current_ mode: {current_mode}\n{modes}'.format(current_mode=self.player.mode.name, modes='\n'.join(['{name} - {value}'.format(name=i.name, value=i.value) for i in [Mode.Single, Mode.TrackList, Mode.Random]]))
        if arg:
            try:
                mode = Mode(int(arg))
                self.player.mode = Mode(mode)
            except TypeError:
                return mode_help
        else:
            return mode_help


class ServiceCommand:
    def __init__(self, command_processor):
        Command.__init__(self, command_processor)

    def __call__(self, arg, user):
        service_help = 'current service: {current_service}\nevailable: {available_services}'.format(current_service=self.service_manager.service.name, available_services=', '.join([i for i in self.service_manager.available_services]))
        if arg:
            arg = arg.lower()
            if arg in self.service_manager.available_services:
                self.service_manager.service = self.service_manager.available_services[arg]
            else:
                return service_help
        else:
            return service_help


class SelectTrackCommand:
    def __init__(self, command_processor):
        Command.__init__(self, command_processor)

    def __call__(self, arg, user):
        if arg:
            try:
                self.player.play_by_index(int(arg) - 1)
                return _('now playing {} {}').format(arg, self.player.track.name)
            except errors.IncorrectTrackIndexError:
                return _('Out of list')
            except errors.NothingIsPlayingError:
                return _('Nothing is playing')
            except ValueError:
                return _('Enter number')
        else:
            if self.player.track and self.player.track_index >= 0:
                return _('now playing {} {}').format(self.player.track_index + 1, self.player.track.name)
            else:
                return _('now nothing is not playing')


class ChangeNicknameCommand:
    def __init__(self, command_processor):
        Command.__init__(self, command_processor)

    def __call__(self, arg, user):
        self.ttclient.change_nickname(arg)


class PositionCommand:
    def __init__(self, command_processor):
        Command.__init__(self, command_processor)

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
                return _('Now nothing is playing')
