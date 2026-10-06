---
name: log-file-parsing-and-triage
description: Use when parsing and summarizing log files into structured JSON error reports
---
1. Filter log entries strictly by the required levels (e.g., ERROR and CRITICAL), case-insensitive.
2. Normalize service names to lower-case with '-' replaced by '_'.
3. Convert all timestamps to UTC in the exact format YYYY-MM-DDTHH:MM:SSZ.
4. Extract the first line message after the service name and level, and the last line of any traceback as the exception; use null if no exception.
5. Calculate repeat_count by summing the initial occurrence plus all subsequent '-- last message repeated N times --' lines.
6. Sort the final errors list by service name, then by timestamp_utc ascending.
7. Include top-level keys "schema_version": 2 and "generated_by": "log-triage" exactly.
8. Aggregate counts_by_service by summing repeat_count per service.
9. Before finishing, verify the number of entries, timestamps, service names, repeat counts, and exception fields all conform exactly to the rules.
10. Self-check:
    - Are service names normalized correctly?
    - Are timestamps converted and formatted correctly?
    - Are repeat counts calculated correctly?
    - Is the output sorted as required?
    - Are schema_version and generated_by present and correct?
