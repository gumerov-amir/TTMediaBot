from youtube_dl import YoutubeDL
from youtubesearchpython import VideosSearch

from bot.player.track import Track
from bot import errors


class Service:
    def __init__(self, config):
        self.name = 'yt'
        self.hostnames = ['www.youtube.com', 'youtube.com', 'youtu.be', 'www.youtu.be']

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
            return Track(url=video['url'], name="{} - {}".format(video['title'], video['uploader']))
        except Exception as e:
            raise errors.ServiceError(e)

    def search(self, text):
        search = VideosSearch(text, limit=300).result()
        if search['result']:
            tracks = []
            for video in search['result']:
                try:
                    with YoutubeDL(self._ydl_config) as ydl:
                        real_url = ydl.extract_info(video['link'])['url']
                    name = '{} - {}'.format(video['title'], video['channel']['name'])
                    track = Track(url=real_url, name=name)
                    tracks.append(track)
                except (AttributeError, KeyError):
                    continue
                except Exception as e:
                    raise errors.ServiceError(e)
            return tracks
        else:
            raise errors.NothingFoundError('')
