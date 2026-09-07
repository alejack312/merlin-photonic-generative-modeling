# Isolated resource pilots for local quantum maps
Date: 2026-09-07 · Scope: project · Recurs when: a bounded deployment size needs timing and RSS evidence without a global superoperator

## Context & constraints
- The deployment evaluator stores local 2x2/4x4 maps and a `(2**n, 2**n)` density matrix; a `4^n x 4^n` circuit matrix is outside scope.
- Windows venv workers expose RSS through the process working set; optional RSS packages are not required.
- The n=10 gate is strict: peak RSS minus the first baseline must be below 400 MiB.

## Approach
1. Run one deterministic representative path-chain case per size in a fresh subprocess.
2. Let the worker report a ready baseline before compilation, then start it explicitly so parent sampling covers only the measured workload.
3. Time compilation, complete local-map construction, and exact density evaluation separately; sample parent-observed peak working set.
4. Validate finite timing, normalized probability mass, state shape, and the no-global-superoperator contract before accepting a worker result.
5. Write commands, source commit/hash, environment, baselines, peaks, growth, and strict PASS/INCONCLUSIVE/FAIL status to the scoped JSON artifact.

## Decision rules that generalize
- IF a memory sampler is unavailable THEN keep timing evidence but mark the RSS criterion INCONCLUSIVE.
- IF a worker times out, exits nonzero, or violates the allocation contract THEN mark the measurement FAIL even if its partial RSS is below budget.
- IF n=10 growth is exactly the limit THEN mark it FAIL; the requirement is strictly less than 400 MiB.
- IF a shared manifest or test changes concurrently THEN preserve it and report its result separately from the owned pilot.

## Mistakes avoided / dead ends
- A direct `--worker` invocation waits for the parent start signal; use the top-level pilot command for valid isolated evidence.
- The initial loop-based n=10 density walk exceeded the bounded timeout; vectorized local reshaping preserved the local-map algebra while making the pilot finish.

## Verification
- `venv\\Scripts\\python.exe -m pytest -q tests\\v4_tcdp\\test_resource_pilot.py` → 4 passed.
- `venv\\Scripts\\python.exe -m py_compile scripts\\v4_tcdp\\resource_pilot.py` → passed.
- Four isolated cases n=4/6/8/10 passed; n=10 measured 4.72 s and 0 MiB growth.

## Next time (for a weaker model)
- Do: inspect the existing evaluator, define the allocation invariant, and add a parent/worker handshake before measuring.
- Don't: infer RSS from the parent process, run an unbounded n=10 chain, or call a partial timeout a PASS.

## Changed files
- `scripts/v4_tcdp/resource_pilot.py` — bounded subprocess timing/RSS pilot.
- `results/v4_tcdp/deploy/resource_budget.json` — reproducible pilot evidence and provenance.
