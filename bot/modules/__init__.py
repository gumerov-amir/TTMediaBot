from .streamer import Streamer


class ModuleManager:
    def __init__(self, player, ttclient, service_manager):
        self.streamer = Streamer(service_manager)
