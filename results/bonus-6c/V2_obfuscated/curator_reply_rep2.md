=== SKILL: code-package-quality-assurance ===
---
name: code-package-quality-assurance
description: Use when developing or fixing a code package to ensure compliance with coding and testing conventions.
---
1. Always add full type annotations (type hints) on all public functions (those whose names do not start with '_'), including all parameters and return types, as required by rule_type_hints.
2. Implement regression tests for every bug fix: create or update tests/test_regressions.py with at least one test function per fixed bug (minimum 3), ensuring the test file passes without errors, as required by rule_regression_tests.
3. Update CHANGELOG.md under the '## Unreleased' heading with a bullet for each fix in the format '- fix(<function name>): <short description>', with at least 3 bullets, as required by rule_changelog.
4. Before finishing, run all tests with the correct environment setup (e.g., PYTHONPATH) to confirm no import errors or test failures remain.
5. Re-check all code changes against the rules to ensure no violations remain.
6. Self-check:
   - Are all public functions fully type-annotated?
   - Is tests/test_regressions.py present with ≥3 test functions for fixed bugs, and does it pass?
   - Is CHANGELOG.md updated with ≥3 fix bullets under '## Unreleased'?
   - Have all tests passed with correct environment variables set?
=== END ===

=== SKILL: data-analysis-cleaning-and-reporting ===
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
=== END ===

=== SKILL: log-file-parsing-and-triage ===
---
name: log-file-parsing-and-triage
description: Use when parsing log files to extract error entries and produce structured JSON summaries following strict schema and sorting rules.
---
1. Filter log entries strictly by required levels (e.g., ERROR and CRITICAL), case-insensitive.
2. Convert all timestamps to UTC timezone and format as YYYY-MM-DDTHH:MM:SSZ exactly.
3. Normalize service names to lower-case with hyphens replaced by underscores, as per rule_service_names.
4. Extract message text exactly after the service name and colon on the first line.
5. Extract the last line of the traceback as the exception field; if no traceback, set exception to null.
6. Calculate repeat_count by summing the initial occurrence plus all subsequent "-- last message repeated N times --" lines.
7. Sort the errors array by service name ascending, then by timestamp_utc ascending, as required by rule_sorted_errors.
8. Include top-level keys "schema_version": 2 and "generated_by": "log-triage" exactly as required by rule_schema_header.
9. Aggregate counts_by_service correctly by summing repeat_count per normalized service.
10. Verify the total number of entries matches the expected count exactly.
11. Self-check:
    - Are all timestamps converted and formatted correctly?
    - Are service names normalized exactly?
    - Is the errors list sorted correctly?
    - Are repeat_count and exception fields correct for every entry?
    - Does the output JSON include required top-level keys and counts_by_service?
=== END ===