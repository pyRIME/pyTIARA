"""Remake the screenshots in docs/images from a synthetic demo session.

    env\\python.exe scripts\\make_screenshots.py [WORK_DIR]

Builds two small synthetic tilt series (Lamella_01, Lamella_02) in WORK_DIR (default:
output_e2e\\demo_session, which git ignores), runs frame alignment on the first, then
captures the pages of the app. The app's saved settings are not read or changed.
"""

import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from synthetic import make_movie  # noqa: E402

from pytiara import pipeline  # noqa: E402
from pytiara.io import mrc  # noqa: E402
from pytiara.settings import ProcessingSettings  # noqa: E402
from pytiara.tiltseries import load_tilt_series  # noqa: E402

IMAGES = ROOT / "docs" / "images"
SHOWN_SESSION = r"D:\Sessions\demo_session"          # what the path boxes show in the pictures
ANGLES = [0, 3, -3, -6, 6, 9, -9, -12, 12, 15, -15]  # dose-symmetric, in acquisition order
NY, NX, FRAMES, DOSE = 768, 1152, 4, 3.0


def fraction_name(series: str, i: int, angle: float) -> str:
    return f"{series}_{i + 1:03d}_{angle:.2f}_20260930_120000_fractions.mrc"


def build_series(folder: Path, name: str, seed: int, missing: int | None = None) -> Path:
    """Tomo5-style mdoc + fraction files; ``missing`` is an acquisition index whose file is left out."""
    rng = np.random.default_rng(seed)
    lines = ["DataMode = 6", f"ImageSize = {NX} {NY}", f"ImageFile = {name}.mrc", "PixelSpacing = 3.30",
             "Voltage = 300.00", "", "[T = Tomography: DEMO    30-Sep-2026  12:00:00]", "",
             "[T =   TiltAxisAngle = -176.20  Binning = 1  SpotSize = 6]", ""]
    for i, angle in enumerate(ANGLES):
        file = fraction_name(name, i, angle)
        lines += [f"[ZValue = {i}]", f"TiltAngle = {angle:.2f}", f"ExposureDose = {DOSE:.2f}", "RotationAngle = 86.20",
                  f"PriorRecordDose = {DOSE * i:.2f}", rf"SubFramePath = \\server\DoseFractions\demo\{file}",
                  f"NumSubFrames = {FRAMES}", f"FrameDosesAndNumber = {DOSE / FRAMES:.2f} {FRAMES}", ""]
        if i == missing or (folder / file).exists():
            continue
        drift = np.cumsum(rng.normal(0, 2.5, (FRAMES, 2)), axis=0)
        frames, _ = make_movie(NY, NX, FRAMES, shifts=drift, seed=seed * 100 + i)
        mrc.write_mrc(folder / file, frames, pixel_size=3.3)
    mdoc = folder / f"{name}.mdoc"
    mdoc.write_text("\n".join(lines) + "\n")
    return mdoc


def main() -> int:
    work = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "output_e2e" / "demo_session"
    work.mkdir(parents=True, exist_ok=True)
    out_root = work / "pyTIARA"
    first = build_series(work, "Lamella_01", 1)
    build_series(work, "Lamella_02", 2, missing=len(ANGLES) - 1)
    settings = ProcessingSettings()
    series = load_tilt_series(first)
    if not pipeline.is_complete(series, settings, out_root):
        pipeline.process_series(series, settings, out_root, log_callback=print)

    from PySide6.QtCore import QSettings, Qt
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    from pytiara.gui import app as gui_app, launcher, theme
    # the user's saved session, settings and window layout stay out of this (and are not overwritten)
    gui_app.QSettings = lambda org, name: QSettings(str(work / f"{org}_settings.ini"), QSettings.IniFormat)
    for f in work.glob("*_settings.ini"):
        f.unlink()
    launcher.set_app_identity(app)
    theme.apply_theme(app)
    w = gui_app.MainWindow()
    w.setAttribute(Qt.WA_DontShowOnScreen, True)
    w.resize(1500, 940)
    w.show()

    def settle(seconds=0.4, until=None):
        end = time.time() + seconds
        while time.time() < end or (until is not None and not until() and time.time() < end + 60):
            app.processEvents()
            time.sleep(0.01)

    def shoot(name):
        w.top.session.edit.setText(SHOWN_SESSION)
        w.top.output.edit.setText(SHOWN_SESSION + r"\pyTIARA")
        settle()
        w.grab().save(str(IMAGES / f"{name}.png"))
        print("wrote", IMAGES / f"{name}.png")

    w.top.session.edit.setText(str(work))
    w.top.output.edit.setText(str(out_root))
    w.scan()
    w.table.selectRow(1)                                 # Lamella_02: one fraction file is missing
    shoot("tilt_series")
    for key, name in (("alignment", "frame_alignment"), ("outputs", "outputs"), ("recon", "reconstruction")):
        w.show_page(key)
        shoot(name)
    w.table.selectRow(0)
    w.show_page("results")
    w.results.load_series(out_root / "Lamella_01", prefer="stack")
    settle(1.0, until=lambda: not w.results.loading.isVisible())
    shoot("results")
    return 0


if __name__ == "__main__":
    sys.exit(main())
