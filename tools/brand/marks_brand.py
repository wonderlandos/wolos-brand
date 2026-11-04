# SPDX-License-Identifier: GPL-2.0-or-later
"""WolOS marks in the brand proportion (docs/adr/brand-calculus.md section 9).

  python3 -I design/tools/brand/marks_brand.py [outdir]      (default design/brand/marks)

The stack is the zucai: a cai (15 fen) over a zhi (6 fen). The shipped WolOS letters are the cai,
15 fen of ink; the zhi under them is 2 fen of gap and 4 fen of katakana (the zhi block is
6 high and 4 thick), ウォルOS as a small centred design element at the bottom of the mark,
tracked to 2/3 of the Latin width (the cai section 10:15). The door mark beside it is 21 fen
tall, 6 fen away. Clear space is 6 fen. Text is outlined (fontTools); no font is embedded.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import calculus as K  # noqa: E402
from geom import f, circle, rrect  # noqa: E402

from fontTools.pens.boundsPen import BoundsPen  # noqa: E402
from fontTools.pens.svgPathPen import SVGPathPen  # noqa: E402
from fontTools.pens.transformPen import TransformPen  # noqa: E402
from fontTools.ttLib import TTCollection, TTFont  # noqa: E402

D = os.path.normpath(os.path.join(HERE, "..", ".."))
P = K.brand_palette()
INK_L, INK_D = P["light.text"][0], P["dark.text"][0]
BG_L, BG_D = P["light.bg"][0], P["dark.bg"][0]
NOTO = "/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc"
INTER = "/usr/share/fonts/opentype/inter/Inter-{w}.otf"
LIC = ('<!-- SPDX-License-Identifier: LicenseRef-Wonderland-Brand-1.0. (c) 2026 Julia Klee. WolOS brand study. '
       'Katakana and hanzi outlined from Noto Sans CJK (SIL OFL 1.1), Latin captions from Inter (SIL OFL 1.1); '
       'no font is embedded. -->')
KANA = "ウォルOS"
_fonts = {}


def font(path, index=None):
    key = (path, index)
    if key not in _fonts:
        _fonts[key] = TTCollection(path).fonts[index] if index is not None else TTFont(path)
    return _fonts[key]


def outline(text, fnt, ink_h=None, size=None, track=0.0, width=None):
    """Outline `text`. Scale so the ink height is `ink_h` (or em size `size`); tracking in em, or
    solved so the ink width is `width`. Returns (d, w, h) with the ink box at (0, 0)."""
    gs, cmap = fnt.getGlyphSet(), fnt.getBestCmap()
    upm = fnt["head"].unitsPerEm
    items = []
    for ch in text:
        g = cmap[ord(ch)]
        bp = BoundsPen(gs)
        gs[g].draw(bp)
        items.append((g, gs[g].width, bp.bounds))
    ys = [b for _, _, b in items if b]
    y0, y1 = min(b[1] for b in ys), max(b[3] for b in ys)
    s = (ink_h / (y1 - y0)) if ink_h else size / upm

    def lay(t):
        xs, x = [], 0.0
        for g, adv, b in items:
            xs.append(x)
            x += adv * s + t
        return xs
    if width is not None:
        # equal gaps between ink boxes (optical tracking: a small kana gets no extra air)
        inks = [(b[2] - b[0]) * s for _, _, b in items]
        gap = (width - sum(inks)) / (len(items) - 1)
        xs, x = [], 0.0
        for (g, adv, b), iw in zip(items, inks):
            xs.append(x - b[0] * s)
            x += iw + gap
        shift = 0.0
    else:
        t = track * upm * s
        xs = lay(t)
        shift = -(xs[0] + items[0][2][0] * s)
    ds, x1 = [], 0
    for (g, adv, b), x in zip(items, xs):
        if not b:
            continue
        pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, x + shift, y1 * s)))
        ds.append(pen.getCommands())
        x1 = max(x1, x + shift + b[2] * s)
    return "".join(ds), x1, (y1 - y0) * s


def latin():
    """The shipped WolOS letters (brand/wolos-wordmark-ja-boot.svg): d, ink w 1725, h 404."""
    src = open(os.path.join(D, "brand", "wolos-wordmark-ja-boot.svg"), encoding="utf-8").read()
    return re.search(r'<path transform="translate\(0 4\)" d="([^"]+)"', src).group(1), 1725.0, 404.0


def door(h):
    """The nested-door mark (brand/wolos-mark.svg geometry) at height h, ink box at (0, 0)."""
    s = h / 380.0
    parts = [("M192 880V500A320 320 0 0 1 832 500V880Z", "#7C5CFF"), ("M288 880V614A224 224 0 0 1 736 614V880Z", "#4B2FD6"),
             ("M355.2 880V693.8A156.8 156.8 0 0 1 668.8 693.8V880Z", "#33208A"),
             ("M402.24 880V749.66A109.76 109.76 0 0 1 621.76 749.66V880Z", "#E9E3FF")]
    g = "".join(f'<path d="{d}" fill="{c}"/>' for d, c in parts)
    # outer door: x 192..832 (640), y 180..880 (700)
    s = h / 700.0
    return f'<g transform="scale({f(s)}) translate(-192 -180)">{g}</g>', 640 * s


def stack(ink, fen):
    """WolOS (15 fen) over the katakana (2 fen gap + 4 fen ink), centred. Returns (svg, w, h)."""
    d, lw, lh = latin()
    s = 15 * fen / lh
    W = lw * s
    kd, kw, kh = outline(KANA, font(NOTO.format(w="Medium"), 0), ink_h=4 * fen, width=W * 2 / 3)
    kx = (W - kw) / 2
    out = (f'<path transform="scale({f(s)})" d="{d}" fill="{ink}"/>'
           f'<path transform="translate({f(kx)} {f(17 * fen)})" d="{kd}" fill="{ink}"/>')
    return out, W, 21 * fen


def svg(w, h, title, body, bg=None):
    b = f'<rect width="{f(w)}" height="{f(h)}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {f(w)} {f(h)}" width="{f(w)}" height="{f(h)}">'
            f'<title>{title}</title>{LIC}{b}{body}</svg>\n')


def mark_files(out):
    fen = 20.0
    pad = 6 * fen
    for mode, ink in (("light", INK_L), ("dark", INK_D)):
        body, w, h = stack(ink, fen)
        sfx = "" if mode == "light" else "-dark"
        open(os.path.join(out, f"wolos-mark-brand{sfx}.svg"), "w").write(
            svg(w + 2 * pad, h + 2 * pad, f"WolOS over ウォルOS, brand stack ({mode} grounds)",
                f'<g transform="translate({f(pad)} {f(pad)})">{body}</g>'))
        dg, dw = door(21 * fen)
        lock = f'<g transform="translate({f(pad)} {f(pad)})">{dg}<g transform="translate({f(dw + 6 * fen)} 0)">{body}</g></g>'
        open(os.path.join(out, f"wolos-lockup-brand{sfx}.svg"), "w").write(
            svg(dw + 6 * fen + w + 2 * pad, h + 2 * pad, f"door, WolOS over ウォルOS, brand lockup ({mode} grounds)", lock))


def boot(out, W=1920, H=1080):
    """Boot: the stack 576 px wide (the 144 fen ruler) on dark.bg, its centre on the optical centre
    (0.45 H); one light from the upper left as a faint glow; a short progress seat 30 fen wide,
    9 fen under the stack's ground line, ending inside the frame."""
    _, lw, lh = latin()
    target_w = 576.0
    fen = target_w / (lw * 15 / lh)
    body, w, h = stack(INK_D, fen)
    x0, y0 = (W - w) / 2, 0.45 * H - h / 2
    glow = ('<defs><radialGradient id="L" cx="0.18" cy="0.12" r="0.75">'
            f'<stop offset="0" stop-color="{P["accent"][0]}" stop-opacity="0.16"/>'
            f'<stop offset="1" stop-color="{BG_D}" stop-opacity="0"/></radialGradient></defs>'
            f'<rect width="{W}" height="{H}" fill="url(#L)"/>')
    bar_w, bar_h = 30 * K.U * W / 1920, K.U
    by = y0 + h + 9 * fen
    bar = (f'<path d="{rrect((W - bar_w) / 2, by, bar_w, bar_h, bar_h / 2)}" fill="{INK_D}" opacity="0.18"/>'
           f'<path d="{rrect((W - bar_w) / 2, by, bar_w * 0.4, bar_h, bar_h / 2)}" fill="{P["dark.accent-text"][0]}"/>')
    open(os.path.join(out, "wolos-boot-brand.svg"), "w").write(
        svg(W, H, "WolOS boot, brand", glow + f'<g transform="translate({f(x0)} {f(y0)})">{body}</g>' + bar, bg=BG_D))


def release(out):
    """0.13 lockup: the stack, then 0.13 Qíjiā (cap height = zhi, 6 fen) on the WolOS
    baseline, the seal 齐家 (cinnabar, 10 fen square) closing the line, and under them, 6 fen down,
    'Put the house in order' (4 fen caps), flush left with the letters."""
    fen = 12.0
    for mode, ink, bg in (("light", INK_L, BG_L), ("dark", INK_D, BG_D)):
        body, w, h = stack(ink, fen)
        inter_sb, inter_r = font(INTER.format(w="SemiBold")), font(INTER.format(w="Regular"))
        # cap height of Inter = ink of "H"; scale so caps are 10 fen
        _, _, hcap = outline("H", inter_sb, size=1000)
        inter_m = font(INTER.format(w="Medium"))
        vd, vw, vh = outline("0.13 Qíjiā", inter_m, size=1000 * 6 * fen / hcap, track=0.02)
        _, _, hq = outline("0.13", inter_m, size=1000 * 6 * fen / hcap)
        gap = 6 * fen
        vx = w + gap
        vy = 15 * fen - hq           # digits sit on the WolOS baseline (ink top of '0.13' aligned to cap)
        # Qíjiā has an accent above and a descender; place by the digits' ink box
        sx = vx + vw + gap
        seal_s = 10 * fen
        sy = 15 * fen - seal_s
        sd, sw, sh = outline("齐家", font(NOTO.format(w="Bold"), 2), ink_h=seal_s * 0.36)
        seal = (f'<path d="{rrect(sx, sy, seal_s, seal_s, 1.2 * fen)}" fill="{P["fire"][0]}"/>'
                f'<g transform="translate({f(sx + (seal_s - sh) / 2)} {f(sy + 0.7 * fen)}) rotate(0)">'
                + vertical("齐家", seal_s * 0.38, "#FFFFFF", seal_s) + '</g>')
        hi = outline("H", inter_r, size=1000)[2]
        td, tw, th = outline("Put the house in order", inter_r, size=1000 * 4 * fen / hi)
        ty = h + gap
        W_ = sx + seal_s
        H_ = ty + th + 2 * fen
        pad = 6 * fen
        grp = (body + f'<path transform="translate({f(vx)} {f(vy - (vh - hq) + 0)})" d="{vd}" fill="{ink}"/>' + seal +
               f'<path transform="translate(0 {f(ty)})" d="{td}" fill="{ink}" opacity="0.72"/>')
        sfx = "" if mode == "light" else "-dark"
        open(os.path.join(out, f"wolos-0.13-qijia-brand{sfx}.svg"), "w").write(
            svg(W_ + 2 * pad, H_ + 2 * pad, f"WolOS 0.13 Qíjiā, Put the house in order ({mode})",
                f'<g transform="translate({f(pad)} {f(pad)})">{grp}</g>', bg=bg))


def vertical(text, glyph_h, colour, box):
    """Hanzi set top to bottom (a seal reads in columns), centred in a `box` square."""
    out, y = [], 0.0
    fnt = font(NOTO.format(w="Bold"), 2)
    parts = []
    for ch in text:
        d, w, h = outline(ch, fnt, ink_h=glyph_h)
        parts.append((d, w, h))
    total = sum(h for _, _, h in parts) + glyph_h * 0.18 * (len(parts) - 1)
    y = (box - total) / 2 - 0.7 * K.U * 3
    for d, w, h in parts:
        out.append(f'<path transform="translate({f((box - w) / 2 - (box - glyph_h) / 2 + (box - glyph_h) / 2 - (box - w) / 2 + (box - w) / 2 - (box - glyph_h) / 2)} {f(y)})" d="{d}" fill="{colour}"/>')
        y += h + glyph_h * 0.18
    return "".join(out)


def main(argv):
    out = argv[0] if argv else os.path.join(D, "brand", "marks")
    os.makedirs(out, exist_ok=True)
    mark_files(out)
    boot(out)
    release(out)
    print("wrote marks to", os.path.normpath(out))


if __name__ == "__main__":
    main(sys.argv[1:])
