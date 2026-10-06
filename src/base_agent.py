"""Lớp cơ sở chung cho Coordinator và mọi worker agent."""
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

    def _track_usage(self, response) -> dict:
        """Cộng `usage_metadata` của một AIMessage vào bộ đếm; trả về usage của riêng lần gọi đó."""
        usage = getattr(response, "usage_metadata", None) or {}
        delta = {
            "input": usage.get("input_tokens", 0),
            "output": usage.get("output_tokens", 0),
            "total": usage.get("total_tokens", 0),
        }
        for k, v in delta.items():
            self.tokens[k] += v
        return delta

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.name!r})"
