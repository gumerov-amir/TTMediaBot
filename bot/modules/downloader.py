from __future__ import annotations
import logging
import threading
import time
import os
import tempfile
from typing import TYPE_CHECKING
from queue import Empty
from urllib import request


from bot.player.enums import TrackType
from bot.TeamTalk.structs import ErrorType
from bot import utils, vars

if TYPE_CHECKING:
    from bot import Bot


class Downloader:
    def __init__(self, bot: Bot):
            self.ttclient = bot.ttclient
            self.config = bot.config

    def __call__(self, track, user):
        t = threading.Thread(target=self.run, daemon=True, args=(track, user,))
        t.start()

    def run(self,  track, user):
        error_exit = False
        if track.type == TrackType.Default:
            temp_dir = tempfile.TemporaryDirectory()
            temp_file_name = os.path.join(temp_dir.name, "file.dat")
            request.urlretrieve(track.url, temp_file_name)
            extension = track.format
            file_name = track.name + "." + extension
            file_name= utils.clean_file_name(file_name)
            file_path = os.path.join(os.path.dirname(temp_file_name), file_name)
            os.rename(temp_file_name, file_path)
        else:
            file_path = track.url
        command_id = self.ttclient.send_file(self.ttclient.channel.id, file_path)
        file_name = os.path.basename(file_path)
        while True:
            try:
                file = self.ttclient.uploaded_files_queue.get_nowait()
                if file.name == file_name:
                    break
                else:
                    self.ttclient.uploaded_files_queue.put(file)
            except Empty:
                pass
            try:
                error = self.ttclient.errors_queue.get_nowait()
                if error.command_id == command_id and error.type == ErrorType.MaxDiskusageExceeded:
                    self.ttclient.send_message(_("Error: {}").format("Max diskusage exceeded"), user)
                    error_exit = True
                else:
                    self.ttclient.errors_queue.put(error)
            except Empty:
                pass
            time.sleep(vars.loop_timeout)
        time.sleep(vars.loop_timeout)
        if track.type == TrackType.Default:
            temp_dir.cleanup()
        if error_exit:
            return
        if self.config.general.delete_uploaded_files_after > 0:
            timeout = self.config.general.delete_uploaded_files_after
        else:
            return
        time.sleep(timeout)
        self.ttclient.delete_file(file.channel.id, file.id)
