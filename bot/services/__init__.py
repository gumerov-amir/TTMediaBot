import logging

from bot import errors
from bot.services import vk, yt


class ServiceManager:
    def __init__(self, config):
        self.available_services = {}
        self.fallback_service = 'yt'
        for service_name in config.available_services:
            service_class = globals()[service_name].Service
            self.available_services[service_name] = service_class(config.available_services[service_name])
        self.service = self.available_services[config.default_service]

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
