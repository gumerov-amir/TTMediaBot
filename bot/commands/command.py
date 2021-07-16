
class Command:  
    def __init__(self, command_processor):
        self._bot = command_processor.bot

    @property
    def help(self):
        return _("help text not found")

    def __getattr__(self, attr):
        return Obj([self._bot, attr])

class Obj:
    def __init__(self, attrs):
        self.attrs = attrs

    def __call__(self, *args, **kwargs):
        obj = self.attrs[0]
        for i, attr in enumerate(self.attrs):
            if i == 0:
                continue
            obj = getattr(obj, attr)
        print(obj)

    def __getattr__(self, attr):
        return Obj(self.attrs + [attr])

class AdminCommand(Command):
    def __init__(self, command_processor):
        super().__init__(command_processor)
        self.bot = command_processor.bot
