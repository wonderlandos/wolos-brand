# SPDX-License-Identifier: GPL-2.0-or-later
"""Contact sheets of the full-colour set (a review tool; needs rsvg-convert and ImageMagick).

  python3 -I design/tools/icons/sheet.py OUT_DIR [--before DIR] [--only apps,places,...]

Writes OUT_DIR/sheet-<size>-<light|dark>.png: with --before (a copy of icons/ as it was) the sheet has
two blocks, before and after; 48 px cells are the real 48 px renders (the small variant), enlarged 2x
with nearest-neighbour for reading. The "after" renders are the generator's own, not the files on disk."""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import families  # noqa: E402
from build import file_name  # noqa: E402
from raster import render_png  # noqa: E402

GROUND = {"light": ("#F5F5F7", "#1C1C1E"), "dark": ("#1C1C1E", "#F5F5F7")}


def cells(tmp, before, size, only):
    after, bef = [], []
    for ic in families.all_icons():
        if only and ic.ctx not in only:
            continue
        p = os.path.join(tmp, f"{ic.ctx}-{ic.name}-{size}.svg")
        with open(p, "w", encoding="utf-8") as f:
            f.write(ic.svg(size <= 64))
        out = p[:-4] + ".png"
        with open(out, "wb") as f:
            f.write(render_png(p, size))
        after.append((ic.name, out))
        if before:
            old = os.path.join(before, ic.ctx, file_name(ic))
            ob = os.path.join(tmp, f"b-{ic.ctx}-{ic.name}-{size}.png")
            if os.path.isfile(old):
                with open(ob, "wb") as f:
                    f.write(render_png(old, size))
            else:
                subprocess.run(["convert", "-size", f"{size}x{size}", "xc:none", ob], check=True)
            bef.append((ic.name, ob))
    return bef, after


def block(tmp, items, size, bg, fg, cols, label, scale):
    cell = size + 16
    ims = [p for _, p in items]
    if not ims:
        return None
    out = os.path.join(tmp, f"block-{label}-{size}-{bg[1:]}.png")
    subprocess.run(["montage", *ims, "-background", bg, "-tile", f"{cols}x", "-geometry", f"{size}x{size}+8+8", out], check=True)
    if scale != 1:
        subprocess.run(["convert", out, "-filter", "point", "-resize", f"{scale * 100}%", out], check=True)
    lab = os.path.join(tmp, f"lab-{label}-{size}-{bg[1:]}.png")
    w = int(subprocess.run(["identify", "-format", "%w", out], capture_output=True, text=True).stdout)
    subprocess.run(["convert", "-size", f"{w}x34", f"xc:{bg}", "-fill", fg, "-pointsize", "18", "-gravity", "West",
                    "-annotate", "+12+0", label, lab], check=True)
    full = os.path.join(tmp, f"full-{label}-{size}-{bg[1:]}.png")
    subprocess.run(["convert", lab, out, "-append", full], check=True)
    return full


def main(argv):
    if not argv:
        sys.exit(__doc__)
    outdir = argv[0]
    before = argv[argv.index("--before") + 1] if "--before" in argv else None
    only = argv[argv.index("--only") + 1].split(",") if "--only" in argv else None
    os.makedirs(outdir, exist_ok=True)
    for size, scale, cols in ((128, 1, 13), (48, 2, 13)):
        with tempfile.TemporaryDirectory() as tmp:
            bef, aft = cells(tmp, before, size, only)
            for mode, (bg, fg) in GROUND.items():
                parts = []
                if before:
                    parts.append(block(tmp, bef, size, bg, fg, cols, f"HEAD (before), {size} px", scale))
                parts.append(block(tmp, aft, size, bg, fg, cols, f"v2 (crafted objects, pressed paper), {size} px" + (" small variant, 2x" if scale == 2 else ""), scale))
                out = os.path.join(outdir, f"sheet-{size}-{mode}.png")
                subprocess.run(["convert", "-background", bg, *[p for p in parts if p], "-append", out], check=True)
                print(out)


if __name__ == "__main__":
    main(sys.argv[1:])
