from __future__ import annotations
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from urllib.parse import urlparse
import logging
import mpv
from vkpymusic import Service

if TYPE_CHECKING:
    from bot import Bot

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
            "vk.com", "://vk.com", "vkontakte.ru", 
            "www.vkontakte.ru", "://vk.com", "m.vkontakte.ru"
        ]
        self.is_enabled = config.enabled
        self.error_message = ""
        self.warning_message = ""
        self.help = ""
        self.format = "mp3"
        self.hidden = False
        self.service: Optional[Service] = None

    def initialize(self) -> None:
        self.service = Service(
            token=self.config.token, 
            user_agent=self.config.user_agent
        )

    def download(self, track: Track, file_path: str) -> None:
        if ".m3u8" not in track.url:
            super().download(track, file_path)
            return
        
        _mpv = mpv.MPV(demuxer_lavf_o="http_persistent=false", ao="null", ao_null_untimed=True)
        _mpv.play(track.url)
        _mpv.record_file = file_path
        while not _mpv.idle_active:
            pass
        _mpv.terminate()

    def _to_tracks(self, songs: List[Song]) -> List[Track]:
        """Вспомогательный метод для быстрой конвертации объектов vkpymusic в объекты Bot Track."""
        tracks = [
            Track(
                service=self.name,
                url=song.url,
                name=f"{song.artist} - {song.title}",
                format=self.format,
            )
            for song in songs if song.url
        ]
        if not tracks:
            raise errors.NothingFoundError()
        return tracks

    def get(
        self,
        url: str,
        extra_info: Optional[Dict[str, Any]] = None,
        process: bool = False,
    ) -> List[Track]:
        path = urlparse(url).path.lstrip("/")
        if path.startswith("video-"):
            raise errors.ServiceError()

        try:
            # 1. Ссылка на плейлист или альбом
            if "music/" in path:
                owner_id, playlist_id = path.split("/")[-1].split("_")
                playlist = self.service.get_songs_by_playlist_id(int(owner_id), int(playlist_id))
                songs = playlist.songs if playlist else []

            # 2. Ссылка на конкретный трек (audioXXXX_XXXX)
            elif "audio" in path:
                owner_id, song_id = path.replace("audio", "").split("_")
                song = self.service.get_song_by_id(int(owner_id), int(song_id))
                songs = [song] if song else []

            # 3. Прямой ID пользователя или сообщества (например, ://vk.com или ://vk.com)
            else:
                songs = self.service.get_songs_by_userid(int(path), count=100)

            return self._to_tracks(songs)

        except (ValueError, Exception) as e:
            logging.error(f"Ошибка при обработке VK URL '{url}': {e}")
            raise errors.NothingFoundError()

    def search(self, query: str) -> List[Track]:
        if not self.service:
            raise errors.ServiceError("Сервис VK не инициализирован")

        songs = self.service.search_songs_by_text(query, self.config.tracks_limit)
        return self._to_tracks(songs)
