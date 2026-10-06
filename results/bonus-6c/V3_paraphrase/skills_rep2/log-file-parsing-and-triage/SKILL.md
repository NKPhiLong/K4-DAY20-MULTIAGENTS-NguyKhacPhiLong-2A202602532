---
name: log-file-parsing-and-triage
description: Use when parsing log files to extract error entries and produce structured JSON summaries
---
1. Filter log entries to include only those with level ERROR or CRITICAL (case insensitive).
2. Convert all timestamps to UTC in the exact format YYYY-MM-DDTHH:MM:SSZ.
3. Normalize service names to lower-case with hyphens replaced by underscores (e.g., payment-service → payment_service).
4. Extract the message text after the service name and level on the first line of the entry.
5. Extract the last line of the traceback as the exception field; if no traceback, set exception to null.
6. Calculate repeat_count by summing the initial occurrence plus all subsequent lines of the form "-- last message repeated N times --".
7. Sort the errors array by service name, then by timestamp_utc ascending.
8. Include top-level keys "schema_version": 2 and "generated_by": "log-triage" exactly as stated.
9. Aggregate counts_by_service with service names normalized as above and counts equal to the sum of repeat_count per service.
10. Verify the total number of entries matches the expected count.
11. Re-check all output fields, formats, and sorting against the RULE texts before finishing.
12. This skill also applies to the held-out evaluation task of the logs family.

Self-check:
- Are only ERROR and CRITICAL entries included?
- Are timestamps converted and formatted correctly?
- Are service names normalized properly?
- Are repeat counts calculated correctly including repeats?
- Is the errors array sorted by service and timestamp ascending?
- Are schema_version and generated_by keys present and correct?
- Are counts_by_service correct and keys normalized?
- Have you verified the total entry count matches the expected number?
