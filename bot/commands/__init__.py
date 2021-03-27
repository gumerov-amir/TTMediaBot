import logging
import re

from .commands import *


class CommandProcessor(object):
    def __init__(self, player, ttclient, module_manager, service_manager):
        self.player = player
        self.ttclient = ttclient
        self.service_manager = service_manager
        self.module_manager = module_manager
        self.locked = False
        self.commands_dict = {
            'h': self.help,
            'a': AboutCommand(self),
            'p': PlayPauseCommand(self),
            'u': PlayUrlCommand(self),
            'sv': ServiceCommand(self),
            's': StopCommand(self),
            'n': NextTrackCommand(self),
            'c': SelectTrackCommand(self),
            'b': PreviousTrackCommand(self),
            'sf': SeekForwardCommand(self),
            'ps': PositionCommand(self),
            'sb': SeekBackCommand(self),
            'v': VolumeCommand(self),
            'r': RateCommand(self),
            'm': ModeCommand(self),
            'dl': lambda arg, user: self.player.track.url,
        }
        self.admin_commands_dict = {
            'girl': lambda arg, user: 'Настенька',
            'cn': ChangeNicknameCommand(self),
            'l': self.lock,
            'va': VoiceTransmissionCommand(self),
            'q': QuitCommand(self),
        }

    def __call__(self, message):
        if message.user.is_banned:
            return _('You are banned.')
        if not message.user.is_admin:
            if message.user.channel_id != self.ttclient.get_my_channel_id():
                return _('You aren\'t in bot\'s channel.')
            if self.locked:
                return _('Bot is locked')
        try:
            command = re.findall('[a-z]+', message.text.split(' ')[0].lower())[0]
        except IndexError:
            return self.help('', message.user)
        arg = ' '.join(message.text.split(' ')[1::])
        try:
            if command in self.commands_dict:
                return self.commands_dict[command](arg, message.user)
            elif message.user.is_admin and command in self.admin_commands_dict:
                return self.admin_commands_dict[command](arg, message.user)
            else:
                return _('Unknown command') + ' "' + command + '".\n' + self.help('', message.user)
        except Exception as e:
            logging.error(e)
            return f'error: {e}'

    def help(self, arg, user):
        if arg:
            if not user.is_admin and arg in self.commands_dict:
                try:
                    return self.commands_dict[arg].help
                except AttributeError:
                    return _('Help text not found')
            elif user.is_admin and arg in self.admin_commands_dict:
                try:
                    return self.admin_commands_dict[arg].help
                except AttributeError:
                    return _('Help text not found')
            else:
                return _('Unknown command "{command}".\n{help}').format(command=command, help=self.help('', user))
        else:
            help_strings = []
            for i in list(self.commands_dict)[1::]:
                try:
                    help_strings.append(
                        '{}: {}'.format(i, self.commands_dict[i].help)
                    )
                except AttributeError:
                    help_strings.append('{}: help text not found'.format(i))
            if user.is_admin:
                for i in list(self.admin_commands_dict)[1::]:
                    try:
                        help_strings.append(
                            '{}: {}'.format(i, self.admin_commands_dict[i].help)
                        )
                    except AttributeError:
                        help_strings.append('{}: help text not found'.format(i))
            return '\n'.join(help_strings)

    def lock(self, arg, user):
        self.locked = not self.locked
        return _('Locked') if self.locked else _('Unlocked')
