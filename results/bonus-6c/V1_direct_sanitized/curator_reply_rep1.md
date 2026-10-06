=== SKILL: code-package-fixes-and-tests ===
---
name: code-package-fixes-and-tests
description: Use when fixing bugs in a code package and adding regression tests
---
1. Always add or update type annotations on all public functions (those not starting with '_'), including all parameters and return types, exactly as required.
2. For every bug fix, add a corresponding regression test function in tests/test_regressions.py; include at least one test per bug fixed.
3. Ensure tests/test_regressions.py passes without errors or import issues; set PYTHONPATH or fix imports so the package modules are found.
4. Update CHANGELOG.md under the '## Unreleased' heading with a bullet for each fix in the format: '- fix(<function name>): <short description>'.
5. Before finishing, run all tests and confirm they pass.
6. Verify all fixes strictly follow the documented behavior and formatting rules (e.g., sorting, rounding, string escaping).
7. Self-check:
   - Are all public functions fully type-annotated?
   - Is tests/test_regressions.py present and passing?
   - Is CHANGELOG.md updated correctly?
   - Are all fixes verified by tests and conforming to rules?
=== END ===

=== SKILL: data-cleaning-and-aggregation ===
---
name: data-cleaning-and-aggregation
description: Use when cleaning, normalizing, and aggregating tabular data from CSV or similar sources
---
1. Parse all input data programmatically; do not compute or transform data manually.
2. Normalize all categorical fields exactly as specified (e.g., region names canonical spelling and capitalization).
3. Parse all date/time fields handling all documented formats and time zones; convert all timestamps to UTC naive datetime or specified format.
4. Remove duplicate rows based on the specified key(s), keeping the first occurrence.
5. Convert monetary values to the required units and formats exactly (e.g., integer cents, no decimals).
6. Write output files with exact headers, column order, and formats as specified by rules.
7. Include a meta block in JSON outputs with exact keys and values: source filename, rows_in (including duplicates), rows_used (filtered rows).
8. Avoid using external libraries not guaranteed to be installed; implement parsing and conversions with standard libraries.
9. Before finishing, verify output files conform exactly to all formatting and content rules.
10. Self-check:
    - Are all date/time fields parsed and converted correctly?
    - Are duplicates removed as required?
    - Are monetary values converted to integer cents?
    - Is the meta block present and correct?
    - Are output files named and formatted exactly as required?
=== END ===

=== SKILL: log-file-parsing-and-triage ===
---
name: log-file-parsing-and-triage
description: Use when parsing and summarizing log files into structured JSON error reports
---
1. Filter log entries strictly by the required levels (e.g., ERROR and CRITICAL), case-insensitive.
2. Normalize service names to lower-case with '-' replaced by '_'.
3. Convert all timestamps to UTC in the exact format YYYY-MM-DDTHH:MM:SSZ.
4. Extract the first line message after the service name and level, and the last line of any traceback as the exception; use null if no exception.
5. Calculate repeat_count by summing the initial occurrence plus all subsequent '-- last message repeated N times --' lines.
6. Sort the final errors list by service name, then by timestamp_utc ascending.
7. Include top-level keys "schema_version": 2 and "generated_by": "log-triage" exactly.
8. Aggregate counts_by_service by summing repeat_count per service.
9. Before finishing, verify the number of entries, timestamps, service names, repeat counts, and exception fields all conform exactly to the rules.
10. Self-check:
    - Are service names normalized correctly?
    - Are timestamps converted and formatted correctly?
    - Are repeat counts calculated correctly?
    - Is the output sorted as required?
    - Are schema_version and generated_by present and correct?
=== END ===