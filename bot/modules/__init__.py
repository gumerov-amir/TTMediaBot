from __future__ import annotations
from typing import TYPE_CHECKING

from bot.modules.uploader import Uploader
from bot.modules.shortener import Shortener
from bot.modules.streamer import Streamer

# from bot.modules.task_scheduler import TaskScheduler

if TYPE_CHECKING:
    from bot import Bot


class ModuleManager:
    def __init__(self, bot: Bot):
        self.shortener = (
            Shortener(bot.config.shortening)
            if bot.config.shortening.shorten_links
            else None
        )
        self.streamer = Streamer(bot)
        # self.task_scheduler = TaskScheduler(bot)
        self.uploader = Uploader(bot)
