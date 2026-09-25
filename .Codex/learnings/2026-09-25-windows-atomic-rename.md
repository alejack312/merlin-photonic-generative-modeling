# Windows artifact rename retries
Date: 2026-09-25 · Scope: project · Recurs when: full Windows test runs intermittently deny atomic artifact commits

## Context & constraints
- Python 3.12 on Windows uses `os.rename` for no-overwrite artifact commits.
- Full-suite failures were `PermissionError` / `WinError 5`, while isolated writer tests passed.
- `FileExistsError` is a collision signal and must not be retried or overwritten.

## Approach
1. Record the exact failing test and exception before changing code.
2. Confirm no concurrent pytest or scanner was launched by the session.
3. Centralize `os.rename` in one helper with four short backoff sleeps and five total attempts.
4. Route every existing direct artifact-writer call through the helper.
5. Test transient permission failure, persistent permission failure, and immediate collision behavior.

## Decision rules that generalize
- IF an artifact rename raises `PermissionError`, THEN retry only within a bounded sub-second budget.
- IF an artifact rename raises `FileExistsError`, THEN re-raise immediately and preserve the destination.
- IF isolated tests pass but full-order tests fail on Windows, THEN use a fresh temp root and inspect handle-sensitive atomic writers before changing semantics.

## Mistakes avoided / dead ends
- Do not replace `os.rename` with `os.replace`; that changes no-overwrite behavior.
- Do not classify a full-suite failure as a scientific failure when the stack trace is a filesystem commit error.

## Verification
- Focused helper/ring/replay tests: `28 passed`.
- Two consecutive full suites outside the sandbox: `729 passed, 1 skipped` each.
- Artifact validator: `579` JSON, `72` JSONL rows, `19` payload hashes, zero failures.

## Next time (for a weaker model)
- Do: isolate the writer, capture the Windows error code, and test collision semantics first.
- Don't: retry all exceptions or run scientific experiments before the baseline is green.

## Changed files
- `src/merlin_iqp/_atomic.py` — shared bounded rename helper.
- `tests/v4_tcdp/test_atomic.py` — retry and collision contract tests.
