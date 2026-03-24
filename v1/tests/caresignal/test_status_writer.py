import json
import os
import tempfile
import pytest
from v1.src.caresignal.status_writer import StatusWriter
from v1.src.sensing.classifier import MotionLevel


@pytest.fixture
def writer():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    w = StatusWriter(status_file=path)
    yield w, path
    if os.path.exists(path):
        os.unlink(path)


def test_writer_creates_json_file(writer):
    w, path = writer
    w.update("r1", "Schlafzimmer", MotionLevel.ACTIVE, alarm=False)
    w.flush()
    assert os.path.exists(path)


def test_json_has_rooms_and_updated_at(writer):
    w, path = writer
    w.update("r1", "Z1", MotionLevel.ACTIVE, alarm=False)
    w.flush()
    data = json.loads(open(path, encoding="utf-8").read())
    assert "rooms" in data
    assert "updated_at" in data


def test_status_ok_when_active_no_alarm(writer):
    w, path = writer
    w.update("r1", "Z1", MotionLevel.ACTIVE, alarm=False)
    w.flush()
    room = json.loads(open(path, encoding="utf-8").read())["rooms"][0]
    assert room["status"] == "ok"


def test_status_alarm_when_flagged(writer):
    w, path = writer
    w.update("r1", "Z1", MotionLevel.PRESENT_STILL, alarm=True)
    w.flush()
    room = json.loads(open(path, encoding="utf-8").read())["rooms"][0]
    assert room["status"] == "alarm"


def test_status_absent_when_absent(writer):
    w, path = writer
    w.update("r1", "Z1", MotionLevel.ABSENT, alarm=False)
    w.flush()
    room = json.loads(open(path, encoding="utf-8").read())["rooms"][0]
    assert room["status"] == "absent"
