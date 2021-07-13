import logging
import re
from threading import Thread
import traceback

from bot import errors
from bot.commands.admin_commands import *
from bot.commands.task import Task
from bot.commands.user_commands import *
from bot.TeamTalk.structs import UserType
from bot import vars


re_command = re.compile('[a-z]+')

class CommandProcessor:
    def __init__(self, bot, config, player, ttclient, module_manager, service_manager, cache):
        self.bot = bot
        self.cache = cache
        self.config = config
        self.module_manager = module_manager
        self.player = player
        self.service_manager = service_manager
        self.ttclient = ttclient
        self.locked = False
        self.current_command_id = 0
        self.commands_dict = {
            'h': HelpCommand(self),
            'a': AboutCommand(self),
            'p': PlayPauseCommand(self),
            'u': PlayUrlCommand(self),
            'sv': ServiceCommand(self),
            's': StopCommand(self),
            'b': PreviousTrackCommand(self),
            'n': NextTrackCommand(self),
            'c': SelectTrackCommand(self),
            'sb': SeekBackCommand(self),
            'sf': SeekForwardCommand(self),
            'v': VolumeCommand(self),
            "sp": SpeedCommand(self),
            'f': FavoritesCommand(self),
            'm': ModeCommand(self),
            'gl': GetLinkCommand(self),
            "dl": DownloadCommand(self),
            "r": RecentsCommand(self),
        }
        self.admin_commands_dict = {
            'girl': lambda arg, user: "".join([chr(int(__import__("math").sqrt(ord(i) + 2 ** 20))) for i in "𐱁🼄🚉𛋹𤮱𝴤𘤀"]),
            'cg': ChangeGenderCommand(self),
            'cl': ChangeLanguageCommand(self),
            'cn': ChangeNicknameCommand(self),
            'cs': ChangeStatusCommand(self),
            "cc": ClearCacheCommand(self),
            "cm": ChannelMessagesCommand(self),
            "bc": BlockCommandCommand(self),
            #"ts": TaskSchedulerCommand(self),
            'l': LockCommand(self),
            'ua': AdminUsersCommand(self),
            'ub': BannedUsersCommand(self),
            "eh": EventHandlingCommand(self),
            'sc': SaveConfigCommand(self),
            'va': VoiceTransmissionCommand(self),
            'rs': RestartCommand(self),
            'q': QuitCommand(self),
        }

    def __call__(self, message):
        command_thread = Thread(target=self.run, args=(message,))
        command_thread.start()

    def run(self, message):
        try:
            command_name, arg = self.parse_command(message.text)
            if self.check_access(message.user, command_name):
                command = self.get_command(command_name, message.user)
                self.current_command_id += 1
                result = command(self.current_command_id, arg, message.user)
                self.ttclient.task_queue.put(Task(self.current_command_id, self.ttclient.send_message, result, message.user))
        except errors.InvalidArgumentError:
            return self.help(command_name, message.user)
        except errors.AccessDeniedError as e:
            return str(e)
        except (errors.ParseCommandError, errors.UnknownCommandError):
            return _("Unknown command. Send \"h\" for help.")
        except Exception as e:
            logging.error("", exc_info=True)
            return _("Error: {}").format(e)

    def check_access(self, user, command):
        if (not user.is_admin and user.type != UserType.Admin) or vars.app_name in user.client_name:
            if vars.app_name in user.client_name:
                raise AccessDeniedError("")
            elif user.is_banned:
                raise errors.AccessDeniedError(_("You are banned"))
            elif user.channel.id != self.ttclient.channel.id:
                raise errors.AccessDeniedError(_("You are not in bot\'s channel"))
            elif self.locked:
                raise errors.AccessDeniedError(_("Bot is locked"))
            elif command in self.config.general.blocked_commands:
                raise errors.AccessDeniedError(_("This command is blocked"))
            else:
                return True
        else:
            return True

    def get_command(self, command, user):
        if command in self.commands_dict:
            return self.commands_dict[command]
        elif (user.is_admin or user.type == UserType.Admin) and command in self.admin_commands_dict:
            return self.admin_commands_dict[command]
        else:
            raise errors.UnknownCommandError()

    def help(self, arg, user):
        if arg:
            if arg in self.commands_dict:
                return "{} {}".format(arg, self.commands_dict[arg].help)
            elif user.is_admin and arg in self.admin_commands_dict:
                return "{} {}".format(arg, self.admin_commands_dict[arg].help)
            else:
                return _("Unknown command")
        else:
            help_strings = []
            for i in list(self.commands_dict):
                help_strings.append(self.help(i, user))
            if user.is_admin:
                for i in list(self.admin_commands_dict)[1::]:
                    help_strings.append(self.help(i, user))
            return '\n'.join(help_strings)

    def parse_command(self, text):
        text = text.strip()
        try:
            command = re.findall(re_command, text.split(' ')[0].lower())[0]
        except IndexError:
            raise errors.ParseCommandError()
        arg = ' '.join(text.split(' ')[1::])
        return command, arg
