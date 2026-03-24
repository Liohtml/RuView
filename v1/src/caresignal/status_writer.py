"""Writes a JSON status snapshot for the dashboard to poll."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Dict

from v1.src.sensing.classifier import MotionLevel


@dataclass
class RoomStatus:
    room_id: str
    name: str
    status: str        # "ok" | "alarm" | "absent"
    motion_level: str
    alarm: bool
    updated_at: str


def _derive_status(level: MotionLevel, alarm: bool) -> str:
    if alarm:
        return "alarm"
    if level == MotionLevel.ABSENT:
        return "absent"
    return "ok"


class StatusWriter:
    def __init__(self, status_file: str = "caresignal_status.json") -> None:
        self._path = status_file
        self._rooms: Dict[str, RoomStatus] = {}

    def update(self, room_id: str, name: str, level: MotionLevel, alarm: bool) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._rooms[room_id] = RoomStatus(
            room_id=room_id,
            name=name,
            status=_derive_status(level, alarm),
            motion_level=level.value,
            alarm=alarm,
            updated_at=now,
        )

    def flush(self) -> None:
        payload = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "rooms": [asdict(r) for r in self._rooms.values()],
        }
        with open(self._path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
