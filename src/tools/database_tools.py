"""Tool cơ sở dữ liệu cho Data Agent: SQL chỉ-đọc trên SQLite, và bộ sinh CSDL demo `sales`."""
import random
import re
import sqlite3
import threading
from datetime import date, timedelta
from pathlib import Path

from src.tools.base_tool import BaseTool

FORBIDDEN = ("DROP", "DELETE", "TRUNCATE", "ALTER", "INSERT", "UPDATE", "CREATE", "REPLACE",
             "ATTACH", "DETACH", "PRAGMA", "VACUUM", "GRANT")


class QueryDatabaseTool(BaseTool):
    """SELECT trên SQLite. Ba lớp bảo vệ: kiểm tra từ khóa, chỉ một câu lệnh, và mở CSDL ở chế độ read-only."""

    def __init__(self, connection_string, max_rows: int = 1000, return_rows: int = 100):
        self.conn_string = str(connection_string)
        self.max_rows = max_rows
        self.return_rows = return_rows
        self.connection = None
        self._lock = threading.Lock()          # worker chạy trong thread pool; sqlite3 connection không thread-safe
        super().__init__(
            name="query_database",
            description=("Execute ONE read-only SQL SELECT query on the SQLite database and return the rows. "
                         "Use SQL aggregates (SUM, AVG, COUNT, GROUP BY) instead of fetching raw rows. "
                         f"Schema: {self.schema()}"),
            parameters={"type": "object",
                        "properties": {"query": {"type": "string", "description": "a single SELECT (or WITH ... SELECT)"},
                                       "limit": {"type": "integer", "description": f"max rows, default {max_rows}"}},
                        "required": ["query"]},
        )

    def connect(self):
        """Mở (và cache) kết nối read-only; tái sử dụng cho các truy vấn sau."""
        if self.connection is None:
            if not Path(self.conn_string).exists():
                raise FileNotFoundError(f"database not found: {self.conn_string}")
            self.connection = sqlite3.connect(f"file:{self.conn_string}?mode=ro", uri=True, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
        return self.connection

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def schema(self) -> str:
        try:
            rows = self.connect().execute("SELECT sql FROM sqlite_master WHERE type='table'").fetchall()
            return " ".join(r[0] for r in rows if r[0])
        except Exception as exc:  # noqa: BLE001
            return f"(unavailable: {exc})"

    def validate_input(self, input_dict):
        super().validate_input(input_dict)
        query = str(input_dict.get("query", "")).strip().rstrip(";").strip()
        if not query:
            raise ValueError("empty query")
        if ";" in query:
            raise ValueError("only one statement is allowed")
        upper = query.upper()
        for kw in FORBIDDEN:                    # \b: cột tên `updated_at` không bị chặn nhầm như khi dùng `in`
            if re.search(rf"\b{kw}\b", upper):
                raise ValueError(f"Dangerous operation: {kw} not allowed")
        if not upper.startswith(("SELECT", "WITH")):
            raise ValueError("Only SELECT queries allowed")
        return True

    def _run(self, input_dict):
        query = str(input_dict["query"]).strip().rstrip(";")
        limit = max(1, min(int(input_dict.get("limit") or self.max_rows), self.max_rows))
        with self._lock:
            cur = self.connect().execute(f"SELECT * FROM ({query}) LIMIT {limit}")   # bọc lại: LIMIT luôn hợp lệ
            rows = cur.fetchall()
            columns = [d[0] for d in cur.description]
        return {"rows": len(rows), "columns": columns, "data": [dict(r) for r in rows[: self.return_rows]],
                "truncated": len(rows) > self.return_rows}


REGIONS = ["North", "South", "East", "West"]
PRODUCTS = {"laptop": ("electronics", 900), "phone": ("electronics", 600), "monitor": ("electronics", 250),
            "desk": ("furniture", 300), "chair": ("furniture", 120), "notebook": ("stationery", 4),
            "pen": ("stationery", 2)}


def create_demo_db(path, n_rows: int = 600, seed: int = 20) -> Path:
    """Tạo CSDL demo `sales` (năm 2026, xác định theo seed) cho Data Agent. Ghi đè nếu đã có."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    rnd = random.Random(seed)
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE sales (id INTEGER PRIMARY KEY, order_date TEXT, region TEXT, product TEXT, "
                "category TEXT, quantity INTEGER, unit_price REAL, amount REAL)")
    start = date(2026, 1, 1)
    for i in range(1, n_rows + 1):
        d = start + timedelta(days=rnd.randrange(365))
        product = rnd.choice(list(PRODUCTS))
        category, base = PRODUCTS[product]
        qty = rnd.randint(1, 10)
        price = round(base * rnd.uniform(0.9, 1.1), 2)
        con.execute("INSERT INTO sales VALUES (?,?,?,?,?,?,?,?)",
                    (i, d.isoformat(), rnd.choice(REGIONS), product, category, qty, price, round(qty * price, 2)))
    con.commit()
    con.close()
    return path
