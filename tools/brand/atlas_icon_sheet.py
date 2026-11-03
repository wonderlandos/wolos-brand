# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2026 Julia Klee
"""Contact sheet of the Atlas theme icon as it ships: `wolos-atlas` (icons/apps/wolos-atlas.svg and its
small drawing, written by tools/icons/build.py) and the symbolic `atlas-symbolic` (tools/icons.py).

Each size is the renderer's real output at that size: 512 and 128 from the full drawing, 48 from the small
one (tools/icons/overlay.py, the overlay PNG rule), 16 the symbolic in the ground's text colour (GTK
recolours currentColor; under 32 px the theme uses the symbolic, never a shrunk colour icon). The 48 and 16
renders are repeated enlarged with nearest neighbour so their pixels can be read. Light ground above,
dark below (tokens/colors.json).

  python3 -I atlas_icon_sheet.py <design dir>     write brand/atlas/icon/contact-sheet.png (rsvg-convert)
"""
import base64
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "icons"))
from overlay import pixels  # noqa: E402  (stdlib PNG reader of the overlay check)


def render(svg, px):
    return subprocess.run(["rsvg-convert", "-w", str(px), "-h", str(px), svg], capture_output=True, check=True).stdout


def tint(svg_path, colour, tmp):
    """The symbolic with currentColor set the way GTK sets it: the ground's text colour."""
    text = open(svg_path, encoding="utf-8").read().replace("color:#2e3436", f"color:{colour}")
    p = os.path.join(tmp, f"sym-{colour[1:]}.svg")
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def enlarge(png, k):
    """Nearest-neighbour k-times enlargement of an RGBA PNG (stdlib)."""
    import struct
    import zlib
    w, h, px = pixels(png)
    raw = bytearray()
    for y in range(h * k):
        raw.append(0)
        row = px[(y // k) * w * 4:(y // k + 1) * w * 4]
        for x in range(w * k):
            raw += row[(x // k) * 4:(x // k) * 4 + 4]
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w * k, h * k, 8, 6, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def sheet(design, tmp):
    T = json.load(open(os.path.join(design, "tokens", "colors.json"), encoding="utf-8"))
    full = os.path.join(design, "icons", "apps", "wolos-atlas.svg")
    small = os.path.join(design, "icons", "apps", "small", "wolos-atlas.svg")
    sym = os.path.join(design, "icons", "symbolic", "atlas-symbolic.svg")
    font = "Inter, 'Noto Sans', 'DejaVu Sans', sans-serif"
    pad, head, rowh = 40, 96, 640
    cols = ((512, "512 px", 0), (128, "128 px", 0), (48, "48 px (small drawing)", 0), (16, "16 px (atlas-symbolic)", 0),
            (48, "48 px, x4", 4), (16, "16 px, x8", 8))
    colw = [max(px * (k or 1), 150) for px, _, k in cols]       # small renders get room for their label
    W = pad + sum(colw) + 40 * (len(cols) - 1) + pad
    H = head + rowh * 2
    out = [f'<rect width="{W}" height="{head}" fill="{T["light"]["bg"]}"/>',
           f'<text x="{pad}" y="52" font-family="{font}" font-size="28" font-weight="700" fill="{T["light"]["text"]}">'
           'Atlas: the theme icon wolos-atlas (direction B, Folio)</text>',
           f'<text x="{pad}" y="78" font-family="{font}" font-size="14" fill="{T["light"]["text-2"]}">'
           'Real renders at each size (rsvg-convert); the 48 and 16 renders repeated enlarged, nearest neighbour</text>']
    for ri, mode in enumerate(("light", "dark")):
        ground, ink, sub = T[mode]["bg"], T[mode]["text"], T[mode]["text-2"]
        y0 = head + ri * rowh
        out.append(f'<rect x="0" y="{y0}" width="{W}" height="{rowh}" fill="{ground}"/>')
        x = pad
        for (px, label, k), cw in zip(cols, colw):
            if px == 16:
                png = render(tint(sym, ink, tmp), 16)
            else:
                png = render(small if px <= 64 else full, px)
            if k:
                png = enlarge(png, k)
            size = px * (k or 1)
            y = y0 + 56 + (512 - size) // 2
            out.append(f'<image x="{x}" y="{y}" width="{size}" height="{size}" '
                       f'href="data:image/png;base64,{base64.b64encode(png).decode()}"/>')
            out.append(f'<text x="{x}" y="{y0 + 604}" font-family="{font}" font-size="13" fill="{sub}">{label}</text>')
            x += cw + 40
        out.append(f'<text x="{pad}" y="{y0 + 32}" font-family="{font}" font-size="13" font-weight="600" '
                   f'fill="{ink}">{mode} ground {ground}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'{"".join(out)}</svg>\n')


def main(design):
    import tempfile
    design = os.path.abspath(design)
    dst = os.path.join(design, "brand", "atlas", "icon", "contact-sheet.png")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "sheet.svg")
        with open(p, "w", encoding="utf-8") as f:
            f.write(sheet(design, tmp))
        subprocess.run(["rsvg-convert", p, "-o", dst], check=True)
    print(f"atlas_icon_sheet: {dst}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", ".."))
