from bot.modules.downloader import Downloader
from bot.modules.streamer import Streamer
from bot.modules.task_scheduler import TaskScheduler


class ModuleManager:
    def __init__(self, config, player, ttclient, service_manager):
        self.downloader = Downloader(config, ttclient)
        self.streamer = Streamer(service_manager)
        self.task_scheduler = TaskScheduler()
