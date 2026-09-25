"""Small filesystem primitives shared by artifact writers."""

from __future__ import annotations

import os
import time
from pathlib import Path

_RENAME_RETRY_DELAYS_SECONDS = (0.02, 0.04, 0.08, 0.16)


def rename_no_overwrite(source: str | Path, destination: str | Path) -> None:
    """Rename without replacing an existing destination.

    Windows can transiently deny a rename while a just-written artifact is
    released by another process. Retry only that transient permission error;
    preserve immediate ``FileExistsError`` behavior for collision detection.
    """

    for attempt in range(len(_RENAME_RETRY_DELAYS_SECONDS) + 1):
        try:
            os.rename(source, destination)
            return
        except FileExistsError:
            raise
        except PermissionError:
            if attempt == len(_RENAME_RETRY_DELAYS_SECONDS):
                raise
            time.sleep(_RENAME_RETRY_DELAYS_SECONDS[attempt])


__all__ = ["rename_no_overwrite"]
