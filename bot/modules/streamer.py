from __future__ import annotations

import os
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from bot import errors
from bot.player.enums import TrackType
from bot.player.track import Track

if TYPE_CHECKING:
    from bot import Bot


class Streamer:
    def __init__(self, bot: Bot) -> None:
        self.allowed_schemes: list[str] = ["http", "https", "rtmp", "rtsp"]
        self.config = bot.config
        self.service_manager = bot.service_manager

    def get(self, url: str, is_admin: bool) -> list[Track]:
        parsed_url = urlparse(url)
        if parsed_url.scheme in self.allowed_schemes:
            track = Track(url=url, type=TrackType.Direct)
            fetched_data = [track]
            for service in self.service_manager.services.values():
                try:
                    if (
                        parsed_url.hostname in service.hostnames
                        or service.name == self.service_manager.fallback_service
                    ):
                        fetched_data = service.get(url)
                        break
                except errors.ServiceError:
                    continue
                except Exception:
                    if service.name == self.service_manager.fallback_service:
                        return [
                            track,
                        ]
            if len(fetched_data) == 1 and fetched_data[0].url.startswith(
                str(track.url),
            ):
                return [
                    track,
                ]
            return fetched_data
        if is_admin:
            if os.path.isfile(url):
                track = Track(
                    url=url,
                    name=os.path.split(url)[-1],
                    format=os.path.splitext(url)[1],
                    type=TrackType.Local,
                )
                return [
                    track,
                ]
            if os.path.isdir(url):
                tracks: list[Track] = []
                for path, _, files in os.walk(url):
                    for file in sorted(files):
                        url = os.path.join(path, file)
                        name = os.path.split(url)[-1]
                        format = os.path.splitext(url)[1]
                        track = Track(
                            url=url,
                            name=name,
                            format=format,
                            type=TrackType.Local,
                        )
                        tracks.append(track)
                return tracks
            msg = ""
            raise errors.PathNotFoundError(msg)
        msg = ""
        raise errors.IncorrectProtocolError(msg)
