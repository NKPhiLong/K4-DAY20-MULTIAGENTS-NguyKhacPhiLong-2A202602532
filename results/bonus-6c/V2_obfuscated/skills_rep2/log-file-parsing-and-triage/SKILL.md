---
name: log-file-parsing-and-triage
description: Use when parsing log files to extract error entries and produce structured JSON summaries following strict schema and sorting rules.
---
1. Filter log entries strictly by required levels (e.g., ERROR and CRITICAL), case-insensitive.
2. Convert all timestamps to UTC timezone and format as YYYY-MM-DDTHH:MM:SSZ exactly.
3. Normalize service names to lower-case with hyphens replaced by underscores, as per rule_service_names.
4. Extract message text exactly after the service name and colon on the first line.
5. Extract the last line of the traceback as the exception field; if no traceback, set exception to null.
6. Calculate repeat_count by summing the initial occurrence plus all subsequent "-- last message repeated N times --" lines.
7. Sort the errors array by service name ascending, then by timestamp_utc ascending, as required by rule_sorted_errors.
8. Include top-level keys "schema_version": 2 and "generated_by": "log-triage" exactly as required by rule_schema_header.
9. Aggregate counts_by_service correctly by summing repeat_count per normalized service.
10. Verify the total number of entries matches the expected count exactly.
11. Self-check:
    - Are all timestamps converted and formatted correctly?
    - Are service names normalized exactly?
    - Is the errors list sorted correctly?
    - Are repeat_count and exception fields correct for every entry?
    - Does the output JSON include required top-level keys and counts_by_service?
