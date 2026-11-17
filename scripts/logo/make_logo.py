"""Build the pyTIARA logo set into pytiara/gui/logo (pyFIB family; see that folder's README.md).

    env\\python.exe scripts\\logo\\make_logo.py

Needs fontTools (pip install fonttools) besides pyTIARA's own PySide6, which renders the PNGs.
"""
import math
import struct
import sys
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[1] / "pytiara" / "gui" / "logo"
NAME = "pyTIARA"

# the family palette (LOGO_STYLE_GUIDE.md of the pyFIB logo kit)
ACC, ACC_LIGHT = "#17c3b2", "#12776f"
TICK, TICK_LIGHT = "#f5b841", "#b07508"
TILE, EDGE = "#161a22", "#3a4150"
TEXT_DARK_BG, TEXT_LIGHT_BG = "#e7ebf2", "#1c212b"


def _n(v):
    return ("%.2f" % v).rstrip("0").rstrip(".")


def svg(body, w, h):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%s" height="%s" viewBox="0 0 %s %s" role="img" '
            'aria-label="%s"><title>%s</title>%s</svg>' % (_n(w), _n(h), _n(w), _n(h), NAME, NAME, body))


# ---- the mark (120 x 120): a tilt series, drawn as a tiara ----------------------- #
FAN = (-50, -25, 0, 25, 50)             # beam angles from the vertical, degrees


def _tip(cx, cy, length, a):
    return cx + length * math.sin(math.radians(a)), cy - length * math.cos(math.radians(a))


def fan(cx, cy, length, sw, angles=FAN, opacity=0.32):
    """Beams converging on (cx, cy), with the angular range they cover filled in."""
    (lx, ly), (rx, ry) = _tip(cx, cy, length, angles[0]), _tip(cx, cy, length, angles[-1])
    b = ['<path d="M%s %s L%s %s A%s %s 0 0 1 %s %s Z" fill="%s" fill-opacity="%s"/>'
         % (_n(cx), _n(cy), _n(lx), _n(ly), _n(length), _n(length), _n(rx), _n(ry), ACC, opacity)]
    d = " ".join("M%s %s L%s %s" % (_n(cx), _n(cy), *map(_n, _tip(cx, cy, length, a))) for a in angles)
    b.append('<path d="%s" stroke="%s" stroke-width="%s" stroke-linecap="round" fill="none"/>' % (d, ACC, _n(sw)))
    return "".join(b)


def mark_body():
    return "".join([
        '<rect x="2" y="2" width="116" height="116" rx="26" fill="%s" stroke="%s" stroke-width="2"/>' % (TILE, EDGE),
        fan(60, 87, 50, 3),
        '<rect x="24" y="84" width="72" height="8" rx="2" fill="%s"/>' % TEXT_DARK_BG,      # the specimen
        '<rect x="56.5" y="25" width="7" height="12" rx="2" fill="%s"/>' % TICK])           # the zero-tilt view


def mark_16():
    """Pixel-fitted: three beams, drawn as whole pixels (the diagonals as steps); no tile edge."""
    px = lambda cells, col, extra="": '<path d="%s" fill="%s"%s/>' % (
        "".join("M%d %dh%dv1h-%dz" % (x, y, w, w) for x, y, w in cells), col, extra)
    return svg("".join([
        '<rect width="16" height="16" rx="3.5" fill="%s"/>' % TILE,
        px([(4, 7, 8), (5, 8, 6), (6, 9, 4)], ACC, ' fill-opacity="0.35"'),              # the covered range
        px([(3, 7, 1), (4, 8, 1), (5, 9, 1), (6, 10, 1), (12, 7, 1), (11, 8, 1), (10, 9, 1), (9, 10, 1)], ACC),
        '<rect x="7" y="5" width="2" height="6" fill="%s"/>' % ACC,
        '<rect x="3" y="11" width="10" height="2" fill="%s"/>' % TEXT_DARK_BG,
        '<rect x="7" y="2" width="2" height="2" fill="%s"/>' % TICK]), 16, 16)


def mark_24():
    """Pixel-fitted: all five beams, the middle one 2 px wide; no tile edge."""
    return svg("".join([
        '<rect width="24" height="24" rx="5" fill="%s"/>' % TILE,
        fan(12, 18, 10.5, 1.1, opacity=0.35),
        '<rect x="11" y="7" width="2" height="11" fill="%s"/>' % ACC,
        '<rect x="4" y="17" width="16" height="3" rx="0.5" fill="%s"/>' % TEXT_DARK_BG,
        '<rect x="11" y="3" width="2" height="3" fill="%s"/>' % TICK]), 24, 24)


# ---- wordmark: "py" from pyFIB, "TIARA" in Archivo ExtraBold ---------------------- #
SCALE, BASE, ORIGIN, CAP_TOP = 0.12, 200.0, 88.0, 117.56
PY_BOTTOM = 212.6                       # descender of "py"


def glyph(font, ch, ox):
    gs = font.getGlyphSet()
    g = font.getBestCmap()[ord(ch)]
    pen = SVGPathPen(gs)
    gs[g].draw(TransformPen(pen, (SCALE, 0, 0, -SCALE, ox, BASE)))
    bp = BoundsPen(gs)
    gs[g].draw(bp)
    return pen.getCommands(), gs[g].width * SCALE, bp.bounds


def wordmark(on_light, pad=6.0):
    """The "I" is the mark's zero-tilt beam: a teal bar with the amber tick as its top.
    Returns (svg body, left, top, right, bottom) of the ink box in wordmark coordinates."""
    font = TTFont(HERE / "archivo-latin-800-normal.woff")
    py = (HERE / "py_outline.txt").read_text().strip()
    acc, text = (ACC_LIGHT, TEXT_LIGHT_BG) if on_light else (ACC, TEXT_DARK_BG)
    tick = TICK_LIGHT if on_light else TICK
    parts, letters, x = ['<path fill="%s" d="%s"/>' % (acc, py)], [], ORIGIN
    for ch in "TIARA":
        if ch == "I":
            x += pad - 4.0                              # the T's arm already leaves room on that side
            _, adv, b = glyph(font, ch, x)
            x0, w = x + b[0] * SCALE, (b[2] - b[0]) * SCALE
            sw, tick_h, gap = 2.47, 11.0, 3.5           # 2.47: pyFIB's I-pattern stroke (3 x 0.8232)
            top = CAP_TOP + tick_h + gap
            parts.append('<rect x="%s" y="%s" width="%s" height="%s" rx="2" fill="%s"/>'
                         % (_n(x0), _n(CAP_TOP), _n(w), _n(tick_h), tick))
            parts.append('<rect x="%s" y="%s" width="%s" height="%s" rx="2.5" fill="%s" fill-opacity="%s" '
                         'stroke="%s" stroke-width="%s"/>'
                         % (_n(x0 + sw / 2), _n(top + sw / 2), _n(w - sw), _n(BASE - top - sw), acc,
                            0.28 if on_light else 0.32, acc, _n(sw)))
            x += adv + pad - 3.0                        # as does the A's slope
            continue
        d, adv, b = glyph(font, ch, x)
        letters.append(d)
        right = x + b[2] * SCALE
        x += adv
    parts.append('<path fill="%s" d="%s"/>' % (text, " ".join(letters)))
    return "".join(parts), 5.88, CAP_TOP, right, PY_BOTTOM


def write(name, text):
    (OUT / name).write_text(text, encoding="utf-8", newline="\n")


def build_svgs():
    write("pytiara_mark.svg", svg(mark_body(), 120, 120))
    write("pytiara_mark_16.svg", mark_16())
    write("pytiara_mark_24.svg", mark_24())
    for tone in ("dark", "light"):
        body, x0, y0, x1, y1 = wordmark(tone == "light")
        write("pytiara_wordmark_on_%s.svg" % tone,
              svg('<g transform="translate(%s %s)">%s</g>' % (_n(-x0), _n(-y0), body), x1 - x0, y1 - y0))
        # lockup as pyFIB's: mark at 1.715x, wordmark 250.96 to the right, capitals centred on the mark
        k, dx = 1.715, 250.96
        mh = 120 * k
        dy = mh / 2 - (CAP_TOP + BASE) / 2
        top, bot = min(0.0, y0 + dy), max(mh, y1 + dy)
        inner = ('<g transform="scale(%s)">%s</g><g transform="translate(%s %s)">%s</g>'
                 % (_n(k), mark_body(), _n(dx), _n(dy), body))
        write("pytiara_logo_on_%s.svg" % tone,
              svg('<g transform="translate(0 %s)">%s</g>' % (_n(-top), inner), dx + x1, bot - top))


# ---- PNGs (Qt's SVG renderer) and the .ico ---------------------------------------- #
def render(svg_name, png_name, w=None, h=None):
    from PySide6.QtCore import QRectF, Qt
    from PySide6.QtGui import QImage, QPainter
    from PySide6.QtSvg import QSvgRenderer
    r = QSvgRenderer(str(OUT / svg_name))
    size = r.defaultSize()
    if w is None:
        w = round(h * size.width() / size.height())
    if h is None:
        h = round(w * size.height() / size.width())
    img = QImage(w, h, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
    r.render(p, QRectF(0, 0, w, h))
    p.end()
    img.save(str(OUT / png_name))


def write_ico(sizes):
    """PNG entries written by hand, so the pixel-fitted 16 and 24 px images are kept as drawn."""
    pngs = [(OUT / ("pytiara_mark_%d.png" % s)).read_bytes() for s in sizes]
    dirs, data, off = b"", b"", 6 + 16 * len(pngs)
    for s, png in zip(sizes, pngs):
        dirs += struct.pack("<BBBBHHII", s % 256, s % 256, 0, 0, 1, 32, len(png), off + len(data))
        data += png
    (OUT / "pytiara.ico").write_bytes(struct.pack("<HHH", 0, 1, len(pngs)) + dirs + data)


if __name__ == "__main__":
    from PySide6.QtGui import QGuiApplication
    app = QGuiApplication(sys.argv)
    OUT.mkdir(parents=True, exist_ok=True)
    build_svgs()
    render("pytiara_mark_16.svg", "pytiara_mark_16.png", 16, 16)
    render("pytiara_mark_24.svg", "pytiara_mark_24.png", 24, 24)
    for s in (32, 48, 64, 128, 256, 512, 1024):
        render("pytiara_mark.svg", "pytiara_mark_%d.png" % s, s, s)
    for tone in ("dark", "light"):
        render("pytiara_logo_on_%s.svg" % tone, "pytiara_logo_on_%s.png" % tone, h=600)
        render("pytiara_wordmark_on_%s.svg" % tone, "pytiara_wordmark_on_%s.png" % tone, h=300)
    write_ico((16, 24, 32, 48, 64, 128, 256))
    print("\n".join(sorted(p.name for p in OUT.iterdir())))
