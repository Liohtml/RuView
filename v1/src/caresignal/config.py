"""CareSignal configuration dataclasses."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Union


@dataclass
class RoomConfig:
    """Configuration for a single monitored room."""
    room_id: str
    name: str
    node_id: int = 0          # ESP32 node_id for this room
    ntfy_topic: str = ""      # overrides global topic when set


@dataclass
class CareSignalConfig:
    """Global CareSignal configuration."""

    # Alert after this many seconds without ACTIVE motion (minimum 60)
    inactivity_threshold_seconds: int = 1200   # 20 min default

    # Polling interval in seconds
    poll_interval_seconds: int = 30

    # ntfy.sh push topic — caregivers subscribe to this on their phone
    ntfy_topic: str = "caresignal-default"
    ntfy_base_url: str = "https://ntfy.sh"

    # Paths (relative to CWD = repo root D:\CodeENV\ruview)
    status_file_path: str = "caresignal_status.json"
    alarm_log_path: str = "caresignal_alarms.db"

    rooms: List[Union[RoomConfig, dict]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.inactivity_threshold_seconds < 60:
            raise ValueError(
                f"inactivity_threshold_seconds must be >= 60, "
                f"got {self.inactivity_threshold_seconds}"
            )
        # Coerce plain dicts to RoomConfig (supports loading from JSON)
        self.rooms = [
            r if isinstance(r, RoomConfig) else RoomConfig(**r)
            for r in self.rooms
        ]
