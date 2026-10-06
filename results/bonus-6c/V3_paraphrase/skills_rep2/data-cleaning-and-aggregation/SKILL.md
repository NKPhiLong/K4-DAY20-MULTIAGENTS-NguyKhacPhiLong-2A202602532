---
name: data-cleaning-and-aggregation
description: Use when cleaning, normalizing, and aggregating tabular data from CSV or similar sources
---
1. Read the input data carefully; identify and handle duplicates by a unique key, keeping only the first occurrence.
2. Normalize categorical fields exactly as specified (e.g., region names must be canonical spelling and capitalization).
3. Parse all date/time fields into UTC naive datetime objects in the exact format YYYY-MM-DDTHH:MM:SSZ; handle all input date formats explicitly.
4. Convert all monetary values to integer cents in the output JSON (e.g., 1606.67 USD → 160667).
5. Write output CSV files with exact header lines and column order as specified by the RULE.
6. Include a meta block in answer.json with keys: "source" (input file name), "rows_in" (total input rows including duplicates), and "rows_used" (distinct rows with known amounts).
7. Exclude rows with missing or invalid amounts from calculations as specified.
8. Re-check all output formats, keys, and values against the RULE texts before finishing.
9. This skill also applies to the held-out evaluation task of the data family.

Self-check:
- Are duplicates removed correctly by unique key?
- Are all dates parsed and converted to UTC naive format?
- Are region names normalized exactly as required?
- Are monetary amounts converted to integer cents?
- Is the meta block present and correct in answer.json?
- Is the output CSV written with the exact header and format?
- Have you verified all output against the rules?
