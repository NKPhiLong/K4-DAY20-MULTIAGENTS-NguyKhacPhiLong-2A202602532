---
name: code-package-quality-assurance
description: Use when developing or fixing a code package to ensure compliance with coding and testing conventions.
---
1. Always add full type annotations on all public functions (functions whose names do not start with '_'), including all parameters and return types, as required by rule_type_hints.
2. Implement regression tests for every bug fix: create or update tests/test_regressions.py with at least one test function per fixed bug (minimum three), ensuring the test file passes without errors, as required by rule_regression_tests.
3. Update CHANGELOG.md under the '## Unreleased' heading with a bullet for each fix in the format '- fix(<function name>): <short description>', with at least three bullets per task, as required by rule_changelog.
4. Before finishing, run all tests with the correct environment variables (e.g., PYTHONPATH) set so that imports resolve correctly; verify tests pass without import or runtime errors.
5. Re-check all code changes against the rules to ensure no violations remain.
6. Self-check:
   - Are all public functions fully type-annotated?
   - Is tests/test_regressions.py present with at least three test functions for fixed bugs?
   - Is CHANGELOG.md updated with at least three fix bullets under '## Unreleased'?
   - Do all tests pass when run with the correct environment?
