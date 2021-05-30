import json


class Config(dict):
    def __init__(self, file_name):
        self.file_name = file_name
        with open(file_name, 'r', encoding='UTF-8') as f:
            config_dict = json.load(f)
        super().__init__(config_dict)

    def save(self):
        with open(self.file_name, 'w', encoding='UTF-8') as f:
            json.dump(self, f, indent=4)

