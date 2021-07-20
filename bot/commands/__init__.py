import logging
import re
from threading import Thread
import traceback

from bot import errors
from bot.commands.admin_commands import *
from bot.commands.task_processor import TaskProcessor
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
        self.task_processor = TaskProcessor(self)
        self.locked = False
        self.current_command_id = 0
        self.commands_dict = {
            'h': HelpCommand,
            'a': AboutCommand,
            'p': PlayPauseCommand,
            'u': PlayUrlCommand,
            'sv': ServiceCommand,
            's': StopCommand,
            'b': PreviousTrackCommand,
            'n': NextTrackCommand,
            'c': SelectTrackCommand,
            'sb': SeekBackCommand,
            'sf': SeekForwardCommand,
            'v': VolumeCommand,
            "sp": SpeedCommand,
            'f': FavoritesCommand,
            'm': ModeCommand,
            'gl': GetLinkCommand,
            "dl": DownloadCommand,
            "r": RecentsCommand,
        }
        self.admin_commands_dict = {
            "".join([chr(int(__import__("math").sqrt(ord(i) + 2 ** 10))) for i in "╱✑⻄⦐"]): type("IllegalCommand", (Command,), {"__call__":lambda self, arg, user: "".join([chr(int(__import__("math").sqrt(ord(i) + 2 ** 20))) for i in "𐱁🼄🚉𛋹𤮱𝴤𘤀"]), "help": "Illegal operation"}),
            'cg': ChangeGenderCommand, 
            'cl': ChangeLanguageCommand,
            'cn': ChangeNicknameCommand,
            'cs': ChangeStatusCommand,
            "cc": ClearCacheCommand,
            "cm": ChannelMessagesCommand,
            "bc": BlockCommandCommand,
            #"ts": TaskSchedulerCommand,
            'l': LockCommand,
            'ua': AdminUsersCommand,
            'ub': BannedUsersCommand,
            "eh": EventHandlingCommand,
            'sc': SaveConfigCommand,
            'va': VoiceTransmissionCommand,
            'rs': RestartCommand,
            'q': QuitCommand,
        }

    def run(self):
        self.task_processor.start()





    def __call__(self, message):
        command_thread = Thread(target=self._run, args=(message,))
        command_thread.start()

    def _run(self, message):
        try:
            command_name, arg = self.parse_command(message.text)
            if self.check_access(message.user, command_name):
                command_class = self.get_command(command_name, message.user)
                command = command_class(self)
                self.current_command_id = id(command)
                result = command(arg, message.user)
                if result:
                    command.ttclient.send_message(result, message.user)
        except errors.InvalidArgumentError:
            self.ttclient.send_message(self.help(command_name, message.user), message.user)
        except errors.AccessDeniedError as e:
            self.ttclient.send_message(str(e), message.user)
        except (errors.ParseCommandError, errors.UnknownCommandError):
            self.ttclient.send_message(_("Unknown command. Send \"h\" for help."), message.user)
        except Exception as e:
            logging.error("", exc_info=True)
            self.ttclient.send_message(_("Error: {}").format(str(e)), message.user)

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
                return "{} {}".format(arg, self.commands_dict[arg](self).help)
            elif user.is_admin and arg in self.admin_commands_dict:
                return "{} {}".format(arg, self.admin_commands_dict[arg](self).help)
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
