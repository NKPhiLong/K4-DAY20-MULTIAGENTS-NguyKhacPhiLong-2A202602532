---
name: parse-and-structure-logs-with-standard-format
description: Use when extracting structured error information from raw log files.
---
1. Filter log entries to include only those with specified severity levels (e.g., ERROR, CRITICAL), case-insensitive.
2. Normalize timestamps to UTC timezone and format as ISO 8601 with 'Z' suffix (YYYY-MM-DDTHH:MM:SSZ).
3. Extract service names and convert them to lowercase with dashes replaced by underscores.
4. Extract the main message text after the service name and level.
5. If a traceback is present, extract the last line as the exception message; otherwise, set exception to null.
6. Detect and sum repeated log entries indicated by lines like '-- last message repeated N times --' to compute repeat_count.
7. Sort the final error list by service name and timestamp ascending.
8. Include top-level metadata fields such as schema_version and generated_by in the output JSON.
9. Self-check:
   - Are only the required severity levels included?
   - Are timestamps correctly converted and formatted?
   - Are service names normalized as per convention?
   - Are exceptions extracted correctly?
   - Are repeat counts aggregated properly?
   - Is the output sorted and schema-compliant?
