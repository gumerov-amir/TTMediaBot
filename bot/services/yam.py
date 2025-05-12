from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

if TYPE_CHECKING:
    from bot import Bot
    from bot.config.models import YamModel

from yandex_music import Client
from yandex_music.exceptions import NetworkError, UnauthorizedError

from bot import errors
from bot.player.enums import TrackType
from bot.player.track import Track
from bot.services import Service


class YamService(Service):
    def __init__(self, bot: Bot, config: YamModel) -> None:
        self.bot = bot
        self.config = config
        self.name = "yam"
        self.hostnames = ["music.yandex.ru"]
        self.is_enabled = self.config.enabled
        self.error_message = ""
        self.warning_message = ""
        self.help = ""
        self.hidden = False
        self.format = ".mp3"

    def initialize(self) -> None:
        self.api = Client(token=self.config.token)
        try:
            self.api.init()
        except (UnauthorizedError, NetworkError) as e:
            logging.exception(e)
            raise errors.ServiceError(e)
        if not self.api.account_status().account.uid:
            self.warning_message = self.bot.translator.translate(
                "Token is not provided",
            )
        elif not self.api.account_status().plus["has_plus"]:
            self.warning_message = self.bot.translator.translate(
                "You don't have Yandex Plus",
            )

    def get(
        self,
        url: str,
        extra_info: dict[str, Any] | None = None,
        process: bool = False,
    ) -> list[Track]:
        if not process:
            parsed_data = urlparse(url)
            path = parsed_data.path
            if "/album/" in path and "/track/" in path:
                split_path = path.split("/")
                real_id = split_path[4] + ":" + split_path[2]
                return self.get(None, extra_info={"track_id": real_id}, process=True)
            if "/album/" in path:
                tracks = []
                album = self.api.albums_with_tracks(path.split("/")[2])
                if len(album.volumes) == 0 or len(album.volumes[0]) == 0:
                    raise errors.ServiceError
                for volume in album.volumes:
                    for track in volume:
                        tracks.append(
                            Track(
                                service=self.name,
                                extra_info={"track_id": track.track_id},
                                type=TrackType.Dynamic,
                            ),
                        )
                return tracks
            if "/artist/" in path:
                tracks = []
                artist_tracks = self.api.artists_tracks(path.split("/")[2]).tracks
                if len(artist_tracks) == 0:
                    raise errors.ServiceError
                for track in artist_tracks:
                    tracks.append(
                        Track(
                            service=self.name,
                            extra_info={"track_id": track.track_id},
                            type=TrackType.Dynamic,
                        ),
                    )
                return tracks
            if "users" in path and "playlist" in path:
                tracks = []
                split_path = path.split("/")
                user_id = split_path[2]
                kind = split_path[4]
                playlist = self.api.users_playlists(kind=kind, user_id=user_id)
                if playlist.track_count == 0:
                    raise errors.ServiceError
                for track in playlist.tracks:
                    tracks.append(
                        Track(
                            service=self.name,
                            extra_info={"track_id": track.track_id},
                            type=TrackType.Dynamic,
                        ),
                    )
                return tracks
            return None
        track = self.api.tracks(extra_info["track_id"])[0]
        return [
            Track(
                service=self.name,
                name="{} - {}".format(
                    " & ".join(track.artists_name()),
                    track.title,
                ),
                url=track.get_download_info(get_direct_links=True)[0].direct_link,
                type=TrackType.Default,
                format=self.format,
            ),
        ]

    def search(self, query: str) -> list[Track]:
        tracks: list[Track] = []
        found_tracks = self.api.search(text=query, nocorrect=True, type_="all").tracks
        if found_tracks:
            for track in found_tracks.results:
                tracks.append(
                    Track(
                        service=self.name,
                        type=TrackType.Dynamic,
                        extra_info={"track_id": track.track_id},
                    ),
                )
        found_podcast_episodes = self.api.search(
            text=query,
            nocorrect=True,
            type_="podcast_episode",
        ).podcast_episodes
        if found_podcast_episodes:
            for podcast_episode in found_podcast_episodes.results:
                tracks.append(
                    Track(
                        service=self.name,
                        type=TrackType.Dynamic,
                        extra_info={"track_id": podcast_episode.track_id},
                    ),
                )
        if tracks:
            return tracks
        msg = ""
        raise errors.NothingFoundError(msg)
