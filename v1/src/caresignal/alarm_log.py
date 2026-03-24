"""SQLite-backed alarm log for CareSignal."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List


@dataclass
class AlarmRecord:
    alarm_id: int
    room_id: str
    room_name: str
    still_seconds: int
    triggered_at: str   # ISO 8601 UTC


class AlarmLog:
    """Persistent log of inactivity alarms stored in SQLite."""

    def __init__(self, db_path: str = "caresignal_alarms.db") -> None:
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self) -> None:
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS alarms (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id       TEXT    NOT NULL,
                room_name     TEXT    NOT NULL,
                still_seconds INTEGER NOT NULL,
                triggered_at  TEXT    NOT NULL
            )"""
        )
        self._conn.commit()

    def record(self, room_id: str, room_name: str, still_seconds: int) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            "INSERT INTO alarms (room_id, room_name, still_seconds, triggered_at) "
            "VALUES (?, ?, ?, ?)",
            (room_id, room_name, still_seconds, now),
        )
        self._conn.commit()

    def get_recent(self, limit: int = 20) -> List[AlarmRecord]:
        rows = self._conn.execute(
            "SELECT id, room_id, room_name, still_seconds, triggered_at "
            "FROM alarms ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [AlarmRecord(*row) for row in rows]

    def close(self) -> None:
        self._conn.close()
