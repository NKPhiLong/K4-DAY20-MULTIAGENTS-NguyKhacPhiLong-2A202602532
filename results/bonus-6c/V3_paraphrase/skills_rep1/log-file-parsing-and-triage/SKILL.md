---
name: log-file-parsing-and-triage
description: Use when parsing log files to extract error entries and produce structured triage reports
---
1. Read the entire log file and identify all entries, including multi-line entries and repeated message blocks.
2. Filter entries by level exactly as specified (e.g., only ERROR or CRITICAL, case insensitive).
3. Convert all timestamps to UTC in the exact format YYYY-MM-DDTHH:MM:SSZ.
4. Normalize service names to lower-case with hyphens replaced by underscores as required.
5. Extract the message text exactly as specified, and extract the last line of any traceback as the exception field or null if none.
6. Calculate repeat_count by summing the initial occurrence plus all repeated message counts from following lines.
7. Sort the errors array by service name, then by timestamp_utc ascending.
8. Include the top-level keys "schema_version": 2 and "generated_by": "log-triage" exactly as stated.
9. Calculate counts_by_service as the sum of repeat_count per service.
10. Before finishing, verify the number of entries, timestamps, exception fields, repeat counts, service names, sorting, and schema header all conform exactly to the RULEs.
11. This also applies to the held-out evaluation task of the logs family.
---
Self-check:
- Are only ERROR or CRITICAL entries included?
- Are timestamps converted to UTC and formatted correctly?
- Are service names normalized as required?
- Are messages and exceptions extracted correctly?
- Is repeat_count calculated correctly including repeated messages?
- Is the errors list sorted by service and timestamp ascending?
- Are schema_version and generated_by keys present and correct?
- Are counts_by_service values correct?
- Have I verified all RULEs before finishing?
