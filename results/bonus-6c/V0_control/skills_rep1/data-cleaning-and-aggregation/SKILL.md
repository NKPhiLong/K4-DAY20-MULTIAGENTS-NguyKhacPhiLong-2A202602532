---
name: data-cleaning-and-aggregation
description: Use when cleaning, normalizing, and aggregating tabular data from CSV files with multiple formats and conventions
---
1. Read all RULEs verbatim for output file names, JSON keys, data formats, and units (e.g., money in integer cents, timestamp format YYYY-MM-DDTHH:MM:SSZ UTC).
2. Parse input data carefully, handling all known input formats exactly (e.g., multiple date formats, timezone offsets).
3. Normalize categorical fields exactly as specified (e.g., region names canonical spelling: North, South, East, West).
4. Remove duplicate rows by the specified key (e.g., order_id), keeping the first occurrence.
5. Convert all timestamps to UTC naive datetime and format output timestamps exactly as YYYY-MM-DDTHH:MM:SSZ.
6. Convert monetary values to integer cents by multiplying by 100 and rounding as needed; do not output floats.
7. Write clean CSV output with exact header line and columns in the specified order.
8. Create meta information object with exact keys and values as required (source file name, rows_in including duplicates, rows_used counting distinct valid rows).
9. Validate all output files and JSON against the RULEs before finishing.

Self-check:
- Are all timestamps in UTC and formatted exactly as required?
- Are money values integers in cents, not floats?
- Is the output CSV header exactly as specified?
- Are duplicates removed correctly and meta counts accurate?
