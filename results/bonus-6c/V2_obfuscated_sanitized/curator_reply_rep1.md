=== SKILL: code-package-fixes-and-tests ===
---
name: code-package-fixes-and-tests
description: Use when fixing bugs in a code package and adding regression tests with changelog updates
---
1. Always add full type annotations on all public functions (parameters and return types) exactly as required.
2. For every bug fix, add a corresponding regression test function in tests/test_regressions.py; include at least one test per fix.
3. Ensure tests/test_regressions.py passes without errors before finishing.
4. Update CHANGELOG.md under the heading '## Unreleased' with a bullet for each fix in the format:
   '- fix(<function name>): <short description>'
5. Follow all formatting and naming conventions exactly (file names, test function names, changelog format).
6. Run all tests with the correct environment variables (e.g., PYTHONPATH) so imports resolve correctly.
7. Verify that all fixes fully comply with documented rules (e.g., rounding rules, sorting orders, string escaping).
8. Before submitting, re-run tests and check changelog and test files for completeness and correctness.
---
Self-check:
- Are all public functions fully type-annotated?
- Are there regression tests for every fix in tests/test_regressions.py?
- Does tests/test_regressions.py pass with no errors?
- Is CHANGELOG.md updated correctly under '## Unreleased'?
- Have you run tests with correct environment settings to avoid import errors?
- Are all fixes compliant with the stated rules and conventions?
=== END ===

=== SKILL: data-cleaning-and-aggregation ===
---
name: data-cleaning-and-aggregation
description: Use when cleaning, normalizing, and aggregating tabular data from CSV files with multiple formats and conventions
---
1. Parse all input data files carefully, handling all known data format variants explicitly (e.g., multiple date formats, timezone offsets).
2. Normalize categorical fields exactly as specified (e.g., region names with canonical spelling and capitalization).
3. Remove duplicate rows based on the specified key(s), keeping the first occurrence unless otherwise stated.
4. Convert all timestamps to UTC naive datetime in the exact format YYYY-MM-DDTHH:MM:SSZ.
5. Convert monetary values to the required units and formats exactly (e.g., integer cents, no decimals).
6. Exclude or handle missing or invalid data values as specified (e.g., amount = -999 means missing).
7. Compute all requested aggregates precisely, respecting date ranges and filters.
8. Write output files with exact headers, column order, and formats as per rules.
9. Include a meta block in JSON outputs with exact keys and values as required.
10. Avoid using external libraries not guaranteed to be installed; implement parsing logic manually if needed.
11. Before finishing, verify all outputs against every rule and re-check formats, units, and counts.
---
Self-check:
- Are all date formats handled and converted to UTC naive datetime correctly?
- Are categorical fields normalized exactly as required?
- Are duplicates removed correctly by key?
- Are monetary values converted to integer cents?
- Are missing values handled as specified?
- Are output files written with exact headers and formats?
- Is the meta block present and correct in JSON outputs?
- Did you avoid using unavailable external libraries?
- Have you re-checked all outputs against the rules?
=== END ===

=== SKILL: log-file-parsing-and-triage ===
---
name: log-file-parsing-and-triage
description: Use when parsing and summarizing log files into structured JSON with strict formatting and sorting rules
---
1. Read the entire log file and identify all entries, including multi-line tracebacks and repeated message counts.
2. Filter entries by level exactly as specified (e.g., only ERROR and CRITICAL, case insensitive).
3. Normalize service names to lower-case with '-' replaced by '_' exactly as per rule.
4. Convert all timestamps to UTC in the exact format YYYY-MM-DDTHH:MM:SSZ.
5. Extract the message text after the service name and level, and extract the last line of any traceback as the exception field or null if none.
6. Calculate repeat_count by summing the initial occurrence plus all subsequent repeated message lines.
7. Sort the final errors list by service name, then by timestamp_utc ascending.
8. Include the top-level JSON keys "schema_version": 2 and "generated_by": "log-triage" exactly.
9. Compute counts_by_service as the sum of repeat_count per service.
10. Before finishing, verify the number of entries, all timestamps, service names, repeat counts, and sorting comply exactly with the rules.
---
Self-check:
- Are only ERROR and CRITICAL entries included?
- Are service names normalized correctly?
- Are timestamps converted to UTC and formatted exactly?
- Is the message and exception extracted correctly?
- Is repeat_count calculated correctly including repeats?
- Is the errors list sorted by service and timestamp ascending?
- Are schema_version and generated_by keys present and correct?
- Are counts_by_service values correct sums of repeat_count?
- Have you verified all counts and formats before submitting?
=== END ===