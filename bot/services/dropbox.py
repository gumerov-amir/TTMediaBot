from __future__ import annotations
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from bot import Bot

from bot.config.models import DropboxModel
from bot.player.track import Track
from bot.player.enums import TrackType
from bot.services import Service as _Service


class DropboxService(_Service):
    def __init__(self, bot: Bot, config: DropboxModel) -> None:
        self.bot = bot
        self.config = config
        self.name = "dropbox"
        self.hostnames = [
            "dropbox.com",
            "www.dropbox.com",
            "dropboxusercontent.com",
        ]
        self.is_enabled = config.enabled
        self.error_message = ""
        self.warning_message = ""
        self.help = ""
        self.hidden = False

    def initialize(self) -> None:
        pass  # Nada a inicializar

    def get(
        self,
        url: str,
        extra_info: Optional[Dict[str, Any]] = None,
        process: bool = False,
    ) -> List[Track]:
        # Se dl=0, troca para dl=1
        if "dl=0" in url:
            url = url.replace("dl=0", "dl=1")

        # Retorna Direct - o mpv segue o redirect automaticamente
        return [Track(url=url, type=TrackType.Direct)]

    def search(self, query: str) -> List[Track]:
        raise NotImplementedError("Dropbox não suporta busca")
