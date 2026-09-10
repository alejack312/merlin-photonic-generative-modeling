"""Generate the read-only v4 sibling inventory and source manifests."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from merlin_iqp.experiments.sibling_import import (  # noqa: E402
    PINNED_SIBLING_COMMIT,
    build_sibling_inventory,
    write_inventory_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sibling-root", type=Path, default=Path(r"C:\Users\cuqui\iqp-mmd-barren-plateau"))
    parser.add_argument("--output-root", type=Path, default=REPO_ROOT / "results" / "v4_tcdp")
    parser.add_argument("--pinned-commit", default=PINNED_SIBLING_COMMIT)
    args = parser.parse_args()
    inventory = build_sibling_inventory(args.sibling_root, pinned_commit=args.pinned_commit)
    paths = write_inventory_outputs(inventory, args.output_root)
    print(json.dumps({"summary": inventory["summary"], "outputs": {key: str(value) for key, value in paths.items()}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
