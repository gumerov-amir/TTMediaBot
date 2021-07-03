import logging
import re
import traceback

from bot import errors
from bot.commands.admin_commands import *
from bot.commands.user_commands import *


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
        self.send_channel_messages = self.config["general"]["send_channel_messages"]
        self.locked = False
        self.blocked_commands = self.config["general"]["blocked_commands"]
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
            'f': FavoritesCommand(self),
            'm': ModeCommand(self),
            'gl': GetLinkCommand(self),
            "dl": DownloadCommand(self),
            'r': HistoryCommand(self),
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
        if message.user.is_banned:
            return _('You are banned')
        if not message.user.is_admin:
            if message.user.channel_id != self.ttclient.get_my_channel_id():
                return _('You are not in bot\'s channel')
            if self.locked:
                return _('Bot is locked')
        try:
            command = re.findall(re_command, message.text.split(' ')[0].lower())[0]
        except IndexError:
            command = ""
        arg = ' '.join(message.text.split(' ')[1::])
        if not message.user.is_admin and command in self.blocked_commands:
            return _('This command is blocked')
        try:
            if command in self.commands_dict:
                return self.commands_dict[command](arg, message.user)
            elif message.user.is_admin and command in self.admin_commands_dict:
                return self.admin_commands_dict[command](arg, message.user)
            else:
                return _("Unknown command. Send \"h\" for help.")
        except errors.InvalidArgumentError:
            return self.help(command, message.user)
        except Exception as e:
            logging.error(traceback.format_exc())
            return _("Error: {}").format(e)

    def help(self, arg, user):
        if arg:
            if arg in self.commands_dict:
                return self.commands_dict[arg].help
            elif user.is_admin and arg in self.admin_commands_dict:
                return self.admin_commands_dict[arg].help
            else:
                return _("Unknown command")
        else:
            help_strings = []
            for i in list(self.commands_dict):
                help_strings.append(
                    "{} {}".format(i, self.help(i, user))
                )
            if user.is_admin:
                for i in list(self.admin_commands_dict)[1::]:
                    help_strings.append(
                        "{} {}".format(i, self.help(i, user))
                    )
            return '\n'.join(help_strings)
