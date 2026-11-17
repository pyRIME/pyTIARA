# pyTIARA logo

Made 2026-11-16 as the third logo of the pyFIB family (pyFIB, pyMap, pyTIARA), following
the family's `LOGO_STYLE_GUIDE.md`. Evan chose this direction from three options.

**The mark** is a tilt series, drawn so that it is also a tiara. The light bar is the
specimen (the lamella of pyFIB's and pyMap's marks). The teal beams are the views of the
tilt series converging on it, and the translucent teal sector is the angular range they
cover. The amber tick marks the zero-tilt view. It is the idea of pyPrep's icon (a fan of
beams through a specimen slab), redrawn with the family's parts.

**In the wordmark**, the "I" is the zero-tilt beam: a teal bar with the amber tick as its
top. pyFIB draws its "I" as the mill pattern in the same way.

## Files

| File | Use |
|---|---|
| `pytiara_mark.svg` | The mark (app icon), vector master, 120 × 120 |
| `pytiara_mark_16.svg`, `pytiara_mark_24.svg` | Pixel-fitted versions for 16 and 24 px |
| `pytiara_mark_<n>.png` | The mark at 16, 24, 32, 48, 64, 128, 256, 512 and 1024 px |
| `pytiara.ico` | Windows icon (16, 24, 32, 48, 64, 128, 256; PNG entries, as `pyfib.ico`) |
| `pytiara_logo_on_dark.svg/.png` | Mark + wordmark, for dark backgrounds |
| `pytiara_logo_on_light.svg/.png` | Mark + wordmark, for light backgrounds (slides, papers) |
| `pytiara_wordmark_on_dark.svg/.png`, `pytiara_wordmark_on_light.svg/.png` | Wordmark alone |

The PNGs have transparent backgrounds. The mark keeps its dark tile on any background.
The lockup follows pyFIB's exactly: the mark at 1.715×, the wordmark at the same offset,
and the capitals centred on the mark.

The 16 px mark keeps three of the five beams and draws the diagonal ones as pixel steps.
The 24 px mark keeps all five. Neither has the tile's edge stroke.

## Colours

pyFIB's palette, with nothing added.

| Role | Hex |
|---|---|
| Accent: beams, "py" and the "I" on dark | `#17c3b2` |
| Accent on light backgrounds | `#12776f` |
| Tick | `#f5b841` |
| Tick on light backgrounds | `#b07508` |
| Tile / tile edge | `#161a22` / `#3a4150` |
| Specimen bar and "TIARA" on dark | `#e7ebf2` |
| "TIARA" on light | `#1c212b` |

## Type

Same as pyFIB and pyMap: "py" is JetBrains Mono Medium (500), reused from pyFIB's own
outlines (`scripts/logo/py_outline.txt`). "T", "A" and "R" are Archivo ExtraBold (800), at
the same scale and baseline as pyFIB's "F" and "B". Both fonts are SIL Open Font License
1.1 (`scripts/logo/Archivo_LICENSE_OFL.txt`). The letters are outlines, so no font needs
to be installed.

## In the program

`pytiara/gui/branding.py` loads these files: `app_icon()` for the window and taskbar,
`lockup()` for the splash screen and `brand_label()` for the top of the navigation bar.
If a file is missing the program shows plain text instead.

## Rebuilding

`scripts/logo/make_logo.py` writes every file here:

    env\python.exe -m pip install fonttools
    env\python.exe scripts\logo\make_logo.py

It renders the PNGs with Qt (PySide6), so it needs no other tool. Qt's renderer differs
slightly from `rsvg-convert`, which built pyFIB's and pyMap's PNGs.

Keep clear space around the logo of at least the tick's height. Don't recolour the mark's
parts separately, stretch it, or put the lockup on a busy image.
