from __future__ import annotations
from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import downloader

from bot import app_vars, errors

if TYPE_CHECKING:
    from bot import Bot
    from bot.player.track import Track


class Service(ABC):
    name: str
    is_enabled: bool
    hidden: bool
    hostnames: List[str]
    error_message: str
    warning_message: str
    help: str

    def download(self, track: Track, file_path: str) -> None:
        downloader.download_file(track.url, file_path)

    @abstractmethod
    def get(
        self,
        url: str,
        extra_info: Optional[Dict[str, Any]] = None,
        process: bool = False,
    ) -> List[Track]:
        ...

    @abstractmethod
    def initialize(self) -> None:
        ...

    @abstractmethod
    def search(self, query: str) -> List[Track]:
        ...


from bot.services.vk import VkService
from bot.services.yam import YamService
from bot.services.yt import YtService


class ServiceManager:
    def __init__(self, bot: Bot) -> None:
        self.config = bot.config.services
        self.services: Dict[str, Service] = {
            "vk": VkService(bot, self.config.vk),
            "yam": YamService(bot, self.config.yam),
            "yt": YtService(bot, self.config.yt),
        }
        self.service: Service = self.services[self.config.default_service]
        self.fallback_service = app_vars.fallback_service
        import builtins

        builtins.__dict__["get_service_by_name"] = self.get_service_by_name

    def initialize(self) -> None:
        logging.debug("Initializing services")
        for service in self.services.values():
            if not service.is_enabled:
                continue
            try:
                service.initialize()
            except errors.ServiceError as e:
                service.is_enabled = False
                service.error_message = str(e)
                if self.service == service:
                    self.service = self.services[self.fallback_service]
        logging.debug("Services initialized")

    def get_service_by_name(self, name: str) -> Service:
        try:
            service = self.services[name]
            if not service.is_enabled:
                raise errors.ServiceIsDisabledError(service.error_message)
            return service
        except KeyError as e:
            raise errors.ServiceNotFoundError(str(e))
