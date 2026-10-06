---
name: code-package-quality-assurance
description: Use when developing or fixing a code package to ensure compliance with coding and testing conventions.
---
1. Always add full type annotations (type hints) on all public functions (those whose names do not start with '_'), including all parameters and return types, as required by rule_type_hints.
2. Implement regression tests for every bug fix: create or update tests/test_regressions.py with at least one test function per fixed bug (minimum 3), ensuring the test file passes without errors, as required by rule_regression_tests.
3. Update CHANGELOG.md under the '## Unreleased' heading with a bullet for each fix in the format '- fix(<function name>): <short description>', with at least 3 bullets, as required by rule_changelog.
4. Before finishing, run all tests with the correct environment setup (e.g., PYTHONPATH) to confirm no import errors or test failures remain.
5. Re-check all code changes against the rules to ensure no violations remain.
6. Self-check:
   - Are all public functions fully type-annotated?
   - Is tests/test_regressions.py present with ≥3 test functions for fixed bugs, and does it pass?
   - Is CHANGELOG.md updated with ≥3 fix bullets under '## Unreleased'?
   - Have all tests passed with correct environment variables set?
