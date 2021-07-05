import os
import sys
from urllib.parse import urlparse

from bot import errors
from bot.player.track import Track


class Streamer:
    def __init__(self, service_manager):
        self.allowed_schemes = ['http', 'https', 'rtmp', 'rtsp']
        self.service_manager = service_manager

    def get(self, url, is_admin):
        parsed_url = urlparse(url)
        if parsed_url.scheme in self.allowed_schemes:
            track = Track(url=url, from_url=True)
            fetched_data = [track]
            for service in self.service_manager.available_services.values():
                try:
                    if parsed_url.hostname in service.hostnames or service.name == self.service_manager.fallback_service:
                        fetched_data = service.get(url)
                        break
                except errors.ServiceError:
                    continue
                except:
                    if service.name == self.service_manager.fallback_service:
                        return [track, ]
            if len(fetched_data) == 1 and fetched_data[0].url.startswith(track.url):
                return [track, ]
            else:
                return fetched_data
        elif is_admin:
            if os.path.isfile(url):
                track = Track(url=url, name=os.path.split(url)[-1], format=os.path.splitext(url)[1])
                return [track, ]
            elif os.path.isdir(url):
                tracks = []
                for path, dirs, files in os.walk(url):
                    for file in sorted(files):
                        url = os.path.join(path, file)
                        name = os.path.split(url)[-1]
                        format = os.path.splitext(url)[1]
                        track = Track(url=url, name=name, format=format)
                        tracks.append(track)
                return tracks
            else:
                raise errors.PathNotFoundError('')
        else:
            raise errors.IncorrectProtocolError('')
