---
name: automate-data-processing-and-validation
description: Use when processing data or logs that require normalization, deduplication, timezone handling, and format conversions.
---
1. Always write and run scripts to process data instead of manual calculations.
2. Handle all known data formats explicitly and robustly (e.g., multiple date formats, timezone offsets).
3. Normalize categorical data strictly according to canonical forms (e.g., region names capitalized exactly as specified).
4. Remove duplicates based on unique keys, keeping the first or last occurrence as required.
5. Convert all timestamps to the required timezone and format (e.g., UTC naive or with 'Z' suffix).
6. Convert monetary values to the required units and types (e.g., integer cents, not floats).
7. Validate output data against all rules before submission (e.g., check counts, formats, keys).
8. If external libraries are not available, implement parsing manually or fallback gracefully.
9. Self-check:
   - Did I automate all data transformations in code?
   - Did I handle all input formats and edge cases?
   - Did I normalize and deduplicate data as required?
   - Did I convert timestamps and money values exactly as specified?
   - Did I validate output files against all rules?
