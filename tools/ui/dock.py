# SPDX-License-Identifier: GPL-2.0-or-later
"""The Dock: measured (crates/shell kit.css, ui/dock.rs) and as the calculus sets it.

  python3 -I design/tools/ui/dock.py render OUT_DIR       the shelf at 1x and 2x, light and dark, both versions
  python3 -I design/tools/ui/dock.py table                the measurement table (markdown)

Both versions draw the same 13 default pins with the A2 icons, so the board isolates the geometry, light and
motion rules from the icon art.  CUR is read from the shell sources (cited per field), NEW is the proposal.
Fen = 4 px (tools/brand/calculus.py).
"""
import io
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "brand"))
import calculus as K  # noqa: E402

D = os.path.normpath(os.path.join(HERE, "..", ".."))
A2 = os.path.join(D, "brand", "types", "A2-bold")
FS = os.path.join(D, "brand", "fullset")

PINS = [("Files", f"{A2}/wolos-files.svg"), ("Apps", f"{FS}/wolos-launcher.svg"), ("Browser", f"{A2}/wolos-atlas-folio.svg"), ("Mail", f"{FS}/wolos-mail.svg"),
        ("Music", f"{FS}/wolos-music.svg"), ("Photos", f"{FS}/wolos-photos.svg"), ("Calendar", f"{FS}/wolos-calendar.svg"), ("Notes", f"{FS}/wolos-notes.svg"),
        ("Terminal", f"{A2}/wolos-console.svg"), ("App Store", f"{A2}/wolos-store.svg"), ("Settings", f"{A2}/wolos-settings.svg"),
        None,
        ("Downloads", f"{FS}/folder-download.svg"), ("Trash", f"{FS}/wolos-trash.svg")]

# state shown on the board: running dot, the focused app, the hovered tile, the launching (bouncing) tile
RUNNING, FOCUSED, HOVER, LAUNCH = {"Files", "Notes"}, "Terminal", "Mail", "Photos"

CUR = dict(name="current", tile=56, gap=8, padx=8, padt=4, dotzone=8, dot=(4, 4), radius=24, sep=(1, 8, 12), lift=24, side=32, bottom=8,
           hover=1.15, neigh=1.0, bounce=16, rim="top", shadow=[(0, 6, 18, 0.24, "#000000"), (0, 1, 4, 0.16, "#000000")],
           focused_pill=False, glass_grad=False, dot_in_icon=False)
NEW = dict(name="proposed", tile=60, gap=8, padx=12, padt=4, dotzone=0, dot=(4, 4), radius=24, sep=(1, 10, 10), lift=24, side=32, bottom=8,
           hover=68 / 60, neigh=64 / 60, bounce=16, rim="lit", shadow=[(3, 6, 24, 0.22, "ink"), (1, 2, 4, 0.16, "ink")],
           focused_pill=True, glass_grad=True, dot_in_icon=True)
MODES = {"light": dict(glass=(255, 255, 255, 140), ink=(21, 21, 32), dot=(21, 21, 32), accent=(116, 82, 245), wall="wonderland-day.svg"),
         "dark": dict(glass=(41, 41, 50, 128), ink=(2, 2, 6), dot=(248, 248, 252), accent=(145, 129, 255), wall="wonderland-night.svg")}


def geometry(P):
    """px layout of the shelf: returns dict with shelf rect (x, y, w, h) inside the board frame and tile rects"""
    n = len(PINS)
    kids = n                                   # children of the box (separator included)
    t = P["tile"]
    sep_w = P["sep"][0]
    inner = sum(sep_w if p is None else t for p in PINS) + P["gap"] * (kids - 1)
    w = inner + 2 * P["padx"] + 2                   # + 1 px hairline each side
    h = P["padt"] + t + P["dotzone"] + 2 + (0 if P["dot_in_icon"] else 0) + (P["padt"] if P["dot_in_icon"] else 0)
    if not P["dot_in_icon"]:
        h = P["padt"] + t + P["dotzone"] + 2
    else:
        h = P["padt"] + t + P["padt"] + 2
    return w, h


def raster(path, px):
    src = path
    if px <= 32:
        sm = os.path.join(os.path.dirname(path), "small", os.path.basename(path))
        src = sm if os.path.exists(sm) else path
    out = subprocess.run(["rsvg-convert", "-w", str(px), "-h", str(px), src], check=True, capture_output=True).stdout
    return Image.open(io.BytesIO(out)).convert("RGBA")


def wall(mode, w, h):
    svg = os.path.join(D, "wallpapers", MODES[mode]["wall"])
    out = subprocess.run(["rsvg-convert", "-w", "2400", svg], check=True, capture_output=True).stdout
    im = Image.open(io.BytesIO(out)).convert("RGBA")
    # the bottom-centre of the desktop: where the Dock sits
    cx, by = im.width // 2, im.height
    box = (cx - w // 2, by - h, cx - w // 2 + w, by)
    return im.crop(box)


def rr_mask(size, box, r, ss=4):
    W, H = size
    m = Image.new("L", (W * ss, H * ss), 0)
    ImageDraw.Draw(m).rounded_rectangle([box[0] * ss, box[1] * ss, box[2] * ss - 1, box[3] * ss - 1], radius=r * ss, fill=255)
    return m.resize((W, H), Image.LANCZOS)


def render(P, mode, s=1):
    """board for one version and mode at scale s (1 = 1x, 2 = 2x HiDPI). Returns (image, tree)."""
    M = MODES[mode]
    w, h = geometry(P)
    FW = w + 2 * P["side"]
    FH = P["lift"] + h + P["bottom"]
    W, H = FW * s, FH * s
    base = wall(mode, FW * s, FH * s)
    sx, sy = P["side"] * s, P["lift"] * s
    box = (sx, sy, sx + w * s, sy + h * s)
    r = P["radius"] * s
    mask = rr_mask((W, H), box, r)
    ink = M["ink"] if P["shadow"][0][4] == "ink" else (0, 0, 0)
    # shadows: coloured by the ink of the surface, offset along 1:2 for the proposal
    canvas = base.copy()
    for dx, dy, blur, op, _ in P["shadow"]:
        if mode == "dark" and P["name"] == "proposed":
            op = op * 2                           # tokens: the dark shadow is .45 against .18 by day
        layer = Image.new("RGBA", (W, H), ink + (0,))
        a = ImageChops.offset(mask, dx * s, dy * s).filter(ImageFilter.GaussianBlur(blur * s / 2))
        layer.putalpha(a.point(lambda v, op=op: int(v * op)))
        canvas = Image.alpha_composite(canvas, layer)
    # the glass: the wallpaper behind it blurred, then tinted
    blurred = canvas.filter(ImageFilter.GaussianBlur(14 * s))
    canvas.paste(blurred, (0, 0), mask)
    glass = Image.new("RGBA", (W, H), M["glass"])
    if P["glass_grad"]:
        # lit upper left: +12 alpha at the lit corner, -12 at the shadow corner, along 1:2
        ys, xs = np.mgrid[0:H, 0:W]
        t = ((xs - sx) * 1 + (ys - sy) * 2) / (w * s * 1 + h * s * 2)
        a = np.clip(M["glass"][3] + (0.5 - t) * 40, 0, 255).astype(np.uint8)
        glass.putalpha(Image.fromarray(a))
    ga = ImageChops.multiply(glass.getchannel("A"), mask)
    glass.putalpha(ga)
    canvas = Image.alpha_composite(canvas, glass)
    # hairline (1 px) all round; the rim highlight: whole top edge (current) or the lit upper-left edge (proposal)
    inner = rr_mask((W, H), (box[0] + s, box[1] + s, box[2] - s, box[3] - s), max(r - s, 0))
    ring = ImageChops.subtract(mask, inner)
    hl = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    hl.putalpha(ring.point(lambda v: int(v * 0.22)))
    canvas = Image.alpha_composite(canvas, hl)
    if P["rim"] == "top":
        edge = ImageChops.subtract(inner, ImageChops.offset(inner, 0, s))
        rim_a = edge.point(lambda v: int(v * 0.5))
    else:
        sh = ImageChops.offset(inner, s // 2 or 1, s)
        edge = ImageChops.subtract(inner, sh)
        ys, xs = np.mgrid[0:H, 0:W]
        t = np.clip(1 - (((xs - sx) + (ys - sy) * 0.5) / (w * s * 0.55)), 0, 1)
        rim_a = Image.fromarray((np.asarray(edge).astype(float) * 0.7 * t).astype(np.uint8))
    rim = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    rim.putalpha(rim_a)
    canvas = Image.alpha_composite(canvas, rim)
    # children
    t = P["tile"] * s
    x = sx + s + P["padx"] * s
    ty = sy + s + P["padt"] * s
    nodes = [{"id": "frame", "rect": [0, 0, FW, FH], "role": "box"},
             {"id": "shelf", "rect": [P["side"], P["lift"], w, h], "role": "opening", "parent": "frame", "radius": P["radius"]}]
    tiles = []
    ti = 0
    for p in PINS:
        if p is None:
            sw = P["sep"][0] * s
            top = ty + P["sep"][1] * s
            bot = ty + t - P["sep"][2] * s
            sep = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(sep).rectangle([x, top, x + sw - 1, bot], fill=M["dot"] + (46,))
            canvas = Image.alpha_composite(canvas, sep)
            nodes.append({"id": "sep", "rect": [x / s, top / s, P["sep"][0], (bot - top) / s], "role": "line", "parent": "shelf"})
            x += sw + P["gap"] * s
            continue
        name, path = p
        # magnify: the hovered tile and (proposal) its neighbours grow about their bottom centre
        k = 1.0
        idx = [q[0] for q in PINS if q].index(name)
        hov = [q[0] for q in PINS if q].index(HOVER)
        if name == HOVER:
            k = P["hover"]
        elif abs(idx - hov) == 1:
            k = P["neigh"]
        lift_px = P["bounce"] * s if name == LAUNCH else 0
        px = round(t * k)
        ic = raster(path, px)
        cx = x + t / 2
        bottom = ty + t - lift_px
        canvas.alpha_composite(ic, (round(cx - px / 2), round(bottom - px)))
        tiles.append((name, cx, ty))
        nodes.append({"id": f"t{ti}", "rect": [x / s, ty / s, P["tile"], P["tile"]], "role": "control", "parent": "shelf", "group": "tiles"})
        ti += 1
        # running dot / focused pill
        if name in RUNNING or name == FOCUSED:
            dw, dh = P["dot"]
            if name == FOCUSED and P["focused_pill"]:
                dw = 12
            dy = (ty + t - (dh + 0) * s) if P["dot_in_icon"] else (ty + t + 2 * s)
            col = M["accent"] if (name == FOCUSED and P["focused_pill"]) else M["dot"]
            dd = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(dd).rounded_rectangle([round(cx - dw * s / 2), round(dy), round(cx + dw * s / 2) - 1, round(dy + dh * s) - 1], radius=dh * s // 2, fill=col + ((255 if col == M["accent"] else 217),))
            canvas = Image.alpha_composite(canvas, dd)
        x += t + P["gap"] * s
    return canvas.convert("RGB"), {"frame": [FW, FH], "nodes": nodes}


def table():
    rows = [
        ("tile (icon canvas)", "56 (`kit/widgets.rs` DOCK_TILE; prefs TILE_SIZE 32..96, default 56)", "60 = 15 fen (cai); range 32..96 and the Size slider unchanged"),
        ("gap between tiles", "8 (`dock.rs` content_with: `gtk::Box::new(.., S2)`)", "8 = 2 fen (unchanged)"),
        ("shelf padding", "4 top, 8 sides, 0 bottom (`.dock-shelf` padding)", "4 top, 12 sides (3 fen), 4 bottom"),
        ("running dot", "4 x 4 in a 8 px row under the tile (margin 2 / 2)", "4 x 4 inside the icon's own 1.5-fen air (tile bottom 4 px); focused app: 12 x 4 accent pill"),
        ("shelf height", "68 = 4 + 56 + 8 (test `the_dock_reserves_the_shelf_not_its_lift_room`: 24 + 4 + 64 + 8)", "68 = 4 + 60 + 4 (17 fen, band cai, unchanged)"),
        ("shelf width (13 pins)", "851 (golden dock-light.png: 13 x 56 + 13 x 8 + 1 + 16 + 2)", "911 (13 x 60 + 13 x 8 + 1 + 24 + 2)"),
        ("radius", "24 (`--glass-radius`)", "24 = 6 fen (unchanged)"),
        ("margins", "lift 24 (SHELF_LIFT), sides 32, bottom 8", "unchanged (6 / 8 / 2 fen)"),
        ("separator", "1 px, margin 8 top / 12 bottom", "1 px, 10 top / 10 bottom: 40 px tall, centred on the art"),
        ("shadow", "0 6px 18px rgba(0,0,0,.24), 0 1px 4px rgba(0,0,0,.16): straight down, black", "3px 6px 24px ink .22, 1px 2px 4px ink .16: dx:dy = 1:2, the ink of the surface"),
        ("rim", "inset 0 1px 0 rgba(255,255,255,.5): the whole top edge", "1 px white .5 on the upper-left edge only, fading by 55% of the width"),
        ("glass", "50% of --glass, flat", "same tint, +/- 16% alpha along 1:2 (lit upper left)"),
        ("magnify", "scale 1.15 under the pointer (`MAGNIFY`, spring SNAPPY 320/30)", "60 -> 68 (+2 fen) = 17/15; neighbours 64 (+1 fen); same spring"),
        ("bounce", "-16 px, 640 ms ease-in-out (kit.css dock-bounce)", "-16 px (4 fen): unchanged"),
        ("focus ring", "2 px accent, offset 2", "unchanged"),
    ]
    return rows


def main(argv):
    if argv[0] == "table":
        for r in table():
            print("| " + " | ".join(r) + " |")
        return
    out = argv[1]
    os.makedirs(out, exist_ok=True)
    for P in (CUR, NEW):
        for mode in MODES:
            for s in (1, 2):
                im, tree = render(P, mode, s)
                im.save(os.path.join(out, f"dock-{P['name']}-{mode}-{s}x.png"))
                if s == 1:
                    json.dump(tree, open(os.path.join(out, f"dock-{P['name']}.json"), "w"), indent=1)
    print("dock.py ->", out)


if __name__ == "__main__":
    main(sys.argv[1:])
