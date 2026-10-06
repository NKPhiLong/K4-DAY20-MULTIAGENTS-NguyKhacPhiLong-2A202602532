"""Code Agent: viết và chạy mã Python, tạo tệp (script, báo cáo, biểu đồ SVG) trong thư mục outputs."""
from src.agents.base_worker import BaseWorker
from src.tools.code_tools import CreateFileTool, EditFileTool, PythonREPLTool, RunScriptTool


class CodeAgent(BaseWorker):
    result_type = "code"

    def __init__(self, model, output_dir, **kwargs):
        tools = [PythonREPLTool(output_dir), CreateFileTool(output_dir), EditFileTool(output_dir), RunScriptTool(output_dir)]
        super().__init__("code_agent", model, tools, **kwargs)
        self.system_prompt = (
            "You are a Code Generation Specialist working for a coordinator agent.\n"
            "1. Write Python code that solves the task. Only the Python STANDARD LIBRARY is available "
            "(no pandas, numpy or matplotlib); for a chart, write an SVG file with plain Python string formatting.\n"
            "2. Save files with create_file (relative names only), then run them with run_script or test snippets with "
            "python_repl. ALWAYS run the code before you answer and fix it if it fails.\n"
            "3. Use the data given in the parameters (results of other agents); do not invent data.\n"
            "4. Reply with the files you created, what they contain, and the console output of the last run. "
            "Mention only files that really exist."
        )
