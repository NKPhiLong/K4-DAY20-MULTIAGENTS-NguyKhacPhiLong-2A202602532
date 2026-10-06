=== SKILL: code-package-fixes-and-tests ===
---
name: code-package-fixes-and-tests
description: Use when fixing bugs and improving a Python code package with regression tests and changelog updates
---
1. Before editing, read all RULE comments verbatim and note every required convention exactly (e.g., type hints on all public functions, exact test file name and location, changelog format).
2. Add or update type annotations on all public functions (names not starting with '_') for all parameters and return values.
3. For every bug fix, add a regression test function in the file tests/test_regressions.py; name tests clearly and cover all fixed bugs; ensure the test file passes without errors.
4. Update CHANGELOG.md under the heading '## Unreleased' with one bullet per fix, using the exact format: '- fix(<function name>): <short description>'.
5. After all edits, run all tests with the correct PYTHONPATH or environment so imports resolve; fix import errors before finishing.
6. Re-check that all RULEs are fully satisfied: type hints, test file presence and passing, changelog entries exactly as specified.
7. Commit or finalize only after all tests pass and all conventions are met.

Self-check:
- Are all public functions fully type-annotated?
- Is tests/test_regressions.py present with one test per fix and passing?
- Is CHANGELOG.md updated exactly under '## Unreleased' with correct bullet format?
- Did tests run successfully with correct environment settings?

=== END ===

=== SKILL: data-cleaning-and-aggregation ===
---
name: data-cleaning-and-aggregation
description: Use when cleaning, normalizing, and aggregating tabular data from CSV files with multiple formats and conventions
---
1. Read all RULEs verbatim for output file names, JSON keys, data formats, and units (e.g., money in integer cents, timestamp format YYYY-MM-DDTHH:MM:SSZ UTC).
2. Parse input data carefully, handling all known input formats exactly (e.g., multiple date formats, timezone offsets).
3. Normalize categorical fields exactly as specified (e.g., region names canonical spelling: North, South, East, West).
4. Remove duplicate rows by the specified key (e.g., order_id), keeping the first occurrence.
5. Convert all timestamps to UTC naive datetime and format output timestamps exactly as YYYY-MM-DDTHH:MM:SSZ.
6. Convert monetary values to integer cents by multiplying by 100 and rounding as needed; do not output floats.
7. Write clean CSV output with exact header line and columns in the specified order.
8. Create meta information object with exact keys and values as required (source file name, rows_in including duplicates, rows_used counting distinct valid rows).
9. Validate all output files and JSON against the RULEs before finishing.

Self-check:
- Are all timestamps in UTC and formatted exactly as required?
- Are money values integers in cents, not floats?
- Is the output CSV header exactly as specified?
- Are duplicates removed correctly and meta counts accurate?

=== END ===

=== SKILL: log-file-parsing-and-triage ===
---
name: log-file-parsing-and-triage
description: Use when parsing service logs to extract error entries with normalized fields and summary counts
---
1. Read the entire log file and identify entries with level ERROR or CRITICAL (case insensitive).
2. Convert all timestamps to UTC and format as YYYY-MM-DDTHH:MM:SSZ exactly.
3. Normalize service names to lower-case with '-' replaced by '_' (e.g., payment-service → payment_service).
4. Extract the first line message after "<service>: " as the main message.
5. Extract the last line of the traceback as the exception field; if no traceback, set exception to null.
6. Calculate repeat_count by summing the initial occurrence plus all following lines of the form "-- last message repeated N times --".
7. Sort the final errors list by service name, then by timestamp_utc ascending.
8. Include top-level keys "schema_version": 2 and "generated_by": "log-triage" exactly in the output JSON.
9. Aggregate counts_by_service summing repeat_count per normalized service.
10. Validate the output JSON structure and values against all RULEs before finishing.

Self-check:
- Are all timestamps converted and formatted exactly as required?
- Are service names normalized exactly as specified?
- Are repeat counts correctly summed including repeated lines?
- Is the errors list sorted by service then timestamp ascending?
- Does the output JSON include required top-level keys and correct counts?

=== END ===