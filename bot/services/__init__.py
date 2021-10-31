from __future__ import annotations
import logging
from sys import exec_prefix
from typing import TYPE_CHECKING

from bot import errors
from bot.services import vk, yt

if TYPE_CHECKING:
    from bot import Bot


class ServiceManager:
    def __init__(self, bot: Bot):
        self.config = bot.config.services
        self.available_services = {}
        self.fallback_service = 'yt'
        for service_name in self.config.available_services:
            service_class = globals()[service_name].Service
            self.available_services[service_name] = service_class(self.config.available_services[service_name])
        self.service = self.available_services[self.config.default_service]
        import builtins
        builtins.__dict__["get_service_by_name"] = self.get_service_by_name


    def initialize(self):
        logging.debug('Initializing services')
        unavailable_services = []
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

    def get_service_by_name(self, name):
        if not isinstance(name, str):
            raise errors.InvalidArgumentError()
        try:
            service = self.available_services[name]
            return service
        except KeyError as e:
            raise errors.ServiceNotFoundError(str(e))
