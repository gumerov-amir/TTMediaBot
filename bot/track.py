class Track:
    def __init__(self, url=None, name=None, from_url=False):
        self.url = url
        self.name = name
        self.from_url = from_url

    def get_meta(self):
        return {"name": self.name, "url": self.url}

    def __repr__(self):
        return "{name} ({url})".format(name=self.name, url=self.url)
