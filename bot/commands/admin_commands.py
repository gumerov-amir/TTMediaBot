from __future__ import annotations
import json
import os
import subprocess
import sys
import time
from typing import Optional, TYPE_CHECKING
from queue import Empty

from bot.commands.command import Command
from bot.player.enums import State
from bot import app_vars, errors

if TYPE_CHECKING:
    from bot.TeamTalk.structs import User

class OptionShowMetaCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate(
            "Toggles metadata display in the status message."
        )

    def __call__(self, arg: str, user: User) -> Optional[str]:
        if self.config.general.showmeta:
            self.config.general.showmeta = False
            return self.translator.translate("Metadata display disabled.")
        else:
            self.config.general.showmeta = True
            return self.translator.translate("Metadata display enabled.")

class OptionBackToRootChannelCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate(
            "Toggles the ability for users to move the bot to their channels automatically."
        )

    def __call__(self, arg: str, user: User) -> Optional[str]:
        if self.config.general.back_to_root_channel:
            self.config.general.back_to_root_channel = False
            return self.translator.translate("Users can't move the bot to their channels.")
        else:
            self.config.general.back_to_root_channel = True
            return self.translator.translate("Users can move the bot to their channels.")

class BlockCommandCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate(
            "+/-COMMAND Blocks or unblocks commands. +COMMAND adds command to the blocklist. -COMMAND removes from it. Without a command shows the blocklist"
        )

    def __call__(self, arg: str, user: User) -> Optional[str]:
        arg = arg.lower()
        if len(arg) >= 1 and arg[1:] not in self.command_processor.commands_dict:
            raise errors.InvalidArgumentError()
        if not arg:
            return (
                ", ".join(self.config.general.blocked_commands)
                if self.config.general.blocked_commands
                else self.translator.translate("The list is empty")
            )
        if arg[0] == "+":
            if arg[1::] not in self.config.general.blocked_commands:
                self.config.general.blocked_commands.append(arg[1::])
                return self.translator.translate("Added")
            else:
                return self.translator.translate("This command is already added")
        elif arg[0] == "-":
            if arg[1::] in self.config.general.blocked_commands:
                del self.config.general.blocked_commands[
                    self.config.general.blocked_commands.index(arg[1::])
                ]
                return self.translator.translate("Deleted")
            else:
                return self.translator.translate("This command is not blocked")
        else:
            raise errors.InvalidArgumentError()


class ChangeGenderCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate(
            "GENDER Changes bot's gender. n neutral, m male, f female"
        )

    def __call__(self, arg: str, user: User) -> Optional[str]:
        try:
            self.ttclient.change_gender(arg)
            self.config.teamtalk.gender = arg
        except KeyError:
            raise errors.InvalidArgumentError()


class ChangeLanguageCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate("LANGUAGE Changes bot's language")

    def __call__(self, arg: str, user: User) -> Optional[str]:
        if arg:
            try:
                self.translator.set_locale(arg)
                self.config.general.language = arg
                self.ttclient.change_status_text("")
                return self.translator.translate("The language has been changed")
            except errors.LocaleNotFoundError:
                return self.translator.translate("Incorrect language")
        else:
            return self.translator.translate(
                "Current language: {current_language}. Available languages: {available_languages}"
            ).format(
                current_language=self.translator.get_locale(),
                available_languages=", ".join(self.translator.get_locales()),
            )


class ChangeNicknameCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate("NICKNAME Changes bot's nickname")

    def __call__(self, arg: str, user: User) -> Optional[str]:
        self.ttclient.change_nickname(arg)
        self.config.teamtalk.nickname = arg


class ClearCacheCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate(
            "r/f/q/p Clears bot's cache. r clears recents, f clears favorites, q clears the queue, p clears saved positions, without an option clears the entire cache"
        )

    def __call__(self, arg: str, user: User) -> Optional[str]:
        if not arg:
            try:
                for track in self.cache.recents:
                    track.resume_position = None
                    track.resume_duration = None
            except Exception:
                ...
            self.cache.recents.clear()
            self.cache.favorites.clear()
            self.cache.queue.clear()
            self.cache_manager.save()
            return self.translator.translate("Cache cleared")
        elif arg == "r":
            self.cache.recents.clear()
            self.cache_manager.save()
            return self.translator.translate("Recents cleared")
        elif arg == "f":
            self.cache.favorites.clear()
            self.cache_manager.save()
            return self.translator.translate("Favorites cleared")
        elif arg == "q":
            self.cache.queue.clear()
            self.cache_manager.save()
            return self.translator.translate("Queue cleared")
        elif arg == "p":
            try:
                for track in self.cache.recents:
                    track.resume_position = None
                    track.resume_duration = None
                self.cache_manager.save()
            except Exception:
                self.cache_manager.save()
            return self.translator.translate("Positions cleared")


class JoinChannelCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate(
            'Join channel. first argument is channel name or id, second argument is password, split argument " | ", if password is undefined, don\'t type second argument'
        )

    def __call__(self, arg: str, user: User) -> Optional[str]:
        args = self.command_processor.split_arg(arg)
        if not arg:
            channel = self.config.teamtalk.channel
            password = self.config.teamtalk.channel_password
        elif len(args) == 2:
            channel = args[0]
            password = args[1]
        else:
            channel = arg
            password = ""
        if isinstance(channel, str) and channel.isdigit():
            channel = int(channel)
        try:
            cmd = self.ttclient.join_channel(channel, password)
        except ValueError:
            return self.translator.translate("This channel does not exist")
        while True:
            try:
                event = self.ttclient.event_success_queue.get_nowait()
                if event.source == cmd:
                    break
                else:
                    self.ttclient.event_success_queue.put(event)
            except Empty:
                pass
            try:
                error = self.ttclient.errors_queue.get_nowait()
                if error.command_id == cmd:
                    return self.translator.translate(
                        "Error joining channel: {error}".format(error=error.message)
                    )
                else:
                    self.ttclient.errors_queue.put(error)
            except Empty:
                pass
            time.sleep(app_vars.loop_timeout)


""" class TaskSchedulerCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate("Task scheduler")

    def __call__(self, arg: str, user: User) -> Optional[str]:
        if arg[0] == "+":
            self._add(arg[1::])

    def _add(self, arg: str) -> None:
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
                return self.translator.translate("Unknown command. Send \"h\" for help.")
            except errors.InvalidArgumentError:
                return self.help(command, message.user)
        if timestamp in self.module_manager.task_scheduler.tasks:
            self.module_manager.task_scheduler[timestamp].append(task)
        else:
            self.module_manager.task_scheduler.tasks[timestamp] = [task,]


    def _get_timestamp(self, t):
        return int(datetime.combine(datetime.today(), datetime.strptime(t, self.config["general"]["time_format"]).time()).timestamp())
 """


class VoiceTransmissionCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate("Enables or disables voice transmission")

    def __call__(self, arg: str, user: User) -> Optional[str]:
        if not self.ttclient.is_voice_transmission_enabled:
            self.ttclient.enable_voice_transmission()
            if self.player.state == State.Stopped:
                self.ttclient.change_status_text(
                    self.translator.translate("Voice transmission enabled")
                )
            return self.translator.translate("Voice transmission enabled")
        else:
            self.ttclient.disable_voice_transmission()
            if self.player.state == State.Stopped:
                self.ttclient.change_status_text("")
            return self.translator.translate("Voice transmission disabled")


class LockCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate("Locks or unlocks the bot")

    def __call__(self, arg: str, user: User) -> Optional[str]:
        self.command_processor.locked = not self.command_processor.locked
        return (
            self.translator.translate("Locked")
            if self.command_processor.locked
            else self.translator.translate("Unlocked")
        )


class ChangeStatusCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate("STATUS Changes bot's status")

    def __call__(self, arg: str, user: User) -> Optional[str]:
        self.ttclient.change_status_text(arg)
        self.config.teamtalk.status = arg


class EventHandlingCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate("Enables or disables event handling")

    def __call__(self, arg: str, user: User) -> Optional[str]:
        self.config.teamtalk.event_handling.load_event_handlers = (
            not self.config.teamtalk.event_handling.load_event_handlers
        )
        return (
            self.translator.translate("Event handling is enabled")
            if self.config.teamtalk.event_handling.load_event_handlers
            else self.translator.translate("Event handling is disabled")
        )


class ChannelMessagesCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate(
            "Enables or disables sending of channel messages"
        )

    def __call__(self, arg: str, user: User) -> Optional[str]:
        self.config.general.send_channel_messages = (
            not self.config.general.send_channel_messages
        )
        return (
            self.translator.translate("Channel messages enabled")
            if self.config.general.send_channel_messages
            else self.translator.translate("Channel messages disabled")
        )


class SaveConfigCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate("Saves bot's configuration")

    def __call__(self, arg: str, user: User) -> Optional[str]:
        self.config_manager.save()
        return self.translator.translate("Configuration saved")


class AdminUsersCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate(
            "+/-USERNAME Manages a list of administrators. +USERNAME adds a user. -USERNAME removes it. Without an option shows the list"
        )

    def __call__(self, arg: str, user: User) -> Optional[str]:
        if arg:
            if arg[0] == "+":
                self.config.teamtalk.users.admins.append(arg[1::])
                return self.translator.translate("Added")
            elif arg[0] == "-":
                try:
                    del self.config.teamtalk.users.admins[
                        self.config.teamtalk.users.admins.index(arg[1::])
                    ]
                    return self.translator.translate("Deleted")
                except ValueError:
                    return self.translator.translate(
                        "This user is not in the admin list"
                    )
        else:
            admins = self.config.teamtalk.users.admins.copy()
            if len(admins) > 0:
                if "" in admins:
                    admins[admins.index("")] = "<Anonymous>"
                return ", ".join(admins)
            else:
                return self.translator.translate("The list is empty")


class BannedUsersCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate(
            "+/-USERNAME Manages a list of banned users. +USERNAME adds a user. -USERNAME removes it. Without an option shows the list"
        )

    def __call__(self, arg: str, user: User) -> Optional[str]:
        if arg:
            if arg[0] == "+":
                self.config.teamtalk.users.banned_users.append(arg[1::])
                return self.translator.translate("Added")
            elif arg[0] == "-":
                try:
                    del self.config.teamtalk.users.banned_users[
                        self.config.teamtalk.users.banned_users.index(arg[1::])
                    ]
                    return self.translator.translate("Deleted")
                except ValueError:
                    return self.translator.translate("This user is not banned")
        else:
            banned_users = self.config.teamtalk.users.banned_users.copy()
            if len(banned_users) > 0:
                if "" in banned_users:
                    banned_users[banned_users.index("")] = "<Anonymous>"
                return ", ".join(banned_users)
            else:
                return self.translator.translate("The list is empty")


class QuitCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate("Quits the bot")

    def __call__(self, arg: str, user: User) -> Optional[str]:
        self._bot.close()


class RestartCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate("Restarts the bot")

    def __call__(self, arg: str, user: User) -> Optional[str]:
        self._bot.close()
        args = sys.argv
        if sys.platform == "win32":
            subprocess.run([sys.executable] + args)
        else:
            args.insert(0, sys.executable)
            os.execv(sys.executable, args)


class GetChannelIDCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate("Returns current channel's ID")

    def __call__(self, arg: str, user: User) -> Optional[str]:
        return str(self.ttclient.channel.id)


class UpdateCommand(Command):
    @property
    def help(self) -> str:
        return self.translator.translate("Checks for updates and restarts the bot if packages are updated")

    def __call__(self, arg: str, user: User) -> Optional[str]:
        # Enviar mensagem de que está verificando
        self.ttclient.send_message(
            self.translator.translate("Checking for updates..."),
            user
        )

        # Capturar versões atuais
        old_packages = self._get_installed_packages()

        # Executar upgrade
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--upgrade"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return self.translator.translate("Error updating packages: {}").format(result.stderr)

        # Capturar novas versões
        new_packages = self._get_installed_packages()

        # Comparar e encontrar diferenças
        updated = self._find_updated_packages(old_packages, new_packages)

        if not updated:
            return self.translator.translate("No updates available.")

        # Format message com as atualizações
        updates_text = self.translator.translate("Updates installed:\n{}").format(
            "\n".join(updated)
        )
        self.ttclient.send_message(updates_text, user)

        # Reiniciar o bot (igual ao RestartCommand)
        self._bot.close()
        args = sys.argv
        if sys.platform == "win32":
            subprocess.run([sys.executable] + args)
        else:
            args.insert(0, sys.executable)
            os.execv(sys.executable, args)
        return None

    def _get_installed_packages(self) -> dict:
        """Retorna dict com nome do pacote -> versão"""
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            packages = json.loads(result.stdout)
            return {pkg["name"].lower(): pkg["version"] for pkg in packages}
        return {}

    def _find_updated_packages(self, old: dict, new: dict) -> list:
        """Retorna lista de mensagens descrevendo as atualizações"""
        updated = []
        for name, old_version in old.items():
            new_version = new.get(name)
            if new_version and new_version != old_version:
                # Formatar mensagem tipo "Atualizado yt-dlp de 2024.1.1 para 2024.2.1"
                msg = self.translator.translate(
                    "Updated {package} from {old_version} to {new_version}"
                ).format(
                    package=name,
                    old_version=old_version,
                    new_version=new_version
                )
                updated.append(msg)
        return updated
