import copy
from typing import Any, Dict, Optional

from bot.player.enums import TrackType


class Track:
    def __init__(
        self,
        service: Optional[str] = None,
        url: Optional[str] = None,
        name: Optional[str] = None,
        format: Optional[str] = None,
        extra_info: Optional[Dict[str, Any]] = None,
        type: TrackType = TrackType.Default,
    ) -> None:
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
        self._original_track = copy.deepcopy(self)
        service = get_service_by_name(self.service)
        track = service.get(self._url, extra_info=self.extra_info, process=True)[0]
        self.url = track.url
        self.name = track.name
        self._original_track.name = track.name
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
        if not self._name:
            self._fetch_stream_data()
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def get_meta(self):
        try:
            return {"name": self.name, "url": self.url}
        except:
            return {"name": None, "url": ""}

    def get_raw(self):
        if hasattr(self, "_original_track"):
            return self._original_track
        else:
            return self

    def __bool__(self):
        if self.service or self.url:
            return True
        else:
            return False
