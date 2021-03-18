import youtube_search
import pafy

from urllib.parse import urljoin

from bot.track import Track

class Service:
    def __init__(self, config):
        self.hostnames = ['www.youtube.com', 'youtube.com', 'youtu.be', 'www.youtu.be']

    def get(self, url):
        video = pafy.new(url)
        best_audio = video.getbestaudio()
        return Track(url=best_audio.url, name="{} - {}".format(video.title, video.author))

    def search(self, text):
        search = youtube_search.YoutubeSearch(text, max_results=100)
        if search.videos:
            tracks = []
            for video in search.videos:
                try:
                    video = pafy.new(urljoin('https://www.youtube.com', video['url_suffix']))
                    best_audio = video.getbestaudio()
                    real_url = best_audio.url
                    name = '{} - {}'.format(video.title, video.author)
                    track = Track(url=real_url, name=name)
                    tracks.append(track)
                except KeyError:
                    continue
            return tracks
        else:
            return None
