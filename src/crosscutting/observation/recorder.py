import datetime
import json
import os
import threading
from typing import Any, Dict, Optional

from src.crosscutting.config.settings import settings
from src.crosscutting.logging.logger import get_logger


logger = get_logger(__name__)

MAX_BYTES = 5 * 1024 * 1024
BACKUP_COUNT = 3

_lock = threading.Lock()


def _utc_now_iso() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")


def _events_dir() -> str:
    return os.path.join(settings.BASE_DIR, "data", "observations")


def _events_path() -> str:
    return os.path.join(_events_dir(), "events.jsonl")


def _rotate_if_needed(path: str):
    try:
        if not os.path.exists(path):
            return
        if os.path.getsize(path) <= MAX_BYTES:
            return

        for i in range(BACKUP_COUNT, 0, -1):
            src = f"{path}.{i}"
            dst = f"{path}.{i+1}"
            if os.path.exists(src):
                if i == BACKUP_COUNT:
                    try:
                        os.remove(src)
                    except Exception:
                        pass
                else:
                    try:
                        os.replace(src, dst)
                    except Exception:
                        pass

        try:
            os.replace(path, f"{path}.1")
        except Exception:
            pass
    except Exception:
        pass


def _append_line(path: str, line: str):
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)
        f.write("\n")


def record_event(
    event_type: str,
    baseline_id: Optional[str],
    request_id: Optional[str],
    actor: Optional[str],
    context: Optional[Dict[str, Any]] = None,
):
    try:
        os.makedirs(_events_dir(), exist_ok=True)
        path = _events_path()
        with _lock:
            _rotate_if_needed(path)
            payload = {
                "ts": _utc_now_iso(),
                "event_type": event_type,
                "baseline_id": baseline_id,
                "request_id": request_id,
                "actor": actor,
                "context": context or {},
            }
            _append_line(path, json.dumps(payload, ensure_ascii=False, default=str))
    except Exception as e:
        try:
            logger.warning(f"Observation record_event failed: {e}")
        except Exception:
            pass

