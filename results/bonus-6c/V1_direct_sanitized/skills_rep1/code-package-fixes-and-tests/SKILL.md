---
name: code-package-fixes-and-tests
description: Use when fixing bugs in a code package and adding regression tests
---
1. Always add or update type annotations on all public functions (those not starting with '_'), including all parameters and return types, exactly as required.
2. For every bug fix, add a corresponding regression test function in tests/test_regressions.py; include at least one test per bug fixed.
3. Ensure tests/test_regressions.py passes without errors or import issues; set PYTHONPATH or fix imports so the package modules are found.
4. Update CHANGELOG.md under the '## Unreleased' heading with a bullet for each fix in the format: '- fix(<function name>): <short description>'.
5. Before finishing, run all tests and confirm they pass.
6. Verify all fixes strictly follow the documented behavior and formatting rules (e.g., sorting, rounding, string escaping).
7. Self-check:
   - Are all public functions fully type-annotated?
   - Is tests/test_regressions.py present and passing?
   - Is CHANGELOG.md updated correctly?
   - Are all fixes verified by tests and conforming to rules?
