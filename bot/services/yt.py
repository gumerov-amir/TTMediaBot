import youtube_search
import pafy

from ..track import Track

class Service:
    def __init__(self, config):
        pass

    def get_real_url(self, url):
        video = pafy.new(url)
        best_audio = video.getbestaudio()
        return best_audio.url

    def search(self, text):
        search = youtube_search.YoutubeSearch(text, max_results=100)
        if search.videos:
            tracks = []
            for video in search.videos:
                try:
                    tracks.append(Track(url=self.get_real_url("https://www.youtube.com" + video["url_suffix"]), name="{} - {}".format(video["title"], video["channel"])))
                except KeyError:
                    pass
            return tracks
        else:
            return
