---
name: code-package-fixes-and-tests
description: Use when fixing bugs and improving a Python code package with regression tests and changelog updates
---
1. Before editing, read all RULE comments verbatim and note exact requirements for:
   - Type hints on every public function parameter and return value.
   - Regression test file name and location: tests/test_regressions.py.
   - Test coverage: one test function per fixed bug, minimum three tests.
   - Changelog file: CHANGELOG.md, under ## Unreleased, with bullet format:
     '- fix(<function name>): <short description>'.
2. Implement fixes by editing source files; ensure all public functions have complete type annotations.
3. Write regression tests in tests/test_regressions.py, one test per bug fixed; tests must pass.
4. Update CHANGELOG.md exactly as specified, listing all fixes made in this run.
5. Run tests with PYTHONPATH set correctly to avoid import errors.
6. Verify all tests pass before finishing.
7. Self-check:
   - All public functions have type hints on parameters and return.
   - tests/test_regressions.py exists with ≥3 test functions, all passing.
   - CHANGELOG.md updated under ## Unreleased with all fixes listed.
   - Tests run without import or path errors.
