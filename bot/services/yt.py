import logging

from yt_dlp import YoutubeDL
from youtubesearchpython import VideosSearch

from bot.player.enums import TrackType
from bot.player.track import Track
from bot import errors

class Service:
    def __init__(self, config: dict):
        self.name = 'yt'
        self.hostnames = []
        self.hidden = False

    def initialize(self):
        self._ydl_config = {
            'skip_download': True,
            'format': 'm4a/bestaudio/best',
            'socket_timeout': 5,
            'logger': logging.getLogger('root')
        }

    def get(self, url, extra_info=None, process=False):
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
            if info_type == 'url' and not info['ie_key']:
                return self.get(info['url'], process=False)
            elif info_type == 'playlist':
                tracks = []
                for entry in info['entries']:
                    data = self.get(None, extra_info=entry, process=False)
                    tracks += data
                return tracks
            if not process:
                return [Track(service=self.name, extra_info=info)]
            try:
                stream = ydl.process_ie_result(info)
            except Exception:
                raise errors.ServiceError()
            if 'url' in stream:
                url = stream['url']
            else:
                raise errors.ServiceError()
            title = stream['title']
            if 'uploader' in stream:
                title += ' - {}'.format(stream['uploader'])
            format = stream['ext']
            if 'is_live' in stream and stream['is_live']:
                type = TrackType.Live
            else:
                type = TrackType.Default
            return [Track(url=url, name=title, format=format, type=type)]

    def search(self, text):
        search = VideosSearch(text, limit=300).result()
        if search['result']:
            tracks = []
            for video in search['result']:
                track = Track(url=video['link'], service=self.name)
                tracks.append(track)
            return tracks
        else:
            raise errors.NothingFoundError('')
