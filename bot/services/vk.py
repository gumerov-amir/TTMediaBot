import requests
import vk_api

from urllib.parse import urlparse

from bot.player.track import Track
from bot import errors


class Service:
    def __init__(self, config):
        self.name = 'vk'
        self.hostnames = ['vk.com', 'www.vk.com', 'vkontakte.ru', 'www.vkontakte.ru', 'm.vk.com', 'm.vkontakte.ru']
        self.config = config
        self.format = "mp3"

    def initialize(self):
        http = requests.Session()
        http.headers.update({
            'User-agent': 'KateMobileAndroid/47-427 (Android 6.0.1; SDK 23; armeabi-v7a; samsung SM-G900F; ru)'
        })
        self._session = vk_api.VkApi(token=self.config['token'], session=http)
        self.api = self._session.get_api()
        try:
            self.api.account.getInfo()
        except vk_api.exceptions.ApiError:
            raise errors.ServiceError()

    def get(self, url):
        parsed_url = urlparse(url)
        path = parsed_url.path[1::]
        if 'video' in path:
            raise errors.ServiceError()
        try:
            if 'music/' in path:
                id = path.split('/')[-1]
                ids = id.split('_')
                o_id = ids[0]
                p_id = ids[1]
                audios = self.api.audio.get(owner_id=int(o_id), album_id=int(p_id))
            else:
                id = self.api.utils.resolveScreenName(screen_name=path)['object_id']
                audios = self.api.audio.get(owner_id=id, count=6000)
            if 'count' in audios and audios['count'] > 0:
                tracks = []
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

    def search(self, text):
        results = self.api.audio.search(q=text, count=300, sort=0)
        if 'count' in results and results['count'] > 0:
            tracks = []
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
