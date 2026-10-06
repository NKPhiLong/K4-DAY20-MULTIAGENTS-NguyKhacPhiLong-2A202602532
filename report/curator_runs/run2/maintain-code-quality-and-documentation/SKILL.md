---
name: maintain-code-quality-and-documentation
description: Use when writing or fixing code to ensure maintainability, correctness, and traceability.
---
1. Add type annotations to all public functions on parameters and return values.
2. Write regression tests for every bug fixed; place them in the specified test file (e.g., `tests/test_regressions.py`).
3. Follow the exact test naming and structure conventions (one test function per bug).
4. Update the changelog file (`CHANGELOG.md`) under the '## Unreleased' heading with a bullet for each fix, using the exact format:
   `- fix(<function name>): <short description>`
5. Use automated test runs to verify all tests pass before finishing.
6. Avoid manual fixes without tests; every fix must be covered by a regression test.
7. Use consistent code style and formatting.
8. Self-check:
   - Are all public functions fully type-annotated?
   - Have I added regression tests for all fixed bugs?
   - Does the changelog include all fixes in the correct format and section?
   - Do all tests pass without errors?
   - Is the code style consistent and clear?
