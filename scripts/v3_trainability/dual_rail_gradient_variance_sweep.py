"""Native-autograd gradient-variance sweep CLI -- v3.0 Phase 17 analogue of
gradient_variance_sweep.py, using trainability/dual_rail_autograd_sweep.py
(MerLin native autograd on the dual-rail encoding) instead of
trainability/sweep.py (hand-rolled parameter-shift on the polarization
encoding). Same CSV shape (n, generator_scope, init_scheme, n_tracked_params,
n_samples, mean, var, std, median, abs_mean, rms), directly comparable/
pluggable into the same downstream analysis (trainability/curve_fit.py,
trainability_analysis.py). n_tracked_params == n always here (no cap; see
dual_rail_autograd_sweep.py's module docstring for why).

Usage:
    python dual_rail_gradient_variance_sweep.py --scope weight1 \\
        --n-values 2 3 4 5 --init-schemes small_angle uniform \\
        --out results/v3_trainability/phase17_dual_rail_weight1_gradient_variance.csv

Same --draw-start/--draw-count/--combine-chunks chunking support as
gradient_variance_sweep.py, for consistency, though native autograd's much
lower per-draw cost (1 pass vs 2*n Perceval evals) makes chunking less
likely to be needed in practice.
"""

import argparse
import csv
import glob
import json
import os
import re
import time

import numpy as np

from merlin_iqp.trainability import stats
from merlin_iqp.trainability.dual_rail_autograd_sweep import pooled_native_gradients_for_cell

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
]


def _validated_chunk_files(pattern, expected_draws=None, expected_config=None):
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
            raise ValueError(f"overlapping draw chunks: {previous_path} and {path}")
        if start != previous_end:
            raise ValueError(f"gap between draw chunks: {previous_path} and {path}")
    if expected_draws is not None and (
        intervals[0][0] != 0 or intervals[-1][1] != expected_draws
    ):
        raise ValueError(
            f"chunk coverage is [{intervals[0][0]},{intervals[-1][1]}), "
            f"expected [0,{expected_draws})"
        )
    if expected_config is not None:
        for start, end, path in intervals:
            manifest_path = f"{path}.json"
            if not os.path.exists(manifest_path):
                raise ValueError(f"missing chunk manifest: {manifest_path}")
            with open(manifest_path, encoding="utf-8") as manifest_file:
                manifest = json.load(manifest_file)
            if manifest.get("draw_start") != start or manifest.get("draw_count") != end - start:
                raise ValueError(
                    f"chunk manifest draw interval mismatch for {path}: "
                    f"draw_start={manifest.get('draw_start')!r}, "
                    f"draw_count={manifest.get('draw_count')!r}, "
                    f"expected draw_start={start}, draw_count={end - start}"
                )
            for key, expected in expected_config.items():
                if manifest.get(key) != expected:
                    raise ValueError(
                        f"chunk configuration mismatch for {path}: {key}={manifest.get(key)!r}, "
                        f"expected {expected!r}"
                    )
    return [path for _, _, path in intervals]


def _load_validated_chunk_arrays(chunk_files, n_tracked_params):
    """Load pooled gradient chunks and require tracked gradients per draw."""
    arrays = []
    for path in chunk_files:
        match = re.search(r"_(\d+)-(\d+)\.npy$", path)
        if match is None:
            raise ValueError(f"chunk filename has no draw interval: {path}")
        start, end = map(int, match.groups())
        array = np.load(path)
        expected_rows = (end - start) * n_tracked_params
        if array.ndim == 0 or array.shape[0] != expected_rows:
            actual_rows = array.shape[0] if array.ndim else "scalar"
            raise ValueError(
                f"chunk array row count mismatch for {path}: "
                f"got {actual_rows!r}, expected {expected_rows} "
                f"({end - start} draws x {n_tracked_params} tracked params)"
            )
        arrays.append(array)
    return arrays


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the dual-rail/MerLin native-autograd gradient-variance-vs-n sweep."
    )
    parser.add_argument("--scope", required=True, choices=["weight1", "mixed"])
    parser.add_argument("--n-values", required=True, type=int, nargs="+")
    parser.add_argument(
        "--init-schemes", required=True, nargs="+", choices=["small_angle", "uniform"]
    )
    parser.add_argument("--out", required=True)
    parser.add_argument("--n-draws", type=int, default=100)
    parser.add_argument("--append", action="store_true")
    parser.add_argument("--draw-start", type=int, default=None)
    parser.add_argument("--draw-count", type=int, default=None)
    parser.add_argument("--combine-chunks", action="store_true")
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


def _chunk_path(out_path, scope, n, init_scheme, draw_start, draw_count):
    return os.path.join(
        _chunk_dir(out_path),
        f"{scope}_n{n}_{init_scheme}_{draw_start}-{draw_start + draw_count}.npy",
    )


def run_chunk(args):
    n = args.n_values[0]
    init_scheme = args.init_schemes[0]
    start = time.time()
    pooled_grads, n_tracked = pooled_native_gradients_for_cell(
        n, args.scope, init_scheme, draw_start=args.draw_start, draw_count=args.draw_count
    )
    elapsed = time.time() - start
    path = _chunk_path(args.out, args.scope, n, init_scheme, args.draw_start, args.draw_count)
    np.save(path, pooled_grads)
    with open(f"{path}.json", "w", encoding="utf-8") as manifest_file:
        json.dump({
            "scope": args.scope, "n": n, "init_scheme": init_scheme,
            "n_draws": args.n_draws, "draw_start": args.draw_start,
            "draw_count": args.draw_count,
        }, manifest_file, sort_keys=True)
    print(
        f"n={n} init={init_scheme} draws=[{args.draw_start},{args.draw_start + args.draw_count}): "
        f"{len(pooled_grads)} pooled grads, n_tracked_params={n_tracked} ({elapsed:.1f}s) -> {path}",
        flush=True,
    )


def combine_chunks(args, writer, f):
    n = args.n_values[0]
    init_scheme = args.init_schemes[0]
    pattern = os.path.join(_chunk_dir(args.out), f"{args.scope}_n{n}_{init_scheme}_*.npy")
    chunk_files = _validated_chunk_files(
        pattern,
        expected_draws=args.n_draws,
        expected_config={
            "scope": args.scope, "n": n, "init_scheme": init_scheme,
            "n_draws": args.n_draws,
        },
    )
    pooled_grads = np.concatenate(
        _load_validated_chunk_arrays(chunk_files, n_tracked_params=n)
    )
    result = {
        "n": n,
        "generator_scope": args.scope,
        "init_scheme": init_scheme,
        "n_tracked_params": n,
        **stats.summarize_gradient_samples(pooled_grads),
    }
    writer.writerow(result)
    f.flush()
    os.fsync(f.fileno())
    print(f"n={n} init={init_scheme}: combined {len(chunk_files)} chunks -> {args.out}", flush=True)
    return [result]


def run(args, writer, f):
    rows = []
    for init_scheme in args.init_schemes:
        for n in args.n_values:
            start = time.time()
            pooled_grads, n_tracked = pooled_native_gradients_for_cell(
                n, args.scope, init_scheme, draw_start=0, draw_count=args.n_draws
            )
            elapsed = time.time() - start
            result = {
                "n": n,
                "generator_scope": args.scope,
                "init_scheme": init_scheme,
                "n_tracked_params": n_tracked,
                **stats.summarize_gradient_samples(pooled_grads),
            }
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
