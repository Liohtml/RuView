import pytest
from v1.src.caresignal.config import CareSignalConfig, RoomConfig


def test_default_config_has_required_fields():
    config = CareSignalConfig()
    assert config.inactivity_threshold_seconds > 0
    assert config.poll_interval_seconds > 0
    assert isinstance(config.rooms, list)
    assert config.ntfy_base_url.startswith("https://")


def test_room_config_requires_id_and_name():
    room = RoomConfig(room_id="room_1", name="Schlafzimmer Frau Mueller")
    assert room.room_id == "room_1"
    assert room.name == "Schlafzimmer Frau Mueller"


def test_room_config_has_node_id():
    room = RoomConfig(room_id="room_1", name="Zimmer 1", node_id=3)
    assert room.node_id == 3


def test_inactivity_threshold_minimum_60_seconds():
    with pytest.raises(ValueError):
        CareSignalConfig(inactivity_threshold_seconds=30)


def test_rooms_as_dicts_are_coerced_to_roomconfig():
    """Passing rooms as plain dicts must produce RoomConfig objects."""
    config = CareSignalConfig(
        rooms=[{"room_id": "r1", "name": "Wohnzimmer", "node_id": 2}]
    )
    assert isinstance(config.rooms[0], RoomConfig)
    assert config.rooms[0].room_id == "r1"
    assert config.rooms[0].node_id == 2
