---
name: log-file-parsing-and-triage
description: Use when parsing service logs to extract error entries and produce structured error reports
---
1. Read the entire log file and identify entries with level ERROR or CRITICAL (case insensitive).
2. Normalize service names to lower-case and replace '-' with '_' exactly as specified.
3. Convert all timestamps to UTC in the exact format YYYY-MM-DDTHH:MM:SSZ.
4. Extract the message text after the service name and level on the first line of each entry.
5. Extract the last line of the traceback as the exception field; if no traceback, set exception to null.
6. Calculate repeat_count by summing the initial occurrence plus all subsequent lines of the form '-- last message repeated N times --'.
7. Sort the final errors list by service name, then by timestamp_utc ascending.
8. Include top-level keys "schema_version": 2 and "generated_by": "log-triage" in the output JSON.
9. Aggregate counts_by_service as the sum of repeat_count per service.
10. Self-check:
    - Are all timestamps converted and formatted correctly?
    - Are service names normalized exactly?
    - Are repeat counts correctly summed?
    - Is the errors list sorted as required?
    - Does the output JSON include all required top-level keys?
