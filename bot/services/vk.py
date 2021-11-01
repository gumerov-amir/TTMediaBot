import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests
import vk_api

from bot.player.track import Track
from bot.services import Service as _Service
from bot import errors


class Service(_Service):
    def __init__(self, config: Dict[str, Any]) -> None:
        self.name = 'vk'
        self.hostnames = ['vk.com', 'www.vk.com', 'vkontakte.ru', 'www.vkontakte.ru', 'm.vk.com', 'm.vkontakte.ru']
        self.config = config
        self.format = "mp3"
        self.hidden = False

    def initialize(self) -> None:
        http = requests.Session()
        http.headers.update({
            'User-agent': 'VKAndroidApp/4.13.1-1206 (Android 7.1.1; SDK 25; armeabi-v7a; ; ru)'
        })
        self._session = vk_api.VkApi(token=self.config['token'], session=http, api_version='5.68')
        self.api = self._session.get_api()
        try:
            self.api.account.getInfo()
        except (vk_api.exceptions.ApiHttpError, vk_api.exceptions.ApiError, requests.exceptions.ConnectionError) as e:
            logging.error(e)
            raise errors.ServiceError(e)

    def get(self, url: str) -> Optional[List[Track]]:
        parsed_url = urlparse(url)
        path = parsed_url.path[1::]
        if path.startswith('video_'):
            raise errors.ServiceError()
        try:
            if 'music/' in path:
                id = path.split('/')[-1]
                ids = id.split('_')
                o_id = ids[0]
                p_id = ids[1]
                audios: Dict[str, Any] = self.api.audio.get(owner_id=int(o_id), album_id=int(p_id))
            else:
                object_info: Dict[str, Any] = self.api.utils.resolveScreenName(screen_name=path)
                if object_info['type'] == 'group':
                    id = -object_info['object_id']
                else:
                    id = object_info['object_id']
                audios: Dict[str, Any] = self.api.audio.get(owner_id=id, count=6000)
            if 'count' in audios and audios['count'] > 0:
                tracks: List[Track] = []
                for audio in audios['items']:
                    if 'url' not in audio or not audio['url']:
                        continue
                    track = Track(url=audio['url'], name='{} - {}'.format(audio['artist'], audio['title']), format=self.format)
                    tracks.append(track)
                if tracks:
                    return tracks
                else:
                    raise errors.NothingFoundError()
            else:
                raise errors.NothingFoundError
        except NotImplementedError as e:
            print('vk get error')
            print(e)

    def search(self, text: str) -> List[Track]:
        results: Dict[str, Any] = self.api.audio.search(q=text, count=300, sort=0)
        if 'count' in results and results['count'] > 0:
            tracks: List[Track] = []
            for track in results['items']:
                if 'url' not in track or not track['url']:
                    continue
                track = Track(url=track['url'], name='{} - {}'.format(track['artist'], track['title']), format=self.format)
                tracks.append(track)
            if tracks:
                return tracks
            else:
                raise errors.NothingFoundError()
        else:
            raise errors.NothingFoundError()
