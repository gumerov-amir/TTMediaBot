from __future__ import annotations
from abc import ABC, abstractmethod
import logging
from typing import Any, Any, Dict, List, TYPE_CHECKING

from bot import errors
from bot,player.track import Track
from bot.services import vk, yt

services = {"vk": vk, "yt": yt}

if TYPE_CHECKING:
    from bot import Bot


class Service(ABC):
    @abstractmethod
    def get(self, *args, **kwargs) -> List[Track]: ...

    @abstractmethod
    def search(self, query) -> List[Track]): ...


class ServiceManager:
    def __init__(self, bot: Bot) -> None:
        self.config = bot.config.services
        self.available_services: Dict[str, Service] = {}
        self.fallback_service = 'yt'
        for service_name in self.config.available_services:
            service_class = services[service_name].Service
            self.available_services[service_name] = service_class(getattr(self.config, service_name))
        self.service = self.available_services[self.config.default_service]
        import builtins
        builtins.__dict__["get_service_by_name"] = self.get_service_by_name


    def initialize(self) -> None:
        logging.debug('Initializing services')
        unavailable_services: List[Service] = []
        for service in self.available_services.values():
            try:
                service.initialize()
            except errors.ServiceError:
                unavailable_services.append(service)
                if self.service == service:
                    self.service = self.available_services[self.fallback_service]
        for service in unavailable_services:
            del self.available_services[service.name]
        logging.debug('Services initialized')

    def get_service_by_name(self, name: str) -> Service:
        try:
            service = self.available_services[name]
            return service
        except KeyError as e:
            raise errors.ServiceNotFoundError(str(e))
