---
name: code-package-fixes-and-tests
description: Use when fixing bugs and improving a Python code package with regression tests and changelog updates
---
1. Before editing, read all RULE comments verbatim and note exact requirements for:
   - type hints on all public functions (all parameters and return types)
   - regression test file name and structure (tests/test_regressions.py, one test per bug fixed, must pass)
   - changelog format and location (CHANGELOG.md, under ## Unreleased, bullet format with function names)
2. When fixing code:
   - Always add or update type annotations on all public functions exactly as required.
   - Implement fixes fully according to the specification, including edge cases (e.g., string parsing, rounding rules).
   - Follow exact sorting, filtering, and formatting rules stated in the RULEs.
3. After code fixes:
   - Write regression tests for each bug fixed, in the specified test file and format.
   - Run tests with the correct environment variables or PYTHONPATH to ensure imports work.
   - Fix import errors by adjusting PYTHONPATH or test imports as needed.
4. Update CHANGELOG.md exactly as specified, listing each fix with function name and short description.
5. Before finishing:
   - Run all tests and confirm they pass without errors.
   - Re-check all RULEs are satisfied verbatim.
   - Confirm no import or environment errors remain.
6. Self-check:
   - Are all public functions fully type-annotated?
   - Is tests/test_regressions.py present with one test per fix and passing?
   - Is CHANGELOG.md updated under ## Unreleased with all fixes?
   - Did all tests run successfully with correct PYTHONPATH?
