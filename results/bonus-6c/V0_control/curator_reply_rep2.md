=== SKILL: code-package-fixes-and-tests ===
---
name: code-package-fixes-and-tests
description: Use when fixing bugs in a code package and adding regression tests with changelog updates
---
1. Always add or update type annotations on all public functions (those not starting with '_'), including all parameters and return types, exactly as required.
2. For every bug fix, add a corresponding regression test function in tests/test_regressions.py; include at least one test per fixed bug.
3. Ensure tests/test_regressions.py passes without errors before finishing.
4. Update CHANGELOG.md under the heading '## Unreleased' with a bullet for each fix in the format: '- fix(<function name>): <short description>'.
5. Follow all formatting and naming conventions exactly as stated in the RULE texts.
6. Run all tests with the correct environment variables (e.g., PYTHONPATH) so imports resolve correctly.
7. Before submitting, re-run tests to confirm no import errors or test failures remain.
8. Self-check:
   - Are all public functions fully type-annotated?
   - Are regression tests added and passing?
   - Is CHANGELOG.md updated correctly?
   - Did tests run without import or runtime errors?

=== END ===

=== SKILL: data-cleaning-and-aggregation ===
---
name: data-cleaning-and-aggregation
description: Use when cleaning, normalizing, and aggregating tabular data with multiple formats and outputting JSON summaries
---
1. Parse all input data files carefully, handling all known data formats explicitly (e.g., multiple date formats, timezones).
2. Normalize categorical fields exactly as specified (e.g., region names canonical capitalization and spelling).
3. Remove duplicate rows based on the specified key(s), keeping the first occurrence, and count duplicates removed.
4. Convert all timestamps to UTC naive datetime in the exact format YYYY-MM-DDTHH:MM:SSZ.
5. Convert monetary values to integer cents as required (e.g., 1606.67 USD → 160667).
6. Exclude rows with missing or invalid data as specified (e.g., amount = -999).
7. Compute all requested aggregates precisely and output the JSON answer with all required keys and exact key names.
8. Avoid using unavailable external libraries; implement parsing and conversions with standard libraries only.
9. Self-check:
   - Are all date/time values normalized and converted correctly?
   - Are duplicates removed and counted correctly?
   - Are monetary values converted to integer cents?
   - Does the output JSON contain all required keys with correct values?

=== END ===

=== SKILL: log-file-parsing-and-triage ===
---
name: log-file-parsing-and-triage
description: Use when parsing service logs to extract error entries and produce structured error reports
---
1. Read the entire log file and identify entries with level ERROR or CRITICAL (case insensitive).
2. Normalize service names to lower-case and replace '-' with '_' exactly as specified.
3. Convert all timestamps to UTC in the exact format YYYY-MM-DDTHH:MM:SSZ.
4. Extract the message text after the service name and level on the first line of each entry.
5. Extract the last line of the traceback as the exception field; if no traceback, set exception to null.
6. Calculate repeat_count by summing the initial occurrence plus all subsequent lines of the form '-- last message repeated N times --'.
7. Sort the final errors list by service name, then by timestamp_utc ascending.
8. Include top-level keys "schema_version": 2 and "generated_by": "log-triage" in the output JSON.
9. Aggregate counts_by_service as the sum of repeat_count per service.
10. Self-check:
    - Are all timestamps converted and formatted correctly?
    - Are service names normalized exactly?
    - Are repeat counts correctly summed?
    - Is the errors list sorted as required?
    - Does the output JSON include all required top-level keys?

=== END ===