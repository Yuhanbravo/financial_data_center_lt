from __future__ import annotations

import sys
from pathlib import Path

from _pytest.tmpdir import TempPathFactory

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _safe_getbasetemp(self: TempPathFactory) -> Path:
    if self._basetemp is None:
        basetemp = ROOT / "data" / "pytest-tmp-safe"
        basetemp.mkdir(parents=True, exist_ok=True)
        self._basetemp = basetemp.resolve()
    return self._basetemp


def _safe_mktemp(self: TempPathFactory, basename: str, numbered: bool = True) -> Path:
    basename = self._ensure_relative_to_basetemp(basename)
    basetemp = self.getbasetemp()

    if not numbered:
        path = basetemp / basename
        path.mkdir()
        return path

    for index in range(1000):
        path = basetemp / f"{basename}{index}"
        try:
            path.mkdir()
        except FileExistsError:
            continue
        return path
    raise FileExistsError(f"Unable to create pytest temp directory for {basename!r}")


TempPathFactory.getbasetemp = _safe_getbasetemp
TempPathFactory.mktemp = _safe_mktemp
