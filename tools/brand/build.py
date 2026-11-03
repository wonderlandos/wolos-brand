# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2026 Julia Klee
"""Build the shipped WolOS brand set (logo direction C, rabbit mascot).  Fill-only SVG, no strokes.

  python3 -I build.py <design dir> [<site-drop dir>]
or  import build; build.build(design_dir, site_dir=None)

Writes <design>/brand/*.svg + wolos-splash.png (256) + os_wolos.png (128), the rabbit into
<design>/illustrations/ (white-rabbit.svg, white-rabbit-expressions.svg and their PNGs), and,
if given, the site assets into <site-drop dir>.  Needs rsvg-convert (and convert for favicon.ico).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from marks import (svg, mark_c, mark_c_mono, mark_c16, wordmark, door_boxes, WM_W, WM_H,  # noqa: E402
                   ACC, ACC_D, INK, PAPER, LIGHT)
import mascots as M  # noqa: E402

C_DARK = (ACC_D, "#5E3FE6", "#36209A", LIGHT)      # mark C on dark grounds
BOX = (192, 180, 640, 700)                         # visible box of mark C on its 1024 canvas
DARK_BG = "#1C1C1E"                                # tokens dark.bg


def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def png(src, out, px, py=None):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.run(["rsvg-convert", "-w", str(px), "-h", str(py or px), src, "-o", out], check=True)


def rgba(path):
    """Force 8-bit RGBA (colour type 6): the loader and the checks read PNG32 only."""
    subprocess.run(["convert", path, "-strip", "-define", "png:color-type=6", f"PNG32:{path}"], check=True)


def placed(inner, x, y, height):
    """Mark C (drawn on its 1024 canvas) with its box top-left at (x, y), `height` tall."""
    s = height / BOX[3]
    return f'<g transform="translate({x - BOX[0] * s:g} {y - BOX[1] * s:g}) scale({s:.6g})">{inner}</g>', BOX[2] * s


def mark64(cols):
    body, _ = placed(mark_c(cols), 6.4, 4, 56)
    return body


def lockup360(cols, ink):
    """Mark + wordmark in the 360 x 96 box (the viewBox the old wordmark files had)."""
    cap, mh, gap = 400, 620, 240
    mw = BOX[2] * mh / BOX[3]
    total = mw + gap + WM_W
    k = 344 / total
    inner, _ = placed(mark_c(cols), 0, 0, mh)
    body = inner + wordmark(ink, mw + gap, (mh - cap) / 2)
    return f'<g transform="translate(8 {(96 - mh * k) / 2:g}) scale({k:.6g})">{body}</g>'


def ring16():
    # the 16 px glyph: door and inner door as one U-shaped outline (no coincident edges)
    return "M3 15V7A5 5 0 0 1 13 7V15H10V11A2 2 0 0 0 6 11V15Z"


def build(DESIGN, SITE=None):
    DESIGN = os.path.abspath(DESIGN)
    SITE = os.path.abspath(SITE) if SITE else None
    # ------------------------------------------------------------------------------ brand/
    B = os.path.join(DESIGN, "brand")
    t = "WolOS"
    w(f"{B}/wolos-mark.svg", svg((0, 0, 64, 64), mark64((ACC, "#4B2FD6", "#33208A", LIGHT)), 64, 64, "WolOS mark"))
    w(f"{B}/wolos-mark-on-dark.svg", svg((0, 0, 64, 64), mark64(C_DARK), 64, 64, "WolOS mark, for dark grounds"))
    b, _ = placed(mark_c_mono(INK), 6.4, 4, 56)
    w(f"{B}/wolos-mark-mono.svg", svg((0, 0, 64, 64), b, 64, 64, "WolOS mark, one colour"))
    b, _ = placed(mark_c_mono("#FFFFFF"), 6.4, 4, 56)
    w(f"{B}/wolos-mark-mono-white.svg", svg((0, 0, 64, 64), b, 64, 64, "WolOS mark, one colour, white"))
    w(f"{B}/wolos-mark-16.svg", svg((0, 0, 16, 16), mark_c16((ACC, LIGHT)), 16, 16, "WolOS mark, 16 px"))
    w(f"{B}/wolos-mark-16-on-dark.svg", svg((0, 0, 16, 16), mark_c16((ACC_D, LIGHT)), 16, 16, "WolOS mark, 16 px, for dark grounds"))
    # the symbolic glyph: GTK recolours currentColor; the old file's style="color:#2e3436" is kept
    w(f"{B}/wolos-glyph-symbolic.svg",
      svg((0, 0, 16, 16), f'<path fill="currentColor" d="{ring16()}"/>', 16, 16, "WolOS").replace(
          'height="16">', 'height="16" style="color:#2e3436">', 1))
    w(f"{B}/wolos-wordmark.svg", svg((0, 0, 360, 96), lockup360((ACC, "#4B2FD6", "#33208A", LIGHT), INK), 360, 96, "WolOS"))
    w(f"{B}/wolos-wordmark-dark.svg", svg((0, 0, 360, 96), lockup360(C_DARK, PAPER), 360, 96, "WolOS"))

    # boot splash 1920x1080: the white mark centred on black + a progress bar (as before)
    mh = 240
    inner, mw = placed(mark_c_mono("#FFFFFF"), 960 - BOX[2] * mh / BOX[3] / 2, 456 - mh / 2, mh)
    w(f"{B}/wolos-boot.svg", svg((0, 0, 1920, 1080),
      '<rect width="1920" height="1080" fill="#000"/>' + inner +
      '<rect x="810" y="720" width="300" height="6" rx="3" fill="#fff" fill-opacity=".22"/>'
      '<rect x="810" y="720" width="110" height="6" rx="3" fill="#fff"/>', 1920, 1080, "WolOS boot"))

    # kernel / plymouth splash: 256 x 256 RGBA, white mark on opaque black
    tmp = os.path.join(B, ".splash.svg")
    inner, mw = placed(mark_c_mono("#FFFFFF"), 128 - BOX[2] * 190 / BOX[3] / 2, 128 - 95, 190)
    w(tmp, svg((0, 0, 256, 256), '<rect width="256" height="256" fill="#000"/>' + inner, 256, 256))
    png(tmp, f"{B}/wolos-splash.png", 256)
    os.remove(tmp)
    rgba(f"{B}/wolos-splash.png")
    png(f"{B}/wolos-mark.svg", f"{B}/os_wolos.png", 128)
    rgba(f"{B}/os_wolos.png")

    # ------------------------------------------------------------------------------ rabbit
    I = os.path.join(DESIGN, "illustrations")
    # square canvas around the 512 x 660 figure, so the PNGs keep the 256 / 512 squares the apps load
    w(f"{I}/white-rabbit.svg", M.rabbit_svg())
    png(f"{I}/white-rabbit.svg", f"{I}/png/white-rabbit@1x.png", 256)
    png(f"{I}/white-rabbit.svg", f"{I}/png/white-rabbit@2x.png", 512)
    M.sheet("The White Rabbit · neutral + expressions", M.rabbit_pose(), M.RABBIT_EXPR, M.rabbit_head,
            f"{I}/white-rabbit-expressions.svg", vb_head=(16, -24, 480, 480))
    png(f"{I}/white-rabbit-expressions.svg", f"{I}/png/white-rabbit-expressions@1x.png", 1296, 760)

    # ------------------------------------------------------------------------------ site drop
    if SITE:
        S = SITE
        LIGHT_C = (ACC, "#4B2FD6", "#33208A", LIGHT)
        for name in ("wolos-mark.svg", "wolos-mark-on-dark.svg", "wolos-glyph-symbolic.svg", "wolos-wordmark.svg",
                     "wolos-wordmark-dark.svg", "wolos-boot.svg"):
            w(f"{S}/brand/{name}", open(f"{B}/{name}").read())
        w(f"{S}/icons/wolos-mark.svg", open(f"{B}/wolos-mark.svg").read())
        w(f"{S}/img/wolos-rabbit.svg", open(f"{I}/white-rabbit.svg").read())
        # favicon: the 16 px drawing reads in light and dark tabs (accent + tint)
        fav = svg((0, 0, 16, 16), mark_c16((ACC, LIGHT)), 16, 16, "WolOS")
        w(f"{S}/favicon.svg", fav)
        w(f"{S}/wolos-mark.svg", fav)        # index.html:26 links /wolos-mark.svg as the SVG icon
        png(f"{S}/favicon.svg", f"{S}/favicon-16.png", 16)
        # 32 px and up: the full mark on a transparent ground (24 px is the full mark's minimum)
        def padded(px, margin, bg=None, cols=LIGHT_C):
            mw = BOX[2] * (px - 2 * margin) / BOX[3]
            inner, _ = placed(mark_c(cols), (px - mw) / 2, margin, px - 2 * margin)
            rect = f'<rect width="{px}" height="{px}" fill="{bg}"/>' if bg else ""
            p = os.path.join(S, f".t{px}.svg")
            w(p, svg((0, 0, px, px), rect + inner, px, px))
            return p
        for px, mg, bg, out in ((32, 2, None, "favicon-32.png"), (180, 30, PAPER, "apple-touch-icon.png"),
                                (512, 96, PAPER, "icon-512.png")):
            p = padded(px, mg, bg)
            png(p, f"{S}/{out}", px)
            os.remove(p)
        subprocess.run(["convert", f"{S}/favicon-16.png", f"{S}/favicon-32.png", f"{S}/favicon.ico"], check=True)
        # social card: lockup on dark, 1200 x 630 (mark 620 u tall, wordmark cap 400 u, scale sc)
        sc = 0.28
        mark_h = 620 * sc
        lw = (BOX[2] * 620 / BOX[3] + 240 + WM_W) * sc
        x0 = (1200 - lw) / 2
        inner, mw3 = placed(mark_c(C_DARK), x0, (630 - mark_h) / 2, mark_h)
        word = wordmark(PAPER, x0 + mw3 + 240 * sc, (630 - 400 * sc) / 2, sc)
        w(f"{S}/.og.svg", svg((0, 0, 1200, 630), f'<rect width="1200" height="630" fill="{DARK_BG}"/>' + inner + word, 1200, 630))
        png(f"{S}/.og.svg", f"{S}/og/wolos-mark.png", 1200, 630)
        os.remove(f"{S}/.og.svg")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
