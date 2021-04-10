from youtube_dl import YoutubeDL
from youtubesearchpython import VideosSearch

from bot.player.track import Track
from bot import errors

class Service:
    def __init__(self, config):
        self.name = 'yt'
        self.hostnames = []

    def initialize(self):
        self._ydl_config = {
            'skip_download': True,
            #'quiet': True,
            'format': '141/bestaudio/140/best'
        }

    def get(self, url, extra_info=None, defer=False):
        if not (url or extra_info):
            raise errors.InvalidArgumentError()
        with YoutubeDL(self._ydl_config) as ydl:
            if not extra_info:
                info = ydl.extract_info(url, process=False)
            else:
                info = extra_info
            info_type = None
            if '_type' in info:
                info_type = info['_type']
            if info_type == 'url':
                return self.get(info['url'], defer=True)
            elif info_type == 'playlist':
                tracks = []
                for entry in info['entries']:
                    data = self.get(None, extra_info=entry, defer=True)
                    tracks += data
                return tracks
            if defer:
                return [Track(service=self, extra_info=info), ]
            stream = ydl.process_ie_result(info)
            if 'url' in stream:
                url = stream['url']
            else:
                raise errors.ServiceError('Cannot fetch direct URL')
            title = stream['title']
            if 'uploader' in stream:
                title += ' - {}'.format(stream['uploader'])
            return [Track(url=url, name=title), ]

    def search(self, text):
        try:
            search = VideosSearch(text, limit=300).result()
        except:
            raise errors.SearchError()
        if search['result']:
            tracks = []
            for video in search['result']:
                track = Track(url=video['link'], service=self)
                tracks.append(track)
            return tracks
        else:
            raise errors.NothingFoundError('')
