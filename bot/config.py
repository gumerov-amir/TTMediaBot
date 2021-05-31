import json
import os
import sys

from bot import vars






class Config(dict):
    def __init__(self, file_name):
            if os.path.isfile(config_file):
            self.file_name = file_name
        elif os.path.isfile(os.path.join(vars.directory, config_file)):
            self.file_name = os.path.join(vars.directory, file_name)
        else:
            sys.exit('Incorrect config file path')
        with open(self.file_name, 'r', encoding='UTF-8') as f:
            config_dict = json.load(f)
        super().__init__(config_dict)

    def save(self):
        with open(self.file_name, 'w', encoding='UTF-8') as f:
            json.dump(self, f, indent=4)

