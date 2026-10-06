---
name: code-package-quality-assurance
description: Use when developing or fixing a Python code package to ensure compliance with coding and project conventions.
---
1. Always add complete type annotations on all parameters and return values of every public function (functions whose names do not start with '_').
2. For every bug fix or feature added, create or update tests/test_regressions.py with at least one test function per fix; ensure the test file passes without errors.
3. Update CHANGELOG.md under the heading '## Unreleased' with a bullet for each fix in the format: '- fix(<function name>): <short description>'.
4. Before finishing, run all tests to confirm no errors or failures remain.
5. Use exact file names, test function names, and changelog formatting as specified by the rules.
6. Do not hardcode or manually compute results; implement code changes and verify correctness via automated tests.
7. Self-check:
   - Are all public functions fully type-annotated?
   - Is tests/test_regressions.py present and passing with tests for all fixes?
   - Is CHANGELOG.md updated exactly as required?
   - Have all tests been run and passed successfully?
