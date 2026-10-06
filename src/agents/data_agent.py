"""Data Agent: phân tích dữ liệu bằng SQL chỉ-đọc và các tool tổng hợp."""
from pathlib import Path

from src.agents.base_worker import BaseWorker
from src.tools.data_tools import AggregationTool, CSVParserTool, DataValidationTool
from src.tools.database_tools import QueryDatabaseTool


class DataAgent(BaseWorker):
    result_type = "data"

    def __init__(self, model, db_connection, data_dir=None, name: str = "data_agent", **kwargs):
        tools = [QueryDatabaseTool(db_connection), AggregationTool(), CSVParserTool(data_dir or Path(db_connection).parent),
                 DataValidationTool()]
        super().__init__(name, model, tools, **kwargs)
        self.system_prompt = (
            "You are a Data Analysis Specialist working for a coordinator agent.\n"
            "1. Answer the data question with the query_database tool. Prefer SQL aggregates (SUM, AVG, COUNT, "
            "GROUP BY) over fetching raw rows; inspect the schema in the tool description first.\n"
            "2. Dates are ISO strings (YYYY-MM-DD): filter with order_date >= '2026-07-01' AND order_date < '2026-10-01' "
            "style ranges. Q1=Jan-Mar, Q2=Apr-Jun, Q3=Jul-Sep, Q4=Oct-Dec.\n"
            "3. Never invent numbers: every number in your answer must come from a tool result.\n"
            "4. Return concise insights with the exact figures (rounded to 2 decimals) and the SQL you used, "
            "e.g. 'Q3 revenue: 123456.78 (SQL: SELECT ...)'. If the question cannot be answered from the data, say so."
        )
