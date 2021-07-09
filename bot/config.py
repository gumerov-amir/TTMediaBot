import json
import sys

import portalocker

from bot import utils

default_config = {
    "general": {
        "language": "en",
        "cache_file_name": "TTMediaBotCache.dat",
        "blocked_commands": [],
        "send_channel_messages": True,
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
        "player_options": {
            "video": False,
            "ytdl": False
        },
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
        "reconnection_timeout": 0,
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
        "mode": 2,
        "file_name": "TTMediaBot.log",
        "max_file_size": 0,
        "backup_count": 0
    }
}

class Config(dict):
    def __init__(self, file_name):
        if file_name:
            if utils.check_file_path(file_name):
                self.file_name = file_name
                with open(self.file_name, 'r', encoding='UTF-8') as f:
                    try:
                        config_dict = json.load(f)
                    except json.decoder.JSONDecodeError as e:
                        print("Syntax error in configuration file:", e)
                        sys.exit(1)
                self.file_locker = portalocker.Lock(self.file_name, timeout=0, flags=portalocker.LOCK_EX|portalocker.LOCK_NB)
                try:
                    self.file_locker.acquire()
                except portalocker.exceptions.LockException:
                    raise PermissionError()
            else:
                print("Incorrect config file path")
                sys.exit(1)
        else:
            config_dict = {}
        super().__init__(self.fill(config_dict, default_config))

    def close(self):
        self.file_locker.release()

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

    def save(self):
        self.file_locker.release()
        with open(self.file_name, 'w', encoding='UTF-8') as f:
            json.dump(self, f, indent=4, ensure_ascii=False)
        self.file_locker.acquire()
