import pytest
from unittest.mock import patch
from v1.src.caresignal.alert_service import InactivityTracker, AlertService
from v1.src.caresignal.config import CareSignalConfig, RoomConfig
from v1.src.sensing.classifier import MotionLevel


# --- InactivityTracker — all times are explicit floats ---

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


# --- Notification tests ---

def test_send_notification_posts_to_ntfy():
    config = CareSignalConfig(
        ntfy_topic="test-pflege",
        rooms=[RoomConfig(room_id="r1", name="Schlafzimmer")],
    )
    service = AlertService(config=config)

    with patch("v1.src.caresignal.alert_service.httpx.post") as mock_post:
        mock_post.return_value.status_code = 200
        service._send_notification(room=config.rooms[0], still_seconds=1300)

    mock_post.assert_called_once()
    url_called = mock_post.call_args[0][0]
    assert "test-pflege" in url_called
    body = mock_post.call_args[1]["content"].decode("utf-8")
    assert "Schlafzimmer" in body


def test_send_notification_never_raises_on_error():
    config = CareSignalConfig(ntfy_topic="t", rooms=[RoomConfig(room_id="r1", name="Z")])
    service = AlertService(config=config)

    with patch("v1.src.caresignal.alert_service.httpx.post",
               side_effect=Exception("network error")):
        service._send_notification(room=config.rooms[0], still_seconds=1200)
    # Must not raise
