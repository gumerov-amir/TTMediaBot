from __future__ import annotations

from typing import Any, TYPE_CHECKING, Callable

from bot.commands.task_processor import Task

if TYPE_CHECKING:
    from bot.commands import CommandProcessor


class Command:
    def __init__(self, command_processor: CommandProcessor):
        self._bot = command_processor.bot
        self.cache = command_processor.cache
        self.cache_manager = command_processor.cache_manager
        self.command_processor = command_processor
        self.config = command_processor.config
        self.config_manager = command_processor.config_manager
        self.module_manager = command_processor.module_manager
        self.player = command_processor.player
        self.service_manager = command_processor.service_manager
        self._task_processor = command_processor.task_processor
        self.ttclient = command_processor.ttclient
        self.translator = command_processor.translator

    @property
    def help(self) -> str:
        return self.translator.translate("help text not found")

    def run_async(self, func: Callable[..., None], *args: Any, **kwargs: Any) -> None:
        self._task_processor.task_queue.put(Task(id(self), func, args, kwargs))
