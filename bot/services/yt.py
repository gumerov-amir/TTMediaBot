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
            'quiet': True,
            'format': '141/bestaudio/140/best'
        }

    def get(self, url, *args):
        if not (url or args):
            raise ValueError()
        if args:
            extra_info = args[0]
        else:
            extra_info = None
        try:
            with YoutubeDL(self._ydl_config) as ydl:
                if not extra_info:
                    info = ydl.extract_info(url, process=False)
                else:
                    info = extra_info
                if '_type' in info and info['_type'] == 'playlist':
                    tracks = []
                    for entry in info['entries']:
                        track = Track(service=self, extra_info=entry)
                        tracks.append(track)
                    return tracks
                stream = ydl.process_ie_result(info)
                if 'url' in stream:
                    url = stream['url']
                else:
                    raise errors.ServiceError('Cannot fetch direct URL')
                title = stream['title']
                if 'uploader' in stream:
                    title += ' - {}'.format(stream['uploader'])
                return Track(url=url, name=title)
        except Exception as e:
            raise errors.ServiceError(e.__class__.__name__ + ': ' + str(e))

    def search(self, text):
        try:
            search = VideosSearch(text, limit=300).result()
        except:
            raise errors.SearchError()
        if search['result']:
            tracks = []
            for video in search['result']:
                try:
                    track = Track(url=video['link'], service=self)
                    tracks.append(track)
                except (AttributeError, KeyError):
                    continue
                except Exception as e:
                    raise errors.ServiceError(e.__class__.__name__ + ': ' + str(e))
            return tracks
        else:
            raise errors.NothingFoundError('')
