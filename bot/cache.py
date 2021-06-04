from collections import deque
import pickle

from bot import vars


class Cache(dict):
    def __init__(self, config):
        host = '{}:{}'.format(config['teamtalk']['hostname'], config['teamtalk']['tcp_port'])
        try:
            with open(vars.cache_file_name, 'rb') as f:
                self.data = pickle.load(f)
            host_data = self.data[host]
        except FileNotFoundError:
            self.data = {}
            self.data[host] = {'history': deque(maxlen=vars.history_max_lenth), 'favorites':  {}}
            host_data = self.data[host]
        except KeyError:
            self.data[host] = {'history': deque(maxlen=vars.history_max_lenth), 'favorites': {}}
            host_data = self.data[host]
        self.history = host_data['history']
        self.favorites = host_data['favorites']

    def save(self):
        with open(vars.cache_file_name, 'wb') as f:
            pickle.dump(self.data, f)
