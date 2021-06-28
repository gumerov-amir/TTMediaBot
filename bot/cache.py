from collections import deque
import portalocker
import os
import pickle

from bot import vars


class Cache:
    def __init__(self, file_name):
        self.file_name = file_name
        try:
            with open(self.file_name, 'rb') as f:
                self.data = pickle.load(f)
        except FileNotFoundError:
            self.data = {'history': deque(maxlen=vars.history_max_lenth), 'favorites':  {}}
            with open(self.file_name, 'wb') as f:
                pickle.dump(self.data, f)
        self.file_locker = portalocker.Lock(self.file_name, timeout=0, flags=portalocker.LOCK_EX|portalocker.LOCK_NB)
        try:
            self.file_locker.acquire()
        except portalocker.exceptions.LockException:
            raise PermissionError()
        self.history = self.data['history']
        self.favorites = self.data['favorites']

    def close(self):
        self.file_locker.release()

    def save(self):
        self.file_locker.release()
        with open(self.file_name, 'wb') as f:
                pickle.dump(self.data, f)
        self.file_locker.acquire()


