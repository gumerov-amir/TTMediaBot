from __future__ import annotations

import time
from typing import Any, TYPE_CHECKING, Callable

from bot.commands.task_processor import Task
from bot.player.enums import TrackType

if TYPE_CHECKING:
    from bot.commands import CommandProcessor


class Command:
    def __init__(self, command_processor: CommandProcessor):
        self._bot = command_processor.bot
        self.cache = command_processor.cache
        self.cache_manager = command_processor.cache_manager
        self.command_processor = command_processor
        self.config = command_processor.config
        self.config_manager = command_processor.config_manager
        self.module_manager = command_processor.module_manager
        self.player = command_processor.player
        self.service_manager = command_processor.service_manager
        self._task_processor = command_processor.task_processor
        self.ttclient = command_processor.ttclient
        self.translator = command_processor.translator

    @property
    def help(self) -> str:
        return self.translator.translate("help text not found")

    def run_async(self, func: Callable[..., None], *args: Any, **kwargs: Any) -> None:
        self._task_processor.task_queue.put(Task(id(self), func, args, kwargs))

    def _report_position(self, user: "User", action: str) -> None:
        try:
            position = float(self.player._player.time_pos or 0)
            duration_value = self.player._player.duration
            duration = float(duration_value) if duration_value else 0
            track = self.player.track
            saved = False
            if track and track.url and track.type != TrackType.Live:
                if self.config.general.enable_positions:
                    # set on current track
                    track.resume_position = position
                    track.resume_duration = duration
                    # update matching entry in recents
                    try:
                        for i, recent_track in enumerate(reversed(self.cache.recents)):
                            if recent_track.url == track.url:
                                recent_track.resume_position = position
                                recent_track.resume_duration = duration
                                break
                    except Exception:
                        ...
                    try:
                        self.cache_manager.save()
                        saved = True
                    except Exception as e:
                        saved = False
                        fail_msg = f"save error: {e}"
                else:
                    saved = False
            if saved:
                msg = self.translator.translate(
                    "Position {action}: {pos:.1f}s of {duration}"
                ).format(
                    action=action,
                    pos=position,
                    duration=duration,
                )
            else:
                extra = f" ({fail_msg})" if "fail_msg" in locals() else ""
                msg = self.translator.translate(
                    "Position not saved (disabled or unsupported)"
                ) + extra
            self.ttclient.send_message(msg, user)
        except Exception:
            pass

    def _save_current_position(self) -> None:
        try:
            if (
                self.config.general.enable_positions
                and self.player.state != State.Stopped
                and self.player.track
                and self.player.track.url
                and self.player.track.type != TrackType.Live
            ):
                position = float(self.player._player.time_pos or 0)
                duration_value = self.player._player.duration
                duration = float(duration_value) if duration_value else 0
                track = self.player.track
                track.resume_position = position
                track.resume_duration = duration
                try:
                    for recent_track in reversed(self.cache.recents):
                        if recent_track.url == track.url:
                            recent_track.resume_position = position
                            recent_track.resume_duration = duration
                            break
                except Exception:
                    ...
                self.cache_manager.save()
        except Exception:
            pass
