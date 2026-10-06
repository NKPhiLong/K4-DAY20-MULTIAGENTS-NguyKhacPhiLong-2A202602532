=== SKILL: code-package-quality-assurance ===
---
name: code-package-quality-assurance
description: Use when developing or fixing a Python code package for code-eval, data-eval, or logs-eval tasks.
---
1. Always add complete type annotations on all parameters and return values of every public function (functions whose names do not start with '_').
2. For every bug fix, add a regression test function in tests/test_regressions.py; include at least three such tests if fixing multiple bugs.
3. Ensure tests/test_regressions.py passes without errors or import issues; set PYTHONPATH or fix imports if needed.
4. Update CHANGELOG.md under the '## Unreleased' heading with one bullet per fix, using the format: '- fix(<function name>): <short description>'.
5. Before finishing, run all tests and confirm they pass.
6. Follow all naming, formatting, and sorting conventions exactly as stated in the RULE comments.
7. Self-check:
   - Are all public functions fully type-annotated?
   - Is tests/test_regressions.py present, correct, and passing?
   - Is CHANGELOG.md updated with all fixes under '## Unreleased'?
   - Have you run tests with PYTHONPATH set if needed and confirmed success?
=== END ===

=== SKILL: data-file-cleaning-and-aggregation ===
---
name: data-file-cleaning-and-aggregation
description: Use when cleaning, normalizing, and aggregating data from CSV or similar files for data-eval, code-eval, or logs-eval tasks.
---
1. Read the input data file exactly as named in the task or RULE.
2. Normalize all categorical fields exactly as specified (e.g., region names must be canonical spelling and capitalization).
3. Parse all date/time fields handling all specified formats and convert timestamps to UTC in the exact format YYYY-MM-DDTHH:MM:SSZ.
4. Remove duplicate rows based on the specified key(s), keeping the first occurrence.
5. Convert all monetary values to integer cents (multiply by 100 and convert to int) if required by the RULE.
6. Write the cleaned CSV file with the exact header line and column order as specified.
7. Produce the answer JSON with the exact keys and value formats required by the RULE.
8. Before finishing, verify:
   - The output CSV file exists with the correct header and data format.
   - The answer JSON contains all required keys with correct data types and formats.
   - Monetary values are integer cents, not floats.
   - Dates and timestamps are in the exact UTC format.
9. Self-check:
   - Did you handle all date formats and timezone offsets correctly?
   - Did you normalize categorical fields exactly as required?
   - Did you remove duplicates correctly?
   - Did you convert money values to integer cents?
   - Did you write output files with exact names and formats?
=== END ===

=== SKILL: log-file-parsing-and-triage ===
---
name: log-file-parsing-and-triage
description: Use when parsing and summarizing log files for code-eval, data-eval, or logs-eval tasks.
---
1. Read the entire log file as specified.
2. Filter entries by the exact log levels required (e.g., ERROR and CRITICAL), case-insensitive.
3. Normalize service names by converting to lower-case and replacing '-' with '_'.
4. Convert all timestamps to UTC timezone and format as YYYY-MM-DDTHH:MM:SSZ exactly.
5. Extract the message text after the service name and level, as specified.
6. Extract the last line of the traceback as the exception field; use null if no traceback.
7. Correctly handle repeated messages by summing the repeat counts from all following '-- last message repeated N times --' lines plus one for the original.
8. Sort the errors array by service name, then by timestamp_utc ascending.
9. Include the top-level keys "schema_version": 2 and "generated_by": "log-triage" exactly.
10. Calculate counts_by_service as the sum of repeat_count per service.
11. Before finishing, verify:
    - The number of entries matches the expected count.
    - All timestamps are correctly converted and formatted.
    - Service names are normalized exactly.
    - The errors list is sorted as required.
    - The output JSON has the exact schema keys and structure.
12. Self-check:
    - Did you handle all timestamp formats and timezone offsets correctly?
    - Did you normalize service names exactly as required?
    - Did you correctly parse and sum repeat counts?
    - Did you sort errors by service and timestamp ascending?
    - Did you include all required top-level keys with exact values?
=== END ===