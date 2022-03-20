from __future__ import annotations
import threading
import time
import os
import tempfile
from typing import TYPE_CHECKING
from queue import Empty


from bot.player.track import Track
from bot.player.enums import TrackType
from bot.TeamTalk.structs import ErrorType, User
from bot import app_vars

if TYPE_CHECKING:
    from bot import Bot


class Uploader:
    def __init__(self, bot: Bot):
        self.config = bot.config
        self.ttclient = bot.ttclient
        self.translator = bot.translator

    def __call__(self, track: Track, user: User) -> None:
        thread = threading.Thread(
            target=self.run,
            daemon=True,
            args=(
                track,
                user,
            ),
        )
        thread.start()

    def run(self, track: Track, user: User) -> None:
        error_exit = False
        if track.type == TrackType.Default:
            temp_dir = tempfile.TemporaryDirectory()
            file_path = track.download(temp_dir.name)
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
                if (
                    error.command_id == command_id
                    and error.type == ErrorType.MaxDiskusageExceeded
                ):
                    self.ttclient.send_message(
                        self.translator.translate("Error: {}").format(
                            "Max diskusage exceeded"
                        ),
                        user,
                    )
                    error_exit = True
                else:
                    self.ttclient.errors_queue.put(error)
            except Empty:
                pass
            time.sleep(app_vars.loop_timeout)
        time.sleep(app_vars.loop_timeout)
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
