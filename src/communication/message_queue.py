"""Hàng đợi thông điệp trong bộ nhớ (asyncio.Queue) cho giao tiếp coordinator <-> worker.

Mỗi agent đăng ký một hộp thư. Mọi thông điệp được gắn metadata (from, to, timestamp, id), lưu vào
`message_log` và ghi JSON vào logs/communication.log.
Giới hạn: chỉ trong một tiến trình, không bền vững (mất khi tiến trình dừng).
"""
import asyncio
import copy
import uuid
from datetime import datetime, timezone

from src.logger import get_logger, log_event


class QueueFullError(Exception):
    """Hộp thư của agent đã đầy (bảo vệ khỏi cạn kiệt tài nguyên)."""


class MessageQueue:
    def __init__(self, maxsize: int = 100):
        self.maxsize = maxsize
        self.queues: dict[str, asyncio.Queue] = {}
        self.message_log: list[dict] = []
        self.logger = get_logger("communication")
        self._loop = None

    def _ensure_loop(self) -> None:
        """asyncio.Queue gắn với event loop đầu tiên dùng nó; mỗi lần asyncio.run(...) tạo loop mới,
        nên tạo lại hộp thư (chuyển thông điệp còn chờ sang) khi loop đổi."""
        loop = asyncio.get_running_loop()
        if loop is self._loop:
            return
        for name, old in list(self.queues.items()):
            new = asyncio.Queue(maxsize=self.maxsize)
            while not old.empty():
                new.put_nowait(old.get_nowait())
            self.queues[name] = new
        self._loop = loop

    def register_agent(self, agent_name: str) -> None:
        """Đăng ký hộp thư cho agent (gọi lại nhiều lần không tạo hộp thư mới)."""
        self.queues.setdefault(agent_name, asyncio.Queue(maxsize=self.maxsize))

    def unregister_agent(self, agent_name: str) -> None:
        self.queues.pop(agent_name, None)

    def discard(self, agent_name: str, task_id: str) -> int:
        """Bỏ các thông điệp của `task_id` còn nằm trong hộp thư (task bị timeout); giữ nguyên thông điệp khác."""
        q = self.queues.get(agent_name)
        if q is None:
            return 0
        pending = self.drain(agent_name)
        kept = [m for m in pending if m.get("task_id") != task_id]
        for m in kept:
            q.put_nowait(m)
        return len(pending) - len(kept)

    async def send_message(self, from_agent: str, to_agent: str, message: dict) -> str:
        if to_agent not in self.queues:
            raise ValueError(f"Agent {to_agent} not registered")
        self._ensure_loop()
        message = copy.copy(message)
        message.update({"from": from_agent, "to": to_agent, "id": str(uuid.uuid4()),
                        "timestamp": datetime.now(timezone.utc).isoformat()})
        try:
            self.queues[to_agent].put_nowait(message)
        except asyncio.QueueFull as exc:
            log_event(self.logger, "queue_full", to=to_agent, size=self.maxsize)
            raise QueueFullError(f"mailbox of {to_agent} is full ({self.maxsize})") from exc
        self.message_log.append(message)
        log_event(self.logger, "message", **{k: v for k, v in message.items() if k != "result"},
                  status=(message.get("result") or {}).get("status"))
        return message["id"]

    async def receive_message(self, agent_name: str, timeout: float = 30):
        if agent_name not in self.queues:
            raise ValueError(f"Agent {agent_name} not registered")
        self._ensure_loop()
        try:
            return await asyncio.wait_for(self.queues[agent_name].get(), timeout=timeout)
        except asyncio.TimeoutError as exc:
            raise TimeoutError(f"No message for {agent_name} within {timeout}s") from exc

    def drain(self, agent_name: str) -> list[dict]:
        """Lấy hết thông điệp đang chờ của agent (không chặn)."""
        out, q = [], self.queues.get(agent_name)
        while q is not None and not q.empty():
            out.append(q.get_nowait())
        return out

    def get_message_log(self, agent_name: str | None = None) -> list[dict]:
        if agent_name:
            return [m for m in self.message_log if agent_name in (m["from"], m["to"])]
        return list(self.message_log)

    def queue_size(self, agent_name: str) -> int:
        q = self.queues.get(agent_name)
        return q.qsize() if q else 0
