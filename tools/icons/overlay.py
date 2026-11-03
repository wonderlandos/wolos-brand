# SPDX-License-Identifier: GPL-2.0-or-later
"""One source for the app icons: design/icons/apps/*.svg. The PNGs the image installs
(desktop/overlay/usr/share/icons/WolOS/<n>x<n>/apps/) are renders of those SVGs, nothing else.

  python3 -I design/tools/icons/overlay.py            render the overlay PNGs from the SVGs on disk
  python3 -I design/tools/icons/overlay.py --check    change nothing; exit 1 when the overlay is not
                                                      the render of the SVGs (missing, stale, extra,
                                                      or a different picture), or when the app icons
                                                      do not all share one grid (a mixed set)

The SVGs are never written here: whoever draws them (tools/icons.py, a painter) runs this after
them. The renderer is rsvg-convert, the one GTK itself loads SVGs with. Python 3 stdlib only."""
import os
import shutil
import struct
import subprocess
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.normpath(os.path.join(HERE, "..", ".."))
APPS = os.path.join(DESIGN, "icons", "apps")
THEME = os.path.normpath(os.path.join(DESIGN, "..", "desktop", "overlay", "usr", "share", "icons", "WolOS"))
SIZES = (48, 128, 512)
BRAND = {"wolos-mark"}      # the brand mark is drawn in design/brand, on its own grid
# Still drawn on the old 64-unit card, not in the set's 1024 art. A ratchet: redraw one, delete it
# here, never add. The check fails when the list is out of date either way. (Empty since the whole
# set was redrawn in the crafted language, 2026-11-03.)
OLD_GRID = set()
# The small drawings (tools/icons/build.py writes them: same icon, larger glyph, simpler detail) are
# what the PNGs up to SMALL_MAX px are rendered from; bigger PNGs come from the scalable drawing.
SMALL = os.path.join(APPS, "small")
SMALL_MAX = 64
# Renders of one SVG differ a little between librsvg builds (anti-aliasing): a channel may be off
# by this much, and only this share of pixels may be off at all, before the picture counts as another.
CHANNEL = 12
SHARE = 0.002


def sources():
    """-> {icon name: svg path} of every app icon (wolos-<name>.svg)."""
    return {f[:-4]: os.path.join(APPS, f) for f in sorted(os.listdir(APPS)) if f.endswith(".svg")}


def drawing(svg, size):
    """The SVG a PNG of this size is rendered from."""
    small = os.path.join(SMALL, os.path.basename(svg))
    return small if size <= SMALL_MAX and os.path.isfile(small) else svg


def render(svg, size):
    exe = shutil.which("rsvg-convert")
    if not exe:
        sys.exit("overlay: rsvg-convert not found (librsvg)")
    r = subprocess.run([exe, "-w", str(size), "-h", str(size), svg], capture_output=True)
    if r.returncode != 0 or not r.stdout.startswith(b"\x89PNG"):
        sys.exit(f"overlay: {svg} @{size}: {r.stderr.decode(errors='replace').strip()}")
    return r.stdout


def pixels(data):
    """-> (w, h, RGBA bytes) of an 8-bit RGBA or RGB PNG."""
    w, h, depth, ctype = struct.unpack(">IIBB", data[16:26])
    if depth != 8 or ctype not in (2, 6):
        raise ValueError("only 8-bit RGB/RGBA PNG")
    bpp = 4 if ctype == 6 else 3
    raw, pos = b"", 8
    while pos < len(data):
        ln, = struct.unpack(">I", data[pos:pos + 4])
        if data[pos + 4:pos + 8] == b"IDAT":
            raw += data[pos + 8:pos + 8 + ln]
        pos += 12 + ln
    raw = zlib.decompress(raw)
    stride, prev, out = w * bpp, bytearray(w * bpp), bytearray()
    for y in range(h):
        ft, line = raw[y * (stride + 1)], bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            a = line[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if ft == 1:
                line[i] = (line[i] + a) & 255
            elif ft == 2:
                line[i] = (line[i] + b) & 255
            elif ft == 3:
                line[i] = (line[i] + (a + b) // 2) & 255
            elif ft == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        if bpp == 3:
            for x in range(w):
                out += line[x * 3:x * 3 + 3] + b"\xff"
        else:
            out += line
        prev = line
    return w, h, bytes(out)


def same_picture(a, b):
    """True when two PNGs show the same thing, give or take renderer anti-aliasing."""
    wa, ha, pa = pixels(a)
    wb, hb, pb = pixels(b)
    if (wa, ha) != (wb, hb):
        return False
    off = sum(1 for i in range(0, len(pa), 4)
              if max(abs(pa[i + k] - pb[i + k]) for k in range(4)) > CHANNEL)
    return off <= SHARE * wa * ha


def grid_of(svg):
    with open(svg, encoding="utf-8") as f:
        head = f.read(4096)
    i = head.find("viewBox=")
    return head[i + 9:head.find(head[i + 8], i + 9)] if i >= 0 else ""


def png_path(size, name):
    return os.path.join(THEME, f"{size}x{size}", "apps", f"{name}.png")


def check(src):
    errs = []
    grids = {}
    for name, svg in src.items():
        if name not in BRAND:
            grids.setdefault(grid_of(svg), []).append(name)
    main_grid = max(grids, key=lambda g: len(grids[g])) if grids else ""
    odd = {n for g, ns in grids.items() if g != main_grid for n in ns}
    for name in sorted(odd - OLD_GRID):
        errs.append(f"{name} is on the grid {grid_of(src[name])!r}, the set is on {main_grid!r}: one set only")
    for name in sorted(OLD_GRID - odd):
        errs.append(f"{name} is on the set's grid now: delete it from OLD_GRID in overlay.py")
    for size in SIZES:
        have = set()
        d = os.path.dirname(png_path(size, "x"))
        if os.path.isdir(d):
            have = {f[:-4] for f in os.listdir(d) if f.endswith(".png")}
        for name in sorted(have - set(src)):
            errs.append(f"{size}x{size}/apps/{name}.png has no SVG in design/icons/apps")
        for name, svg in src.items():
            p = png_path(size, name)
            if not os.path.isfile(p):
                errs.append(f"{size}x{size}/apps/{name}.png is missing")
                continue
            with open(p, "rb") as f:
                if not same_picture(f.read(), render(drawing(svg, size), size)):
                    errs.append(f"{size}x{size}/apps/{name}.png is not the render of {os.path.relpath(drawing(svg, size), APPS)}")
    return errs


def write(src):
    n = 0
    for size in SIZES:
        d = os.path.dirname(png_path(size, "x"))
        os.makedirs(d, exist_ok=True)
        for f in os.listdir(d):
            if f.endswith(".png") and f[:-4] not in src:
                os.remove(os.path.join(d, f))   # an icon the set no longer has
        for name, svg in src.items():
            with open(png_path(size, name), "wb") as f:
                f.write(render(drawing(svg, size), size))
            n += 1
    return n


def main(argv):
    src = sources()
    if "--check" in argv:
        errs = check(src)
        if errs:
            print("\n".join(f"overlay: {e}" for e in errs), file=sys.stderr)
            sys.exit(1)
        print(f"overlay: {len(src)} app icons, {len(src) * len(SIZES)} PNGs match their SVGs")
        return
    print(f"overlay: {write(src)} PNGs rendered from {len(src)} SVGs (rsvg-convert)")


if __name__ == "__main__":
    main(sys.argv[1:])
