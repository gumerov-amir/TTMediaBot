import re
import time
import traceback
from urllib.parse import urlparse

from .player import Mode, State
from .track import Track

class ProcessCommand(object):
    def __init__(self, player, ttclient, services, default_service):
        self.player = player
        self.ttclient = ttclient
        self.services = services
        self.service = default_service
        self.commands_dict = {'p': self.play_pause, 's': self.stop, 'm': self.mode,     'sb': self.seek_back, 'sf': self.seek_forward, 'r': self.rate, 'v': self.volume, 'u': self.play_by_url, 'h': self.help, 'n': self.next, 'b': self.back, 'c': self.change_service}
        self.admin_commands_dict = {'girl': lambda arg: 'Настенька', "cn": self.change_nickname}


    def __call__(self, message, is_admin):
        print(is_admin)
        try:
            command = re.findall('[a-z]+', message.split(' ')[0].lower())[0]
        except IndexError:
            return self.help()
        arg = ' '.join(message.split(' ')[1::])
        try:
            if command in self.commands_dict:
                return self.commands_dict[command](arg)
            elif is_admin and command in self.admin_commands_dict:
                return self.admin_commands_dict[command](arg)
            else:
                return _('Unknown command.\n') + self.help()
        except Exception as e:
            traceback.print_exc()
            return f'error: {e}'

    def play_pause(self, arg):
        if arg:
            s = time.time()
            track_list = self.service.search(arg)
            print(time.time() - s)
            if track_list:
                self.player.play(track_list)
            else:
                return _('not found')
        else:
            if self.player.state == State.Playing:
                self.player.pause()
            elif self.player.state == State.Paused:
                self.player.play()


    def rate(self, arg):
        '''Изменяет скорость'''
        if not arg:
            self.player._vlc_player.set_rate(1)
        try:
            rate_number = abs(float(arg))
            if rate_number > 0 and rate_number <= 4:
                self.player._vlc_player.set_rate(rate_number)
            else:
                return _('Speed must be from 1 to 4')
        except ValueError:
            return _('Введите число, используйте .')

    def play_by_url(self, arg):
        allow_schemes = ['http', 'https']
        parsed_url = urlparse(arg)
        if parsed_url.scheme in allow_schemes:
            track = Track(url=arg, from_url=True)
            for service in self.services.values():
                if parsed_url.hostname in service.hostnames:
                    track = service.get(arg)
                    break
            self.player.play(track)
        elif not arg:
            return self.help()
        else:
            return _('Введите коректный url или разрешённый протокол')

    def stop(self, arg):
        '''Останавливает аудио'''
        self.player.stop()

    def volume(self, arg):
        '''Изменяет Громкость'''
        try:
            volume = int(arg)
            if volume >= 0 and volume <= 100:
                self.player.set_volume(int(arg))
            else:
                return _('Громкость в диапозоне 1 100')
        except ValueError:
            return _('Недопустимое значение. Укажите число от 1 до 100.')

    def seek_back(self, arg):
        try:
            self.player.seek_back(arg)
        except ValueError:
            return _('Недопустимое значение. Укажите число от 1 до 100.')

    def seek_forward(self, arg):
        try:
            self.player.seek_forward(arg)
        except ValueError:
            return _('Недопустимое значение. Укажите число от 1 до 100.')

    def next(self, arg):
        try:
            self.player.next()
        except IndexError:
            return _('это последний трек')

    def back(self, arg):
        try:
            self.player.back()
        except IndexError:
            return _('Это первый трек')

    def mode(self, arg):
        mode_help = 'current_ mode: {current_mode}\n{modes}'.format(current_mode=self.player.mode.name, modes='\n'.join(['{name} - {value}'.format(name=i.name, value=i.value) for i in [Mode.Single, Mode.TrackList]]))
        if arg:
            try:
                mode = Mode(int(arg))
                self.player.mode = Mode(mode)
            except TypeError:
                return mode_help
        else:
            return mode_help

    mode.help = 'ModeHelp'

    def change_service(self, arg):
        service_help = 'current service: {current_service}\nevalable: {services}'.format(current_service=self.service.__module__.split('.')[-1], services=', '.join([i for i in self.services]))
        if arg:
            if arg in self.services:
                self.service = self.services[arg]
            else:
                return service_help
        else:
            return service_help

    def change_nickname(self, arg):
        try:
            self.ttclient.change_nickname(arg)
        except UnicodeError:
            return _('Не коректное nickname')


    def help(self, arg=None):
        help_strings = []
        for i in list(self.commands_dict):
            try:
                help_strings.append(
                    '{}: {}'.format(i, self.commands_dict[i].help)
                )
            except AttributeError:
                pass
        return '\n'.join(help_strings)

    help.help = 'Возращает справку'
