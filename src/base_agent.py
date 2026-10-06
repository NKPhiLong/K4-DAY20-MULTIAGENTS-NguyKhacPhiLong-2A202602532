"""Lớp cơ sở chung cho Coordinator và mọi worker agent."""
import threading

from src.logger import get_logger


class AgentError(Exception):
    """Lỗi chung của hệ đa tác tử."""


class BaseAgent:
    """Một "nhân viên" LLM: có tên, mô hình và logger riêng; cộng dồn token của mọi lần gọi mô hình."""

    def __init__(self, name: str, model=None):
        self.name = name
        self.model = model
        self.logger = get_logger(name)
        self.tokens = {"input": 0, "output": 0, "total": 0}
        self._tokens_lock = threading.Lock()      # một worker có thể xử lý nhiều task song song (nhiều thread)

    def _track_usage(self, response) -> dict:
        """Cộng `usage_metadata` của một AIMessage vào bộ đếm tổng; trả về usage của riêng lần gọi đó.

        Số liệu của MỘT task phải cộng từ các giá trị trả về này (không lấy hiệu của bộ đếm tổng), vì các task
        chạy song song trên cùng worker cùng cộng vào bộ đếm tổng.
        """
        usage = getattr(response, "usage_metadata", None) or {}
        delta = {
            "input": usage.get("input_tokens", 0),
            "output": usage.get("output_tokens", 0),
            "total": usage.get("total_tokens", 0),
        }
        with self._tokens_lock:
            for k, v in delta.items():
                self.tokens[k] += v
        return delta

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.name!r})"
