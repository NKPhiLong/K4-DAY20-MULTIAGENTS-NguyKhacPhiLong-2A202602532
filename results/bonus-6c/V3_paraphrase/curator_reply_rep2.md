=== SKILL: code-package-fixes-and-tests ===
---
name: code-package-fixes-and-tests
description: Use when fixing bugs and improving a code package with regression tests and changelog updates
---
1. Always add full type annotations (type hints) on all parameters and return values of every public function (functions whose names do not start with '_').
2. For every bug fix, add a corresponding test function in the file tests/test_regressions.py; include at least three such tests if fixing multiple bugs.
3. Ensure tests/test_regressions.py passes without errors or import issues; set PYTHONPATH or fix imports as needed.
4. Record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function name>): <short description>'; add at least three bullets if fixing multiple bugs.
5. Follow all naming, formatting, and sorting conventions exactly as stated in the RULE texts.
6. Re-check the entire package for compliance with all rules before finishing.
7. This skill also applies to the held-out evaluation task of the code family.

Self-check:
- Are all public functions fully type-annotated?
- Are regression tests added and passing?
- Is CHANGELOG.md updated with all fixes under '## Unreleased'?
- Are all naming and formatting rules strictly followed?
- Have you tested the package import and test execution environment?

=== SKILL: data-cleaning-and-aggregation ===
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

=== SKILL: log-file-parsing-and-triage ===
---
name: log-file-parsing-and-triage
description: Use when parsing log files to extract error entries and produce structured JSON summaries
---
1. Filter log entries to include only those with level ERROR or CRITICAL (case insensitive).
2. Convert all timestamps to UTC in the exact format YYYY-MM-DDTHH:MM:SSZ.
3. Normalize service names to lower-case with hyphens replaced by underscores (e.g., payment-service → payment_service).
4. Extract the message text after the service name and level on the first line of the entry.
5. Extract the last line of the traceback as the exception field; if no traceback, set exception to null.
6. Calculate repeat_count by summing the initial occurrence plus all subsequent lines of the form "-- last message repeated N times --".
7. Sort the errors array by service name, then by timestamp_utc ascending.
8. Include top-level keys "schema_version": 2 and "generated_by": "log-triage" exactly as stated.
9. Aggregate counts_by_service with service names normalized as above and counts equal to the sum of repeat_count per service.
10. Verify the total number of entries matches the expected count.
11. Re-check all output fields, formats, and sorting against the RULE texts before finishing.
12. This skill also applies to the held-out evaluation task of the logs family.

Self-check:
- Are only ERROR and CRITICAL entries included?
- Are timestamps converted and formatted correctly?
- Are service names normalized properly?
- Are repeat counts calculated correctly including repeats?
- Is the errors array sorted by service and timestamp ascending?
- Are schema_version and generated_by keys present and correct?
- Are counts_by_service correct and keys normalized?
- Have you verified the total entry count matches the expected number?

=== END ===