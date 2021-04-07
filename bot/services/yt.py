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
        'format': 'bestaudio/140/best'
        }

    def get(self, url):
        try:
            with YoutubeDL(self._ydl_config) as ydl:
                video = ydl.extract_info(url)
                if 'url' in video:
                    url = video['url']
                elif 'entries' in video:
                    url = video['entries'][0]['url']
                else:
                    raise errors.ServiceError('Cannot fetch direct URL')
                title = video['title']
                if 'uploader' in video:
                    uploader = video['uploader']
                else:
                    uploader = video['extractor']
            return Track(url=url, name="{} - {}".format(title, uploader))
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
