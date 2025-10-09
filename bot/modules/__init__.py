from __future__ import annotations

from typing import TYPE_CHECKING

from bot.modules.shortener import Shortener
from bot.modules.streamer import Streamer
from bot.modules.uploader import Uploader

if TYPE_CHECKING:
    from bot import Bot


class ModuleManager:
    def __init__(self, bot: Bot) -> None:
        self.shortener = (
            Shortener(bot.config.shortening)
            if bot.config.shortening.shorten_links
            else None
        )
        self.streamer = Streamer(bot)
        self.uploader = Uploader(bot)
