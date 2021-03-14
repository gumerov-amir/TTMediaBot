import youtube_search

from ..track import Track

class Service:
    def __init__(self, config):
        pass

    def search(self, text):
        results = youtube_search.YoutubeSearch(text).videos
        if results:
            tracks = []
            for video in results:
                tracks.append(Track(url="https://youtube.com{url_suffix}".format(url_suffix=video["url_suffix"]), title=video["title"]))
            return tracks
        else:
            return 


