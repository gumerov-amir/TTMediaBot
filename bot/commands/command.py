from bot.commands.task_processor import Task

class Command:  
    def __init__(self, command_processor):
        self._task_processor = command_processor.task_processor
        self._bot = command_processor.bot
        self.cache = command_processor.cache
        self.command_processor = command_processor
        self.config = command_processor.config
        self.module_manager = command_processor.module_manager
        self.player = command_processor.player
        self.service_manager = command_processor.service_manager
        self.ttclient = command_processor.ttclient

    @property
    def help(self):
        return _("help text not found")

    def run_async(self, func, *args, **kwargs):
        self._task_processor.task_queue.put(Task(id(self), func, args, kwargs))
