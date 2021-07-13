class Task:
    def __init__(self, command_id, function, *args, **kwargs):
        self.command_id = command_id
        self.function = function
        self.args = args
        self.kwargs = kwargs
