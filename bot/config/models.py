from typing import Dict, List, Union

from pydantic import (
    BaseModel,
    StrictBool,
    StrictFloat,
    StrictInt,
    StrictStr
)


class General(BaseModel):
    language: StrictStr = "en"
    send_channel_messages: StrictBool = True
    cache_file_name: StrictStr = "TTMediaBotCache.dat"
    blocked_commands: List[StrictStr] = []
    delete_uploaded_files_after: StrictInt = 300
    time_format: StrictStr = r"%H:%M"
    load_event_handlers: StrictBool = False
    event_handlers_file_name: StrictStr = "event_handlers.py"


class SoundDevices(BaseModel):
    output_device: StrictInt = 0
    input_device: StrictInt = 0

class Player(BaseModel):
    default_volume: StrictInt = 50
    max_volume: StrictInt = 100
    volume_fading: StrictBool = True
    volume_fading_interval: StrictFloat = 0.025
    seek_step: StrictInt = 5
    player_options: dict = {"video": False, "ytdl": False}


class TeamTalk(BaseModel):
    hostname: StrictStr = "localhost"
    tcp_port: StrictInt = 10333
    udp_port: StrictInt = 10333
    encrypted: StrictBool = False
    nickname: StrictStr = "TTMediaBot"
    status: StrictStr = ""
    gender: StrictStr = "n"
    username: StrictStr = ""
    password: StrictStr = ""
    channel: Union[int, str] = "/"
    channel_password: StrictStr = ""
    license_name: StrictStr = ""
    license_key: StrictStr = ""
    reconnection_attempts: StrictInt = -1
    reconnection_timeout: StrictInt = 10
    users: Dict[str, List[str]] = {"admins": ["admin"], "banned_users": []}

class Services(BaseModel):
    available_services: Dict[str, dict] = {"vk": {"token": ""}, "yt": {}}
    default_service: StrictStr = "vk"


class Logger(BaseModel):
    log: StrictBool = True
    level: StrictStr = "INFO"
    format: StrictStr = "%(levelname)s [%(asctime)s]: %(message)s in %(threadName)s file: %(filename)s line %(lineno)d function %(funcName)s"
    mode: Union[int, str] = "File"
    file_name: StrictStr = "TTMediaBot.log"
    max_file_size: StrictInt = 0
    backup_count: StrictInt = 0


class Config(BaseModel):
    general: General = General()
    sound_devices: SoundDevices = SoundDevices()
    player: Player = Player()
    teamtalk: TeamTalk = TeamTalk()
    services: Services = Services()
    logger: Logger = Logger()
