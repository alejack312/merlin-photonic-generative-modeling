"""Phase 17 (Trainability/Barren-Plateau Study) sweep runner CLI.

Root-level script matching this repo's `cp_alpha_sweep.py`/`sigma_resweep.py`
naming convention. Wraps `trainability.sweep.run_gradient_variance_sweep`
(Plan 17-05) for a given generator scope across one or more system sizes and
initialization regimes, writing a single flat CSV.

Usage:
    python gradient_variance_sweep.py --scope weight1 --n-values 2 3 4 5 6 \\
        --init-schemes small_angle uniform \\
        --out results/v3_trainability/phase17_weight1_gradient_variance.csv

    python gradient_variance_sweep.py --scope weight1 --n-values 2 3 4 5 6 \\
        --init-schemes uniform --sigma 0.3 \\
        --out results/v3_trainability/phase17_1_weight1_sigma0.3_gradient_variance.csv

    python gradient_variance_sweep.py --scope weight1 --n-values 2 3 4 5 6 \\
        --init-schemes data_dependent --n-draws 1 --out results/foo.csv

(note --n-draws 1 in the example above -- TRAIN-10's own owner-decided setting,
since data_dependent's thetas are identical on every draw; Plan 17.1-05 will
use this explicitly when it actually runs TRAIN-10.)

This same script serves both the CORE sweeps (synchronous, must complete)
and the STRETCH attempts (n=7 weight-1 / n=6 mixed, run in the background
with no time-box per CONTEXT.md's locked decision) -- only the CLI
arguments differ, no code changes needed between the two.

Draw chunking (--draw-start/--draw-count/--combine-chunks): some (n, scope)
cells accumulate enough memory across ~n_draws x tracked_params x 2 circuit
evaluations within one long-running process to hit a MemoryError inside
Perceval's backend, even though a single evaluation is cheap (confirmed live
during Phase 17 execution -- weight-2's mixed n=5 cell leaks across ~600
repeated calls in one process, while a single call succeeds in ~4s). Since
draw indices are deterministic RNG substream keys (trainability/rng.py),
computing draws [0,20) in one process and draws [20,40) in a fresh process
is bit-identical to computing draws [0,40) in a single process -- chunking
across several fresh processes, each handling a draw sub-range, sidesteps
the leak without changing any result:

    python gradient_variance_sweep.py --scope mixed --n-values 5 \\
        --init-schemes small_angle --out results/foo.csv \\
        --draw-start 0 --draw-count 20
    python gradient_variance_sweep.py --scope mixed --n-values 5 \\
        --init-schemes small_angle --out results/foo.csv \\
        --draw-start 20 --draw-count 20
    ... (5 chunks of 20 = 100 draws total) ...
    python gradient_variance_sweep.py --scope mixed --n-values 5 \\
        --init-schemes small_angle --out results/foo.csv --append \\
        --combine-chunks
"""

import argparse
import csv
import glob
import os
import time
import re

import numpy as np

from merlin_iqp.trainability import stats, target_grid
from merlin_iqp.trainability.sweep import pooled_gradients_for_cell, run_gradient_variance_sweep

# "sigma" and "bin_spacing" are per-row reporting columns (TRAIN-09/ROADMAP.md Phase
# 17.1 success criterion 1) -- they record what bandwidth/grid-geometry produced this
# row, but are NOT inputs to summarize_gradient_samples's summary statistics themselves.
FIELDNAMES = [
    "n",
    "generator_scope",
    "init_scheme",
    "n_tracked_params",
    "n_samples",
    "mean",
    "var",
    "std",
    "median",
    "abs_mean",
    "rms",
    "sigma",
    "bin_spacing",
]


def _validated_chunk_files(pattern):
    """Return chunk files after rejecting malformed or overlapping ranges."""
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
            raise ValueError(f"overlapping draw chunks: {previous_path} and {path}")
    return [path for _, _, path in intervals]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run Phase 17's exact parameter-shift gradient-variance-vs-n sweep."
    )
    parser.add_argument(
        "--scope",
        required=True,
        choices=["weight1", "mixed"],
        help="Generator scope: weight1-only or mixed weight-1+weight-2.",
    )
    parser.add_argument(
        "--n-values",
        required=True,
        type=int,
        nargs="+",
        help="System sizes (number of qubits/modes) to sweep, e.g. 2 3 4 5 6.",
    )
    parser.add_argument(
        "--init-schemes",
        required=True,
        nargs="+",
        choices=["small_angle", "uniform", "data_dependent"],
        help="Initialization regime(s) to run, e.g. small_angle uniform data_dependent.",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output CSV path.",
    )
    parser.add_argument(
        "--n-draws",
        type=int,
        default=100,
        help="Number of independent random parameter draws per (n, init_scheme) cell (default: 100).",
    )
    parser.add_argument(
        "--max-tracked-params",
        type=int,
        default=3,
        help="Cap on tracked parameter indices per n (default: 3).",
    )
    parser.add_argument(
        "--sigma",
        type=float,
        default=0.1,
        help=(
            "MMD kernel bandwidth, held fixed across the whole n-range for this "
            "invocation (default: 0.1, Phase 17's original value)."
        ),
    )
    parser.add_argument(
        "--scale-factor",
        type=float,
        default=1.0,
        help=(
            "Weight-2 pair covariance-scaling hyperparameter for "
            "init_scheme='data_dependent' (default: 1.0, owner-decided per "
            "17.1-RESEARCH.md -- unused for small_angle/uniform)."
        ),
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
            "for a single (n, init_scheme) cell and save raw gradients to a .npy chunk "
            "file instead of writing a CSV row. Requires exactly one --n-values and one "
            "--init-schemes value, and --draw-count."
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
            "for a single (n, init_scheme) cell, concatenate, summarize once, and write/"
            "append the final CSV row. Requires exactly one --n-values and one "
            "--init-schemes value."
        ),
    )
    args = parser.parse_args()
    if (args.draw_start is None) != (args.draw_count is None):
        parser.error("--draw-start and --draw-count must be given together")
    if args.draw_start is not None or args.combine_chunks:
        if len(args.n_values) != 1 or len(args.init_schemes) != 1:
            parser.error(
                "--draw-start/--draw-count/--combine-chunks require exactly one "
                "--n-values and one --init-schemes value"
            )
    if args.draw_start is not None and args.combine_chunks:
        parser.error("--draw-start/--draw-count and --combine-chunks are mutually exclusive")
    return args


def _chunk_dir(out_path):
    d = out_path + ".chunks"
    os.makedirs(d, exist_ok=True)
    return d


def _chunk_path(out_path, scope, n, init_scheme, sigma, draw_start, draw_count):
    return os.path.join(
        _chunk_dir(out_path),
        f"{scope}_n{n}_{init_scheme}_sigma{sigma:g}_{draw_start}-{draw_start + draw_count}.npy",
    )


def run_chunk(args):
    """Draw-chunk mode: compute one draw sub-range for one cell, save raw
    gradients to a .npy file. No CSV row is written."""
    n = args.n_values[0]
    init_scheme = args.init_schemes[0]
    start = time.time()
    pooled_grads, n_tracked = pooled_gradients_for_cell(
        n,
        args.scope,
        init_scheme,
        draw_start=args.draw_start,
        draw_count=args.draw_count,
        max_tracked_params=args.max_tracked_params,
        weight2_pair=(0, 1),
        seed_base=170917,
        sigma=args.sigma,
        scale_factor=args.scale_factor,
    )
    elapsed = time.time() - start
    path = _chunk_path(
        args.out, args.scope, n, init_scheme, args.sigma, args.draw_start, args.draw_count
    )
    np.save(path, pooled_grads)
    print(
        f"n={n} init={init_scheme} draws=[{args.draw_start},{args.draw_start + args.draw_count}): "
        f"{len(pooled_grads)} pooled grads, n_tracked_params={n_tracked} ({elapsed:.1f}s) -> {path}",
        flush=True,
    )


def combine_chunks(args, writer, f):
    """Load every .npy chunk for this (scope, n, init_scheme), concatenate,
    summarize once (identical math to a single-process run over the full
    draw range), and write the final CSV row."""
    n = args.n_values[0]
    init_scheme = args.init_schemes[0]
    pattern = os.path.join(
        _chunk_dir(args.out), f"{args.scope}_n{n}_{init_scheme}_sigma{args.sigma:g}_*.npy"
    )
    chunk_files = _validated_chunk_files(pattern)
    arrays = [np.load(p) for p in chunk_files]
    pooled_grads = np.concatenate(arrays)
    # n_tracked_params is constant across chunks of the same cell; derive it from
    # this cell's own tracked-index count rather than re-deriving from array shape.
    _, n_tracked = pooled_gradients_for_cell(
        n, args.scope, init_scheme, draw_start=0, draw_count=0,
        max_tracked_params=args.max_tracked_params, weight2_pair=(0, 1), seed_base=170917,
        sigma=args.sigma, scale_factor=args.scale_factor,
    )
    result = {
        "n": n,
        "generator_scope": args.scope,
        "init_scheme": init_scheme,
        "n_tracked_params": n_tracked,
        **stats.summarize_gradient_samples(pooled_grads),
        "sigma": args.sigma,
        "bin_spacing": target_grid.bin_spacing(n),
    }
    writer.writerow(result)
    f.flush()
    os.fsync(f.fileno())
    print(
        f"n={n} init={init_scheme}: combined {len(chunk_files)} chunks, "
        f"{len(pooled_grads)} total pooled grads, mean={result['mean']:.3e} "
        f"var={result['var']:.3e} -> {args.out}",
        flush=True,
    )
    return [result]


def run(args, writer, f):
    """Run every (init_scheme, n) cell, writing+flushing each row to disk
    immediately after it completes (not buffered until the whole sweep
    finishes) -- a crash mid-sweep (e.g. a MemoryError deep inside a
    perceval call) then loses at most the in-progress cell, not every
    already-completed cell before it.
    """
    rows = []
    for init_scheme in args.init_schemes:
        for n in args.n_values:
            start = time.time()
            cell_results = run_gradient_variance_sweep(
                n_values=[n],
                generator_scope=args.scope,
                init_scheme=init_scheme,
                n_draws=args.n_draws,
                max_tracked_params=args.max_tracked_params,
                weight2_pair=(0, 1),
                seed_base=170917,
                sigma=args.sigma,
                scale_factor=args.scale_factor,
            )
            elapsed = time.time() - start
            result = cell_results[0]
            result["sigma"] = args.sigma
            result["bin_spacing"] = target_grid.bin_spacing(n)
            rows.append(result)
            writer.writerow(result)
            f.flush()
            os.fsync(f.fileno())
            print(
                f"n={n} init={init_scheme}: mean={result['mean']:.3e} "
                f"var={result['var']:.3e} ({elapsed:.1f}s)",
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
