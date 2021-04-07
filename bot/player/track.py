class Track:
    def __init__(self, service=None, url=None, name=None, from_url=False):
        self.service = service
        self.url = url
        self.name = name
        self.from_url = from_url
        self._is_fetched = False

    def _fetch_stream_data(self):
        if (not self.service) or self._is_fetched:
            return
        track = self.service.get(self._url)
        self.url = track.url
        self.name = track.name
        self._is_fetched = True

    @property
    def url(self):
            self._fetch_stream_data()
            return self._url

    @url.setter
    def url(self, value):
        self._url = value

    @property
    def name(self):
            self._fetch_stream_data()
            return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def get_meta(self):
        return {'name': self.name, 'url': self.url}

    def __bool__(self):
        if self.url:
            return True
        else:
            return False

    def __repr__(self):
        return '{name} ({url})'.format(name=self.name, url=self.url)
