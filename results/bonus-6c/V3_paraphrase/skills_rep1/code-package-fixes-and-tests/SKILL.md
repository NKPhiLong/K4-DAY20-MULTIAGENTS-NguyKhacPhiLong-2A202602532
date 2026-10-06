---
name: code-package-fixes-and-tests
description: Use when fixing bugs and improving a code package with regression tests and changelog updates
---
1. Always add full type annotations (type hints) on all parameters and return values of every public function (functions whose names do not start with '_').
2. For every bug fix, add a corresponding regression test function in the file tests/test_regressions.py; include at least three such tests if fixing multiple bugs.
3. Ensure tests/test_regressions.py passes without errors or import issues; set PYTHONPATH or fix imports as needed.
4. Record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function name>): <short description>'; include at least three bullets if fixing multiple bugs.
5. Follow all naming, formatting, and sorting conventions exactly as stated in the RULE texts.
6. Before finishing, run all tests and confirm they pass.
7. This also applies to the held-out evaluation task of the code family.
---
Self-check:
- Are all public functions fully type-annotated?
- Are regression tests added and passing?
- Is CHANGELOG.md updated with all fixes under '## Unreleased'?
- Are imports and test environment configured so tests run without import errors?
- Have I run all tests and confirmed success?
