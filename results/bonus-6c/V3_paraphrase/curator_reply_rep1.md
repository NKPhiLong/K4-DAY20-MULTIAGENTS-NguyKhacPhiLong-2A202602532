=== SKILL: code-package-fixes-and-tests ===
---
name: code-package-fixes-and-tests
description: Use when fixing bugs and improving a code package with regression tests and changelog updates
---
1. Always add full type annotations (type hints) on all parameters and return values of every public function (functions whose names do not start with '_').
2. For every bug fix, add a corresponding regression test function in the file tests/test_regressions.py; include at least three such tests if fixing multiple bugs.
3. Ensure tests/test_regressions.py passes without errors or import issues; set PYTHONPATH or fix imports as needed.
4. Record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function name>): <short description>'; include at least three bullets if fixing multiple bugs.
5. Follow all naming, formatting, and sorting conventions exactly as stated in the RULE texts.
6. Before finishing, run all tests and confirm they pass.
7. This also applies to the held-out evaluation task of the code family.
---
Self-check:
- Are all public functions fully type-annotated?
- Are regression tests added and passing?
- Is CHANGELOG.md updated with all fixes under '## Unreleased'?
- Are imports and test environment configured so tests run without import errors?
- Have I run all tests and confirmed success?
=== END ===

=== SKILL: data-cleaning-and-aggregation ===
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
=== END ===

=== SKILL: log-file-parsing-and-triage ===
---
name: log-file-parsing-and-triage
description: Use when parsing log files to extract error entries and produce structured triage reports
---
1. Read the entire log file and identify all entries, including multi-line entries and repeated message blocks.
2. Filter entries by level exactly as specified (e.g., only ERROR or CRITICAL, case insensitive).
3. Convert all timestamps to UTC in the exact format YYYY-MM-DDTHH:MM:SSZ.
4. Normalize service names to lower-case with hyphens replaced by underscores as required.
5. Extract the message text exactly as specified, and extract the last line of any traceback as the exception field or null if none.
6. Calculate repeat_count by summing the initial occurrence plus all repeated message counts from following lines.
7. Sort the errors array by service name, then by timestamp_utc ascending.
8. Include the top-level keys "schema_version": 2 and "generated_by": "log-triage" exactly as stated.
9. Calculate counts_by_service as the sum of repeat_count per service.
10. Before finishing, verify the number of entries, timestamps, exception fields, repeat counts, service names, sorting, and schema header all conform exactly to the RULEs.
11. This also applies to the held-out evaluation task of the logs family.
---
Self-check:
- Are only ERROR or CRITICAL entries included?
- Are timestamps converted to UTC and formatted correctly?
- Are service names normalized as required?
- Are messages and exceptions extracted correctly?
- Is repeat_count calculated correctly including repeated messages?
- Is the errors list sorted by service and timestamp ascending?
- Are schema_version and generated_by keys present and correct?
- Are counts_by_service values correct?
- Have I verified all RULEs before finishing?
=== END ===