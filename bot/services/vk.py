import requests
import vk_api

from bot.player.track import Track
from bot import errors


class Service:
    def __init__(self, config):
        self.name = 'vk'
        self.hostnames = []
        self.config = config

    def initialize(self):
        http = requests.Session()
        http.headers.update({
            'User-agent': 'KateMobileAndroid/47-427 (Android 6.0.1; SDK 23; armeabi-v7a; samsung SM-G900F; ru)'
        })
        self._session = vk_api.VkApi(token=self.config['token'], session=http)
        self.api = self._session.get_api()

    def search(self, text):
        results = self.api.audio.search(q=text, count=300, sort=0)
        if 'count' in results and results['count'] > 0:
            tracks = []
            for track in results['items']:
                print(type(track))
                if 'url' not in track or not track['url']:
                    continue
                track = Track(url=track['url'], name='{} - {}'.format(track['artist'], track['title']))
                tracks.append(track)
            if tracks:
                return tracks
            else:
                raise errors.NothingFoundError()
        else:
            raise errors.NothingFoundError()
