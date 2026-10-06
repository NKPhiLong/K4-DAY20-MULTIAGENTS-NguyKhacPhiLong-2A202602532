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
