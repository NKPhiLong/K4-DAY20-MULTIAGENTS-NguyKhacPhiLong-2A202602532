---
name: data-cleaning-and-aggregation
description: Use when cleaning, normalizing, and aggregating tabular data from CSV or similar sources
---
1. Parse all input data programmatically; do not compute or transform data manually.
2. Normalize all categorical fields exactly as specified (e.g., region names canonical spelling and capitalization).
3. Parse all date/time fields handling all documented formats and time zones; convert all timestamps to UTC naive datetime or specified format.
4. Remove duplicate rows based on the specified key(s), keeping the first occurrence.
5. Convert monetary values to the required units and formats exactly (e.g., integer cents, no decimals).
6. Write output files with exact headers, column order, and formats as specified by rules.
7. Include a meta block in JSON outputs with exact keys and values: source filename, rows_in (including duplicates), rows_used (filtered rows).
8. Avoid using external libraries not guaranteed to be installed; implement parsing and conversions with standard libraries.
9. Before finishing, verify output files conform exactly to all formatting and content rules.
10. Self-check:
    - Are all date/time fields parsed and converted correctly?
    - Are duplicates removed as required?
    - Are monetary values converted to integer cents?
    - Is the meta block present and correct?
    - Are output files named and formatted exactly as required?
