import logging
import threading
import time
import os
import tempfile

import requests
from bot import utils, vars


class Downloader:
    def __init__(self, config, ttclient):
        self.config = config
        self.ttclient = ttclient

    def __call__(self, track):
        t = threading.Thread(target=self.run, args=(track,))
        t.start()

    def run(self,  track):
        if not os.path.exists(track.url):
            is_local = False
            response = requests.get(track.url)
            with tempfile.NamedTemporaryFile(delete=False) as f:
                temp_file_name = f.name
                f.write(response.content)
            extension = track.format
            file_name = track.name + "." + extension
            file_name= utils.clean_file_name(file_name)
            file_path = os.path.join(os.path.dirname(temp_file_name), file_name)
            os.rename(temp_file_name, file_path)
        else:
            is_local = True
            file_path = track.url
        self.ttclient.send_file(self.ttclient.get_my_channel_id(), file_path)
        file = self.ttclient.uploaded_files_queue.get()
        time.sleep(vars.loop_timeout)
        if not is_local:
            os.remove(file_path)
        if "delete_uploaded_files_after" in self.config["general"] and self.config["general"]["delete_uploaded_files_after"] > 0:
            timeout = self.config["general"]["delete_uploaded_files_after"]
        elif not "delete_uploaded_files_after" in self.config["general"]:
            timeout = vars.delete_uploaded_files_after
        else:
            return
        time.sleep(timeout)
        self.ttclient.delete_file(file.channel.id, file.id)
