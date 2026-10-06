---
name: log-file-parsing-and-triage
description: Use when parsing log files to extract, normalize, and summarize error entries according to strict schema and formatting rules.
---
1. Read the entire log file and identify all entries, including multi-line entries with tracebacks and repeated message counts.
2. Filter entries to include only those with levels ERROR or CRITICAL (case insensitive).
3. Normalize service names by converting to lower-case and replacing '-' with '_'.
4. Convert all timestamps to UTC timezone and format as YYYY-MM-DDTHH:MM:SSZ exactly.
5. Extract the first line message after the service name and level, and extract the last line of the traceback as the exception if present; otherwise, set exception to null.
6. Calculate repeat_count by summing 1 plus all subsequent lines indicating repeated messages (e.g., "-- last message repeated N times --").
7. Sort the final errors list by service name ascending, then by timestamp_utc ascending.
8. Include a top-level object with keys "schema_version": 2 and "generated_by": "log-triage".
9. Calculate counts_by_service as the sum of repeat_count per normalized service.
10. Write the output JSON file exactly as specified, with all required keys and formats.
11. Before finishing, verify:
    - The number of entries matches the expected count.
    - All timestamps are correctly converted and formatted.
    - All service names are normalized.
    - The errors list is sorted correctly.
    - The top-level schema keys are present and correct.
12. Self-check:
    - Are all repeated messages counted correctly?
    - Are all timestamps converted to UTC and formatted exactly?
    - Are service names normalized as required?
    - Is the output JSON schema exactly as specified?
