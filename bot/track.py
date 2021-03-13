class Track:
    def __init__(self, url=None, title=None, artist=None):
        self.url = url
        self.title = title
        self.artist = artist
        self.media = None

    def get_meta_dict(self):
        return {"artist": self.artist, "title": self.title, "url": self.url}

    def __repr__(self):
        return "{title} - {artist} ({url})".format(title=self.title, artist=self.artist, url=self.url)
