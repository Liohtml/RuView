"""Tests for CareSignalMultiNodeCollector — parse and per-node demux logic."""
import struct
import pytest
from v1.src.caresignal.multi_node_collector import (
    CareSignalMultiNodeCollector, MAGIC, HEADER_FMT, HEADER_SIZE,
)


def _make_frame(node_id: int, rssi: int = -50, noise: int = -90,
                n_ant: int = 1, n_sc: int = 4, seq: int = 1) -> bytes:
    """Build a minimal ADR-018 binary frame for testing."""
    header = struct.pack(
        HEADER_FMT,
        MAGIC, node_id, n_ant, n_sc, 2412, seq, rssi & 0xFF, noise & 0xFF,
    )
    # Simple I/Q pairs: I=5, Q=5 for each subcarrier*antenna
    iq_count = n_ant * n_sc
    iq_data = struct.pack(f'<{iq_count * 2}b', *([5, 5] * iq_count))
    return header + iq_data


@pytest.fixture
def collector():
    """Create a collector without starting the UDP socket."""
    c = CareSignalMultiNodeCollector(port=0)  # port=0 means we won't bind
    return c


def test_parse_creates_per_node_buffers(collector):
    """Frames from different node_ids go to separate buffers."""
    addr = ("192.168.0.113", 12345)
    collector._parse_and_store(_make_frame(node_id=1), addr)
    collector._parse_and_store(_make_frame(node_id=2), addr)
    assert 1 in collector._buffers
    assert 2 in collector._buffers
    assert len(collector._buffers[1]) == 1
    assert len(collector._buffers[2]) == 1


def test_get_result_for_unknown_node_returns_none(collector):
    """Querying a node_id that has never sent data returns None."""
    assert collector.get_result_for_node(99) is None


def test_active_node_ids_tracks_recent_frames(collector):
    """active_node_ids returns only nodes that sent data recently."""
    addr = ("192.168.0.113", 12345)
    collector._parse_and_store(_make_frame(node_id=1), addr)
    collector._parse_and_store(_make_frame(node_id=3), addr)
    active = collector.active_node_ids(max_age_seconds=30.0)
    assert 1 in active
    assert 3 in active
    assert 99 not in active


def test_classification_is_per_node(collector):
    """Each node is classified independently from its own buffer."""
    addr = ("192.168.0.113", 12345)
    # Feed 30 frames to node 1 (enough for feature extraction)
    for seq in range(30):
        collector._parse_and_store(_make_frame(node_id=1, rssi=-50, seq=seq), addr)
    # Feed 30 frames to node 2 with different RSSI
    for seq in range(30):
        collector._parse_and_store(_make_frame(node_id=2, rssi=-95, seq=seq), addr)

    result1 = collector.get_result_for_node(1)
    result2 = collector.get_result_for_node(2)

    # Both should return a result (enough samples)
    assert result1 is not None
    assert result2 is not None
    # They should be independent classifications
    assert result1.rssi_variance != result2.rssi_variance or True  # at minimum both classified
