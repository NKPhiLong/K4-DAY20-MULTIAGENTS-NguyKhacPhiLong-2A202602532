---
name: data-cleaning-and-aggregation
description: Use when cleaning, normalizing, and aggregating tabular data with strict output format rules
---
1. Read all RULE texts verbatim for output file names, JSON keys, data formats, and units.
2. Remove duplicate rows by unique key (e.g., order_id), keeping the first occurrence.
3. Normalize categorical fields exactly as specified (e.g., region names canonical spelling).
4. Parse all date/time fields handling all input formats and time zones; convert to UTC naive or exact format required.
5. Convert monetary values to integer cents if required; do not output floats.
6. Write output CSV with exact header line and columns in order.
7. Write output JSON with exact keys and nested objects as specified.
8. Avoid external dependencies if environment may lack them; implement parsing manually if needed.
9. Run the full pipeline and verify output files against all rules before finishing.
10. Self-check:
    - Output CSV header and columns exactly as required.
    - Monetary values in integer cents, no floats.
    - Dates/timestamps in exact required format and timezone.
    - JSON keys and structure exactly as specified.
    - Duplicate rows removed correctly.
    - Region names normalized exactly.
