# Discrete catalog optimization with continuous parameters
Date: 2026-09-06 · Scope: project · Recurs when: a deployed circuit quantizes some parameters onto a finite catalog but leaves others continuous

## Context & constraints
- `deploy.compile` owns the nonuniform wrapped catalog `0.1*j` for `j=0..62`.
- Quantized pair parameters are piecewise constant, so finite differences through compilation do not provide a pair gradient.
- The exact Hamming Gaussian MMD and analytic gradient already exist in `classical.objectives`.

## Approach
1. Represent every pair as an integer catalog key plus an explicit winding; derive the lifted angle from that state.
2. Compile each candidate through the deployment compiler and evaluate the exact objective on compiler-produced lifted pair angles.
3. Search circular `key-1`/`key+1` neighbors coordinate-wise with a strict-improvement rule and a finite evaluation budget.
4. Apply the existing exact analytic gradient update only to the first `n` continuous single-angle coordinates.
5. Serialize settings, seed, compiler/catalog contract, objective, budgets, keys, winding/lift metadata, and hashes.

## Decision rules that generalize
- IF a parameter is catalog-quantized THEN optimize its discrete key directly; do not differentiate through rounding.
- IF a candidate crosses the wrapped catalog boundary THEN choose the winding nearest to the current lifted angle.
- IF an equal-budget continuation is needed THEN hold pair keys fixed while spending the same neighbor-evaluation budget and label the control explicitly.

## Mistakes avoided / dead ends
- Quantized central differences were rejected because most nearby evaluations select the same compiled map.
- Pair interpolation and straight-through gradients were excluded because they optimize a model different from the deployed catalog.

## Verification
- `venv\\Scripts\\python.exe -m pytest -q tests/v4_tcdp/test_nat.py` -> 4 passed.
- CLI n=4 one-step smoke -> 6/6 pair evaluations, 3 key moves, and NAT/control artifacts with matching budgets.
- `venv\\Scripts\\python.exe -m py_compile src\\merlin_iqp\\experiments\\nat.py tests\\v4_tcdp\\test_nat.py scripts\\v4_tcdp\\run_nat.py` -> passed.

## Next time (for a weaker model)
- Do: inspect the compiler's actual key/winding contract, then make the optimizer state match it exactly.
- Don't: claim a pair gradient from finite differences of a quantized circuit.

## Changed files
- `src/merlin_iqp/experiments/nat.py` — bounded NAT optimizer and serializable result.
- `tests/v4_tcdp/test_nat.py` — key movement, catalog/winding, continuous singles, and replay tests.
- `scripts/v4_tcdp/run_nat.py` — bounded smoke/control CLI.
