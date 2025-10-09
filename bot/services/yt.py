from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from bot import Bot
    from bot.config.models import YtModel

from youtubesearchpython import VideosSearch
from yt_dlp import YoutubeDL
from yt_dlp.downloader import get_suitable_downloader

from bot import errors
from bot.player.enums import TrackType
from bot.player.track import Track
from bot.services import Service as _Service


class YtService(_Service):
    def __init__(self, bot: Bot, config: YtModel) -> None:
        self.bot = bot
        self.config = config
        self.name = "yt"
        self.hostnames = []
        self.is_enabled = self.config.enabled
        self.error_message = ""
        self.warning_message = ""
        self.help = ""
        self.hidden = False

    def initialize(self) -> None:
        self._ydl_config = {
            "skip_download": True,
            "format": "m4a/bestaudio/best[protocol!=m3u8_native]/best",
            "socket_timeout": 5,
            "logger": logging.getLogger("root"),
        }

        if self.config.cookiefile_path and Path(self.config.cookiefile_path).is_file():
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
        extra_info: dict[str, Any] | None = None,
        process: bool = False,
    ) -> list[Track]:
        if not (url or extra_info):
            raise errors.InvalidArgumentError
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
            if info_type == "playlist":
                tracks: list[Track] = []
                for entry in info["entries"]:
                    data = self.get("", extra_info=entry, process=False)
                    tracks += data
                return tracks
            if not process:
                return [
                    Track(
                        service=self.name, extra_info=info, track_type=TrackType.Dynamic
                    ),
                ]
            try:
                stream = ydl.process_ie_result(info)
            except Exception as e:
                raise errors.ServiceError from e
            if "url" in stream:
                url = stream["url"]
            else:
                raise errors.ServiceError
            title = stream["title"]
            if "uploader" in stream:
                title += " - {}".format(stream["uploader"])
            track_format = stream["ext"]
            track_type = TrackType.Live if stream.get("is_live") else TrackType.Default
            return [
                Track(
                    service=self.name,
                    url=url,
                    name=title,
                    track_format=track_format,
                    track_type=track_type,
                    extra_info=stream,
                ),
            ]

    def search(self, query: str) -> list[Track]:
        search = VideosSearch(query, limit=300).result()
        if search["result"]:
            tracks: list[Track] = []
            for video in search["result"]:
                track = Track(
                    service=self.name,
                    url=video["link"],
                    track_type=TrackType.Dynamic,
                )
                tracks.append(track)
            return tracks
        msg = ""
        raise errors.NothingFoundError(msg)
