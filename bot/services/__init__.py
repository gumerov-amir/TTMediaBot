from __future__ import annotations
from abc import ABC, abstractmethod
import logging
from typing import Any, Any, Dict, List, TYPE_CHECKING

from bot import app_vars, errors
from bot.player.track import Track

if TYPE_CHECKING:
    from bot import Bot


class Service(ABC):
    @abstractmethod
    def get(self, *args, **kwargs) -> List[Track]: ...

    @abstractmethod
    def search(self, query) -> List[Track]: ...


from bot.services.vk import VkService
from bot.services.yt import YtService


class ServiceManager:
    def __init__(self, bot: Bot) -> None:
        self.config = bot.config.services
        self.services: Dict[str, Service] = {
            "vk": VkService(self.config.vk),
            "yt": YtService(self.config.yt)
        }
        self.service: Service = self.services[self.config.default_service]
        self.fallback_service = app_vars.fallback_service
        import builtins
        builtins.__dict__["get_service_by_name"] = self.get_service_by_name


    def initialize(self) -> None:
        logging.debug('Initializing services')
        for service in self.services.values():
            try:
                service.initialize()
            except errors.ServiceError as e:
                service.is_enabled = False
                service.error_message = str(e)
                if self.service == service:
                    self.service = self.services[self.fallback_service]
        logging.debug('Services initialized')

    def get_service_by_name(self, name: str) -> Service:
        try:
            service = self.services[name]
            if not service.is_enabled:
                raise errors.ServiceIsDisabledError(service.error_message)
            return service
        except KeyError as e:
            raise errors.ServiceNotFoundError(str(e))
