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
