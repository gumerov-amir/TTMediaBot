from __future__ import annotations

import logging
import re
from threading import Thread
from typing import Any, List, TYPE_CHECKING, Tuple

from bot import app_vars, errors
from bot.TeamTalk.structs import Message, User, UserType
from bot.commands import admin_commands, user_commands
from bot.commands.task_processor import TaskProcessor

re_command = re.compile("[a-z]+")
re_arg_split = re.compile(r"(?<!\\)\|")

if TYPE_CHECKING:
    from bot import Bot


class CommandProcessor:
    def __init__(self, bot: Bot):
        self.task_processor = TaskProcessor(self)
        self.bot = bot
        self.config = bot.config
        self.config_manager = bot.config_manager
        self.cache = bot.cache
        self.cache_manager = bot.cache_manager
        self.module_manager = bot.module_manager
        self.player = bot.player
        self.service_manager = bot.service_manager
        self.ttclient = bot.ttclient
        self.translator = bot.translator
        self.locked = False
        self.current_command_id = 0
        self.commands_dict = {
            "h": user_commands.HelpCommand,
            "a": user_commands.AboutCommand,
            "p": user_commands.PlayPauseCommand,
            "u": user_commands.PlayUrlCommand,
            "sv": user_commands.ServiceCommand,
            "s": user_commands.StopCommand,
            "b": user_commands.PreviousTrackCommand,
            "n": user_commands.NextTrackCommand,
            "c": user_commands.SelectTrackCommand,
            "sb": user_commands.SeekBackCommand,
            "sf": user_commands.SeekForwardCommand,
            "v": user_commands.VolumeCommand,
            "sp": user_commands.SpeedCommand,
            "f": user_commands.FavoritesCommand,
            "m": user_commands.ModeCommand,
            "gl": user_commands.GetLinkCommand,
            "dl": user_commands.DownloadCommand,
            "r": user_commands.RecentsCommand,
        }
        self.admin_commands_dict = {
            "cg": admin_commands.ChangeGenderCommand,
            "cl": admin_commands.ChangeLanguageCommand,
            "cn": admin_commands.ChangeNicknameCommand,
            "cs": admin_commands.ChangeStatusCommand,
            "cc": admin_commands.ClearCacheCommand,
            "cm": admin_commands.ChannelMessagesCommand,
            "jc": admin_commands.JoinChannelCommand,
            "bc": admin_commands.BlockCommandCommand,
            # "ts": TaskSchedulerCommand,
            "l": admin_commands.LockCommand,
            "ua": admin_commands.AdminUsersCommand,
            "ub": admin_commands.BannedUsersCommand,
            "eh": admin_commands.EventHandlingCommand,
            "sc": admin_commands.SaveConfigCommand,
            "va": admin_commands.VoiceTransmissionCommand,
            "rs": admin_commands.RestartCommand,
            "q": admin_commands.QuitCommand,
            "gcid": admin_commands.GetChannelIDCommand,
        }

    def run(self):
        self.task_processor.start()

    def __call__(self, message: Message) -> None:
        command_thread = Thread(target=self._run, args=(message,))
        command_thread.start()

    def _run(self, message: Message) -> None:
        try:
            command_name, arg = self.parse_command(message.text)
            if self.check_access(message.user, command_name):
                command_class = self.get_command(command_name, message.user)
                command = command_class(self)
                self.current_command_id = id(command)
                result = command(arg, message.user)
                if result:
                    self.ttclient.send_message(
                        result,
                        message.user,
                    )  # here was command.ttclient later
        except errors.InvalidArgumentError:
            self.ttclient.send_message(
                self.help(command_name, message.user),
                message.user,
            )
        except errors.AccessDeniedError as e:
            self.ttclient.send_message(str(e), message.user)
        except (errors.ParseCommandError, errors.UnknownCommandError):
            self.ttclient.send_message(
                self.translator.translate('Unknown command. Send "h" for help.'),
                message.user,
            )
        except Exception as e:
            logging.error("", exc_info=True)
            self.ttclient.send_message(
                self.translator.translate("Error: {}").format(str(e)),
                message.user,
            )

    def check_access(self, user: User, command: str) -> bool:
        if (
            not user.is_admin and user.type != UserType.Admin
        ) or app_vars.app_name in user.client_name:
            if app_vars.app_name in user.client_name:
                raise errors.AccessDeniedError("")
            elif user.is_banned:
                raise errors.AccessDeniedError(
                    self.translator.translate("You are banned"),
                )
            elif user.channel.id != self.ttclient.channel.id:
                raise errors.AccessDeniedError(
                    self.translator.translate("You are not in bot's channel"),
                )
            elif self.locked:
                raise errors.AccessDeniedError(
                    self.translator.translate("Bot is locked"),
                )
            elif command in self.config.general.blocked_commands:
                raise errors.AccessDeniedError(
                    self.translator.translate("This command is blocked"),
                )
            else:
                return True
        else:
            return True

    def get_command(self, command: str, user: User) -> Any:
        if command in self.commands_dict:
            return self.commands_dict[command]
        elif (
            user.is_admin or user.type == UserType.Admin
        ) and command in self.admin_commands_dict:
            return self.admin_commands_dict[command]
        else:
            raise errors.UnknownCommandError()

    def help(self, arg: str, user: User) -> str:
        if arg:
            if arg in self.commands_dict:
                return "{} {}".format(arg, self.commands_dict[arg](self).help)
            elif user.is_admin and arg in self.admin_commands_dict:
                return "{} {}".format(arg, self.admin_commands_dict[arg](self).help)
            else:
                return self.translator.translate("Unknown command")
        else:
            help_strings: List[str] = []
            for i in list(self.commands_dict):
                help_strings.append(self.help(i, user))
            if user.is_admin:
                for i in list(self.admin_commands_dict):
                    help_strings.append(self.help(i, user))
            return "\n".join(help_strings)

    def parse_command(self, text: str) -> Tuple[str, str]:
        text = text.strip()
        try:
            command = re.findall(re_command, text.split(" ")[0].lower())[0]
        except IndexError:
            raise errors.ParseCommandError()
        arg = " ".join(text.split(" ")[1::])
        return command, arg

    def split_arg(self, arg: str) -> List[str]:
        args = re.split(re_arg_split, arg)
        for i, arg in enumerate(args):
            args[i] = args[i].strip().replace("\\|", "|")
        return args
