---
name: data-cleaning-and-aggregation
description: Use when cleaning, normalizing, and aggregating tabular data from CSV files with multiple formats and conventions
---
1. Read all RULEs verbatim about output file names, JSON keys, data formats, and units (e.g., money in integer cents).
2. Parse input data carefully:
   - Handle multiple date formats explicitly and convert all timestamps to UTC naive or specified format exactly.
   - Normalize categorical fields (e.g., region names) to canonical spellings exactly as stated.
   - Remove duplicate rows by unique keys, keeping the first occurrence.
   - Exclude or handle missing values exactly as specified (e.g., amount = -999 means missing).
3. Perform all calculations using code, never by hand.
4. Convert monetary values to integer cents by multiplying and rounding as required.
5. Write output CSV files with exact headers and formats, including timestamp formats and canonical region names.
6. Write output JSON files with exact keys and values as specified in the RULEs.
7. Before finishing:
   - Re-check all output files against every RULE verbatim.
   - Confirm no external dependencies are used if not allowed; implement parsing manually if needed.
   - Run the script end-to-end and verify outputs match expected formats and values.
8. Self-check:
   - Are all timestamps converted to UTC and formatted exactly as required?
   - Are monetary values in integer cents in JSON and CSV?
   - Are duplicate rows removed correctly?
   - Are all output files named and formatted exactly per RULEs?
