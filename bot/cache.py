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
                if 'recents' not in self.data or 'favorites' not in self.data:
                    raise KeyError()
        except:
            self.data = {'recents': deque(maxlen=vars.recents_max_lenth), 'favorites':  {}}
            with open(self.file_name, 'wb') as f:
                pickle.dump(self.data, f)
        self.file_locker = portalocker.Lock(self.file_name, timeout=0, flags=portalocker.LOCK_EX|portalocker.LOCK_NB)
        try:
            self.file_locker.acquire()
        except portalocker.exceptions.LockException:
            raise PermissionError()
        self.recents = self.data['recents']
        self.favorites = self.data['favorites']

    def close(self):
        self.file_locker.release()

    def save(self):
        self.file_locker.release()
        with open(self.file_name, 'wb') as f:
                pickle.dump(self.data, f)
        self.file_locker.acquire()


