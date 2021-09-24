import json
import sys

import portalocker

from bot import utils

default_config = {
    "general": {
        "language": "en",
        "send_channel_messages": True,
        "cache_file_name": "TTMediaBotCache.dat",
        "blocked_commands": [],
        "delete_uploaded_files_after": 300,
        "time_format": r"%H:%M",
        "load_event_handlers": False,
        "event_handlers_file_name": "event_handlers.py",
    },
    "sound_devices": {
        "output_device": 0,
        "input_device": 0
    },
    "player": {
        "default_volume": 50,
        "max_volume": 100,
        "volume_fading": True,
        "volume_fading_interval": 0.025,
        "seek_step": 5,
        "player_options": {},
    },
    "teamtalk": {
        "hostname": "localhost",
        "tcp_port": 10333,
        "udp_port": 10333,
        "encrypted": False,
        "nickname": "TTMediaBot",
        "status": "",
        "gender": "n",
        "username": "",
        "password": "",
        "channel": "/",
        "channel_password": "",
        "license_name": "",
        "license_key": "",
        "reconnection_attempts": -1,
        "reconnection_timeout": 10,
        "users": {
            "admins": ["admin"],
            "banned_users": []
        }
    },
    "services": {
        "available_services": {
            "vk": {
                "token": "",
            },
            "yt": {}
        },
        "default_service": "vk"
    },
    "logger": {
        "log": True,
        "level": "INFO",
        "format": "%(levelname)s [%(asctime)s]: %(message)s in %(threadName)s file: %(filename)s line %(lineno)d function %(funcName)s",
        "mode": "STDOUT_AND_FILE",
        "file_name": "TTMediaBot.log",
        "max_file_size": 0,
        "backup_count": 0
    }
}


def save_default_file():
    with open(utils.get_abs_path("config_default.json"), "w") as f:
        json.dump(default_config, f, indent=4, ensure_ascii=False)


class Config(dict):
    def __init__(self, file_name):
        if file_name:
            if utils.check_file_path(file_name):
                self.file_name = file_name
                with open(self.file_name, 'r', encoding='UTF-8') as f:
                    try:
                        config_dict = json.load(f)
                    except json.decoder.JSONDecodeError as e:
                        sys.exit("Syntax error in configuration file: " + str(e))
                self.file_locker = portalocker.Lock(self.file_name, timeout=0, flags=portalocker.LOCK_EX|portalocker.LOCK_NB)
                try:
                    self.file_locker.acquire()
                except portalocker.exceptions.LockException:
                    raise PermissionError()
            else:
                sys.exit("Incorrect configuration file path")
        else:
            config_dict = {}
        filled_config_dict = self.fill(config_dict, default_config)
        types_dict = self.get_types_dict(default_config)
        types_dict["teamtalk"]["channel"] = (int, str)
        types_dict["logger"]["mode"] = (int, str)
        self.check_types(filled_config_dict, types_dict)
        super().__init__(filled_config_dict)

    def close(self):
        self.file_locker.release()

    def check_types(self, data, template):
        type_names_dict = {int: "integer", str: "string", float: "float", bool: "boolean", list: "list", dict: "dictionary"}
        for key in template:
            if type(template[key]) == dict:
                self.check_types(data[key], template[key])
            elif not type(data[key]) in template[key]:
                sys.exit("Invalid type: \"{}\" param in config must be {} not {}".format(key, " or ".join([type_names_dict[i] for i in template[key]]), type_names_dict[type(data[key])]))

    def fill(self, data, template):
        result = {}
        for key in template:
            if key in data and type(template[key]) == dict:
                result[key] = self.fill(data[key], template[key])
                del data[key]
            elif key in data:
                result[key] = data[key]
                del data[key]
            else:
                result[key] = template[key]
        result.update(data)
        return result

    def get_types_dict(self, template):
        result = {}
        for key in template:
            if isinstance(template[key], dict):
                result[key] = self.get_types_dict(template[key])
            else:
                result[key] = (type(template[key]),)
        return result

    def save(self):
        self.file_locker.release()
        with open(self.file_name, 'w', encoding='UTF-8') as f:
            json.dump(self, f, indent=4, ensure_ascii=False)
        self.file_locker.acquire()
