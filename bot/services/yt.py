from __future__ import annotations
import logging
import os
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from bot import Bot

from yt_dlp import YoutubeDL
from yt_dlp.downloader import get_suitable_downloader
from youtubesearchpython import VideosSearch

from bot.config.models import YtModel

from bot.player.enums import TrackType
from bot.player.track import Track
from bot.services import Service as _Service
from bot import errors


class YtService(_Service):
    def __init__(self, bot: Bot, config: YtModel):
        self.bot = bot
        self.config = config
        self.name = "yt"
        self.hostnames = []
        self.is_enabled = self.config.enabled
        self.error_message = ""
        self.warning_message = ""
        self.help = ""
        self.hidden = False

    def initialize(self):
        self._ydl_config = {
            "skip_download": True,
            "format": "m4a/bestaudio/best[protocol!=m3u8_native]/best",
            "socket_timeout": 5,
            "logger": logging.getLogger("root"),
        }

        if self.config.cookiefile_path and os.path.isfile(self.config.cookiefile_path):
            self._ydl_config |= {"cookiefile": self.config.cookiefile_path}
            
    def download(self, track: Track, file_path: str) -> None:
        info = track.extra_info
        if not info:
            super().download(track, file_path)
            return
        with YoutubeDL(self._ydl_config) as ydl:
            dl = get_suitable_downloader(info)(ydl, self._ydl_config)
            dl.download(file_path, info)

    def get(
        self,
        url: str,
        extra_info: Optional[Dict[str, Any]] = None,
        process: bool = False,
    ) -> List[Track]:
        if not (url or extra_info):
            raise errors.InvalidArgumentError()
        with YoutubeDL(self._ydl_config) as ydl:
            if not extra_info:
                info = ydl.extract_info(url, process=False)
            else:
                info = extra_info
            info_type = None
            if "_type" in info:
                info_type = info["_type"]
            if info_type == "url" and not info["ie_key"]:
                return self.get(info["url"], process=False)
            elif info_type == "playlist":
                tracks: List[Track] = []
                for entry in info["entries"]:
                    data = self.get("", extra_info=entry, process=False)
                    tracks += data
                return tracks
            if not process:
                return [
                    Track(service=self.name, extra_info=info, type=TrackType.Dynamic)
                ]
            try:
                stream = ydl.process_ie_result(info)
            except Exception:
                raise errors.ServiceError()
            if "url" in stream:
                url = stream["url"]
            else:
                raise errors.ServiceError()
            title = stream["title"]
            if "uploader" in stream:
                title += " - {}".format(stream["uploader"])
            format = stream["ext"]
            if "is_live" in stream and stream["is_live"]:
                type = TrackType.Live
            else:
                type = TrackType.Default
            return [
                Track(service=self.name, url=url, name=title, format=format, type=type, extra_info=stream)
            ]

    def search(self, query: str) -> List[Track]:
        search = VideosSearch(query, limit=300).result()
        if search["result"]:
            tracks: List[Track] = []
            for video in search["result"]:
                track = Track(
                    service=self.name, url=video["link"], type=TrackType.Dynamic
                )
                tracks.append(track)
            return tracks
        else:
            raise errors.NothingFoundError("")
