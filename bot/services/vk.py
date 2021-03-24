import requests

import vk_api

from bot.player.track import Track
from bot import errors


class Service:
    def __init__(self, config):
        self.name = 'vk'
        self.config = config

    def initialize(self):
        http = requests.Session()
        http.headers.update({
            'User-agent': 'KateMobileAndroid/47-427 (Android 6.0.1; SDK 23; armeabi-v7a; samsung SM-G900F; ru)'
        })
        self._session = vk_api.VkApi(token=self.config['token'], session=http)
        self.api = self._session.get_api()
        self.hostnames = []

    def search(self, text):
        results = self.api.audio.search(q=text, count=300, sort=0)
        if results['count'] > 0:
            return [Track(url=i['url'], name='{title} - {artist}'.format(title=i['title'], artist=i['artist'])) for i in results['items']]
        else:
            raise errors.NotFoundError
