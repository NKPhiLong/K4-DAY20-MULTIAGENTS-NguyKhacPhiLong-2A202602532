---
name: normalize-and-validate-data-before-analysis
description: Use when processing raw data files for analysis or reporting.
---
1. Identify and handle duplicate records by a unique key, keeping only one record per key.
2. Normalize categorical fields (e.g., region names) to a canonical form (e.g., consistent capitalization and spelling).
3. Parse and unify date/time fields from multiple formats into a single standard format, converting timezones to UTC if applicable.
4. Convert monetary values to a consistent unit and format (e.g., integer cents) as required by conventions.
5. Detect and handle missing or invalid data values explicitly (e.g., sentinel values like -999).
6. Write cleaned data to a new file with the required header and format before performing analysis.
7. Include metadata about the input data (e.g., source filename, number of rows read, number of rows used) in output files.
8. Self-check:
   - Are duplicates removed correctly?
   - Are all categorical fields normalized?
   - Are all dates parsed and converted consistently?
   - Are monetary values in the correct units and format?
   - Is missing data handled properly?
   - Is cleaned data saved with correct headers and metadata?
