from queue import Empty
from threading import Thread
import time

from bot import vars


class TaskThread(Thread):
    def __init__(self, bot, ttclient):
        super().__init__(daemon=True)
        self.name = "TeamTalkTaskThread"
        self.bot = bot
        self.ttclient = ttclient

    def run(self):
        self._close = False
        while not self._close:
            try:
                task = self.ttclient.task_queue.get_nowait()
                if task.command_id == self.bot.command_processor.current_command_id:
                    task.function(*task.args, **task.kwargs)
            except Empty:
                pass
            time.sleep(vars.loop_timeout)
