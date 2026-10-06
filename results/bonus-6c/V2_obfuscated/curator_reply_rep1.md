=== SKILL: code-package-quality-assurance ===
---
name: code-package-quality-assurance
description: Use when developing or fixing a code package to ensure compliance with coding and testing conventions.
---
1. Always add full type annotations on all public functions (functions whose names do not start with '_'), including all parameters and return types, as required by rule_type_hints.
2. Implement regression tests for every bug fix: create or update tests/test_regressions.py with at least one test function per fixed bug (minimum three), ensuring the test file passes without errors, as required by rule_regression_tests.
3. Update CHANGELOG.md under the '## Unreleased' heading with a bullet for each fix in the format '- fix(<function name>): <short description>', with at least three bullets per task, as required by rule_changelog.
4. Before finishing, run all tests with the correct environment variables (e.g., PYTHONPATH) set so that imports resolve correctly; verify tests pass without import or runtime errors.
5. Re-check all code changes against the rules to ensure no violations remain.
6. Self-check:
   - Are all public functions fully type-annotated?
   - Is tests/test_regressions.py present with at least three test functions for fixed bugs?
   - Is CHANGELOG.md updated with at least three fix bullets under '## Unreleased'?
   - Do all tests pass when run with the correct environment?
=== END ===

=== SKILL: data-analysis-cleaning-and-reporting ===
---
name: data-analysis-cleaning-and-reporting
description: Use when cleaning, normalizing, and analyzing tabular data to produce JSON reports and cleaned CSV files.
---
1. Carefully read and apply all RULEs verbatim, especially regarding output file names, JSON keys, and data formats.
2. Normalize all categorical fields exactly as specified (e.g., region names must be canonical spelling and capitalization).
3. Parse all date/time fields correctly, handling all specified input formats and converting timestamps to UTC naive datetime or the exact required format (e.g., ISO 8601 with 'Z' suffix).
4. Remove duplicate rows as specified, keeping only the first occurrence per unique key.
5. Convert all monetary values to integer cents in outputs (e.g., 1606.67 USD → 160667), never output floats or strings for money.
6. Write the cleaned CSV file with the exact header line and column order specified by the RULE (e.g., order_id,timestamp_utc,region,amount_cents).
7. Construct the answer JSON with the exact required keys and nested objects, including the meta block with exact keys and values (source filename, rows_in, rows_used).
8. Avoid using external libraries not guaranteed to be installed; implement parsing and conversions manually if needed.
9. Before finishing, verify all output files against every RULE, including formats, keys, and data types.
10. Self-check:
    - Are all money values in integer cents in all outputs?
    - Is the cleaned CSV file named exactly and with the correct header and data format?
    - Does answer.json include the meta block with all required keys and correct values?
    - Are all timestamps converted to UTC and formatted exactly as required?
    - Are duplicates removed correctly and counts accurate?
=== END ===

=== SKILL: log-file-parsing-and-triage ===
---
name: log-file-parsing-and-triage
description: Use when parsing log files to extract error entries and produce structured JSON summaries following strict schema and sorting rules.
---
1. Filter log entries to include only those with level ERROR or CRITICAL (case insensitive).
2. Normalize service names to lower-case and replace all '-' with '_', as required by rule_service_names.
3. Convert all timestamps to UTC and format as YYYY-MM-DDTHH:MM:SSZ exactly, handling all input timezone offsets.
4. Extract the message as the text after "<service>: " on the first line of the entry.
5. Extract the last line of the traceback as the exception field; if no traceback, set exception to null.
6. Calculate repeat_count by summing 1 plus all following lines of the form "-- last message repeated N times --".
7. Sort the errors array by service name ascending, then by timestamp_utc ascending, as required by rule_sorted_errors.
8. Compute counts_by_service as the sum of repeat_count per normalized service.
9. Include the top-level keys "schema_version": 2 and "generated_by": "log-triage" exactly as required by rule_schema_header.
10. Verify the total number of entries matches the expected count (entry_count).
11. Before finishing, re-check all fields and sorting against the rules.
12. Self-check:
    - Are service names normalized correctly?
    - Are timestamps converted and formatted exactly as required?
    - Is errors array sorted by service then timestamp ascending?
    - Are repeat_count and exception fields correct for every entry?
    - Are top-level schema_version and generated_by keys present and correct?
    - Does counts_by_service sum repeat_counts correctly?
=== END ===