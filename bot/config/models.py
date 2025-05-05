from typing import Any, Dict, List, Union

from pydantic import BaseModel


class GeneralModel(BaseModel):
    language: str = "en"
    send_channel_messages: bool = True
    cache_file_name: str = "TTMediaBotCache.dat"
    blocked_commands: List[str] = []
    delete_uploaded_files_after: int = 300
    time_format: str = r"%H:%M"
    start_commands: List[str] = []

class SoundDevicesModel(BaseModel):
    output_device: int = 0
    input_device: int = 0


class PlayerModel(BaseModel):
    default_volume: int = 50
    max_volume: int = 100
    volume_fading: bool = True
    volume_fading_interval: float = 0.025
    seek_step: int = 5
    player_options: Dict[str, Any] = {}

class TeamTalkUserModel(BaseModel):
    admins: List[str] = ["admin"]
    banned_users: List[str] = []


class EventHandlingModel(BaseModel):
    load_event_handlers: bool = False
    event_handlers_file_name: str = "event_handlers.py"


class TeamTalkModel(BaseModel):
    hostname: str = "localhost"
    tcp_port: int = 10333
    udp_port: int = 10333
    encrypted: bool = False
    nickname: str = "TTMediaBot"
    status: str = ""
    gender: str = "n"
    username: str = ""
    password: str = ""
    channel: Union[int, str] = "/"
    channel_password: str = ""
    license_name: str = ""
    license_key: str = ""
    reconnection_attempts: int = -1
    reconnection_timeout: int = 10
    users: TeamTalkUserModel = TeamTalkUserModel()
    event_handling: EventHandlingModel = EventHandlingModel()


class VkModel(BaseModel):
    enabled: bool = True
    token: str = ""


class YtModel(BaseModel):
    enabled: bool = True
class YtModel(BaseModel):
    enabled: bool = True
    cookiefile_path: str = ""


class YamModel(BaseModel):
    enabled: bool = True
    token: str = ""


class ServicesModel(BaseModel):
    default_service: str = "vk"
    vk: VkModel = VkModel()
    yam: YamModel = YamModel()
    yt: YtModel = YtModel()


class LoggerModel(BaseModel):
    log: bool = True
    level: str = "INFO"
    format: str = "%(levelname)s [%(asctime)s]: %(message)s in %(threadName)s file: %(filename)s line %(lineno)d function %(funcName)s"
    mode: Union[int, str] = "FILE"
    file_name: str = "TTMediaBot.log"
    max_file_size: int = 0
    backup_count: int = 0


class ShorteningModel(BaseModel):
    shorten_links: bool = False
    service: str = "clckru"
    service_params: Dict[str, Any] = {}


class ConfigModel(BaseModel):
    config_version: int = 0
    general: GeneralModel = GeneralModel()
    sound_devices: SoundDevicesModel = SoundDevicesModel()
    player: PlayerModel = PlayerModel()
    teamtalk: TeamTalkModel = TeamTalkModel()
    services: ServicesModel = ServicesModel()
    logger: LoggerModel = LoggerModel()
    shortening: ShorteningModel = ShorteningModel()
