"""
from __future__ import annotations
import threading
import time
from typing import TYPE_CHECKING

from bot import app_vars

if TYPE_CHECKING:
    from bot import Bot


class TaskScheduler(threading.Thread):
    def __init__(self, bot: Bot):
        super().__init__(daemon=True)
        self.name = "SchedulerThread"
        self.tasks = {}
        # self.user = User(0, "", "", 0, 0, "", is_admin=True, is_banned=False)

    def run(self):
        while True:
            for t in self.tasks:
                if self.get_time() >= t:
                    task = self.tasks[t]
                    task[0](task[1], self.user)
        time.sleep(app_vars.loop_timeout)

    def get_time(self):
        return int(round(time.time()))


"""
