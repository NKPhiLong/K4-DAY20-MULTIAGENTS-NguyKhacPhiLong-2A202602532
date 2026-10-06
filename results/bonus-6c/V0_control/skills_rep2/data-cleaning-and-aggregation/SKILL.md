---
name: data-cleaning-and-aggregation
description: Use when cleaning, normalizing, and aggregating tabular data with multiple formats and outputting JSON summaries
---
1. Parse all input data files carefully, handling all known data formats explicitly (e.g., multiple date formats, timezones).
2. Normalize categorical fields exactly as specified (e.g., region names canonical capitalization and spelling).
3. Remove duplicate rows based on the specified key(s), keeping the first occurrence, and count duplicates removed.
4. Convert all timestamps to UTC naive datetime in the exact format YYYY-MM-DDTHH:MM:SSZ.
5. Convert monetary values to integer cents as required (e.g., 1606.67 USD → 160667).
6. Exclude rows with missing or invalid data as specified (e.g., amount = -999).
7. Compute all requested aggregates precisely and output the JSON answer with all required keys and exact key names.
8. Avoid using unavailable external libraries; implement parsing and conversions with standard libraries only.
9. Self-check:
   - Are all date/time values normalized and converted correctly?
   - Are duplicates removed and counted correctly?
   - Are monetary values converted to integer cents?
   - Does the output JSON contain all required keys with correct values?
