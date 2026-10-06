---
name: data-analysis-cleaning-and-reporting
description: Use when cleaning, normalizing, and analyzing tabular data to produce JSON reports and cleaned CSV files.
---
1. Carefully read and apply all RULEs verbatim, especially regarding output file names, JSON keys, and data formats.
2. Normalize all categorical fields exactly as specified (e.g., region names must be canonical spelling and capitalization).
3. Parse all date/time fields correctly, handling all specified input formats and converting timestamps to UTC naive datetime or the exact required format (e.g., ISO 8601 with 'Z' suffix).
4. Remove duplicate rows as specified, keeping only the first occurrence per unique key.
5. Convert all monetary values to integer cents in outputs (e.g., 1606.67 USD → 160667), never output floats or strings for money.
6. Write the cleaned CSV file with the exact header line and column order specified by the RULE (e.g., order_id,timestamp_utc,region,amount_cents).
7. Construct the answer JSON with the exact required keys and nested objects, including the meta block with exact keys and values (source filename, rows_in, rows_used).
8. Avoid using external libraries not guaranteed to be installed; implement parsing and conversions manually if needed.
9. Before finishing, verify all output files against every RULE, including formats, keys, and data types.
10. Self-check:
    - Are all money values in integer cents in all outputs?
    - Is the cleaned CSV file named exactly and with the correct header and data format?
    - Does answer.json include the meta block with all required keys and correct values?
    - Are all timestamps converted to UTC and formatted exactly as required?
    - Are duplicates removed correctly and counts accurate?
