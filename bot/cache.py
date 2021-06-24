from collections import deque
import portalocker
import hashlib
import os
import pickle

from bot import vars


class Cache(dict):
    def __init__(self, config):
        try:
            self.file_name = config["general"]["cache_file_name"]
        except KeyError:
            self.file_name = vars.default_cache_file_name
        try:
            with open(self.file_name, 'rb') as f:
                self.data = pickle.load(f)
        except FileNotFoundError:
            self.data = {'history': deque(maxlen=vars.history_max_lenth), 'favorites':  {}}
            if not os.path.isdir(os.path.dirname(self.file_name)):
                os.mkdir(os.path.dirname(self.file_name))
            with open(self.file_name, 'wb') as f:
                pickle.dump(self.data, f)
        self.file_locker = portalocker.Lock(self.file_name, timeout=0, flags=portalocker.LOCK_EX|portalocker.LOCK_NB)
        self.fa = self.file_locker.acquire()
        self.history = self.data['history']
        self.favorites = self.data['favorites']

    def close(self):
        self.file_locker.release()

    def save(self):
        self.file_locker.release()
        with open(self.file_name, 'wb') as f:
                pickle.dump(self.data, f)
        self.file_locker.acquire()


