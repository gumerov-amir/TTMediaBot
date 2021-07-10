import threading
import time

from bot.TeamTalk import User
from bot import vars


class TaskScheduler(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.name = "SchedulerThread"
        self.tasks = {}
        #self.user = User(0, "", "", 0, 0, "", is_admin=True, is_banned=False)

    def run(self):
        while True:
            for t in self.tasks:
                if self.get_time() >= t:
                    task = self.tasks[t]
                    task[0](task[1], self.user)
        time.sleep(vars.loop_timeout)

    def get_time(self):
        return int(round(time.time()))
