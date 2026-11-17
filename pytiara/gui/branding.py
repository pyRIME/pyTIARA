"""pyTIARA's logo in the interface (the files are in ``logo/``; see its README.md).

A missing file means plain text and no icon, never a failure to open."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QGuiApplication, QIcon, QPalette, QPixmap
from PySide6.QtWidgets import QLabel

from .. import __version__

LOGO_DIR = Path(__file__).with_name("logo")
NAME = "pyTIARA"
ICON_SIZES = (16, 24, 32, 48, 64, 128, 256)


def app_icon() -> QIcon:
    icon = QIcon()
    for s in ICON_SIZES:
        f = LOGO_DIR / f"pytiara_mark_{s}.png"
        if f.exists():
            icon.addFile(str(f), QSize(s, s))
    return icon


def lockup(height: int, dpr: float = 1.0, on_light: bool | None = None) -> QPixmap | None:
    """Mark + wordmark, ``height`` logical pixels high; the light or dark version follows the palette."""
    if on_light is None:
        on_light = QGuiApplication.palette().color(QPalette.Window).lightness() > 128
    f = LOGO_DIR / f"pytiara_logo_on_{'light' if on_light else 'dark'}.png"
    pm = QPixmap(str(f)) if f.exists() else QPixmap()
    if pm.isNull():
        return None
    pm = pm.scaledToHeight(max(1, round(height * dpr)), Qt.SmoothTransformation)
    pm.setDevicePixelRatio(dpr)
    return pm


def brand_label(height: int = 46) -> QLabel:
    label = QLabel()
    screen = QGuiApplication.primaryScreen()
    pm = lockup(height, screen.devicePixelRatio() if screen else 1.0)
    if pm is not None:
        label.setPixmap(pm)
    else:
        label.setText(NAME)
        label.setStyleSheet("font-size: 28px; font-weight: 800;")
    label.setToolTip(f"{NAME} {__version__}")
    return label


def set_windows_app_id() -> None:
    """Taskbar identity, so Windows shows pyTIARA's icon instead of Python's."""
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("pyRIME.pyTIARA")
        except Exception:
            pass
