"""
CareSignal entrypoint.

Usage:
    cd D:\\CodeENV\\ruview
    python caresignal_run.py

Reads caresignal_config.json from repo root if present.
Falls back to demo-mode defaults (SimulatedCollector, 1 room).
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
from v1.src.caresignal.multi_node_collector import CareSignalMultiNodeCollector
from v1.src.caresignal.status_writer import StatusWriter
from v1.src.sensing.classifier import MotionLevel

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
        rooms=[RoomConfig(room_id="demo_room", name="Demo Zimmer", node_id=1)],
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

    # Dashboard in background thread
    threading.Thread(target=start_dashboard_server, daemon=True).start()

    # Build IP -> node_id map from config (workaround for firmware node_id bug)
    ip_map = {}
    for room in config.rooms:
        if room.node_ip:
            ip_map[room.node_ip] = room.node_id
    if ip_map:
        logger.info("IP-basiertes Node-Mapping aktiv: %s", ip_map)

    # Multi-node ESP32 collector
    collector = CareSignalMultiNodeCollector(port=5005, ip_to_node_id=ip_map)
    try:
        collector.start()
    except OSError as exc:
        logger.error(str(exc))
        logger.error("Tipp: 'python v1/src/sensing/ws_server.py' beenden, dann nochmal starten.")
        return

    log = AlarmLog(db_path=config.alarm_log_path)
    writer = StatusWriter(status_file=config.status_file_path)
    service = AlertService(config=config, alarm_log=log)

    logger.info("CareSignal gestartet — %d Raum/Raeume ueberwacht", len(config.rooms))
    logger.info("Push-Alarme: https://ntfy.sh/%s", config.ntfy_topic)
    logger.info("Dashboard: http://localhost:%d/index.html", DASHBOARD_PORT)
    logger.info("Warte auf ESP32 UDP-Daten auf Port 5005...")

    try:
        while True:
            t = time.monotonic()
            active = collector.active_node_ids()
            for room in config.rooms:
                result = collector.get_result_for_node(room.node_id)
                if result is None:
                    # Node offline or not enough data — treat as ABSENT
                    level = MotionLevel.ABSENT
                else:
                    level = result.motion_level
                alarmed = service.tick(room=room, level=level, now=t)
                writer.update(room.room_id, room.name, level, alarm=alarmed)
            writer.flush()

            # Log active nodes periodically
            if active:
                logger.debug("Aktive Nodes: %s", active)

            time.sleep(config.poll_interval_seconds)
    except KeyboardInterrupt:
        logger.info("CareSignal beendet.")
    finally:
        collector.stop()
        log.close()


if __name__ == "__main__":
    main()
