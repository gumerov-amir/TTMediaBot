from __future__ import annotations
from typing import TYPE_CHECKING
from threading import Thread

from bot.TeamTalk.structs import *

if TYPE_CHECKING:
    from bot.console import Console


class ConsoleThread(Thread):
    def __init__(self, console: Console):
        Thread.__init__(self, daemon=True)
        self.name = "ConsoleThread"
        self.console = console

    def run(self) -> None:
        self._close = False
        while not self._close:
            message_text = input("Enter command: ")
            message = self.console.build_message(message_text)
            self.console.message_queue.put(message)

    def close(self) -> None:
        self._close = True
