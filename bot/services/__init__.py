import logging

from bot.services import vk, yt

class ServiceManager:
    def __init__(self, config):
        self.available_services = {}
        for service_name in config['available_services']:
            service_class = globals()[service_name].Service
            self.available_services[service_name] = service_class(config['available_services'][service_name])
        self.service = self.available_services[config['default_service']]

    def initialize(self):
        logging.debug('Initializing services')
        for service in self.available_services.values():
            service.initialize()
        logging.debug('Services initialized')
