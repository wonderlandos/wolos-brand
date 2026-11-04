# SPDX-License-Identifier: GPL-2.0-or-later
"""Generator of the UI symbolic set (docs/adr/brand-ui.md section 1).

  python3 -I design/tools/ui/symbolic.py [--sheet OUT.png] [--only a,b]

Writes ui/symbolic/24/<name>-symbolic.svg and ui/symbolic/16/<name>-symbolic.svg (fill-only outlines,
`currentColor`, like icons/symbolic) from the glyph functions in glyphs.py.
"""
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "east"))
import glyphs  # noqa: E402
import pen  # noqa: E402

D = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(D, "ui", "symbolic")
CUR = os.path.join(D, "icons", "symbolic")


GROUPS = {"audio-volume-low": "audio-volume-high", "audio-volume-medium": "audio-volume-high", "audio-volume-muted": "audio-volume-high"}


def bbox(layers):
    xs, ys = [], []
    for l in layers:
        for c in (l[1] if isinstance(l, tuple) else l):
            for x, y in c.points():
                xs.append(x)
                ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


def fitted(name, N):
    """Pen for an icon: if the ink leaves the art box (1 px margin) it is scaled to it; its box is
    centred on the cell (0.5 px); an icon of a group takes the group reference's fit (volume levels)."""
    ref = GROUPS.get(name, name)
    fn = glyphs.ICONS[ref]
    b = bbox(fn(pen.Pen(N)))
    w, h = b[2] - b[0], b[3] - b[1]
    tgt = N - 2.3
    f = min(1.0, tgt / max(w, h)) if max(w, h) > tgt + 0.05 else 1.0
    if f < 1.0:
        b = bbox(fn(pen.Pen(N, f)))
    c = N / 2
    dx, dy = c - (b[0] + b[2]) / 2, c - (b[1] + b[3]) / 2
    q = 1.0 if N == 24 else 0.5
    dx, dy = (round(dx / q) * q if abs(dx) > 0.4 else 0.0), (round(dy / q) * q if abs(dy) > 0.4 else 0.0)
    return pen.Pen(N, f, (dx, dy))


def draw(name, N):
    return pen.svg(glyphs.ICONS[name](fitted(name, N)), N)


def build(names=None):
    names = names or sorted(glyphs.ICONS)
    for N in (16, 24):
        os.makedirs(os.path.join(OUT, str(N)), exist_ok=True)
    for n in names:
        for N in (16, 24):
            with open(os.path.join(OUT, str(N), f"{n}-symbolic.svg"), "w", encoding="utf-8") as f:
                f.write(draw(n, N))
    # the brand glyph is not redrawn (it is the mark): the shipped 16 grid file, also shown at 24
    src = open(os.path.join(CUR, "wolos-glyph-symbolic.svg"), encoding="utf-8").read()
    for N in (16, 24):
        open(os.path.join(OUT, str(N), "wolos-glyph-symbolic.svg"), "w", encoding="utf-8").write(src.replace('width="16" height="16"', f'width="{N}" height="{N}"'))
    return names


def main(argv):
    only = argv[argv.index("--only") + 1].split(",") if "--only" in argv else None
    names = build(only)
    print(f"symbolic.py: {len(names)} icons x 2 sizes -> {OUT}")
    if "--sheet" in argv:
        import sheet
        sheet.contact(names, argv[argv.index("--sheet") + 1])


if __name__ == "__main__":
    main(sys.argv[1:])
