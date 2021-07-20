from bot.commands.task_processor import Task

class BaseCommand:  
    def __init__(self, command_processor):
        self._bot = command_processor.bot
        self.cache = command_processor.cache
        self.command_processor = command_processor
        self.config = command_processor.config
        self.module_manager = command_processor.module_manager
        self.service_manager = command_processor.service_manager

    @property
    def help(self):
        return _("help text not found")


class Command(BaseCommand):
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.player = command_processor.player
        self.ttclient = command_processor.ttclient


class CancelableCommand(BaseCommand):  
    def __getattr__(self, attr):
        return Obj(id(self), self._bot, [attr])

class Obj:
    def __init__(self, cmdid, bot, attrs):
        self.cmdid = cmdid
        self._bot = bot
        self.attrs = attrs

    def get(self, *args, **kwargs):
        obj = self._bot
        for attr in self.attrs:
            obj = getattr(obj, attr)
        return obj

    def __call__(self, *args, **kwargs):
        obj = self.get()
        self._bot.command_processor.task_processor.task_queue.put(Task(self.cmdid, obj, args, kwargs))

    def __getattr__(self, attr):
        return Obj(self.cmdid, self._bot, self.attrs + [attr])
