import os
import sqlite3
import tempfile
import pytest
from v1.src.caresignal.alarm_log import AlarmLog


@pytest.fixture
def tmp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    log = AlarmLog(db_path=path)
    yield log, path
    log.close()
    os.unlink(path)


def test_alarm_log_creates_table(tmp_db):
    log, path = tmp_db
    conn = sqlite3.connect(path)
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    conn.close()
    assert ("alarms",) in tables


def test_record_alarm_stores_entry(tmp_db):
    log, _ = tmp_db
    log.record(room_id="r1", room_name="Schlafzimmer", still_seconds=1300)
    records = log.get_recent(limit=10)
    assert len(records) == 1
    assert records[0].room_id == "r1"
    assert records[0].still_seconds == 1300


def test_get_recent_returns_newest_first(tmp_db):
    log, _ = tmp_db
    log.record(room_id="r1", room_name="Zimmer 1", still_seconds=1200)
    log.record(room_id="r2", room_name="Zimmer 2", still_seconds=1500)
    records = log.get_recent(limit=10)
    assert records[0].room_id == "r2"


def test_get_recent_respects_limit(tmp_db):
    log, _ = tmp_db
    for i in range(5):
        log.record(room_id=f"r{i}", room_name=f"Zimmer {i}", still_seconds=1200)
    assert len(log.get_recent(limit=3)) == 3
