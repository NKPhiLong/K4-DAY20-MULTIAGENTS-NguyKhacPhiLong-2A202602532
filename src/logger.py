"""Logging dạng JSON-lines cho hệ đa tác tử (mỗi agent một tệp logs/<name>.log).

JSON dễ parse khi debug: `cat logs/communication.log | jq .`
Thư mục log lấy từ biến môi trường MAS_LOG_DIR (mặc định <gốc repo>/logs).
"""
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "ts": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "logger": record.name,
            "level": record.levelname,
            "event": record.getMessage(),
        }
        entry.update(getattr(record, "data", {}) or {})
        return json.dumps(entry, ensure_ascii=False, default=str)


def log_dir() -> Path:
    return Path(os.getenv("MAS_LOG_DIR", ROOT / "logs"))


def get_logger(name: str) -> logging.Logger:
    """Logger `mas.<name>` ghi JSON vào logs/<name>.log. Gọi nhiều lần trả về cùng logger (không nhân đôi handler)."""
    logger = logging.getLogger(f"mas.{name}")
    if not logger.handlers:
        d = log_dir()
        d.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(d / f"{name}.log", encoding="utf-8")
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG if os.getenv("MAS_DEBUG") else logging.INFO)
        logger.propagate = bool(os.getenv("MAS_DEBUG"))   # MAS_DEBUG=1 -> cũng in ra console qua root logger
    return logger


def log_event(logger: logging.Logger, event: str, level: int = logging.INFO, **data) -> None:
    """Ghi một sự kiện có cấu trúc, ví dụ log_event(log, "task_end", task_id=..., seconds=...)."""
    logger.log(level, event, extra={"data": data})
