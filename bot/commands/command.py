
class Command:  
    def __init__(self, command_processor):
        self.cache = command_processor.cache
        self.command_processor = command_processor
        self.config = command_processor.config
        self.module_manager = command_processor.module_manager
        self.service_manager = command_processor.service_manager
        self.player = command_processor.player
        self.ttclient = command_processor.ttclient

    @property
    def help(self):
        return _("help text not found")


class AdminCommand(Command):
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.bot = command_processor.bot
