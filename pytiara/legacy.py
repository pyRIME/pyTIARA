"""Names from before the rename: pyTIARA was called pyPrep until November 2026.

Output written by pyPrep carries ``pyprep`` where pyTIARA writes ``pytiara``
(``TS_1_pyprep.json``, ``imod_bin4/pyprep_recon.json``, ``tilt.com.pyprep_orig`` ...).
Readers accept both names; a folder's old files are renamed the next time pyTIARA
writes to them, so one folder never holds both versions of a file.
"""

from __future__ import annotations

import shutil
from pathlib import Path

NAME, OLD_NAME = "pytiara", "pyprep"
OLD_APP_NAME = "pyPrep"                 # mdoc/MRC titles, settings and data folders


def old_path(path) -> Path:
    """The name ``path`` had under pyPrep (``path`` itself if its name has no ``pytiara``)."""
    path = Path(path)
    head, sep, tail = path.name.rpartition(NAME)      # the last one: a series name comes first
    return path.with_name(head + OLD_NAME + tail) if sep else path


def existing(path) -> Path:
    """For reading: ``path``, or its pyPrep-era file when only that one exists."""
    path = Path(path)
    if not path.exists():
        old = old_path(path)
        if old != path and old.exists():
            return old
    return path


def adopt(path) -> Path:
    """For writing: rename the pyPrep-era file to ``path`` first, so its content carries over."""
    path = Path(path)
    old = old_path(path)
    if old != path and old.exists():
        try:
            if path.exists():
                old.unlink()
            else:
                old.rename(path)
        except OSError:
            pass                        # locked or read-only: the new file is simply written beside it
    return path


def remove(path) -> None:
    """Delete ``path`` and its pyPrep-era file."""
    for p in {Path(path), old_path(path)}:
        p.unlink(missing_ok=True)


def glob(folder, pattern: str) -> list[Path]:
    """``folder.glob(pattern)`` plus pyPrep-era matches, each as its current-name path's ``existing``."""
    folder = Path(folder)
    found = {p: p for p in folder.glob(pattern)}
    old_pattern = str(old_path(Path(pattern)))
    if old_pattern != pattern:
        for p in folder.glob(old_pattern):
            head, _, tail = p.name.rpartition(OLD_NAME)
            found.setdefault(p.with_name(head + NAME + tail), p)
    return [found[k] for k in sorted(found)]


def migrate_folder(new: Path, old: Path) -> None:
    """Copy a per-user data folder (presets) from its pyPrep location the first time it is needed."""
    if not new.exists() and old.is_dir():
        try:
            shutil.copytree(old, new)
        except OSError:
            pass


RECON_RECORD = "pytiara_recon.json"
# pyPrep-era files of one series folder (the series record and log, and what lives in imod_bin<N>/)
_SERIES_FILES = ("*_pyprep.json", "*_pyprep.log", "imod_bin*/pyprep_recon.json",
                 "imod_bin*/pyprep_batchruntomo.adoc", "imod_bin*/tilt.com.pyprep_orig", "imod_bin*/pyprep_pos_*.mrc")


def recon_record(recon_dir) -> Path:
    """The reconstruction record of ``imod_bin<N>/``, under whichever name it exists."""
    return existing(Path(recon_dir) / RECON_RECORD)


def adopt_series_folder(series_dir) -> None:
    """Rename every pyPrep-era file of a series folder; called before pyTIARA writes there."""
    for pattern in _SERIES_FILES:
        for old in Path(series_dir).glob(pattern):
            head, _, tail = old.name.rpartition(OLD_NAME)
            adopt(old.with_name(head + NAME + tail))
