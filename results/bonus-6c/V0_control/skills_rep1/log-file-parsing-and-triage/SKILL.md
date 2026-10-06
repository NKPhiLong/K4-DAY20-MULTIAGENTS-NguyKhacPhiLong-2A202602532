---
name: log-file-parsing-and-triage
description: Use when parsing service logs to extract error entries with normalized fields and summary counts
---
1. Read the entire log file and identify entries with level ERROR or CRITICAL (case insensitive).
2. Convert all timestamps to UTC and format as YYYY-MM-DDTHH:MM:SSZ exactly.
3. Normalize service names to lower-case with '-' replaced by '_' (e.g., payment-service → payment_service).
4. Extract the first line message after "<service>: " as the main message.
5. Extract the last line of the traceback as the exception field; if no traceback, set exception to null.
6. Calculate repeat_count by summing the initial occurrence plus all following lines of the form "-- last message repeated N times --".
7. Sort the final errors list by service name, then by timestamp_utc ascending.
8. Include top-level keys "schema_version": 2 and "generated_by": "log-triage" exactly in the output JSON.
9. Aggregate counts_by_service summing repeat_count per normalized service.
10. Validate the output JSON structure and values against all RULEs before finishing.

Self-check:
- Are all timestamps converted and formatted exactly as required?
- Are service names normalized exactly as specified?
- Are repeat counts correctly summed including repeated lines?
- Is the errors list sorted by service then timestamp ascending?
- Does the output JSON include required top-level keys and correct counts?
