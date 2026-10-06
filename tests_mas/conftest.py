"""Cấu hình test của hệ đa tác tử (offline, 0 token).

Đặt ở tests_mas/ (không phải tests/) vì RUBRIC cấm sửa thư mục tests/ của lab.
Chạy: pytest tests_mas/ -v
"""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))                                     # để `import src.coordinator` hoạt động
os.environ.setdefault("MAS_LOG_DIR", tempfile.mkdtemp(prefix="mas-logs-"))   # log test không làm bẩn logs/

import pytest  # noqa: E402
from langchain_core.messages import AIMessage  # noqa: E402

from lab.testing import ScriptedChatModel  # noqa: E402
from src.tools.database_tools import create_demo_db  # noqa: E402


@pytest.fixture
def scripted():
    """scripted(*messages) -> mô hình giả phát lại các AIMessage (mỗi worker nên có mô hình riêng)."""
    def make(*messages):
        return ScriptedChatModel(script=list(messages) or [AIMessage(content="done")])
    return make


@pytest.fixture
def demo_db(tmp_path):
    return create_demo_db(tmp_path / "sales.db", n_rows=200)


def tool_call(name, args, id_="1"):
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": id_}])
