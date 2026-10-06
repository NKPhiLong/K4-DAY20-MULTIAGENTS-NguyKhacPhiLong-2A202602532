---
name: log-file-parsing-and-normalization
description: Use when parsing and normalizing log files into structured JSON with strict schema and sorting rules
---
1. Read all RULE texts verbatim for:
   - Output JSON file name and top-level keys.
   - Required schema_version and generated_by fields.
   - Service name normalization: lowercase, replace '-' with '_'.
   - Sorting order: errors sorted by service then timestamp ascending.
2. Parse timestamps with timezone offsets; convert all to UTC in YYYY-MM-DDTHH:MM:SSZ format.
3. Filter log entries by required levels (e.g., ERROR, CRITICAL), case-insensitive.
4. Extract message and exception fields exactly as specified:
   - Message is the text after "<service>: " on first line.
   - Exception is last line of traceback or null if none.
5. Calculate repeat_count by summing all following "-- last message repeated N times --" lines plus one.
6. Aggregate counts_by_service summing repeat_count per normalized service name.
7. Sort errors by normalized service name, then timestamp ascending.
8. Write output JSON with exact keys and structure, including schema_version and generated_by.
9. Self-check:
   - All timestamps converted to UTC and formatted exactly.
   - Service names normalized exactly.
   - Errors filtered by level correctly.
   - repeat_count calculated correctly.
   - Output JSON keys and structure match the schema.
   - Errors sorted as required.
