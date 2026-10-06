---
name: log-file-parsing-and-triage
description: Use when parsing log files to extract error entries and produce structured JSON summaries following strict schema and sorting rules.
---
1. Filter log entries to include only those with level ERROR or CRITICAL (case insensitive).
2. Normalize service names to lower-case and replace all '-' with '_', as required by rule_service_names.
3. Convert all timestamps to UTC and format as YYYY-MM-DDTHH:MM:SSZ exactly, handling all input timezone offsets.
4. Extract the message as the text after "<service>: " on the first line of the entry.
5. Extract the last line of the traceback as the exception field; if no traceback, set exception to null.
6. Calculate repeat_count by summing 1 plus all following lines of the form "-- last message repeated N times --".
7. Sort the errors array by service name ascending, then by timestamp_utc ascending, as required by rule_sorted_errors.
8. Compute counts_by_service as the sum of repeat_count per normalized service.
9. Include the top-level keys "schema_version": 2 and "generated_by": "log-triage" exactly as required by rule_schema_header.
10. Verify the total number of entries matches the expected count (entry_count).
11. Before finishing, re-check all fields and sorting against the rules.
12. Self-check:
    - Are service names normalized correctly?
    - Are timestamps converted and formatted exactly as required?
    - Is errors array sorted by service then timestamp ascending?
    - Are repeat_count and exception fields correct for every entry?
    - Are top-level schema_version and generated_by keys present and correct?
    - Does counts_by_service sum repeat_counts correctly?
