---
name: data-analysis-cleaning-and-reporting
description: Use when cleaning, normalizing, and analyzing tabular data to produce summary reports and JSON answers.
---
1. Follow all data format rules verbatim, including exact output file names, JSON keys, and value formats (e.g., money in integer cents, timestamps in YYYY-MM-DDTHH:MM:SSZ UTC).
2. Normalize all categorical fields exactly as specified (e.g., region names canonical spelling and capitalization).
3. Parse all date/time fields carefully, handling all specified input formats and converting to UTC naive timestamps in the exact required format.
4. Remove duplicates exactly as required (e.g., one row per distinct order_id), counting and reporting duplicates removed.
5. Exclude or handle missing values exactly as specified (e.g., amount = -999 means missing).
6. Compute all requested metrics precisely, using the cleaned and normalized data.
7. Write output files exactly as specified, including headers and field order.
8. Avoid using unavailable external libraries; implement parsing and conversions with standard libraries or manual code.
9. Self-check:
   - Are all output values in the correct units and formats (e.g., integer cents)?
   - Does the output JSON contain the exact required keys and meta block?
   - Are timestamps in UTC and formatted exactly as required?
   - Are duplicates removed and counted correctly?
   - Are all categorical values normalized exactly as per rules?
