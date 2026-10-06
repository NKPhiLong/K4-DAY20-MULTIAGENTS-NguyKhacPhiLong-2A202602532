---
name: data-cleaning-and-aggregation
description: Use when cleaning, normalizing, and aggregating tabular data from CSV files with multiple formats and conventions
---
1. Parse all input data files carefully, handling all known data format variants explicitly (e.g., multiple date formats, timezone offsets).
2. Normalize categorical fields exactly as specified (e.g., region names with canonical spelling and capitalization).
3. Remove duplicate rows based on the specified key(s), keeping the first occurrence unless otherwise stated.
4. Convert all timestamps to UTC naive datetime in the exact format YYYY-MM-DDTHH:MM:SSZ.
5. Convert monetary values to the required units and formats exactly (e.g., integer cents, no decimals).
6. Exclude or handle missing or invalid data values as specified (e.g., amount = -999 means missing).
7. Compute all requested aggregates precisely, respecting date ranges and filters.
8. Write output files with exact headers, column order, and formats as per rules.
9. Include a meta block in JSON outputs with exact keys and values as required.
10. Avoid using external libraries not guaranteed to be installed; implement parsing logic manually if needed.
11. Before finishing, verify all outputs against every rule and re-check formats, units, and counts.
---
Self-check:
- Are all date formats handled and converted to UTC naive datetime correctly?
- Are categorical fields normalized exactly as required?
- Are duplicates removed correctly by key?
- Are monetary values converted to integer cents?
- Are missing values handled as specified?
- Are output files written with exact headers and formats?
- Is the meta block present and correct in JSON outputs?
- Did you avoid using unavailable external libraries?
- Have you re-checked all outputs against the rules?
