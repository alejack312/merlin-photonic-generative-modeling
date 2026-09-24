"""Root pytest config.

Perceval writes logs under its persistent-data directory at import time
(default: %LOCALAPPDATA%\quandela\perceval-quandela on Windows). Sandboxed
runners can't write there, which aborts collection. Point it at a repo-local,
git-ignored directory unless the caller already chose one.
"""
import os
from pathlib import Path

_PCVL_DIR = Path(__file__).parent / ".pcvl-data"
_PCVL_DIR.mkdir(exist_ok=True)
os.environ.setdefault("PCVL_PERSISTENT_PATH", str(_PCVL_DIR))
