=== SKILL: code-package-quality-assurance ===
---
name: code-package-quality-assurance
description: Use when developing or fixing a Python code package to ensure compliance with coding and project conventions.
---
1. Always add complete type annotations on all parameters and return values of every public function (functions whose names do not start with '_').
2. For every bug fix or feature added, create or update tests/test_regressions.py with at least one test function per fix; ensure the test file passes without errors.
3. Update CHANGELOG.md under the heading '## Unreleased' with a bullet for each fix in the format: '- fix(<function name>): <short description>'.
4. Before finishing, run all tests to confirm no errors or failures remain.
5. Use exact file names, test function names, and changelog formatting as specified by the rules.
6. Do not hardcode or manually compute results; implement code changes and verify correctness via automated tests.
7. Self-check:
   - Are all public functions fully type-annotated?
   - Is tests/test_regressions.py present and passing with tests for all fixes?
   - Is CHANGELOG.md updated exactly as required?
   - Have all tests been run and passed successfully?

=== END ===

=== SKILL: data-file-cleaning-and-aggregation ===
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

=== END ===

=== SKILL: log-file-parsing-and-triage ===
---
name: log-file-parsing-and-triage
description: Use when parsing log files to extract, normalize, and summarize error entries according to strict schema and formatting rules.
---
1. Read the entire log file and identify all entries, including multi-line entries with tracebacks and repeated message counts.
2. Filter entries to include only those with levels ERROR or CRITICAL (case insensitive).
3. Normalize service names by converting to lower-case and replacing '-' with '_'.
4. Convert all timestamps to UTC timezone and format as YYYY-MM-DDTHH:MM:SSZ exactly.
5. Extract the first line message after the service name and level, and extract the last line of the traceback as the exception if present; otherwise, set exception to null.
6. Calculate repeat_count by summing 1 plus all subsequent lines indicating repeated messages (e.g., "-- last message repeated N times --").
7. Sort the final errors list by service name ascending, then by timestamp_utc ascending.
8. Include a top-level object with keys "schema_version": 2 and "generated_by": "log-triage".
9. Calculate counts_by_service as the sum of repeat_count per normalized service.
10. Write the output JSON file exactly as specified, with all required keys and formats.
11. Before finishing, verify:
    - The number of entries matches the expected count.
    - All timestamps are correctly converted and formatted.
    - All service names are normalized.
    - The errors list is sorted correctly.
    - The top-level schema keys are present and correct.
12. Self-check:
    - Are all repeated messages counted correctly?
    - Are all timestamps converted to UTC and formatted exactly?
    - Are service names normalized as required?
    - Is the output JSON schema exactly as specified?

=== END ===