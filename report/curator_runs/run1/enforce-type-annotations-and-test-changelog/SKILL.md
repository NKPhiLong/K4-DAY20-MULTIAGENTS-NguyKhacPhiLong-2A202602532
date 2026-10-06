---
name: enforce-type-annotations-and-test-changelog
description: Use when developing or maintaining code packages with public functions and bug fixes.
---
1. For every public function (not starting with '_'), add complete type annotations for all parameters and the return value.
2. After fixing bugs, add at least one regression test per bug in a dedicated test file (e.g., tests/test_regressions.py).
3. Ensure all regression tests pass before finalizing changes.
4. Record each bug fix in the CHANGELOG.md under the '## Unreleased' heading as a bullet point with the format: '- fix(<function name>): <short description>'.
5. Run automated checks to verify type annotations, test coverage, and changelog entries before submission.
6. Self-check:
   - Are all public functions fully type-annotated?
   - Are regression tests added and passing for all fixes?
   - Is the changelog updated correctly with all fixes listed?
