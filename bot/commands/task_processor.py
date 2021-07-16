from threading import Thread
from queue import Queue

class TaskProcessor(Thread):
    def __init__(self, command_processor):
        super().__init__(daemon=True)
        self.command_processor = command_processor
        self.task_queue = Queue()

    def run(self):
        while True:
            task = self.task_queue.get()
            if task.command_id == self.command_processor.current_command_id:
                task.function(*task.args, **task.kwargs)



class Task:
    def __init__(self, command_id, cancelable, function, *args, **kwargs):
        self.command_id = command_id
        self.cancelable = cancelable
        self.function = function
        self.args = args
        self.kwargs = kwargs
