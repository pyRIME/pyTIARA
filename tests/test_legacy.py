"""Output written before the rename (pyPrep) must stay readable, and move to the new names when written."""

import json

from pytiara import legacy, positioning as P, thumbs
from pytiara.io.mdoc import parse_mdoc
from pytiara.pipeline import _close_logger, _series_logger, result_json_path
from pytiara.tiltseries import load_tilt_series

from test_core import TOMO5_MDOC
from test_positioning import TILT_COM


def _pyprep_series(tmp_path):
    """A series folder as pyPrep left it."""
    d = tmp_path / "out" / "TS_1"
    recon = d / "imod_bin4"
    recon.mkdir(parents=True)
    (d / "TS_1_pyprep.json").write_text(json.dumps({"series": "TS_1", "status": "complete", "tilts": []}))
    (d / "TS_1_pyprep.log").write_text("12:00:00  old line\n")
    (recon / "pyprep_recon.json").write_text(json.dumps({"status": "complete"}))
    repositioned = TILT_COM.replace("THICKNESS	152", "THICKNESS	123")
    assert repositioned != TILT_COM
    (recon / "tilt.com").write_text(repositioned)
    (recon / "tilt.com.pyprep_orig").write_text(TILT_COM)
    return d, recon


def test_old_names():
    assert legacy.old_path("x/TS_1_pytiara.json").name == "TS_1_pyprep.json"
    assert legacy.old_path("x/tilt.com.pytiara_orig").name == "tilt.com.pyprep_orig"
    assert legacy.old_path("x/pytiara_run_pytiara.log").name == "pytiara_run_pyprep.log"   # series name untouched
    assert legacy.old_path("x/TS_1_bin4.mrc").name == "TS_1_bin4.mrc"


def test_pyprep_folder_is_read_without_changing_it(tmp_path):
    d, recon = _pyprep_series(tmp_path)
    before = sorted(p.name for p in d.rglob("*") if p.is_file())
    (tmp_path / "TS_1.mdoc").write_text(TOMO5_MDOC)
    series = load_tilt_series(tmp_path / "TS_1.mdoc")
    assert result_json_path(series, d).name == "TS_1_pyprep.json"
    assert thumbs._record(d)["status"] == "complete"
    assert legacy.recon_record(recon).name == "pyprep_recon.json"
    assert [p.name for p in legacy.glob(d, "imod_bin*/pytiara_recon.json")] == ["pyprep_recon.json"]
    assert legacy.existing(recon / "tilt.com.pytiara_orig").read_text() == TILT_COM
    assert sorted(p.name for p in d.rglob("*") if p.is_file()) == before


def test_pyprep_folder_is_renamed_when_written(tmp_path):
    d, recon = _pyprep_series(tmp_path)
    log = _series_logger(d / "TS_1_pytiara.log", None, mode="a")     # what every pipeline step does first
    log.info("new line")
    _close_logger(log)
    names = sorted(p.name for p in d.rglob("*") if p.is_file())
    assert names == ["TS_1_pytiara.json", "TS_1_pytiara.log", "pytiara_recon.json", "tilt.com", "tilt.com.pytiara_orig"]
    text = (d / "TS_1_pytiara.log").read_text()
    assert "old line" in text and "new line" in text                # the log carries on
    assert thumbs._record(d)["status"] == "complete"


def test_new_file_wins_over_old(tmp_path):
    (tmp_path / "pyprep_selection.json").write_text(json.dumps({"keep": ["old"]}))
    assert thumbs.load_selection(tmp_path) == {"old"}
    thumbs.save_selection(tmp_path, {"new"})
    assert [p.name for p in tmp_path.iterdir()] == ["pytiara_selection.json"]
    assert thumbs.load_selection(tmp_path) == {"new"}


def test_positioning_keeps_the_pyprep_backup(tmp_path, monkeypatch):
    # a second backup made from the already-repositioned tilt.com would lose the original geometry
    _, recon = _pyprep_series(tmp_path)
    monkeypatch.setattr(P, "run_tilt", lambda d, tc, log=None, cancel=None: None)
    monkeypatch.setattr(P, "run_trimvol", lambda d, log=None: None)
    P.apply_positioning(recon, "TS_1", P.Correction(1.0, 0.0, 0.0, 100), margin_px=0, log=lambda s: None)
    assert not (recon / "tilt.com.pyprep_orig").exists()
    assert (recon / "tilt.com.pytiara_orig").read_text() == TILT_COM
    P.restore_original(recon, log=lambda s: None)
    assert (recon / "tilt.com").read_text() == TILT_COM


def test_pyprep_stacks_are_not_taken_for_raw_data():
    # find_mdocs skips the program's own output mdocs; stacks written by pyPrep carry its old name
    for tag in ("pyPrep 0.1.0", "pyTIARA 0.1.0"):
        doc = parse_mdoc(f"PixelSpacing = 1.6\n[T = {tag} 30-Sep-26 18:11: motion-corrected from TS_1.mdoc]\n"
                         "[ZValue = 0]\nTiltAngle = 0\n")
        assert doc.is_pytiara
    assert not parse_mdoc(TOMO5_MDOC).is_pytiara
