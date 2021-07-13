from queue import Empty
from threading import Thread
import time

from bot import vars


class TaskThread(Thread):
    def __init__(self, bot, player):
        super().__init__(daemon=True)
        self.name = "PlayerTaskThread"
        self.bot = bot
        self.player = player

    def run(self):
        self._close = False
        while not self._close:
            try:
                task = self.player.task_queue.get()
                if task.command_id == self.bot.command_processor.current_command_id:
                    task.function(*task.args, **task.kwargs)
            except Empty:
                pass
            time.sleep(vars.loop_timeout)
