"""
Inactivity detection and alert dispatch for CareSignal.

InactivityTracker  — deterministic state machine, all time via explicit `now` arg
AlertService       — orchestrates trackers, sends ntfy.sh notifications
"""
from __future__ import annotations

import logging
import time
from typing import Dict, Optional

import httpx

from v1.src.caresignal.alarm_log import AlarmLog
from v1.src.caresignal.config import CareSignalConfig, RoomConfig
from v1.src.sensing.classifier import MotionLevel

logger = logging.getLogger(__name__)

_ACTIVE_LEVELS = {MotionLevel.ACTIVE}
DEFAULT_COOLDOWN_SECONDS = 1800   # 30 min between repeat alarms per room


class InactivityTracker:
    """
    Deterministic state machine for one room.

    All public methods take an explicit `now: float` (monotonic seconds).
    The caller provides time — this class never calls time.monotonic() itself.
    """

    def __init__(
        self,
        threshold_seconds: int,
        cooldown_seconds: int = DEFAULT_COOLDOWN_SECONDS,
    ) -> None:
        self._threshold = threshold_seconds
        self._cooldown = cooldown_seconds
        self._inactive_since: Optional[float] = None
        self._last_alarm_at: Optional[float] = None

    def update(self, level: MotionLevel, now: float) -> None:
        """Register a new motion reading at time `now`."""
        if level in _ACTIVE_LEVELS:
            self._inactive_since = None
        else:
            if self._inactive_since is None:
                self._inactive_since = now

    def should_alarm(self, now: float) -> bool:
        """True when inactive long enough and not in post-alarm cooldown."""
        if self._inactive_since is None:
            return False
        if (now - self._inactive_since) < self._threshold:
            return False
        if self._last_alarm_at is not None:
            if (now - self._last_alarm_at) < self._cooldown:
                return False
        return True

    def still_seconds(self, now: float) -> float:
        """Seconds since last ACTIVE reading, 0.0 if currently active."""
        if self._inactive_since is None:
            return 0.0
        return now - self._inactive_since

    def mark_alarm_sent(self, now: float) -> None:
        """Record that an alarm was sent at `now` to start cooldown."""
        self._last_alarm_at = now


class AlertService:
    """
    Processes one motion reading per room per tick, dispatches alarms.
    """

    def __init__(
        self,
        config: CareSignalConfig,
        alarm_log: Optional[AlarmLog] = None,
    ) -> None:
        self._config = config
        self._log = alarm_log or AlarmLog(db_path=config.alarm_log_path)
        self._trackers: Dict[str, InactivityTracker] = {
            room.room_id: InactivityTracker(
                threshold_seconds=config.inactivity_threshold_seconds
            )
            for room in config.rooms
        }

    def tick(self, room: RoomConfig, level: MotionLevel, now: Optional[float] = None) -> bool:
        """
        Process one reading for `room`. Returns True if alarm was sent.
        `now` defaults to time.monotonic() — pass explicitly in tests.
        """
        t = now if now is not None else time.monotonic()
        tracker = self._trackers[room.room_id]
        tracker.update(level, now=t)

        if tracker.should_alarm(now=t):
            still = int(tracker.still_seconds(now=t))
            logger.warning("ALARM: %s still for %ds", room.name, still)
            self._send_notification(room=room, still_seconds=still)
            self._log.record(room_id=room.room_id, room_name=room.name,
                             still_seconds=still)
            tracker.mark_alarm_sent(now=t)
            return True
        return False

    def _send_notification(self, room: RoomConfig, still_seconds: int) -> None:
        """POST to ntfy.sh. Never raises — logs errors instead."""
        topic = room.ntfy_topic or self._config.ntfy_topic
        url = f"{self._config.ntfy_base_url}/{topic}"
        minutes = still_seconds // 60
        message = (
            f"{room.name}: keine Bewegung seit {minutes} Minuten. "
            f"Bitte nachsehen."
        )
        try:
            httpx.post(
                url,
                content=message.encode("utf-8"),
                headers={
                    "Title": f"CareSignal Alarm — {room.name}",
                    "Priority": "high",
                    "Tags": "warning,elderly",
                },
                timeout=5,
            )
            logger.info("Notification sent to %s", url)
        except Exception as exc:
            logger.error("Notification failed: %s", exc)
