=== SKILL: code-package-fixes-and-tests ===
---
name: code-package-fixes-and-tests
description: Use when fixing bugs and improving a Python code package with regression tests and changelog updates
---
1. Before editing, read all RULE comments verbatim and note exact requirements for:
   - type hints on all public functions (all parameters and return types)
   - regression test file name and structure (tests/test_regressions.py, one test per bug fixed, must pass)
   - changelog format and location (CHANGELOG.md, under ## Unreleased, bullet format with function names)
2. When fixing code:
   - Always add or update type annotations on all public functions exactly as required.
   - Implement fixes fully according to the specification, including edge cases (e.g., string parsing, rounding rules).
   - Follow exact sorting, filtering, and formatting rules stated in the RULEs.
3. After code fixes:
   - Write regression tests for each bug fixed, in the specified test file and format.
   - Run tests with the correct environment variables or PYTHONPATH to ensure imports work.
   - Fix import errors by adjusting PYTHONPATH or test imports as needed.
4. Update CHANGELOG.md exactly as specified, listing each fix with function name and short description.
5. Before finishing:
   - Run all tests and confirm they pass without errors.
   - Re-check all RULEs are satisfied verbatim.
   - Confirm no import or environment errors remain.
6. Self-check:
   - Are all public functions fully type-annotated?
   - Is tests/test_regressions.py present with one test per fix and passing?
   - Is CHANGELOG.md updated under ## Unreleased with all fixes?
   - Did all tests run successfully with correct PYTHONPATH?
=== END ===

=== SKILL: data-cleaning-and-aggregation ===
---
name: data-cleaning-and-aggregation
description: Use when cleaning, normalizing, and aggregating tabular data from CSV files with multiple formats and conventions
---
1. Read all RULEs verbatim about output file names, JSON keys, data formats, and units (e.g., money in integer cents).
2. Parse input data carefully:
   - Handle multiple date formats explicitly and convert all timestamps to UTC naive or specified format exactly.
   - Normalize categorical fields (e.g., region names) to canonical spellings exactly as stated.
   - Remove duplicate rows by unique keys, keeping the first occurrence.
   - Exclude or handle missing values exactly as specified (e.g., amount = -999 means missing).
3. Perform all calculations using code, never by hand.
4. Convert monetary values to integer cents by multiplying and rounding as required.
5. Write output CSV files with exact headers and formats, including timestamp formats and canonical region names.
6. Write output JSON files with exact keys and values as specified in the RULEs.
7. Before finishing:
   - Re-check all output files against every RULE verbatim.
   - Confirm no external dependencies are used if not allowed; implement parsing manually if needed.
   - Run the script end-to-end and verify outputs match expected formats and values.
8. Self-check:
   - Are all timestamps converted to UTC and formatted exactly as required?
   - Are monetary values in integer cents in JSON and CSV?
   - Are duplicate rows removed correctly?
   - Are all output files named and formatted exactly per RULEs?
=== END ===

=== SKILL: log-file-parsing-and-triage ===
---
name: log-file-parsing-and-triage
description: Use when parsing and summarizing log files into structured JSON with strict formatting and sorting rules
---
1. Read all RULEs verbatim about output JSON structure, keys, sorting order, service name formatting, and schema headers.
2. Parse the log file line-by-line:
   - Extract timestamps and convert all to UTC in the exact format YYYY-MM-DDTHH:MM:SSZ.
   - Normalize service names to lower-case with '-' replaced by '_'.
   - Extract log levels and convert to uppercase.
   - Extract messages exactly as specified (text after "<service>: " on first line).
   - Extract the last line of any traceback as the exception field or null if none.
3. Handle repeated messages:
   - Detect lines like "-- last message repeated N times --" and sum repeat counts correctly.
   - Add 1 for the original message plus repeats.
4. Filter entries by level exactly as required (e.g., only ERROR and CRITICAL).
5. Sort the final errors list by service name, then timestamp ascending.
6. Include top-level JSON keys exactly as specified ("schema_version": 2, "generated_by": "log-triage").
7. Calculate counts_by_service by summing repeat_count per service.
8. Before finishing:
   - Re-check all JSON keys, formats, and sorting orders verbatim.
   - Confirm no entries are missing or extra.
   - Validate JSON schema if possible.
9. Self-check:
   - Are timestamps converted and formatted exactly?
   - Are service names normalized exactly?
   - Are repeat counts calculated correctly?
   - Is the output sorted and structured exactly per RULEs?
=== END ===