from bot.modules.downloader import Downloader
from bot.modules.streamer import Streamer


class ModuleManager:
    def __init__(self, config, player, ttclient, service_manager):
        self.downloader = Downloader(config, ttclient)
        self.streamer = Streamer(service_manager)
