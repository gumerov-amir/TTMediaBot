import os
import subprocess
import sys

from bot.commands.command import AdminCommand
from bot.player.enums import State
from bot import errors, translator, vars


class BlockCommandCommand(AdminCommand):
    @property
    def help(self):
            return _("Blocks or unblocks commands.\nbc +command adds command in blocklist.\nbc -command removes command from blocklist.")

    def __call__(self, arg, user):
        arg = arg.lower()
        if len(arg) >= 1 and not arg[1::] in self.command_processor.commands_dict:
            return _("Unknown user command")
        if not arg:
            return ", ".join(self.command_processor.blocked_commands) if self.command_processor.blocked_commands else _("List is empty")
        if arg[0] == "+":
            if not arg[1::] in self.command_processor.blocked_commands:
                self.command_processor.blocked_commands.append(arg[1::])
                return _("Added")
            else:
                return _("This command is already added")
        elif arg[0] == "-":
            if arg[1::] in self.command_processor.blocked_commands:
                del self.command_processor.blocked_commands[self.command_processor.blocked_commands.index(arg[1::])]
                return _("Deleted")
            else:
                return _("This command is not blocked")
        else:
            raise errors.InvalidArgumentError()


class ChangeGenderCommand(AdminCommand):
    @property
    def help(self):
        return _('Changes the gender of the bot.\ncg n changes to neutral.\ncg m changes to male.\ncg f changes to female.')

    def __call__(self, arg, user):
        try:
            self.ttclient.change_gender(arg)
            self.config['teamtalk']['gender'] = arg
        except KeyError:
            raise errors.InvalidArgumentError()


class ChangeLanguageCommand(AdminCommand):
    @property
    def help(self):
        return _('Changes the bot language')

    def __call__(self, arg, user):
        if arg:
            try:
                translator.install_locale(arg, fallback=arg == 'en')
                self.config['general']['language'] = arg
                self.ttclient.change_status_text('')
                return _('Language has been changed')
            except:
                return _('Incorrect locale')
        else:
            return _('Current locale is {current_locale}. Available locales: {available_locales}').format(current_locale=self.config['general']['language'], available_locales=', '.join(translator.get_locales()))


class ChangeNicknameCommand(AdminCommand):
    @property
    def help(self):
        return _('NICKNAME Sets the bot\'s nickname')

    def __call__(self, arg, user):
        self.ttclient.change_nickname(arg)
        self.config['teamtalk']['nickname'] = arg


class ClearCacheCommand(AdminCommand):
    @property
    def help(self):
        return _("cc without arguments clears the entire cache.\ncc r cleares only recent tracks.\ncc f cleares only favorites.")

    def __call__(self, arg, user):
        if not arg:
            self.cache.recents.clear()
            self.cache.favorites.clear()
            self.cache.save()
            return _("Cache cleared")
        elif arg == "r":
            self.cache.recents.clear()
            self.cache.save()
            return _("Recents cleared")
        elif arg == "f":
            self.cache.favorites.clear()
            self.cache.save()
            return _("Favorites cleared")


class TaskSchedulerCommand(AdminCommand):
    @property
    def help(self):
        return _("Sets task on time")

    def __call__(self, arg, user):
        if arg[0] == "+":
            self._add(arg[1::])

    def _add(self, arg):
        args = arg.split("|")
        timestamp = self._get_timestamp(args[0])
        task = []
        for arg in args[1::]:
            try:
                command, arg = self.parse_command(message.text)
                if self.check_access(message.user, command):
                    command = self.get_command(command, message.user)
                    task.append((command, arg))
            except errors.AccessDeniedError as e:
                return e
            except (errors.ParseCommandError, errors.UnknownCommandError):
                return _("Unknown command. Send \"h\" for help.")
            except errors.InvalidArgumentError:
                return self.help(command, message.user)
        if timestamp in self.module_manager.task_scheduler.tasks:
            self.module_manager.task_scheduler[timestamp].append(task)
        else:
            self.module_manager.task_scheduler.tasks[timestamp] = [task,]


    def _get_timestamp(self, t):
        return int(datetime.combine(datetime.today(), datetime.strptime(t, self.config["general"]["time_format"]).time()).timestamp())


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
    @property
    def help(self):
        return _('Locks or unlocks the bot')


    def __call__(self,  arg, user):
        self.command_processor.locked = not self.command_processor.locked
        return _('Locked') if self.command_processor.locked else _('Unlocked')


class ChangeStatusCommand(AdminCommand):
    @property
    def help(self):
        return _('Changes bot status')


    def __call__(self, arg, user):
        self.ttclient.change_status_text(arg)
        self.config['teamtalk']['default_status'] = self.ttclient.status


class EventHandlingCommand(AdminCommand):
    @property
    def help(self):
            return _("Enables or disables event handling")

    def __call__(self, arg, user):
        self.ttclient.load_event_handlers = not self.ttclient.load_event_handlers
        self.config["general"]["load_event_handlers"] = self.ttclient.load_event_handlers
        return _("Event handling is enabled") if self.config["general"]["load_event_handlers"] else _("Event handling is disabled")


class ChannelMessagesCommand(AdminCommand):
    @property
    def help(self):
        return _("Enables or disables channel messages sent by the bot when requesting to play music, stop current music, and other events")

    def __call__(self, arg, user):
        self.command_processor.send_channel_messages = not self.command_processor.send_channel_messages
        self.config["general"]["send_channel_messages"] = self.command_processor.send_channel_messages
        return _("Channel messages enabled") if self.command_processor.send_channel_messages else _("Channel messages disabled")


class SaveConfigCommand(AdminCommand):
    @property
    def help(self):
        return _('Saves the configuration to a file')

    def __call__(self, arg, user):
        self.config.save()
        return _('Configuration saved')

class AdminUsersCommand(AdminCommand):
    @property
    def help(self):
        return _('Shows a list of administrators.\nua +username adds this username in adminlist.\nua -username removes its username from adminlist.')

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
                    return _('This user is not an admin')
        else:
            admin_users = admin_users.copy()
            if len(admin_users) > 0:
                if '' in admin_users:
                    admin_users[admin_users.index('')] = '<Anonymous>'
                return ', '.join(self.command_processor.config['teamtalk']['users']['admins'])
            else:
                return _('List is empty')


class BannedUsersCommand(AdminCommand):
    @property
    def help(self):
        return _('Shows a list of banned users.\nub +username add this user to banlist.\nub -username removes this user from banlist.')

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
        return _('Restarts the bot')

    def __call__(self, arg, user):
        self.bot.close()
        args = sys.argv
        if sys.platform == 'win32':
            subprocess.run([sys.executable] + args)
        else:
            args.insert(0, sys.executable)
            os.execv(sys.executable, args)
