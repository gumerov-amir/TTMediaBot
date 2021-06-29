import logging
import threading
import time
import os
import tempfile

import filetype
import requests
from bot import vars


class Downloader:
    def __init__(self, config, ttclient):
        self.config = config
        self.ttclient = ttclient

    def __call__(self, track):
        t = threading.Thread(target=self.run, args=(track,))
        t.start()

    def run(self,  track):
        try:
            response = requests.get(track.url)
            with tempfile.NamedTemporaryFile(delete=False) as f:
                temp_file_name = f.name
                f.write(response.content)
            extension = filetype.guess_extension(temp_file_name)
            if extension == None:
                extension = filetype.guess_mime(temp_file_name).split("/")[1]
            file_name = track.name + "." + extension
            for     char in ["\\", "/", "%", "*", "?", ":", "\""]:
                file_name = file_name.replace(char, "_")
            file_name = file_name.strip()
            file_path = os.path.join(os.path.dirname(temp_file_name), file_name)
            os.rename(temp_file_name, file_path)
        except Exception as e:
            logging.fatal(response.headers)
            raise ValueError()
        self.ttclient.send_file(self.ttclient.get_my_channel_id(), file_path)
        file = self.ttclient.uploaded_files_queue.get()
        time.sleep(vars.loop_timeout)
        os.remove(file_path)
        if "delete_uploaded_files_after" in self.config["general"] and self.config["general"]["delete_uploaded_files_after"] > 0:
            timeout = self.config["general"]["delete_uploaded_files_after"]
        elif not "delete_uploaded_files_after" in self.config["general"]:
            timeout = vars.delete_uploaded_files_after
        else:
            return
        time.sleep(timeout)
        self.ttclient.delete_file(file.channel.id, file.id)
