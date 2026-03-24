"""
Multi-node ESP32 CSI collector for CareSignal.

Receives UDP frames from multiple ESP32 nodes on a single port,
demultiplexes by node_id, and maintains per-node RingBuffers.
Each node gets its own feature extraction and classification pipeline.

ADR-018 binary frame format:
    magic(4) node_id(1) n_ant(1) n_sc(2) freq(4) seq(4) rssi(1) noise(1) reserved(2)
    Total header: 20 bytes, followed by I/Q pairs.
"""
from __future__ import annotations

import logging
import socket
import struct
import threading
import time
from typing import Dict, Optional, Set

import numpy as np

from v1.src.sensing.classifier import MotionLevel, PresenceClassifier, SensingResult
from v1.src.sensing.feature_extractor import RssiFeatureExtractor
from v1.src.sensing.rssi_collector import RingBuffer, WifiSample

logger = logging.getLogger(__name__)

# ADR-018 constants (same as Esp32UdpCollector in ws_server.py)
MAGIC = 0xC5110001
HEADER_SIZE = 20
HEADER_FMT = '<IBBHIIBB2x'
DEFAULT_PORT = 5005


class CareSignalMultiNodeCollector:
    """
    UDP listener that demultiplexes ESP32 CSI frames by node_id.

    Each node_id gets its own RingBuffer, RssiFeatureExtractor, and
    PresenceClassifier so that classification is per-room, not global.
    """

    def __init__(
        self,
        bind_addr: str = "0.0.0.0",
        port: int = DEFAULT_PORT,
        sample_rate_hz: float = 10.0,
        buffer_seconds: int = 120,
    ) -> None:
        self._bind = bind_addr
        self._port = port
        self._rate = sample_rate_hz
        self._buf_size = int(sample_rate_hz * buffer_seconds)
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._sock: Optional[socket.socket] = None

        # Per-node state
        self._buffers: Dict[int, RingBuffer] = {}
        self._extractors: Dict[int, RssiFeatureExtractor] = {}
        self._classifier = PresenceClassifier()
        self._last_seen: Dict[int, float] = {}  # node_id -> time.time()
        self._lock = threading.Lock()

    def start(self) -> None:
        if self._running:
            return
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.settimeout(1.0)
        try:
            self._sock.bind((self._bind, self._port))
        except OSError as exc:
            self._sock.close()
            self._sock = None
            raise OSError(
                f"Port {self._port} bereits belegt. "
                f"Bitte ws_server.py stoppen bevor CareSignal gestartet wird."
            ) from exc
        self._running = True
        self._thread = threading.Thread(
            target=self._recv_loop, daemon=True, name="caresignal-udp"
        )
        self._thread.start()
        logger.info("CareSignalMultiNodeCollector listening on %s:%d", self._bind, self._port)

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None
        if self._sock:
            self._sock.close()
            self._sock = None

    def get_result_for_node(self, node_id: int) -> Optional[SensingResult]:
        """Classify the current state of a specific ESP32 node."""
        with self._lock:
            buf = self._buffers.get(node_id)
            if buf is None or len(buf) == 0:
                return None
            extractor = self._extractors.get(node_id)
            if extractor is None:
                return None

        # Need enough samples for meaningful features
        needed = max(20, int(self._rate * 2))
        samples = buf.get_last_n(needed)
        if len(samples) < 10:
            return None

        features = extractor.extract(samples)
        return self._classifier.classify(features)

    def get_all_results(self) -> Dict[int, SensingResult]:
        """Get classification results for all known nodes."""
        results = {}
        with self._lock:
            node_ids = list(self._buffers.keys())
        for nid in node_ids:
            result = self.get_result_for_node(nid)
            if result is not None:
                results[nid] = result
        return results

    def active_node_ids(self, max_age_seconds: float = 30.0) -> Set[int]:
        """Return node_ids that have sent data recently."""
        now = time.time()
        with self._lock:
            return {
                nid for nid, ts in self._last_seen.items()
                if (now - ts) < max_age_seconds
            }

    def _recv_loop(self) -> None:
        while self._running:
            try:
                data, addr = self._sock.recvfrom(4096)
                self._parse_and_store(data, addr)
            except socket.timeout:
                continue
            except Exception:
                if self._running:
                    logger.exception("Error receiving UDP packet")

    def _parse_and_store(self, raw: bytes, addr) -> None:
        """Parse ADR-018 binary frame and store in per-node buffer."""
        if len(raw) < HEADER_SIZE:
            return

        magic, node_id, n_ant, n_sc, freq_mhz, seq, rssi_u8, noise_u8 = \
            struct.unpack_from(HEADER_FMT, raw, 0)

        if magic != MAGIC:
            return

        rssi = rssi_u8 if rssi_u8 < 128 else rssi_u8 - 256
        noise = noise_u8 if noise_u8 < 128 else noise_u8 - 256

        # Parse I/Q data for amplitude-based pseudo-RSSI
        iq_count = n_ant * n_sc
        iq_bytes_needed = HEADER_SIZE + iq_count * 2
        mean_amp = 0.0

        if len(raw) >= iq_bytes_needed and iq_count > 0:
            iq_raw = struct.unpack_from(f'<{iq_count * 2}b', raw, HEADER_SIZE)
            i_vals = np.array(iq_raw[0::2], dtype=np.float64)
            q_vals = np.array(iq_raw[1::2], dtype=np.float64)
            amplitudes = np.sqrt(i_vals ** 2 + q_vals ** 2)
            mean_amp = float(np.mean(amplitudes))

        # Derive effective RSSI (same logic as Esp32UdpCollector)
        effective_rssi = float(rssi)
        if rssi == -80 and mean_amp > 0:
            effective_rssi = -70.0 + min(mean_amp, 20.0) * 2.0

        sample = WifiSample(
            timestamp=time.time(),
            rssi_dbm=effective_rssi,
            noise_dbm=float(noise),
            link_quality=max(0.0, min(1.0, (effective_rssi + 100.0) / 60.0)),
            tx_bytes=seq * 1500,
            rx_bytes=seq * 3000,
            retry_count=0,
            interface=f"esp32-node{node_id}",
        )

        with self._lock:
            if node_id not in self._buffers:
                self._buffers[node_id] = RingBuffer(max_size=self._buf_size)
                self._extractors[node_id] = RssiFeatureExtractor()
                logger.info("New ESP32 node detected: node_id=%d from %s", node_id, addr)
            self._buffers[node_id].append(sample)
            self._last_seen[node_id] = time.time()
