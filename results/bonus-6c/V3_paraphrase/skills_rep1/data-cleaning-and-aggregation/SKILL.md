---
name: data-cleaning-and-aggregation
description: Use when cleaning, normalizing, and aggregating tabular data from CSV or similar sources
---
1. Read the input data fully and identify all relevant columns and their formats.
2. Normalize all categorical fields exactly as specified by the RULEs (e.g., region names must be canonical spelling and capitalization).
3. Parse all date/time fields carefully, handling all specified formats and converting to UTC naive datetime in the exact format YYYY-MM-DDTHH:MM:SSZ.
4. Remove duplicate rows based on the specified key(s), keeping only the first occurrence.
5. Convert all monetary values to integer cents as required (e.g., 1606.67 USD → 160667).
6. Write output CSV files with the exact header line and column order specified by the RULEs.
7. Include a meta block in answer.json with the exact keys and values as required (e.g., source filename, rows_in, rows_used).
8. Handle missing or special values exactly as specified (e.g., -999 means missing amount).
9. Before finishing, verify all output files and JSON answers conform exactly to the RULEs.
10. This also applies to the held-out evaluation task of the data family.
---
Self-check:
- Are all categorical fields normalized exactly as required?
- Are all dates parsed and converted to UTC naive datetime in the correct format?
- Are duplicates removed correctly by the specified key?
- Are monetary values converted to integer cents?
- Does the output CSV have the exact header and format?
- Is the meta block in answer.json present and correct?
- Have I verified all outputs against the RULEs?
