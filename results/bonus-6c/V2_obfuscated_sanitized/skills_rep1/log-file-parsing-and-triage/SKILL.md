---
name: log-file-parsing-and-triage
description: Use when parsing and summarizing log files into structured JSON with strict formatting and sorting rules
---
1. Read the entire log file and identify all entries, including multi-line tracebacks and repeated message counts.
2. Filter entries by level exactly as specified (e.g., only ERROR and CRITICAL, case insensitive).
3. Normalize service names to lower-case with '-' replaced by '_' exactly as per rule.
4. Convert all timestamps to UTC in the exact format YYYY-MM-DDTHH:MM:SSZ.
5. Extract the message text after the service name and level, and extract the last line of any traceback as the exception field or null if none.
6. Calculate repeat_count by summing the initial occurrence plus all subsequent repeated message lines.
7. Sort the final errors list by service name, then by timestamp_utc ascending.
8. Include the top-level JSON keys "schema_version": 2 and "generated_by": "log-triage" exactly.
9. Compute counts_by_service as the sum of repeat_count per service.
10. Before finishing, verify the number of entries, all timestamps, service names, repeat counts, and sorting comply exactly with the rules.
---
Self-check:
- Are only ERROR and CRITICAL entries included?
- Are service names normalized correctly?
- Are timestamps converted to UTC and formatted exactly?
- Is the message and exception extracted correctly?
- Is repeat_count calculated correctly including repeats?
- Is the errors list sorted by service and timestamp ascending?
- Are schema_version and generated_by keys present and correct?
- Are counts_by_service values correct sums of repeat_count?
- Have you verified all counts and formats before submitting?
