# CareSignal Sprint 1 — MVP Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a working inactivity alarm system that notifies caregivers via push notification when a monitored person has been unusually still, plus a simple web dashboard showing room status.

**Architecture:** A thin `caresignal` layer sits on top of the existing RuView sensing pipeline. It polls `SensingResult` from `CommodityBackend`, applies inactivity logic, and fires push notifications via ntfy.sh. A single-page HTML dashboard reads room status from a lightweight JSON status file written to disk. All CareSignal files live in `v1/src/caresignal/` — **never modify RuView core files**.

**Tech Stack:** Python 3.13, RuView sensing backend (RSSI-based, `CommodityBackend`), ntfy.sh (free push notifications), pytest, vanilla HTML/JS (no framework), SQLite (alarm log)

**Important — Working Directory:**
All `pytest` and `python -m` commands must be run from the **repo root** `D:\CodeENV\ruview\`, not from `v1/`. The `pyproject.toml` with `package-dir = {"" = "."}` lives at the repo root.

```bash
# CORRECT (always):
cd D:\CodeENV\ruview
python -m pytest v1/tests/caresignal/test_foo.py -v

# WRONG (never):
cd D:\CodeENV\ruview\v1
python -m pytest tests/caresignal/test_foo.py -v
```

---

## File Map

```
v1/src/caresignal/
├── __init__.py              — package marker, exports CareSignalConfig, RoomConfig
├── config.py                — settings dataclasses (thresholds, room names, ntfy topic)
├── alert_service.py         — InactivityTracker state machine + AlertService polling loop
├── alarm_log.py             — SQLite log of all alarms
└── status_writer.py         — writes caresignal_status.json for dashboard

v1/src/caresignal/dashboard/
└── index.html               — single-page caregiver dashboard (vanilla JS, polls JSON)

v1/tests/caresignal/          — NO __init__.py (matches existing test tree convention)
├── test_config.py
├── test_alert_service.py
├── test_alarm_log.py
├── test_status_writer.py
└── test_integration.py

caresignal_run.py             — entrypoint at repo root (avoids CWD ambiguity)
```

**RuView files read (never modified):**
- `v1/src/sensing/classifier.py` — `MotionLevel` (ABSENT, PRESENT_STILL, ACTIVE), `SensingResult`
- `v1/src/sensing/backend.py` — `CommodityBackend(collector=...)`, `SensingResult`
- `v1/src/sensing/rssi_collector.py` — `SimulatedCollector`, `WindowsWifiCollector`

---

## Chunk 1: Config and Package Foundation

### Task 1: Package Init + Config

**Files:**
- Create: `v1/src/caresignal/__init__.py`
- Create: `v1/src/caresignal/config.py`
- Create: `v1/tests/caresignal/test_config.py`

- [ ] **Step 1: Write failing test**

```python
# v1/tests/caresignal/test_config.py
import pytest
from v1.src.caresignal.config import CareSignalConfig, RoomConfig


def test_default_config_has_required_fields():
    config = CareSignalConfig()
    assert config.inactivity_threshold_seconds > 0
    assert config.poll_interval_seconds > 0
    assert isinstance(config.rooms, list)
    assert config.ntfy_base_url.startswith("https://")


def test_room_config_requires_id_and_name():
    room = RoomConfig(room_id="room_1", name="Schlafzimmer Frau Müller")
    assert room.room_id == "room_1"
    assert room.name == "Schlafzimmer Frau Müller"


def test_inactivity_threshold_minimum_60_seconds():
    with pytest.raises(ValueError):
        CareSignalConfig(inactivity_threshold_seconds=30)


def test_rooms_as_dicts_are_coerced_to_roomconfig():
    """Passing rooms as plain dicts must produce RoomConfig objects."""
    config = CareSignalConfig(
        rooms=[{"room_id": "r1", "name": "Wohnzimmer"}]
    )
    assert isinstance(config.rooms[0], RoomConfig)
    assert config.rooms[0].room_id == "r1"
```

- [ ] **Step 2: Run — confirm fail**

```bash
cd D:\CodeENV\ruview
python -m pytest v1/tests/caresignal/test_config.py -v
```
Expected: `ModuleNotFoundError: No module named 'v1.src.caresignal'`

- [ ] **Step 3: Implement**

```python
# v1/src/caresignal/__init__.py
"""CareSignal — elderly care monitoring layer on top of RuView."""
from v1.src.caresignal.config import CareSignalConfig, RoomConfig

__all__ = ["CareSignalConfig", "RoomConfig"]
```

```python
# v1/src/caresignal/config.py
"""CareSignal configuration dataclasses."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Union


@dataclass
class RoomConfig:
    """Configuration for a single monitored room."""
    room_id: str
    name: str
    ntfy_topic: str = ""   # overrides global topic when set


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
```

- [ ] **Step 4: Run — confirm pass**

```bash
cd D:\CodeENV\ruview
python -m pytest v1/tests/caresignal/test_config.py -v
```
Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
cd D:\CodeENV\ruview
git add v1/src/caresignal/ v1/tests/caresignal/test_config.py
git commit -m "feat(caresignal): add package foundation and config"
```

---

### Task 2: Alarm Log (SQLite)

**Files:**
- Create: `v1/src/caresignal/alarm_log.py`
- Create: `v1/tests/caresignal/test_alarm_log.py`

- [ ] **Step 1: Write failing tests**

```python
# v1/tests/caresignal/test_alarm_log.py
import sqlite3
import pytest
from v1.src.caresignal.alarm_log import AlarmLog, AlarmRecord


@pytest.fixture
def tmp_log(tmp_path):
    log = AlarmLog(db_path=str(tmp_path / "test_alarms.db"))
    yield log
    log.close()


def test_alarm_log_creates_table(tmp_path):
    log = AlarmLog(db_path=str(tmp_path / "alarms.db"))
    with sqlite3.connect(str(tmp_path / "alarms.db")) as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    assert ("alarms",) in tables
    log.close()


def test_record_alarm_stores_entry(tmp_log):
    tmp_log.record(room_id="r1", room_name="Schlafzimmer", still_seconds=1300)
    records = tmp_log.get_recent(limit=10)
    assert len(records) == 1
    assert records[0].room_id == "r1"
    assert records[0].still_seconds == 1300


def test_get_recent_returns_newest_first(tmp_log):
    tmp_log.record(room_id="r1", room_name="Zimmer 1", still_seconds=1200)
    tmp_log.record(room_id="r2", room_name="Zimmer 2", still_seconds=1500)
    records = tmp_log.get_recent(limit=10)
    assert records[0].room_id == "r2"


def test_get_recent_respects_limit(tmp_log):
    for i in range(5):
        tmp_log.record(room_id=f"r{i}", room_name=f"Zimmer {i}", still_seconds=1200)
    assert len(tmp_log.get_recent(limit=3)) == 3
```

- [ ] **Step 2: Run — confirm fail**

```bash
cd D:\CodeENV\ruview
python -m pytest v1/tests/caresignal/test_alarm_log.py -v
```
Expected: `ImportError`

- [ ] **Step 3: Implement**

```python
# v1/src/caresignal/alarm_log.py
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
```

- [ ] **Step 4: Run — confirm pass**

```bash
cd D:\CodeENV\ruview
python -m pytest v1/tests/caresignal/test_alarm_log.py -v
```
Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
cd D:\CodeENV\ruview
git add v1/src/caresignal/alarm_log.py v1/tests/caresignal/test_alarm_log.py
git commit -m "feat(caresignal): add SQLite alarm log"
```

---

## Chunk 2: Alert Service (Kern-Logik)

### Task 3: Inactivity Tracker + Alert Service

**Files:**
- Create: `v1/src/caresignal/alert_service.py`
- Create: `v1/tests/caresignal/test_alert_service.py`

**Design note — time handling:**
`InactivityTracker` uses an explicit `now` float in all public methods. Internally it only does arithmetic on stored `now` values — it **never calls `time.monotonic()` directly**. This makes every state transition deterministic in tests. The caller (`AlertService.run_forever`) passes `time.monotonic()` as `now` in production.

- [ ] **Step 1: Write failing tests**

```python
# v1/tests/caresignal/test_alert_service.py
import pytest
from unittest.mock import patch
from v1.src.caresignal.alert_service import InactivityTracker, AlertService
from v1.src.caresignal.config import CareSignalConfig, RoomConfig
from v1.src.sensing.classifier import MotionLevel


# ─── InactivityTracker — all times are explicit floats ───────────────────────

@pytest.fixture
def tracker():
    return InactivityTracker(threshold_seconds=600, cooldown_seconds=1800)


def test_tracker_starts_with_no_alarm(tracker):
    assert not tracker.should_alarm(now=0.0)


def test_tracker_no_alarm_before_threshold(tracker):
    tracker.update(MotionLevel.PRESENT_STILL, now=0.0)
    assert not tracker.should_alarm(now=500.0)   # 500s < 600s threshold


def test_tracker_alarms_after_threshold(tracker):
    tracker.update(MotionLevel.PRESENT_STILL, now=0.0)
    assert tracker.should_alarm(now=700.0)        # 700s > 600s threshold


def test_tracker_still_seconds_equals_elapsed(tracker):
    tracker.update(MotionLevel.PRESENT_STILL, now=0.0)
    assert tracker.still_seconds(now=700.0) == pytest.approx(700.0)


def test_tracker_resets_on_active(tracker):
    tracker.update(MotionLevel.PRESENT_STILL, now=0.0)
    tracker.update(MotionLevel.ACTIVE, now=800.0)   # activity resets timer
    assert not tracker.should_alarm(now=800.0)
    assert tracker.still_seconds(now=800.0) == pytest.approx(0.0)


def test_tracker_alarms_when_absent(tracker):
    tracker.update(MotionLevel.ABSENT, now=0.0)
    assert tracker.should_alarm(now=700.0)


def test_tracker_cooldown_suppresses_repeat_alarm(tracker):
    tracker.update(MotionLevel.PRESENT_STILL, now=0.0)
    assert tracker.should_alarm(now=700.0)
    tracker.mark_alarm_sent(now=700.0)
    # 100s later — still in 1800s cooldown
    assert not tracker.should_alarm(now=800.0)


def test_tracker_alarms_again_after_cooldown(tracker):
    tracker.update(MotionLevel.PRESENT_STILL, now=0.0)
    tracker.mark_alarm_sent(now=700.0)
    # 1801s after alarm — cooldown expired
    assert tracker.should_alarm(now=700.0 + 1801.0)


# ─── Notification tests ───────────────────────────────────────────────────────

def test_send_notification_posts_to_ntfy():
    config = CareSignalConfig(
        ntfy_topic="test-pflege",
        rooms=[RoomConfig(room_id="r1", name="Schlafzimmer")],
    )
    service = AlertService(config=config)

    with patch("v1.src.caresignal.alert_service.requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        service._send_notification(room=config.rooms[0], still_seconds=1300)

    mock_post.assert_called_once()
    url_called = mock_post.call_args[0][0]
    assert "test-pflege" in url_called
    body = mock_post.call_args[1]["data"].decode("utf-8")
    assert "Schlafzimmer" in body


def test_send_notification_never_raises_on_error():
    config = CareSignalConfig(ntfy_topic="t", rooms=[RoomConfig(room_id="r1", name="Z")])
    service = AlertService(config=config)

    with patch("v1.src.caresignal.alert_service.requests.post",
               side_effect=Exception("network error")):
        service._send_notification(room=config.rooms[0], still_seconds=1200)
    # Must not raise
```

- [ ] **Step 2: Run — confirm fail**

```bash
cd D:\CodeENV\ruview
python -m pytest v1/tests/caresignal/test_alert_service.py -v
```
Expected: `ImportError`

- [ ] **Step 3: Implement**

```python
# v1/src/caresignal/alert_service.py
"""
Inactivity detection and alert dispatch for CareSignal.

InactivityTracker  — deterministic state machine, all time via explicit `now` arg
AlertService       — orchestrates trackers, sends ntfy.sh notifications
"""
from __future__ import annotations

import logging
import time
from typing import Dict, Optional

import requests

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
        backend=None,
        alarm_log: Optional[AlarmLog] = None,
    ) -> None:
        self._config = config
        self._backend = backend
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
            requests.post(
                url,
                data=message.encode("utf-8"),
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

    def run_forever(self) -> None:
        """Blocking poll loop. Use in a thread or background process."""
        if self._backend is None:
            raise RuntimeError("Cannot run_forever without a sensing backend.")
        logger.info("CareSignal polling every %ds", self._config.poll_interval_seconds)
        while True:
            try:
                result = self._backend.get_result()
                t = time.monotonic()
                for room in self._config.rooms:
                    self.tick(room=room, level=result.motion_level, now=t)
            except Exception as exc:
                logger.error("Poll error: %s", exc)
            time.sleep(self._config.poll_interval_seconds)
```

- [ ] **Step 4: Run — confirm pass**

```bash
cd D:\CodeENV\ruview
python -m pytest v1/tests/caresignal/test_alert_service.py -v
```
Expected: `10 passed`

- [ ] **Step 5: Commit**

```bash
cd D:\CodeENV\ruview
git add v1/src/caresignal/alert_service.py v1/tests/caresignal/test_alert_service.py
git commit -m "feat(caresignal): add deterministic inactivity tracker and alert service"
```

---

## Chunk 3: Status Writer + Dashboard

### Task 4: Status Writer

**Files:**
- Create: `v1/src/caresignal/status_writer.py`
- Create: `v1/tests/caresignal/test_status_writer.py`

- [ ] **Step 1: Write failing tests**

```python
# v1/tests/caresignal/test_status_writer.py
import json
import pytest
from pathlib import Path
from v1.src.caresignal.status_writer import StatusWriter
from v1.src.sensing.classifier import MotionLevel


@pytest.fixture
def writer(tmp_path):
    return StatusWriter(status_file=str(tmp_path / "status.json"))


def test_writer_creates_json_file(writer, tmp_path):
    writer.update("r1", "Schlafzimmer", MotionLevel.ACTIVE, alarm=False)
    writer.flush()
    assert (tmp_path / "status.json").exists()


def test_json_has_rooms_and_updated_at(writer, tmp_path):
    writer.update("r1", "Z1", MotionLevel.ACTIVE, alarm=False)
    writer.flush()
    data = json.loads((tmp_path / "status.json").read_text())
    assert "rooms" in data
    assert "updated_at" in data


def test_status_ok_when_active_no_alarm(writer, tmp_path):
    writer.update("r1", "Z1", MotionLevel.ACTIVE, alarm=False)
    writer.flush()
    room = json.loads((tmp_path / "status.json").read_text())["rooms"][0]
    assert room["status"] == "ok"


def test_status_alarm_when_flagged(writer, tmp_path):
    writer.update("r1", "Z1", MotionLevel.PRESENT_STILL, alarm=True)
    writer.flush()
    room = json.loads((tmp_path / "status.json").read_text())["rooms"][0]
    assert room["status"] == "alarm"


def test_status_absent_when_absent(writer, tmp_path):
    writer.update("r1", "Z1", MotionLevel.ABSENT, alarm=False)
    writer.flush()
    room = json.loads((tmp_path / "status.json").read_text())["rooms"][0]
    assert room["status"] == "absent"
```

- [ ] **Step 2: Run — confirm fail**

```bash
cd D:\CodeENV\ruview
python -m pytest v1/tests/caresignal/test_status_writer.py -v
```

- [ ] **Step 3: Implement**

```python
# v1/src/caresignal/status_writer.py
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
```

- [ ] **Step 4: Run — confirm pass**

```bash
cd D:\CodeENV\ruview
python -m pytest v1/tests/caresignal/test_status_writer.py -v
```
Expected: `5 passed`

- [ ] **Step 5: Commit**

```bash
cd D:\CodeENV\ruview
git add v1/src/caresignal/status_writer.py v1/tests/caresignal/test_status_writer.py
git commit -m "feat(caresignal): add status writer for dashboard JSON"
```

---

### Task 5: Caregiver Dashboard

**Files:**
- Create: `v1/src/caresignal/dashboard/index.html`

- [ ] **Step 1: Create directory and file**

```bash
mkdir v1\src\caresignal\dashboard
```

```html
<!-- v1/src/caresignal/dashboard/index.html -->
<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CareSignal — Pflegedashboard</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
           background: #f5f5f5; color: #333; }
    header { background: #2c3e50; color: white; padding: 16px 24px;
             display: flex; justify-content: space-between; align-items: center; }
    header h1 { font-size: 1.3rem; font-weight: 600; }
    #meta { font-size: 0.8rem; opacity: 0.75; }
    #badge { padding: 4px 10px; border-radius: 12px; font-size: 0.75rem;
             font-weight: bold; margin-left: 12px; }
    .online  { background: #27ae60; }
    .offline { background: #e74c3c; }
    main { padding: 24px; }
    #grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px,1fr)); gap: 16px; }
    .card { background: white; border-radius: 12px; padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,.08); border-left: 6px solid #ccc; }
    .card.ok     { border-left-color: #27ae60; }
    .card.alarm  { border-left-color: #e74c3c; animation: pulse 1.5s infinite; }
    .card.absent { border-left-color: #95a5a6; }
    @keyframes pulse {
      0%,100% { box-shadow: 0 2px 8px rgba(0,0,0,.08); }
      50%      { box-shadow: 0 2px 20px rgba(231,76,60,.4); }
    }
    .room-name { font-size: 1.1rem; font-weight: 600; margin-bottom: 8px; }
    .label { font-size: .85rem; font-weight: 500; padding: 3px 10px;
             border-radius: 10px; display: inline-block; }
    .l-ok     { background: #eafaf1; color: #27ae60; }
    .l-alarm  { background: #fdecea; color: #e74c3c; }
    .l-absent { background: #f2f3f4; color: #7f8c8d; }
    .room-time { font-size: .75rem; color: #aaa; margin-top: 10px; }
  </style>
</head>
<body>
<header>
  <h1>CareSignal Pflegedashboard</h1>
  <div style="display:flex;align-items:center">
    <span id="meta">Lade...</span>
    <span id="badge" class="offline">Offline</span>
  </div>
</header>
<main><div id="grid"></div></main>
<script>
  const STATUS_URL = "../../../caresignal_status.json";
  const POLL_MS = 10000;
  const LABELS = {
    ok:     { text: "OK — aktiv",       cls: "l-ok" },
    alarm:  { text: "⚠ ALARM — still", cls: "l-alarm" },
    absent: { text: "Nicht anwesend",   cls: "l-absent" },
  };
  function fmt(iso) {
    return iso ? new Date(iso).toLocaleTimeString("de-DE",{hour:"2-digit",minute:"2-digit"}) : "—";
  }
  function esc(s) {
    return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
  }
  async function poll() {
    try {
      const res  = await fetch(STATUS_URL + "?t=" + Date.now());
      if (!res.ok) throw new Error(res.status);
      const data = await res.json();
      document.getElementById("badge").textContent = "Online";
      document.getElementById("badge").className   = "online";
      document.getElementById("meta").textContent  = "Stand: " + fmt(data.updated_at);
      document.getElementById("grid").innerHTML = (data.rooms || []).map(r => {
        const lbl = LABELS[r.status] || {text: r.status, cls: ""};
        return `<div class="card ${esc(r.status)}">
          <div class="room-name">${esc(r.name)}</div>
          <span class="label ${lbl.cls}">${lbl.text}</span>
          <div class="room-time">Zuletzt: ${fmt(r.updated_at)}</div>
        </div>`;
      }).join("") || "<p style='color:#aaa;text-align:center;margin-top:40px'>Keine Zimmer konfiguriert.</p>";
    } catch {
      document.getElementById("badge").textContent = "Offline";
      document.getElementById("badge").className   = "offline";
    }
  }
  poll();
  setInterval(poll, POLL_MS);
</script>
</body>
</html>
```

*Note: `room.name` is escaped via `esc()` before DOM insertion — no XSS risk.*

- [ ] **Step 2: Visual test**

```bash
cd D:\CodeENV\ruview
python -m http.server 3100
```
Open: `http://localhost:3100/v1/src/caresignal/dashboard/index.html`
Expected: Dashboard loads, shows "Offline" (no `caresignal_status.json` yet)

- [ ] **Step 3: Commit**

```bash
cd D:\CodeENV\ruview
git add v1/src/caresignal/dashboard/
git commit -m "feat(caresignal): add caregiver dashboard (XSS-safe, vanilla JS)"
```

---

## Chunk 4: Integration + Entrypoint

### Task 6: Integration Test

**Files:**
- Create: `v1/tests/caresignal/test_integration.py`

- [ ] **Step 1: Write tests**

```python
# v1/tests/caresignal/test_integration.py
"""End-to-end: 20 minutes of simulated inactivity → alarm fires → logged."""
import json
import pytest
from pathlib import Path
from unittest.mock import patch
from v1.src.caresignal.config import CareSignalConfig, RoomConfig
from v1.src.caresignal.alert_service import AlertService
from v1.src.caresignal.alarm_log import AlarmLog
from v1.src.caresignal.status_writer import StatusWriter
from v1.src.sensing.classifier import MotionLevel


@pytest.fixture
def config():
    return CareSignalConfig(
        inactivity_threshold_seconds=600,
        ntfy_topic="test-topic",
        rooms=[RoomConfig(room_id="r1", name="Schlafzimmer Müller")],
    )


def test_no_alarm_when_active(config, tmp_path):
    log = AlarmLog(db_path=str(tmp_path / "t.db"))
    service = AlertService(config=config, alarm_log=log)

    result = service.tick(room=config.rooms[0], level=MotionLevel.ACTIVE, now=0.0)
    assert not result
    assert len(log.get_recent()) == 0
    log.close()


def test_alarm_fires_after_threshold(config, tmp_path):
    log = AlarmLog(db_path=str(tmp_path / "t.db"))
    service = AlertService(config=config, alarm_log=log)

    with patch("v1.src.caresignal.alert_service.requests.post") as mock_post:
        mock_post.return_value.status_code = 200

        # 10 min inactive (600s = threshold)
        service.tick(room=config.rooms[0], level=MotionLevel.PRESENT_STILL, now=0.0)
        fired = service.tick(room=config.rooms[0], level=MotionLevel.PRESENT_STILL, now=700.0)

    assert fired
    mock_post.assert_called_once()
    records = log.get_recent()
    assert len(records) == 1
    assert records[0].room_id == "r1"
    assert records[0].still_seconds == 700
    log.close()


def test_status_writer_shows_alarm(config, tmp_path):
    status_file = str(tmp_path / "status.json")
    writer = StatusWriter(status_file=status_file)
    writer.update("r1", "Schlafzimmer Müller", MotionLevel.PRESENT_STILL, alarm=True)
    writer.flush()

    data = json.loads(Path(status_file).read_text())
    assert data["rooms"][0]["status"] == "alarm"
```

- [ ] **Step 2: Run all caresignal tests**

```bash
cd D:\CodeENV\ruview
python -m pytest v1/tests/caresignal/ -v
```
Expected: All tests green. Final count: `4 + 4 + 10 + 5 + 3 = 26 passed`

- [ ] **Step 3: Run RuView verification (must still pass)**

```bash
cd D:\CodeENV\ruview\v1
python data/proof/verify.py
```
Expected: `VERDICT: PASS`

- [ ] **Step 4: Commit**

```bash
cd D:\CodeENV\ruview
git add v1/tests/caresignal/test_integration.py
git commit -m "test(caresignal): add integration tests"
```

---

### Task 7: Entrypoint (ein Befehl, alles läuft)

**Files:**
- Create: `caresignal_run.py` (at repo root — avoids CWD ambiguity)

- [ ] **Step 1: Implement**

```python
# caresignal_run.py  (repo root: D:\CodeENV\ruview\caresignal_run.py)
"""
CareSignal entrypoint.

Usage:
    cd D:\\CodeENV\\ruview
    python caresignal_run.py

Reads caresignal_config.json from repo root if present.
Falls back to demo-mode defaults.
"""
from __future__ import annotations

import functools
import json
import logging
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from v1.src.caresignal.alarm_log import AlarmLog
from v1.src.caresignal.alert_service import AlertService
from v1.src.caresignal.config import CareSignalConfig, RoomConfig
from v1.src.caresignal.status_writer import StatusWriter
from v1.src.sensing.backend import CommodityBackend
from v1.src.sensing.rssi_collector import SimulatedCollector

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("caresignal")

REPO_ROOT = Path(__file__).parent
DASHBOARD_DIR = REPO_ROOT / "v1" / "src" / "caresignal" / "dashboard"
DASHBOARD_PORT = 3100


def load_config() -> CareSignalConfig:
    cfg_path = REPO_ROOT / "caresignal_config.json"
    if cfg_path.exists():
        data = json.loads(cfg_path.read_text(encoding="utf-8"))
        return CareSignalConfig(**data)
    logger.warning("caresignal_config.json not found — using DEMO defaults (5 min threshold)")
    return CareSignalConfig(
        inactivity_threshold_seconds=300,
        ntfy_topic="caresignal-demo",
        status_file_path=str(REPO_ROOT / "caresignal_status.json"),
        alarm_log_path=str(REPO_ROOT / "caresignal_alarms.db"),
        rooms=[RoomConfig(room_id="demo_room", name="Demo Zimmer")],
    )


def start_dashboard_server() -> None:
    """Serve dashboard HTML without changing process CWD."""
    handler = functools.partial(SimpleHTTPRequestHandler,
                                directory=str(DASHBOARD_DIR))
    server = HTTPServer(("", DASHBOARD_PORT), handler)
    logger.info("Dashboard: http://localhost:%d/index.html", DASHBOARD_PORT)
    server.serve_forever()


def main() -> None:
    config = load_config()

    # Dashboard in background thread (no os.chdir — uses directory= kwarg)
    threading.Thread(target=start_dashboard_server, daemon=True).start()

    # Sensing backend — SimulatedCollector on Windows without ESP32 hardware
    collector = SimulatedCollector()
    backend   = CommodityBackend(collector=collector)
    backend.start()

    log     = AlarmLog(db_path=config.alarm_log_path)
    writer  = StatusWriter(status_file=config.status_file_path)
    service = AlertService(config=config, backend=backend, alarm_log=log)

    logger.info("CareSignal started — monitoring %d room(s)", len(config.rooms))
    logger.info("Subscribe for alerts: https://ntfy.sh/%s", config.ntfy_topic)
    logger.info("Dashboard: http://localhost:%d/index.html", DASHBOARD_PORT)

    try:
        while True:
            result = backend.get_result()
            t = time.monotonic()
            for room in config.rooms:
                alarmed = service.tick(room=room, level=result.motion_level, now=t)
                writer.update(room.room_id, room.name, result.motion_level, alarm=alarmed)
            writer.flush()
            time.sleep(config.poll_interval_seconds)
    except KeyboardInterrupt:
        logger.info("Shutting down.")
    finally:
        backend.stop()
        log.close()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Start CareSignal**

```bash
cd D:\CodeENV\ruview
python caresignal_run.py
```
Expected output:
```
CareSignal started — monitoring 1 room(s).
Subscribe for alerts: https://ntfy.sh/caresignal-demo
Dashboard: http://localhost:3100/index.html
```

- [ ] **Step 3: Open dashboard**

Open: `http://localhost:3100/index.html`
Expected: "Demo Zimmer" Karte erscheint, Status aktualisiert sich alle 10 Sekunden.

- [ ] **Step 4: Final test run**

```bash
cd D:\CodeENV\ruview
python -m pytest v1/tests/caresignal/ -v --tb=short
```
Expected: `26 passed, 0 failed`

- [ ] **Step 5: Final commit**

```bash
cd D:\CodeENV\ruview
git add caresignal_run.py
git commit -m "feat(caresignal): add one-command startup entrypoint"
```

---

## Zusammenfassung

| Task | Datei | Tests | Abhängigkeiten |
|------|-------|-------|----------------|
| 1 | config.py | 4 | keine |
| 2 | alarm_log.py | 4 | keine |
| 3 | alert_service.py | 10 | config, alarm_log |
| 4 | status_writer.py | 5 | sensing.classifier |
| 5 | dashboard/index.html | visuell | status_writer |
| 6 | test_integration.py | 3 | alle oben |
| 7 | caresignal_run.py | manuell | alle oben |

**Gesamt: 26 automatisierte Tests**

**Nach Implementierung starten:**
```bash
cd D:\CodeENV\ruview
python caresignal_run.py
# Dashboard:     http://localhost:3100/index.html
# Push-Alarm:    ntfy.sh App installieren → "caresignal-demo" abonnieren
# API (RuView):  http://localhost:8000/docs  (optional, separat starten)
```
