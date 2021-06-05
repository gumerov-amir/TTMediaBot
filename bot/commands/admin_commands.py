import os
import subprocess
import sys

from bot.commands.command import AdminCommand
from bot.player.enums import State
from bot import vars


class ChangeNicknameCommand(AdminCommand):
    @property
    def help(self):
        return _('NICKNAME Sets the bot\'s nickname')

    def __call__(self, arg, user):
        self.ttclient.change_nickname(arg)
        self.config['teamtalk']['nickname'] = arg


class VoiceTransmissionCommand(AdminCommand):
    @property
    def help(self):
        return _('Enables or disables voice transmission')

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


class LockCommand(AdminCommand):
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.command_processor = command_processor

    @property
    def help(self):
        return _('Locks or unlocks the bot')

    def __call__(self, arg, user):
        return self.command_processor.lock(arg, user)

class VolumeLockCommand(AdminCommand):
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.command_processor = command_processor

    @property
    def help(self):
        return _('Locks or unlocks volume')

    def __call__(self, arg, user):
        return self.command_processor.volume_lock(arg, user)


class ChangeStatusCommand(AdminCommand):
    @property
    def help(self):
        return _('changes status of bot')


    def __call__(self, arg, user):
        self.ttclient.change_status_text(arg)
        self.config['teamtalk']['default_status'] = self.ttclient.status



class SaveConfigCommand(AdminCommand):
    @property
    def help(self):
        return _('saves config to file')

    def __call__(self, arg, user):
        self.config.save()
        return _('Config saved')

class AdminUsersCommand(AdminCommand):
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.command_processor = command_processor

    @property
    def help(self):
        return _('shows list of admin users, if user_name is given adds it to list')

    def __call__(self, arg, user):
        admin_users = self.command_processor.config['teamtalk']['users']['admins']
        if arg:
            if arg[0] == '+':
                admin_users.append(arg[1::])
                return _('Added')
            elif arg[0] == '-':
                try:
                    del admin_users[admin_users.index(arg[1::])]
                    return _('Deleted')
                except ValueError:
                    return _('This user is not admin')
        else:
            admin_users = admin_users.copy()
            if len(admin_users) > 0:
                if '' in admin_users:
                    admin_users[admin_users.index('')] = '<Anonymous>'
                return ', '.join(self.command_processor.config['teamtalk']['users']['admins'])
            else:
                return _('List is empty')


class BannedUsersCommand(AdminCommand):
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.command_processor = command_processor

    @property
    def help(self):
        return _('shows list of banned users, if user_name is given adds to/deletes from list')

    def __call__(self, arg, user):
        banned_users = self.command_processor.config['teamtalk']['users']['banned_users']
        if arg:
            if arg[0] == '+':
                banned_users.append(arg[1::])
                return _('Added')
            elif arg[0] == '-':
                try:
                    del banned_users[banned_users.index(arg[1::])]
                    return _('Deleted')
                except ValueError:
                    return _('This user is not banned')
        else:
            banned_users = banned_users.copy()
            if len(banned_users) > 0:
                if '' in banned_users:
                    banned_users[banned_users.index('')] = '<Anonymous>'
                return ', '.join(banned_users)
            else:
                return _('List is empty')



class QuitCommand(AdminCommand):
    @property
    def help(self):
        return _('Quits the bot')

    def __call__(self, arg, user):
        self.bot.close()

class RestartCommand(AdminCommand):
    @property
    def help(self):
        return _('restarts bot')

    def __call__(self, arg, user):
        self.bot.close()
        args = sys.argv[:]
        args.insert(0, sys.executable)
        args = ['"%s"' % arg for arg in args]
        os.execv(sys.executable, args)
