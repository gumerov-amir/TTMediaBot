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
            for service in self.service_manager.available_services.values():
                if parsed_url.hostname in service.hostnames:
                    track = service.get(url)
                    break
            return [track, ]
        elif is_admin and parsed_url.scheme == 'file':
            if sys.platform == 'win32':
                local_path = '{}:{}'.format(parsed_url.hostname, parsed_url.path)
            else:
                local_path = parsed_url.path
            if os.path.isfile(local_path):
                track = Track(url=local_path, name='.'.join(os.path.split(local_path)[-1].split(".")[0:-1]))
                return [track, ]
            elif os.path.isdir(local_path):
                tracks = []
                for path, dirs, files in os.walk(local_path):
                    for file in files:
                        url = os.path.join(path, file)
                        name = '.'.join(os.path.split(url)[-1].split(".")[0:-1])
                        track = Track(url=url, name=name)
                        tracks.append(track)
                return tracks
            else:
                raise errors.PathNotExistError('')
        else:
            raise errors.IncorrectProtocolError('')