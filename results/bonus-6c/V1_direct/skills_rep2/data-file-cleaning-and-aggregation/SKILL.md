---
name: data-file-cleaning-and-aggregation
description: Use when cleaning, normalizing, and aggregating data from CSV or similar files for analysis and reporting.
---
1. Read the input data file exactly as specified; do not omit or reorder columns unless required.
2. Normalize all categorical fields exactly as per the rules (e.g., region names must be canonical and spelled exactly as specified).
3. Parse all date/time fields carefully, handling all specified formats and converting timestamps to UTC in the exact format YYYY-MM-DDTHH:MM:SSZ.
4. Remove duplicate rows based on the specified key(s), keeping the first occurrence unless otherwise instructed.
5. Convert all monetary values to integer cents (multiply by 100 and convert to int) if required by the rules.
6. Write the cleaned data to the exact output file name with the exact header line and column order as specified.
7. Construct the answer JSON with the exact keys and value formats required by the rules.
8. Avoid using external libraries not guaranteed to be available; implement parsing and conversions manually if needed.
9. Before finishing, verify:
   - The output file exists with the correct header and data format.
   - The JSON answer file has all required keys with correct value types and formats.
   - All monetary values are in integer cents if required.
   - The number of rows in the output matches the rules.
10. Self-check:
    - Are all date/time values converted and formatted correctly?
    - Are all categorical values normalized exactly as required?
    - Are duplicates removed correctly?
    - Are monetary values converted to integer cents if required?
    - Are output files named and formatted exactly as per the rules?
