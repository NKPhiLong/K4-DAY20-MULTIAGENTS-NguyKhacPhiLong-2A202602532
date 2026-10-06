"""Tool cho Code Agent: chạy Python có giới hạn, tạo/sửa tệp, chạy script.

An toàn (cùng bài học với `make_backend` của lab): mã chạy trong TIẾN TRÌNH CON, thư mục làm việc = sandbox,
biến môi trường tối thiểu (KHÔNG kế thừa khóa API), có timeout và giới hạn CPU; tệp chỉ được ghi trong sandbox.
Đây vẫn chưa phải cách ly mức hệ điều hành: muốn chặt hơn thì chạy trong Docker.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from src.tools.base_tool import BaseTool, safe_path

BLOCKED_MODULES = ("os", "subprocess", "shutil", "socket", "ctypes", "multiprocessing", "signal", "pty")
_IMPORT_RE = re.compile(r"^\s*(?:import|from)\s+(" + "|".join(BLOCKED_MODULES) + r")\b", re.M)
_CALL_RE = re.compile(r"__import__|\bexec\s*\(|\beval\s*\(|\bcompile\s*\(")


def _child_env(base: Path) -> dict:
    return {"PATH": str(Path(sys.executable).parent) + ":/usr/bin:/bin", "HOME": str(base),
            "PYTHONDONTWRITEBYTECODE": "1", "MPLCONFIGDIR": str(base)}


def _limits(cpu_seconds: int):
    def apply():
        try:
            import resource
            # macOS: tiến trình con mang theo thời gian CPU đã dùng của tiến trình cha -> giới hạn TƯƠNG ĐỐI
            used = resource.getrusage(resource.RUSAGE_SELF)
            limit = int(used.ru_utime + used.ru_stime) + cpu_seconds + 1
            resource.setrlimit(resource.RLIMIT_CPU, (limit, limit))
        except Exception:  # noqa: BLE001 - không phải nền tảng nào cũng hỗ trợ
            pass
    return apply


def _run_python(args: list[str], cwd: Path, timeout: int, max_len: int) -> dict:
    try:
        r = subprocess.run([sys.executable, *args], cwd=cwd, env=_child_env(cwd), capture_output=True, text=True,
                           timeout=timeout, preexec_fn=_limits(timeout))
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": f"timeout after {timeout}s", "type": "TimeoutError"}
    out = {"status": "success" if r.returncode == 0 else "error", "returncode": r.returncode,
           "stdout": r.stdout[-max_len:], "stderr": r.stderr[-max_len:]}
    if r.returncode != 0:
        lines = r.stderr.strip().splitlines()
        out["error"] = (f"timeout: CPU limit of {timeout}s exceeded" if r.returncode in (-24, -9)   # SIGXCPU / SIGKILL
                        else lines[-1] if lines else f"exit code {r.returncode}")
    return out


class PythonREPLTool(BaseTool):
    def __init__(self, base_path, timeout: int = 30, max_output_len: int = 10000):
        self.base_path = Path(base_path)
        self.timeout = timeout
        self.max_output_len = max_output_len
        super().__init__(
            name="python_repl",
            description=("Execute a Python snippet (standard library only; no pandas/matplotlib) in a sandboxed "
                         f"subprocess whose working directory is the output folder. Timeout {timeout}s. "
                         "Print what you need to see. Each call starts a fresh interpreter (no shared variables)."),
            parameters={"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]},
        )

    def validate_input(self, input_dict):
        super().validate_input(input_dict)
        code = str(input_dict["code"])
        m = _IMPORT_RE.search(code)
        if m:
            raise ValueError(f"Import {m.group(1)} not allowed")
        if _CALL_RE.search(code):
            raise ValueError("dynamic code execution (__import__/exec/eval/compile) not allowed")
        return True

    def _run(self, input_dict):
        self.base_path.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(input_dict["code"])
            script = f.name
        try:
            return _run_python(["-I", script], self.base_path, self.timeout, self.max_output_len)
        finally:
            Path(script).unlink(missing_ok=True)


class CreateFileTool(BaseTool):
    def __init__(self, base_path, max_bytes: int = 1_000_000):
        self.base_path = Path(base_path)
        self.max_bytes = max_bytes
        super().__init__(
            name="create_file",
            description="Create (or overwrite) a text file inside the output folder. `filename` is relative.",
            parameters={"type": "object",
                        "properties": {"filename": {"type": "string"}, "content": {"type": "string"}},
                        "required": ["filename", "content"]},
        )

    def validate_input(self, input_dict):
        super().validate_input(input_dict)
        safe_path(self.base_path, input_dict["filename"])
        if len(str(input_dict["content"]).encode()) > self.max_bytes:
            raise ValueError(f"content larger than {self.max_bytes} bytes")
        return True

    def _run(self, input_dict):
        path = safe_path(self.base_path, input_dict["filename"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(str(input_dict["content"]), encoding="utf-8")
        return {"path": str(path.relative_to(self.base_path.resolve())), "size": path.stat().st_size}


class EditFileTool(BaseTool):
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        super().__init__(
            name="edit_file",
            description="Replace exactly one occurrence of `old` by `new` in an existing file of the output folder.",
            parameters={"type": "object",
                        "properties": {"filename": {"type": "string"}, "old": {"type": "string"},
                                       "new": {"type": "string"}},
                        "required": ["filename", "old", "new"]},
        )

    def _run(self, input_dict):
        path = safe_path(self.base_path, input_dict["filename"])
        text = path.read_text(encoding="utf-8")
        n = text.count(input_dict["old"])
        if n != 1:
            raise ValueError(f"`old` must occur exactly once, found {n}")
        path.write_text(text.replace(input_dict["old"], input_dict["new"]), encoding="utf-8")
        return {"path": str(path.relative_to(self.base_path.resolve()))}


class RunScriptTool(BaseTool):
    def __init__(self, base_path, timeout: int = 30, max_output_len: int = 10000):
        self.base_path = Path(base_path)
        self.timeout = timeout
        self.max_output_len = max_output_len
        super().__init__(
            name="run_script",
            description=f"Run a .py file of the output folder with optional arguments. Timeout {timeout}s.",
            parameters={"type": "object",
                        "properties": {"filename": {"type": "string"},
                                       "args": {"type": "array", "items": {"type": "string"}}},
                        "required": ["filename"]},
        )

    def validate_input(self, input_dict):
        super().validate_input(input_dict)
        path = safe_path(self.base_path, input_dict["filename"])
        if path.suffix != ".py" or not path.exists():
            raise ValueError("filename must be an existing .py file")
        PythonREPLTool(self.base_path).validate_input({"code": path.read_text(encoding="utf-8")})
        return True

    def _run(self, input_dict):
        path = safe_path(self.base_path, input_dict["filename"])
        args = [str(a) for a in input_dict.get("args") or []]
        return _run_python(["-I", str(path), *args], self.base_path, self.timeout, self.max_output_len)


class SVGChartTool(BaseTool):
    """Vẽ biểu đồ cột SVG từ nhãn và giá trị (tất định, không chạy mã của LLM).

    Thêm ở v2: benchmark v1 cho thấy Code Agent tốn 3-5 vòng LLM để tự viết, chạy rồi sửa script vẽ SVG.
    """

    def __init__(self, base_path, width: int = 640, height: int = 360):
        self.base_path = Path(base_path)
        self.width, self.height = width, height
        super().__init__(
            name="make_bar_chart_svg",
            description=("Create an SVG bar chart file from labels and numeric values in ONE call "
                         "(preferred over writing chart code). Returns the file path."),
            parameters={"type": "object",
                        "properties": {"filename": {"type": "string", "description": "relative, ends with .svg"},
                                       "title": {"type": "string"},
                                       "labels": {"type": "array", "items": {"type": "string"}},
                                       "values": {"type": "array", "items": {"type": "number"}}},
                        "required": ["filename", "labels", "values"]},
        )

    def validate_input(self, input_dict):
        super().validate_input(input_dict)
        if not str(input_dict["filename"]).endswith(".svg"):
            raise ValueError("filename must end with .svg")
        safe_path(self.base_path, input_dict["filename"])
        labels, values = input_dict["labels"], input_dict["values"]
        if not labels or len(labels) != len(values):
            raise ValueError("labels and values must be non-empty and of equal length")
        if any(float(v) < 0 for v in values):
            raise ValueError("values must be >= 0")
        return True

    def _run(self, input_dict):
        from html import escape
        labels = [str(x) for x in input_dict["labels"]]
        values = [float(v) for v in input_dict["values"]]
        w, h, pad, top = self.width, self.height, 50, max(values) or 1
        bw = (w - 2 * pad) / len(values)
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" font-family="sans-serif">',
                 f'<text x="{w / 2}" y="24" text-anchor="middle" font-size="16">{escape(str(input_dict.get("title", "")))}</text>',
                 f'<line x1="{pad}" y1="{h - pad}" x2="{w - pad}" y2="{h - pad}" stroke="#333"/>']
        for i, (label, v) in enumerate(zip(labels, values)):
            bh = v / top * (h - 2 * pad - 20)
            x = pad + i * bw + bw * 0.15
            parts += [f'<rect x="{x:.1f}" y="{h - pad - bh:.1f}" width="{bw * 0.7:.1f}" height="{bh:.1f}" fill="#4a78c2"/>',
                      f'<text x="{x + bw * 0.35:.1f}" y="{h - pad - bh - 6:.1f}" text-anchor="middle" font-size="11">{v:,.2f}</text>',
                      f'<text x="{x + bw * 0.35:.1f}" y="{h - pad + 16:.1f}" text-anchor="middle" font-size="12">{escape(label)}</text>']
        parts.append("</svg>")
        path = safe_path(self.base_path, input_dict["filename"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(parts), encoding="utf-8")
        return {"path": str(path.relative_to(self.base_path.resolve())), "bars": len(values)}
