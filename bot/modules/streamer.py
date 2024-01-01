from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING, List
from urllib.parse import urlparse

from bot import errors
from bot.player.enums import TrackType
from bot.player.track import Track

if TYPE_CHECKING:
    from bot import Bot


class Streamer:
    def __init__(self, bot: Bot):
        self.allowed_schemes: List[str] = ["http", "https", "rtmp", "rtsp"]
        self.config = bot.config
        self.service_manager = bot.service_manager

    def get(self, url: str, is_admin: bool) -> List[Track]:
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
                str(track.url)
            ):
                return [
                    track,
                ]
            else:
                return fetched_data
        elif is_admin:
            if Path(url).is_file():
                track = Track(
                    url=url,
                    name=Path(url).name,
                    format=Path(url).suffix,
                    type=TrackType.Local,
                )
                return [
                    track,
                ]
            elif Path(url).is_dir():
                tracks: List[Track] = []
                for path in sorted(Path(url).rglob('*')):
                    print(str(path))
                    if path.is_file():
                        name = path.name
                        format = path.suffix
                        track = Track(
                            url=str(path), name=name, format=format, type=TrackType.Local
                        )
                        tracks.append(track)
                return tracks
            else:
                raise errors.PathNotFoundError("")
        else:
            raise errors.IncorrectProtocolError("")
