import os
from urllib.parse import urlparse

from bot.track import Track

class Streamer:
    def __init__(self, services):
        self.allow_schemes = ['http', 'https']
        self.services = services

    def get(self, url, is_admin):
        parsed_url = urlparse(url)
        if parsed_url.scheme in self.allow_schemes:
            track = Track(url=url, from_url=True)
            for service in self.services.values():
                if parsed_url.hostname in service.hostnames:
                    track = service.get(url)
                    break
            return [track,]
        elif is_admin and parsed_url.scheme == 'file':
            local_path = '{}:{}'.format(parsed_url.hostname, parsed_url.path)
            if os.path.isfile(local_path):
                track = Track(url=local_path, from_url=True)
                return [track,]
            if os.path.isdir(local_path):
                tracks = []
                for file in os.listdir(local_path):
                    track = Track(url=os.path.join(local_path, file), from_url=True)
                    tracks.append(track)
                return tracks
        else:
            raise ValueError('Invalid protocol')
