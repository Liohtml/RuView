"""End-to-end: simulated inactivity -> alarm fires -> logged + status updated."""
import json
import os
import tempfile
import struct
import pytest
from unittest.mock import patch
from v1.src.caresignal.config import CareSignalConfig, RoomConfig
from v1.src.caresignal.alert_service import AlertService
from v1.src.caresignal.alarm_log import AlarmLog
from v1.src.caresignal.status_writer import StatusWriter
from v1.src.caresignal.multi_node_collector import (
    CareSignalMultiNodeCollector, MAGIC, HEADER_FMT,
)
from v1.src.sensing.classifier import MotionLevel


@pytest.fixture
def config():
    return CareSignalConfig(
        inactivity_threshold_seconds=600,
        ntfy_topic="test-topic",
        rooms=[RoomConfig(room_id="r1", name="Schlafzimmer Mueller", node_id=1)],
    )


@pytest.fixture
def alarm_log():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    log = AlarmLog(db_path=path)
    yield log
    log.close()
    os.unlink(path)


def test_no_alarm_when_active(config, alarm_log):
    service = AlertService(config=config, alarm_log=alarm_log)
    result = service.tick(room=config.rooms[0], level=MotionLevel.ACTIVE, now=0.0)
    assert not result
    assert len(alarm_log.get_recent()) == 0


def test_alarm_fires_after_threshold(config, alarm_log):
    service = AlertService(config=config, alarm_log=alarm_log)

    with patch("v1.src.caresignal.alert_service.httpx.post") as mock_post:
        mock_post.return_value.status_code = 200
        service.tick(room=config.rooms[0], level=MotionLevel.PRESENT_STILL, now=0.0)
        fired = service.tick(room=config.rooms[0], level=MotionLevel.PRESENT_STILL, now=700.0)

    assert fired
    mock_post.assert_called_once()
    records = alarm_log.get_recent()
    assert len(records) == 1
    assert records[0].room_id == "r1"
    assert records[0].still_seconds == 700


def test_status_writer_shows_alarm(config):
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    try:
        writer = StatusWriter(status_file=path)
        writer.update("r1", "Schlafzimmer Mueller", MotionLevel.PRESENT_STILL, alarm=True)
        writer.flush()
        data = json.loads(open(path, encoding="utf-8").read())
        assert data["rooms"][0]["status"] == "alarm"
    finally:
        os.unlink(path)


def test_multi_node_independent_alarms(alarm_log):
    """Two rooms with different node_ids alarm independently."""
    config = CareSignalConfig(
        inactivity_threshold_seconds=600,
        ntfy_topic="test-topic",
        rooms=[
            RoomConfig(room_id="r1", name="Zimmer 1", node_id=1),
            RoomConfig(room_id="r2", name="Zimmer 2", node_id=2),
        ],
    )
    service = AlertService(config=config, alarm_log=alarm_log)

    with patch("v1.src.caresignal.alert_service.httpx.post") as mock_post:
        mock_post.return_value.status_code = 200

        # Room 1: still for 700s -> alarm
        service.tick(room=config.rooms[0], level=MotionLevel.PRESENT_STILL, now=0.0)
        fired_r1 = service.tick(room=config.rooms[0], level=MotionLevel.PRESENT_STILL, now=700.0)

        # Room 2: active -> no alarm
        service.tick(room=config.rooms[1], level=MotionLevel.ACTIVE, now=0.0)
        fired_r2 = service.tick(room=config.rooms[1], level=MotionLevel.ACTIVE, now=700.0)

    assert fired_r1
    assert not fired_r2
    records = alarm_log.get_recent()
    assert len(records) == 1
    assert records[0].room_id == "r1"
