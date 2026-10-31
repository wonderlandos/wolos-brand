# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2026 Julia Klee
"""The Mad Tea Party cup: clean, empty, still warm. Nothing here yet."""
import math
from kit import f, path, sample, volume, band, KEY, sparkle
from parts import glow, ground, BRASS

GOLD = [(0, "#FFF4C9"), (0.3, "#E9B654"), (0.6, "#B07A1E"), (1, "#FFE2A0")]
PORC = [(0, "#FFFFFF"), (0.55, "#F6F3FB"), (1, "#C9C0DD")]


def ell(cx, cy, rx, ry):
    return f"M{f(cx - rx)} {f(cy)}a{f(rx)} {f(ry)} 0 1 0 {f(2 * rx)} 0a{f(rx)} {f(ry)} 0 1 0 {f(-2 * rx)} 0Z"


def ell_poly(cx, cy, rx, ry, n=40):
    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


def mini_mark(x, y, s):
    """A tiny WolOS keyhole, for the china pattern."""
    return (f'<path d="M{f(x - .42 * s)} {f(y - .3 * s)}C{f(x - .6 * s)} {f(y - .9 * s)} {f(x - .3 * s)} {f(y - 1.1 * s)} '
            f'{f(x - .18 * s)} {f(y - .35 * s)}H{f(x + .18 * s)}C{f(x + .3 * s)} {f(y - 1.1 * s)} {f(x + .6 * s)} '
            f'{f(y - .9 * s)} {f(x + .42 * s)} {f(y - .3 * s)}A{f(.5 * s)} {f(.5 * s)} 0 0 1 {f(x + .2 * s)} {f(y + .42 * s)}'
            f'L{f(x + .3 * s)} {f(y + 1.0 * s)}H{f(x - .3 * s)}L{f(x - .2 * s)} {f(y + .42 * s)}A{f(.5 * s)} {f(.5 * s)} 0 0 1 '
            f'{f(x - .42 * s)} {f(y - .3 * s)}Z"/>')


def teacup(cv, shadow=True, steam=True):
    g = ""
    if shadow:
        g += ground(cv, 262, 432, 220, 26, .3)
    # ---- saucer
    sx, sy = 256, 392
    g += f'<path d="{ell(sx + 4, sy + 16, 196, 48)}" fill="#2A1A55" opacity=".25" filter="{cv.blur(8)}"/>'
    # underside thickness
    g += f'<path d="{ell(sx, sy + 9, 192, 50)}" fill="{cv.lin(sx - 190, 0, sx + 190, 0, [(0, "#E8E2F4"), (1, "#9C90BC")])}"/>'
    top = ell(sx, sy, 194, 50)
    g += volume(cv, top, ell_poly(sx, sy, 194, 50), cv.lin(sx - 180, sy - 40, sx + 180, sy + 40, PORC),
                shade=("#6E5BB0", .35, 10, 8), hi=("#fff", .8, 4, 3))
    # violet band and gold lip on the saucer
    g += f'<path d="{ell(sx, sy, 176, 44)}" fill="none" stroke="{cv.lin(sx - 170, 0, sx + 170, 0, [(0, "#9D85FF"), (0.5, "#7C5CFF"), (1, "#4A2FC0")])}" stroke-width="10"/>'
    g += f'<path d="{ell(sx, sy, 170, 42.5)}" fill="none" stroke="#FFE7A3" stroke-width="1.2" stroke-dasharray="1 4" stroke-linecap="round"/>'
    g += f'<path d="{ell(sx, sy, 193, 49.5)}" fill="none" stroke="{cv.lin(sx - 190, 0, sx + 190, 0, GOLD)}" stroke-width="3"/>'
    # the well where the cup sits
    g += f'<path d="{ell(sx, sy + 2, 96, 24)}" fill="{cv.lin(sx, sy - 22, sx, sy + 26, [(0, "#C7BEDD"), (1, "#FFFFFF")])}"/>'
    g += f'<path d="{ell(sx, sy + 2, 96, 24)}" fill="none" stroke="{cv.lin(sx - 96, 0, sx + 96, 0, GOLD)}" stroke-width="2"/>'

    # ---- spoon resting on the saucer
    spoon = cv.lin(330, 400, 430, 450, [(0, "#FFFFFF"), (0.35, "#C9C3D8"), (0.6, "#F4F2F8"), (1, "#8D86A3")])
    g += (f'<g transform="rotate(-12 300 416)">'
          f'<path d="M300 420H424" stroke="#2A1A55" stroke-width="7" opacity=".3" stroke-linecap="round" filter="{cv.blur(3)}" transform="translate(2 6)"/>'
          f'<ellipse cx="300" cy="424" rx="20" ry="9" fill="#2A1A55" opacity=".3" filter="{cv.blur(3)}" transform="translate(2 4)"/>'
          f'<path d="M318 418C352 417 392 416 430 412" stroke="{spoon}" stroke-width="6" stroke-linecap="round" fill="none"/>'
          f'<path d="M318 416.6C352 415.6 392 414.6 430 410.6" stroke="#fff" stroke-width="1.4" stroke-linecap="round" fill="none" opacity=".9"/>'
          f'<ellipse cx="434" cy="411.5" rx="7" ry="5" fill="{spoon}"/>'
          f'<ellipse cx="298" cy="420" rx="22" ry="10.5" fill="{spoon}"/>'
          f'<ellipse cx="295" cy="418" rx="12" ry="4.5" fill="#fff" opacity=".85"/>'
          f'<path d="M278 422q20 8 40 -2" stroke="#7E7796" stroke-width="1.2" fill="none" opacity=".6"/>'
          '</g>')

    # ---- cup
    cx, cy, rx, ry = 248, 250, 128, 36
    g += f'<path d="{ell(cx + 8, 396, 74, 14)}" fill="#2A1A55" opacity=".5" filter="{cv.blur(5)}"/>'
    # foot ring
    foot = f"M{cx - 62} 372C{cx - 64} 386 {cx - 52} 396 {cx} 397C{cx + 52} 396 {cx + 64} 386 {cx + 62} 372Z"
    g += f'<path d="{foot}" fill="{cv.lin(cx - 62, 0, cx + 62, 0, [(0, "#FFFFFF"), (0.6, "#E1DAEF"), (1, "#9C90BC")])}"/>'
    g += f'<path d="M{cx - 62} 390C{cx - 30} 398 {cx + 30} 398 {cx + 62} 390" stroke="{cv.lin(cx - 62, 0, cx + 62, 0, GOLD)}" stroke-width="2.4" fill="none"/>'
    # handle: a Mad Hatter flourish
    h = f"M{cx + 118} 276C{cx + 176} 252 {cx + 196} 300 {cx + 172} 330C{cx + 152} 356 {cx + 118} 352 {cx + 100} 340"
    curl = f"M{cx + 124} 272C{cx + 128} 252 {cx + 150} 244 {cx + 160} 256C{cx + 168} 266 {cx + 156} 276 {cx + 148} 268"
    hg = cv.lin(cx + 110, 250, cx + 190, 350, [(0, "#FFFFFF"), (0.5, "#E9E3F5"), (1, "#8E82B0")])
    g += (f'<path d="{h}" stroke="#2A1A55" stroke-width="16" fill="none" opacity=".3" stroke-linecap="round" '
          f'filter="{cv.blur(4)}" transform="translate(5 7)"/>'
          f'<path d="{h}" stroke="{hg}" stroke-width="15" fill="none" stroke-linecap="round"/>'
          f'<path d="{h}" stroke="{cv.lin(cx + 110, 250, cx + 190, 350, GOLD)}" stroke-width="2.2" fill="none" '
          f'transform="translate(1.5 1.5)" opacity=".9"/>'
          f'<path d="{h}" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round" opacity=".9" '
          f'transform="translate(-2.5 -3)"/>'
          f'<path d="{curl}" stroke="{hg}" stroke-width="8" fill="none" stroke-linecap="round"/>'
          f'<path d="{curl}" stroke="#fff" stroke-width="2" fill="none" stroke-linecap="round" opacity=".9" transform="translate(-1 -1.5)"/>')
    body = (f"M{cx - rx} {cy}A{rx} {ry} 0 0 0 {cx + rx} {cy}"
            f"C{cx + rx - 2} 318 {cx + 86} 372 {cx} 378C{cx - 86} 372 {cx - rx + 2} 318 {cx - rx} {cy}Z")
    bp = [(cx - rx, cy), (cx + rx, cy), (cx + 90, 360), (cx, 378), (cx - 90, 360)]
    # the china pattern: a violet band with a row of little keyholes, scalloped in gold
    pat = ""
    band_top = lambda dy: f"M{cx - rx - 10} {cy + dy}A{rx + 10} {ry + 4} 0 0 0 {cx + rx + 10} {cy + dy}"
    vb = cv.lin(cx - rx, 0, cx + rx, 0, [(0, "#A58FFF"), (0.4, "#7C5CFF"), (1, "#3E24B0")])
    pat += (f'<path d="{band_top(18)}L{cx + rx + 10} {cy + 52}A{rx + 10} {ry + 4} 0 0 1 {cx - rx - 10} {cy + 52}Z" '
            f'fill="{vb}"/>')
    marks = ""
    for i in range(11):
        t = math.pi * (0.08 + 0.84 * i / 10)
        x = cx - math.cos(t) * (rx - 4)
        y = cy + 36 + math.sin(t) * (ry + 3)
        sc = 7 * (.55 + .45 * math.sin(t))
        marks += f'<g transform="translate({f(x)} {f(y)}) scale({f(sc / 7 * math.sin(t) ** .3)} {f(sc / 7)}) translate({f(-x)} {f(-y)})">{mini_mark(x, y, 7)}</g>'
    pat += f'<g fill="#FFF6DA" opacity=".9">{marks}</g>'
    for dy, w in ((18, 2.4), (52, 2.4)):
        pat += (f'<path d="{band_top(dy)}" stroke="{cv.lin(cx - rx, 0, cx + rx, 0, GOLD)}" stroke-width="{w}" '
                f'fill="none"/>')
    # scallop garland under the band
    sc = ""
    for i in range(16):
        t0 = math.pi * (i / 16)
        t1 = math.pi * ((i + 1) / 16)
        x0, y0 = cx - math.cos(t0) * (rx + 6), cy + 52 + math.sin(t0) * (ry + 4)
        x1, y1 = cx - math.cos(t1) * (rx + 6), cy + 52 + math.sin(t1) * (ry + 4)
        sc += f"M{f(x0)} {f(y0)}Q{f((x0 + x1) / 2)} {f((y0 + y1) / 2 + 9)} {f(x1)} {f(y1)}"
    pat += f'<path d="{sc}" stroke="{cv.lin(cx - rx, 0, cx + rx, 0, GOLD)}" stroke-width="1.6" fill="none"/>'
    gloss = (f'<path d="M{cx - 96} 290C{cx - 92} 324 {cx - 70} 350 {cx - 44} 362" stroke="#fff" stroke-width="10" '
             f'fill="none" stroke-linecap="round" opacity=".85" filter="{cv.blur(3)}"/>'
             f'<path d="M{cx - 104} 300C{cx - 100} 318 {cx - 92} 332 {cx - 82} 342" stroke="#fff" stroke-width="3" '
             f'fill="none" stroke-linecap="round"/>')
    g += volume(cv, body, sample(bp), cv.lin(cx - rx, cy, cx + rx, 370, PORC),
                shade=("#5A4796", .5, 26, 18), hi=("#fff", .9, 8, 6), rim=("#C9B8FF", .9, 3, 1.6),
                under=pat, extra=gloss
                # light bounced up from the saucer, and a fine gold line near the foot
                + band(cv, body, sample(bp), (0, 1), 6, 5, "#FFFFFF", .8)
                + f'<path d="M{cx - 84} 352C{cx - 40} 368 {cx + 40} 368 {cx + 84} 352" stroke="{cv.lin(cx - 84, 0, cx + 84, 0, GOLD)}" '
                f'stroke-width="1.6" fill="none"/>')
    # ---- the opening: an empty cup, a ring where the tea was
    op = ell(cx, cy, rx, ry)
    inside = cv.lin(cx, cy - ry, cx, cy + ry, [(0, "#FFFFFF"), (0.5, "#F7F4FC"), (1, "#E2DBEF")])
    ic = cv.clip(op)
    inner = (f'<path d="M{cx - rx} {cy}A{rx} {ry} 0 0 1 {cx + rx} {cy}C{cx + 60} {cy - 8} {cx - 60} {cy + 20} {cx - rx} {cy}Z" '
             f'fill="#8E7BC8" opacity=".2" filter="{cv.blur(9)}"/>'
             f'<path d="{ell(cx - 60, cy + 6, 70, 26)}" fill="#8E7BC8" opacity=".12" filter="{cv.blur(12)}"/>'
             f'<path d="{ell(cx + 6, cy + 14, 70, 15)}" fill="#ECE7F5"/>'
             f'<path d="{ell(cx + 6, cy + 14, 56, 11)}" fill="none" stroke="#C9935A" stroke-width="2.4" opacity=".55"/>'
             f'<path d="{ell(cx + 6, cy + 14, 52, 9.5)}" fill="none" stroke="#E2B78A" stroke-width="1.4" opacity=".4"/>'
             f'<ellipse cx="{cx + 34}" cy="{cy + 16}" rx="5" ry="2.2" fill="#B9844A" opacity=".55"/>'
             f'<ellipse cx="{cx + 33}" cy="{cy + 15.4}" rx="1.8" ry=".8" fill="#fff" opacity=".9"/>'
             # light from the left wall bouncing onto the right
             f'<path d="{ell(cx + 70, cy + 2, 50, 26)}" fill="#fff" opacity=".7" filter="{cv.blur(10)}"/>')
    g += f'<path d="{op}" fill="{inside}"/><g clip-path="{ic}">{inner}</g>'
    g += f'<path d="{op}" fill="none" stroke="{cv.lin(cx - rx, 0, cx + rx, 0, GOLD)}" stroke-width="5"/>'
    g += f'<path d="{ell(cx, cy - 1.2, rx - 1, ry - .6)}" fill="none" stroke="#FFF8DE" stroke-width="1.2" opacity=".9"/>'

    # ---- steam: one last curl, the shape of a question
    if steam:
        s1 = f"M{cx - 12} {cy - 14}C{cx - 40} {cy - 50} {cx + 20} {cy - 70} {cx - 6} {cy - 110}C{cx - 26} {cy - 140} {cx + 10} {cy - 176} {cx + 36} {cy - 160}C{cx + 58} {cy - 146} {cx + 44} {cy - 120} {cx + 26} {cy - 128}"
        s2 = f"M{cx + 36} {cy - 12}C{cx + 60} {cy - 36} {cx + 30} {cy - 60} {cx + 52} {cy - 92}C{cx + 64} {cy - 108} {cx + 60} {cy - 124} {cx + 70} {cy - 134}"
        stm = cv.lin(cx, cy - 20, cx, cy - 180, [(0, "#B9A6FF", 0), (0.3, "#B9A6FF", .9), (0.8, "#D9CCFF", .8), (1, "#E6DCFF", .5)])
        stw = cv.lin(cx, cy, cx, cy - 180, [(0, "#fff", 0), (0.35, "#fff", 1), (1, "#fff", .7)])
        g += (f'<path d="{s1}" stroke="{stm}" stroke-width="16" fill="none" stroke-linecap="round" filter="{cv.blur(6)}"/>'
              f'<path d="{s1}" stroke="{stw}" stroke-width="5" fill="none" stroke-linecap="round" filter="{cv.blur(1.5)}"/>'
              f'<path d="{s2}" stroke="{stm}" stroke-width="10" fill="none" stroke-linecap="round" filter="{cv.blur(5)}" opacity=".8"/>'
              f'<path d="{s2}" stroke="{stw}" stroke-width="3" fill="none" stroke-linecap="round" filter="{cv.blur(1.2)}" opacity=".8"/>')
        g += sparkle(cx + 92, cy - 120, 9, "#B9A6FF", .9) + sparkle(cx - 70, cy - 84, 6, "#C9B8FF", .8)
        g += sparkle(cx + 70, cy - 40, 4, "#D9CCFF", .8)
    return g
