from __future__ import annotations

import pytest

from merlin_iqp import _atomic


def test_rename_retries_permission_error_until_it_clears(monkeypatch) -> None:
    calls = 0
    sleeps: list[float] = []

    def rename(_source, _destination) -> None:
        nonlocal calls
        calls += 1
        if calls < 3:
            raise PermissionError(5, "access denied")

    monkeypatch.setattr(_atomic.os, "rename", rename)
    monkeypatch.setattr(_atomic.time, "sleep", sleeps.append)

    _atomic.rename_no_overwrite("source", "destination")

    assert calls == 3
    assert sleeps == [0.02, 0.04]


def test_rename_reraises_persistent_permission_error_after_five_attempts(monkeypatch) -> None:
    calls = 0

    def rename(_source, _destination) -> None:
        nonlocal calls
        calls += 1
        raise PermissionError(5, "access denied")

    monkeypatch.setattr(_atomic.os, "rename", rename)
    monkeypatch.setattr(_atomic.time, "sleep", lambda _delay: None)

    with pytest.raises(PermissionError):
        _atomic.rename_no_overwrite("source", "destination")

    assert calls == 5


def test_rename_does_not_retry_file_exists_and_preserves_destination(
    monkeypatch, tmp_path
) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.write_text("new", encoding="utf-8")
    destination.write_text("original", encoding="utf-8")
    calls = 0

    def rename(_source, _destination) -> None:
        nonlocal calls
        calls += 1
        raise FileExistsError(183, "already exists")

    monkeypatch.setattr(_atomic.os, "rename", rename)
    monkeypatch.setattr(_atomic.time, "sleep", lambda _delay: None)

    with pytest.raises(FileExistsError):
        _atomic.rename_no_overwrite(source, destination)

    assert calls == 1
    assert source.read_text(encoding="utf-8") == "new"
    assert destination.read_text(encoding="utf-8") == "original"
