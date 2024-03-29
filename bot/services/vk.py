from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from urllib.parse import urlparse

if TYPE_CHECKING:
    from bot import Bot

import mpv
import requests
import vk_api

from bot.config.models import VkModel
from bot.player.track import Track
from bot.services import Service as _Service
from bot import errors


class VkService(_Service):
    def __init__(self, bot: Bot, config: VkModel) -> None:
        self.bot = bot
        self.config = config
        self.name = "vk"
        self.hostnames = [
            "vk.com",
            "www.vk.com",
            "vkontakte.ru",
            "www.vkontakte.ru",
            "m.vk.com",
            "m.vkontakte.ru",
        ]
        self.is_enabled = config.enabled
        self.error_message = ""
        self.warning_message = ""
        self.help = ""
        self.format = "mp3"
        self.hidden = False

    def download(self, track: Track, file_path: str) -> None:
        if ".m3u8" not in track.url:
            super().download(track, file_path)
            return
        _mpv = mpv.MPV(
            **{
                "demuxer_lavf_o": "http_persistent=false",
                "ao": "null",
                "ao_null_untimed": True,
            }
        )
        _mpv.play(track.url)
        _mpv.record_file = file_path
        while not _mpv.idle_active:
            pass
        _mpv.terminate()

    def initialize(self) -> None:
        http = requests.Session()
        http.headers.update(
            {
                "User-agent": "VKAndroidApp/6.2-5091 (Android 9; SDK 28; samsungexynos7870; samsung j6lte; 720x1450)"
            }
        )
        self._session = vk_api.VkApi(
            token=self.config.token, session=http, api_version="5.89"
        )
        self.api = self._session.get_api()
        try:
            self.api.account.getInfo()
        except (
            vk_api.exceptions.ApiHttpError,
            vk_api.exceptions.ApiError,
            requests.exceptions.ConnectionError,
        ) as e:
            logging.error(e)
            raise errors.ServiceError(e)

    def get(
        self,
        url: str,
        extra_info: Optional[Dict[str, Any]] = None,
        process: bool = False,
    ) -> List[Track]:
        parsed_url = urlparse(url)
        path = parsed_url.path[1::]
        if path.startswith("video-"):
            raise errors.ServiceError()
        try:
            if "music/" in path:
                id = path.split("/")[-1]
                ids = id.split("_")
                o_id = ids[0]
                p_id = ids[1]
                audios = self.api.audio.get(owner_id=int(o_id), album_id=int(p_id))
            elif "audio" in path:
                audios = {
                    "count": 1,
                    "items": self.api.audio.getById(audios=[path[5::]]),
                }
            else:
                object_info = self.api.utils.resolveScreenName(screen_name=path)
                if object_info["type"] == "group":
                    id = -object_info["object_id"]
                else:
                    id = object_info["object_id"]
                audios = self.api.audio.get(owner_id=id, count=6000)
            if "count" in audios and audios["count"] > 0:
                tracks: List[Track] = []
                for audio in audios["items"]:
                    if "url" not in audio or not audio["url"]:
                        continue
                    track = Track(
                        service=self.name,
                        url=audio["url"],
                        name="{} - {}".format(audio["artist"], audio["title"]),
                        format=self.format,
                    )
                    tracks.append(track)
                if tracks:
                    return tracks
                else:
                    raise errors.NothingFoundError()
            else:
                raise errors.NothingFoundError
        except NotImplementedError as e:
            print("vk get error")
            print(e)
            raise NotImplementedError()

    def search(self, query: str) -> List[Track]:
        results = self.api.audio.search(q=query, count=300, sort=0)
        if "count" in results and results["count"] > 0:
            tracks: List[Track] = []
            for track in results["items"]:
                if "url" not in track or not track["url"]:
                    continue
                track = Track(
                    service=self.name,
                    url=track["url"],
                    name="{} - {}".format(track["artist"], track["title"]),
                    format=self.format,
                )
                tracks.append(track)
            if tracks:
                return tracks
            else:
                raise errors.NothingFoundError()
        else:
            raise errors.NothingFoundError()
