"""Phase 18 (Hardness-Under-Loss Assessment) sweep runner CLI.

Root-level script matching this repo's `gradient_variance_sweep.py`/
`cp_alpha_sweep.py` naming convention. Wraps `hardness.sweep.pooled_cell_for_neta`
(Plan 18-05) for a given generator scope across one or more system sizes and
eta values, writing a single flat CSV.

The default ``--backend polarization`` preserves Phase 18's original
Processor+LC implementation. ``--backend merlin-dual-rail`` runs the
established polarization-free QuantumLayer parallel with the same eta grid,
theta substreams, metrics, and herald-accounting convention.

Usage:
    python loss_sweep.py --scope weight1 --n-values 2 3 4 5 6 --n-draws 5 \\
        --out results/v3_hardness/phase18_weight1_loss_sweep.csv

Draw chunking (--draw-start/--draw-count/--combine-chunks), mirroring
gradient_variance_sweep.py's established chunked/resumable pattern (required
given this machine's documented memory constraints -- STATE.md): one
(n, scope) cell's draws can be split across multiple fresh processes without
losing already-completed draws. Since weight-2's expense is per-cell-PER-ETA
(not just per-cell), chunk mode computes one draw sub-range for ALL eta
values in hardness.sweep.ETA_GRID within a single invocation -- draw-range
chunking amortizes across the whole eta grid in one process, rather than
needing a third (eta) chunking dimension:

    python loss_sweep.py --scope mixed --n-values 5 --n-draws 5 \\
        --out results/v3_hardness/phase18_mixed_loss_sweep.csv \\
        --draw-start 0 --draw-count 1
    python loss_sweep.py --scope mixed --n-values 5 --n-draws 5 \\
        --out results/v3_hardness/phase18_mixed_loss_sweep.csv \\
        --draw-start 1 --draw-count 1
    ... (5 chunks of 1 draw = 5 draws total) ...
    python loss_sweep.py --scope mixed --n-values 5 --n-draws 5 \\
        --out results/v3_hardness/phase18_mixed_loss_sweep.csv --append --combine-chunks

draw indices are deterministic RNG substream keys (trainability/rng.py), so
draws [0,1) computed in isolation are bit-identical to draws [0,1) computed
as part of a single draws-[0,5) run -- concatenating chunks and summarizing
once (hardness.sweep.combine_pooled_cells) is exactly equivalent to running
all draws in one process.
"""

import argparse
import csv
import glob
import os
import time
import re

import numpy as np

from merlin_iqp.hardness import sweep

FIELDNAMES = [
    "n",
    "generator_scope",
    "simulation_backend",
    "eta",
    "n_draws",
    "tvd_to_lossless_mean",
    "tvd_to_lossless_std",
    "tvd_to_uniform_mean",
    "tvd_to_uniform_std",
    "tvd_to_product_marginals_mean",
    "tvd_to_product_marginals_std",
    "alpha_mean",
    "alpha_std",
    "herald_failure_prob_mean",
    "herald_failure_prob_std",
    "herald_success_rate_mean",
]


def _validated_chunk_files(pattern, expected_draws=None):
    """Return chunk files after rejecting malformed or incompatible ranges."""
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(f"no chunk files found matching {pattern}")
    intervals = []
    for path in files:
        match = re.search(r"_(\d+)-(\d+)\.npy$", path)
        if match is None:
            raise ValueError(f"chunk filename has no draw interval: {path}")
        start, end = map(int, match.groups())
        if start >= end:
            raise ValueError(f"invalid empty/reversed draw interval in {path}")
        intervals.append((start, end, path))
    intervals.sort()
    for (_, previous_end, previous_path), (start, _, path) in zip(intervals, intervals[1:]):
        if start < previous_end:
            raise ValueError(
                f"overlapping draw chunks: {previous_path} and {path}"
            )
        if start != previous_end:
            raise ValueError(f"gap between draw chunks: {previous_path} and {path}")
    if expected_draws is not None and (
        intervals[0][0] != 0 or intervals[-1][1] != expected_draws
    ):
        raise ValueError(
            f"chunk coverage is [{intervals[0][0]},{intervals[-1][1]}), "
            f"expected [0,{expected_draws})"
        )
    return [path for _, _, path in intervals]

# weight2_pair/seed_base are fixed constants across every invocation of this
# CLI (mirroring gradient_variance_sweep.py's own fixed weight2_pair=(0, 1),
# seed_base=170917 convention) -- not exposed as CLI flags, since Phase 18
# has no need to vary either.
WEIGHT2_PAIR = (0, 1)
SEED_BASE = 180814


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run Phase 18's photon-loss TVD/anticoncentration/herald-failure sweep."
    )
    parser.add_argument(
        "--scope",
        required=True,
        choices=["weight1", "mixed"],
        help="Generator scope: weight1-only or mixed weight-1+weight-2.",
    )
    parser.add_argument(
        "--backend",
        choices=list(sweep.BACKENDS),
        default="polarization",
        help=(
            "Loss simulation backend (default: polarization). The "
            "merlin-dual-rail backend runs the equivalent polarization-free "
            "QuantumLayer circuit with MerLin's photon-loss transform."
        ),
    )
    parser.add_argument(
        "--n-values",
        required=True,
        type=int,
        nargs="+",
        help="System sizes (number of qubits/modes) to sweep, e.g. 2 3 4 5 6.",
    )
    parser.add_argument(
        "--eta-grid",
        type=float,
        nargs="+",
        default=None,
        help=(
            "Transmittance eta values to sweep (default: hardness.sweep.ETA_GRID's "
            "own fixed 7-point grid, shared across both scopes per 18-CONTEXT.md)."
        ),
    )
    parser.add_argument(
        "--n-draws",
        type=int,
        default=5,
        help=(
            "Number of independent random-theta draws per (n, eta) cell (default: 5 -- "
            "deliberately lower than Phase 17's 100: TVD/alpha are distribution-level "
            "exact quantities per draw, not noisy per-parameter gradient samples, so a "
            "handful of draws is enough to check robustness across circuit instances)."
        ),
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output CSV path.",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help=(
            "Append rows to --out instead of overwriting it (no header rewrite). "
            "Used for chunked (per-n, per-process) runs so a crash in one chunk "
            "does not lose already-completed cells from earlier chunks."
        ),
    )
    parser.add_argument(
        "--draw-start",
        type=int,
        default=None,
        help=(
            "Draw-chunk mode: compute only draws [draw-start, draw-start+draw-count) "
            "for a single (n, scope) cell, across ALL --eta-grid values, and save raw "
            "per-draw values to .npy chunk files instead of writing CSV rows. Requires "
            "exactly one --n-values value and --draw-count."
        ),
    )
    parser.add_argument(
        "--draw-count",
        type=int,
        default=None,
        help="Draw-chunk mode: number of draws in this chunk. Requires --draw-start.",
    )
    parser.add_argument(
        "--combine-chunks",
        action="store_true",
        help=(
            "Load all .npy chunk files previously written by --draw-start/--draw-count "
            "for a single (n, scope) cell, concatenate per eta, summarize once, and "
            "write/append the final CSV rows (one per eta in --eta-grid). Requires "
            "exactly one --n-values value."
        ),
    )
    args = parser.parse_args()
    if (args.draw_start is None) != (args.draw_count is None):
        parser.error("--draw-start and --draw-count must be given together")
    if args.draw_start is not None or args.combine_chunks:
        if len(args.n_values) != 1:
            parser.error(
                "--draw-start/--draw-count/--combine-chunks require exactly one --n-values value"
            )
    if args.draw_start is not None and args.combine_chunks:
        parser.error("--draw-start/--draw-count and --combine-chunks are mutually exclusive")
    if args.eta_grid is None:
        args.eta_grid = list(sweep.ETA_GRID)
    return args


def _chunk_dir(out_path):
    d = out_path + ".chunks"
    os.makedirs(d, exist_ok=True)
    return d


def _chunk_path(out_path, backend, scope, n, eta, draw_start, draw_count):
    return os.path.join(
        _chunk_dir(out_path),
        f"{backend}_{scope}_n{n}_eta{eta:g}_{draw_start}-{draw_start + draw_count}.npy",
    )


def _row_from_summary(n, scope, backend, eta, summary):
    return {
        "n": n,
        "generator_scope": scope,
        "simulation_backend": backend,
        "eta": eta,
        "n_draws": summary["n_draws"],
        "tvd_to_lossless_mean": summary["tvd_to_lossless_mean"],
        "tvd_to_lossless_std": summary["tvd_to_lossless_std"],
        "tvd_to_uniform_mean": summary["tvd_to_uniform_mean"],
        "tvd_to_uniform_std": summary["tvd_to_uniform_std"],
        "tvd_to_product_marginals_mean": summary["tvd_to_product_marginals_mean"],
        "tvd_to_product_marginals_std": summary["tvd_to_product_marginals_std"],
        "alpha_mean": summary["alpha_mean"],
        "alpha_std": summary["alpha_std"],
        # weight1 has no herald -- left blank/NaN, matching this project's
        # existing "explicit blank, never a fabricated 0" convention for
        # scope-inapplicable columns.
        "herald_failure_prob_mean": summary.get("herald_failure_prob_mean", ""),
        "herald_failure_prob_std": summary.get("herald_failure_prob_std", ""),
        "herald_success_rate_mean": summary.get("herald_success_rate_mean", ""),
    }


def run_chunk(args):
    """Draw-chunk mode: compute one draw sub-range for one (n, scope) cell,
    across ALL --eta-grid values, saving raw per-draw arrays to .npy files.
    No CSV rows are written."""
    n = args.n_values[0]
    for eta in args.eta_grid:
        start = time.time()
        _summary, raw = sweep.pooled_cell_for_neta(
            n,
            eta,
            args.scope,
            draw_start=args.draw_start,
            draw_count=args.draw_count,
            weight2_pair=WEIGHT2_PAIR,
            seed_base=SEED_BASE,
            backend=args.backend,
        )
        elapsed = time.time() - start
        path = _chunk_path(
            args.out,
            args.backend,
            args.scope,
            n,
            eta,
            args.draw_start,
            args.draw_count,
        )
        np.save(path, raw)
        print(
            f"n={n} eta={eta:g} draws=[{args.draw_start},{args.draw_start + args.draw_count}): "
            f"{raw.shape[0]} draws ({elapsed:.1f}s) -> {path}",
            flush=True,
        )


def combine_chunks(args, writer, f):
    """Load every .npy chunk for this (scope, n), one eta at a time,
    concatenate, summarize once (identical math to a single-process run
    over the full draw range), and write the final CSV row per eta."""
    n = args.n_values[0]
    rows = []
    for eta in args.eta_grid:
        pattern = os.path.join(
            _chunk_dir(args.out),
            f"{args.backend}_{args.scope}_n{n}_eta{eta:g}_*.npy",
        )
        chunk_files = _validated_chunk_files(pattern, expected_draws=args.n_draws)
        arrays = [np.load(p) for p in chunk_files]
        summary = sweep.combine_pooled_cells(arrays, args.scope)
        row = _row_from_summary(n, args.scope, args.backend, eta, summary)
        writer.writerow(row)
        f.flush()
        os.fsync(f.fileno())
        rows.append(row)
        print(
            f"n={n} eta={eta:g}: combined {len(chunk_files)} chunks, "
            f"n_draws={summary['n_draws']}, "
            f"tvd_to_lossless_mean={summary['tvd_to_lossless_mean']:.3e} -> {args.out}",
            flush=True,
        )
    return rows


def run(args, writer, f):
    """Run every (n, eta) cell, writing+flushing each row to disk
    immediately after it completes (not buffered until the whole sweep
    finishes) -- a crash mid-sweep loses at most the in-progress cell, not
    every already-completed row."""
    rows = []
    for n in args.n_values:
        for eta in args.eta_grid:
            start = time.time()
            summary, _raw = sweep.pooled_cell_for_neta(
                n,
                eta,
                args.scope,
                draw_start=0,
                draw_count=args.n_draws,
                weight2_pair=WEIGHT2_PAIR,
                seed_base=SEED_BASE,
                backend=args.backend,
            )
            elapsed = time.time() - start
            row = _row_from_summary(n, args.scope, args.backend, eta, summary)
            rows.append(row)
            writer.writerow(row)
            f.flush()
            os.fsync(f.fileno())
            print(
                f"n={n} eta={eta:g}: tvd_to_lossless_mean={summary['tvd_to_lossless_mean']:.3e} "
                f"alpha_mean={summary['alpha_mean']:.3e} ({elapsed:.1f}s)",
                flush=True,
            )
    return rows


if __name__ == "__main__":
    args = parse_args()
    if args.draw_start is not None:
        run_chunk(args)
    else:
        write_header = not (args.append and os.path.exists(args.out))
        mode = "a" if args.append else "w"
        with open(args.out, mode, newline="") as out_f:
            csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES)
            if write_header:
                csv_writer.writeheader()
                out_f.flush()
            if args.combine_chunks:
                all_rows = combine_chunks(args, csv_writer, out_f)
            else:
                all_rows = run(args, csv_writer, out_f)
        print(f"Wrote {len(all_rows)} rows to {args.out}")
