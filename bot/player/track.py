from bot.player.enums import TrackType

class Track:
    def __init__(self, service=None, url=None, name=None, format=None, extra_info=None, type=TrackType.Default):
        self.service = service
        self.url = url
        self.name = name
        self.format = format
        self.extra_info = extra_info
        self.type = type
        if service:
            self.type = TrackType.Dynamic
        self._is_fetched = False

    def _fetch_stream_data(self):
        if (not self.service) or self._is_fetched:
            return
        track = self.service.get(self._url, extra_info=self.extra_info)[0]
        self.url = track.url
        self.name = track.name
        self.format = track.format
        self.type = track.type
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
        try:
            return {'name': self.name, 'url': self.url}
        except:
            return {'name': None, 'url': ''}

    def __bool__(self):
        if self.url or (self.service and self.extra_info):
            return True
        else:
            return False
