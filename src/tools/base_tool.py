"""Lớp cơ sở cho mọi tool của worker agent.

Mẫu template method: `invoke` = validate_input -> _run, đo thời gian, ghi log, và KHÔNG ném lỗi ra ngoài
(lỗi được trả về dạng {"status": "error", ...} để LLM đọc được và tự sửa ở lượt sau).
"""
import time
from pathlib import Path

from src.logger import get_logger, log_event

_log = get_logger("tools")


class BaseTool:
    """name + description (LLM đọc để chọn tool) + parameters (JSON schema của input)."""

    def __init__(self, name: str, description: str, parameters: dict | None = None):
        self.name = name
        self.description = description
        self.parameters = parameters or {"type": "object", "properties": {}, "required": []}

    def validate_input(self, input_dict: dict) -> bool:
        """Mặc định: input là dict và có đủ các khóa bắt buộc. Lớp con mở rộng (kiểm tra an toàn)."""
        if not isinstance(input_dict, dict):
            raise ValueError("input must be an object")
        missing = [k for k in self.parameters.get("required", []) if k not in input_dict]
        if missing:
            raise ValueError(f"missing required field(s): {', '.join(missing)}")
        return True

    def _run(self, input_dict: dict) -> dict:
        raise NotImplementedError

    def invoke(self, input_dict: dict) -> dict:
        t0 = time.perf_counter()
        try:
            self.validate_input(input_dict)
            result = self._run(input_dict)
            result.setdefault("status", "success")
        except Exception as exc:  # noqa: BLE001 - lỗi tool trả về cho LLM, không làm sập worker
            result = {"status": "error", "error": str(exc), "type": type(exc).__name__}
        log_event(_log, "tool_call", tool=self.name, status=result["status"],
                  seconds=round(time.perf_counter() - t0, 3), error=result.get("error"))
        return result

    def to_schema(self) -> dict:
        """Định dạng function-calling của OpenAI, dùng cho model.bind_tools(...)."""
        return {"type": "function",
                "function": {"name": self.name, "description": self.description, "parameters": self.parameters}}


def safe_path(base: Path, filename: str) -> Path:
    """Đường dẫn bên trong `base`; chặn path traversal (`..`), đường dẫn tuyệt đối và symlink thoát ra ngoài."""
    if not filename or Path(filename).is_absolute() or ".." in Path(filename).parts:
        raise ValueError(f"invalid path: {filename!r} (must be relative, without '..')")
    base = Path(base).resolve()
    p = (base / filename).resolve()
    if not p.is_relative_to(base):
        raise ValueError(f"path escapes the sandbox: {filename!r}")
    return p
