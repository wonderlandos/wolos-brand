# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2026 Julia Klee
"""The Rabbit's pocket watch, open, gears turning. Updating."""
import math
from kit import f, path, sample, volume, band, KEY, sparkle
from parts import BRASS, BRASS_SPIN, conic, glow, ground, crescent, motes, chain_links
from keyhole import mark_paths, engraving

BLUE = [(0, "#B9A6FF"), (0.4, "#5B3BE8"), (1, "#24104F")]   # blued-steel hands, our violet


def circ(cx, cy, r):
    return f"M{f(cx - r)} {f(cy)}a{f(r)} {f(r)} 0 1 0 {f(2 * r)} 0a{f(r)} {f(r)} 0 1 0 {f(-2 * r)} 0Z"


def cpoly(cx, cy, r, n=48):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def gear(cv, cx, cy, r, teeth, rot, fill, spokes=5, hub="#7C5CFF"):
    pts = []
    for i in range(teeth * 4):
        a = 2 * math.pi * i / (teeth * 4) + math.radians(rot)
        rr = r if (i % 4) in (1, 2) else r * .86
        pts.append(f"{f(cx + rr * math.cos(a))} {f(cy + rr * math.sin(a))}")
    d = "M" + "L".join(pts) + "Z"
    # cut-outs between spokes
    holes = ""
    for k in range(spokes):
        a0 = 2 * math.pi * k / spokes + math.radians(rot) + .22
        a1 = 2 * math.pi * (k + 1) / spokes + math.radians(rot) - .22
        r0, r1 = r * .3, r * .7
        holes += (f"M{f(cx + r0 * math.cos(a0))} {f(cy + r0 * math.sin(a0))}"
                  f"L{f(cx + r1 * math.cos(a0))} {f(cy + r1 * math.sin(a0))}"
                  f"A{f(r1)} {f(r1)} 0 0 1 {f(cx + r1 * math.cos(a1))} {f(cy + r1 * math.sin(a1))}"
                  f"L{f(cx + r0 * math.cos(a1))} {f(cy + r0 * math.sin(a1))}"
                  f"A{f(r0)} {f(r0)} 0 0 0 {f(cx + r0 * math.cos(a0))} {f(cy + r0 * math.sin(a0))}Z")
    g = (f'<path d="{d}{holes}" fill-rule="evenodd" fill="#1A0D00" opacity=".5" transform="translate(2 3)" '
         f'filter="{cv.blur(2)}"/>')
    g += f'<path d="{d}{holes}" fill-rule="evenodd" fill="{fill}"/>'
    g += f'<path d="{d}{holes}" fill-rule="evenodd" fill="none" stroke="#5E3A08" stroke-width=".8" opacity=".6"/>'
    # a jewel at the arbor
    g += (f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r * .2)}" fill="{cv.lin(cx - r * .2, cy - r * .2, cx + r * .2, cy + r * .2, [(0, "#E8DEFF"), (0.4, hub), (1, "#24104F")])}"/>'
          f'<circle cx="{f(cx - r * .06)}" cy="{f(cy - r * .07)}" r="{f(r * .05)}" fill="#fff"/>')
    return g


def numeral(s, x, y, h, rot, col="#2A1A40"):
    """Roman numerals drawn as strokes with serifs, upright to the rim."""
    w = h * .12
    parts = []
    cx = 0.0
    widths = {"I": h * .22, "V": h * .5, "X": h * .5}
    total = sum(widths[c] for c in s) + h * .06 * (len(s) - 1)
    cx = -total / 2
    for c in s:
        wd = widths[c]
        if c == "I":
            parts.append(f"M{f(cx + wd / 2)} {f(-h / 2)}V{f(h / 2)}")
        elif c == "V":
            parts.append(f"M{f(cx)} {f(-h / 2)}L{f(cx + wd / 2)} {f(h / 2)}L{f(cx + wd)} {f(-h / 2)}")
        else:
            parts.append(f"M{f(cx)} {f(-h / 2)}L{f(cx + wd)} {f(h / 2)}M{f(cx + wd)} {f(-h / 2)}L{f(cx)} {f(h / 2)}")
        if c == "I":
            parts.append(f"M{f(cx - h * .04)} {f(-h / 2)}H{f(cx + wd + h * .04)}M{f(cx - h * .04)} {f(h / 2)}H{f(cx + wd + h * .04)}")
        cx += wd + h * .06
    return (f'<path d="{"".join(parts)}" stroke="{col}" stroke-width="{f(w)}" fill="none" '
            f'transform="translate({f(x)} {f(y)}) rotate({f(rot)})"/>')


def breguet(cv, cx, cy, ang, L, w, ring):
    """Moon hand: tapered blade with an open ring near the tip."""
    a = math.radians(ang - 90)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    tip = (cx + ux * L, cy + uy * L)
    rc = (cx + ux * (L - ring * 2.2), cy + uy * (L - ring * 2.2))
    base = (cx - ux * L * .2, cy - uy * L * .2)
    d = (f"M{f(base[0] + nx * w)} {f(base[1] + ny * w)}L{f(rc[0] + nx * w * .5)} {f(rc[1] + ny * w * .5)}"
         f"L{f(tip[0])} {f(tip[1])}L{f(rc[0] - nx * w * .5)} {f(rc[1] - ny * w * .5)}"
         f"L{f(base[0] - nx * w)} {f(base[1] - ny * w)}Z")
    ringd = circ(rc[0], rc[1], ring)
    ringh = circ(rc[0], rc[1], ring * .55)
    fill = cv.lin(cx - L, cy - L, cx + L, cy + L, BLUE)
    sh = (f'<g transform="translate(4 6)" opacity=".3" filter="{cv.blur(2.5)}" fill="#1A0D33">'
          f'<path d="{d}"/><path d="{ringd}{ringh}" fill-rule="evenodd"/></g>')
    return (sh + f'<path d="{d}" fill="{fill}"/><path d="{ringd}{ringh}" fill-rule="evenodd" fill="{fill}"/>'
            f'<path d="M{f(base[0])} {f(base[1])}L{f(tip[0])} {f(tip[1])}" stroke="#E8DEFF" stroke-width=".8" opacity=".7"/>')


def pocket_watch(cv, shadow=True):
    g = ""
    cx, cy, R = 262, 284, 148
    if shadow:
        g += ground(cv, 256, 470, 190, 16, .28)
    # ---- the chain, sweeping out of frame bottom-left
    ch = f"M{cx} {cy - R - 46}C{cx - 120} {cy - R - 80} {cx - 250} {cy - 60} {cx - 200} {cy + 120}C{cx - 180} {cy + 180} {cx - 120} {cy + 196} {cx - 70} {cy + 186}"
    segs = [((cx, cy - R - 64), (cx - 120, cy - R - 90), (cx - 250, cy - 60), (cx - 200, cy + 120)),
            ((cx - 200, cy + 120), (cx - 180, cy + 180), (cx - 120, cy + 196), (cx - 70, cy + 186))]
    g += chain_links(cv, segs, 10, 3.4)
    # T-bar at the end of the chain
    tx, ty = cx - 70, cy + 186
    g += (f'<rect x="{tx - 4}" y="{ty - 20}" width="9" height="40" rx="4.5" fill="{cv.lin(tx - 4, 0, tx + 5, 0, BRASS)}" '
          f'transform="rotate(-20 {tx} {ty})"/>')

    # ---- open lid, hinged at nine o'clock, seen edge-on
    lx, ly = cx - R - 34, cy
    lid = f"M{f(lx)} {f(ly - R * .98)}C{f(lx - 74)} {f(ly - R * .7)} {f(lx - 74)} {f(ly + R * .7)} {f(lx)} {f(ly + R * .98)}C{f(lx + 30)} {f(ly + R * .7)} {f(lx + 30)} {f(ly - R * .7)} {f(lx)} {f(ly - R * .98)}Z"
    g += f'<path d="{lid}" fill="#1A0D00" opacity=".4" transform="translate(10 12)" filter="{cv.blur(8)}"/>'
    lidp = [(lx, ly - R), (lx - 56, ly), (lx, ly + R), (lx + 22, ly)]
    eng = ""
    ears, head, foot = mark_paths(lx - 16, ly - 4, 1.25)
    sq = f"translate({f(lx - 16)} 0) scale(.45 1) translate({f(-(lx - 16))} 0)"
    cart = f"M{f(lx - 16)} {f(ly - 70)}a40 70 0 1 0 .1 0Z"
    eng += (f'<g transform="{sq}"><path d="{cart}" fill="none" stroke="#7A4E12" stroke-width="2.4"/>'
            f'<path d="{cart}" fill="none" stroke="#FFF1C0" stroke-width="1.1" transform="translate(1 1)"/>'
            f'<path d="{ears}{head}{foot}" fill="#8A5A16" opacity=".55"/>'
            f'<path d="{ears}{head}{foot}" fill="none" stroke="#FFF1C0" stroke-width="1" transform="translate(.8 .8)"/></g>')
    g += volume(cv, lid, sample(lidp), cv.lin(lx - 60, ly - R, lx + 30, ly + R, [(0, "#FFF0B8"), (0.3, "#C98F2C"), (0.55, "#FFE7A3"), (0.8, "#8A5A16"), (1, "#D9A040")]),
                shade=("#3A2205", .5, 12, 8), hi=("#FFF6D6", .8, 5, 3), rim=("#C9B8FF", .9, 2.5, 1.4), extra=eng)
    # hinge
    g += (f'<rect x="{cx - R - 22}" y="{cy - 26}" width="20" height="52" rx="8" fill="{cv.lin(cx - R - 22, 0, cx - R, 0, BRASS)}"/>'
          f'<path d="M{cx - R - 22} {cy - 9}h20M{cx - R - 22} {cy + 9}h20" stroke="#5E3A08" stroke-width="1.4"/>')

    # ---- bow and crown
    g += (f'<ellipse cx="{cx}" cy="{cy - R - 40}" rx="30" ry="24" fill="none" stroke="#2A1A05" stroke-width="10" '
          f'opacity=".35" transform="translate(3 4)" filter="{cv.blur(2.5)}"/>'
          f'<ellipse cx="{cx}" cy="{cy - R - 40}" rx="30" ry="24" fill="none" stroke="{cv.lin(cx - 30, cy - R - 64, cx + 30, cy - R - 16, BRASS)}" stroke-width="9"/>'
          f'<ellipse cx="{cx}" cy="{cy - R - 40}" rx="30" ry="24" fill="none" stroke="#FFF6D6" stroke-width="1.6" '
          f'transform="translate(-1.5 -2)" opacity=".8"/>')
    crown = cv.lin(cx - 16, 0, cx + 16, 0, [(0, "#8A5A16"), (0.3, "#FFF0B8"), (0.6, "#C98F2C"), (1, "#5E3A08")])
    g += (f'<rect x="{cx - 9}" y="{cy - R - 18}" width="18" height="22" fill="{crown}"/>'
          f'<rect x="{cx - 17}" y="{cy - R - 30}" width="34" height="16" rx="5" fill="{crown}"/>')
    kn = "".join(f"M{cx - 15 + i * 3.4} {cy - R - 29}v14" for i in range(10))
    g += f'<path d="{kn}" stroke="#5E3A08" stroke-width="1.1" opacity=".6"/>'

    # ---- case
    g += f'<path d="{circ(cx, cy, R)}" fill="#1A0D00" opacity=".5" transform="translate(10 14)" filter="{cv.blur(10)}"/>'
    g += volume(cv, circ(cx, cy, R), cpoly(cx, cy, R), "#C98F2C", shade=("#3A2205", .55, 14, 9),
                hi=("#FFF6D6", .7, 6, 4), rim=("#C9B8FF", .9, 3, 1.6), extra=conic(cx, cy, R + 4, BRASS_SPIN, 96))
    # coin-edge knurl
    kn = ""
    for i in range(120):
        a = 2 * math.pi * i / 120
        kn += (f"M{f(cx + math.cos(a) * (R - 9))} {f(cy + math.sin(a) * (R - 9))}"
               f"L{f(cx + math.cos(a) * (R - 1.5))} {f(cy + math.sin(a) * (R - 1.5))}")
    g += f'<path d="{kn}" stroke="#5E3A08" stroke-width="1.1" opacity=".45"/>'
    # bezel
    g += (f'<circle cx="{cx}" cy="{cy}" r="{R - 14}" fill="none" stroke="#3A2205" stroke-width="5" opacity=".55"/>'
          f'<circle cx="{cx}" cy="{cy}" r="{R - 16}" fill="none" stroke="{cv.lin(cx, cy - R, cx, cy + R, [(0, "#8A5A16"), (1, "#FFF1C0")])}" stroke-width="5"/>')
    # ---- enamel dial
    Rd = R - 20
    dial = cv.rad(cx - 40, cy - 50, Rd * 1.25, [(0, "#FFFFFF"), (0.55, "#FBF7EE"), (1, "#E4D9C4")])
    guil = ""
    for i in range(36):
        guil += f'<circle cx="{f(cx + 3 * math.cos(i))}" cy="{f(cy + 3 * math.sin(i))}" r="{f(18 + i * 1.6)}"/>'
    dial_in = (f'<g fill="none" stroke="#C9B89A" stroke-width=".5" opacity=".45">{guil}</g>'
               + band(cv, circ(cx, cy, Rd), cpoly(cx, cy, Rd), KEY, 14, 8, "#6B5330", .45))
    # minute track (railway) and numerals
    tr = ""
    for k in range(60):
        a = 2 * math.pi * k / 60
        tr += (f"M{f(cx + math.cos(a) * (Rd - 6))} {f(cy + math.sin(a) * (Rd - 6))}"
               f"L{f(cx + math.cos(a) * (Rd - (14 if k % 5 == 0 else 11)))} {f(cy + math.sin(a) * (Rd - (14 if k % 5 == 0 else 11)))}")
    dial_in += f'<path d="{tr}" stroke="#2A1A40" stroke-width="1.2"/>'
    dial_in += (f'<circle cx="{cx}" cy="{cy}" r="{Rd - 6}" fill="none" stroke="#2A1A40" stroke-width="1"/>'
                f'<circle cx="{cx}" cy="{cy}" r="{Rd - 11}" fill="none" stroke="#2A1A40" stroke-width=".7"/>')
    names = ["XII", "I", "II", "III", "IIII", "V", "VI", "VII", "VIII", "IX", "X", "XI"]
    for k, nm in enumerate(names):
        if k == 6:
            continue   # VI sits where the movement shows through
        a = math.radians(k * 30 - 90)
        dial_in += numeral(nm, cx + math.cos(a) * (Rd - 32), cy + math.sin(a) * (Rd - 32), 17, k * 30)
    # skeleton window: the movement at work
    wx, wy, wr = cx, cy + 50, 46
    win = circ(wx, wy, wr)
    wc = cv.clip(win)
    mv = (f'<rect x="{wx - wr}" y="{wy - wr}" width="{2 * wr}" height="{2 * wr}" fill="{cv.rad(wx, wy - 20, wr * 1.4, [(0, "#4A3A6E"), (1, "#140A26")])}"/>'
          + gear(cv, wx - 20, wy - 6, 30, 16, 6, cv.lin(wx - 50, wy - 36, wx + 10, wy + 24, BRASS), 5)
          + gear(cv, wx + 26, wy + 14, 22, 12, 12, cv.lin(wx, wy - 8, wx + 48, wy + 36, [(0, "#FFFFFF"), (0.5, "#B8B2C8"), (1, "#6E6688")]), 4)
          + gear(cv, wx + 14, wy - 30, 14, 9, 0, cv.lin(wx, wy - 44, wx + 28, wy - 16, BRASS), 3)
          + band(cv, win, cpoly(wx, wy, wr), KEY, 6, 4, "#000", .6))
    dial_in += (f'<path d="{win}" fill="#000"/><g clip-path="{wc}">{mv}</g>'
                f'<circle cx="{wx}" cy="{wy}" r="{wr + 2}" fill="none" stroke="{cv.lin(wx - wr, wy - wr, wx + wr, wy + wr, BRASS)}" stroke-width="4"/>'
                f'<circle cx="{wx}" cy="{wy}" r="{wr + 4}" fill="none" stroke="#2A1A40" stroke-width=".8"/>')
    # maker's line under XII
    dial_in += (f'<path d="M{cx - 18} {cy - 56}h36" stroke="#7C5CFF" stroke-width="1.2" opacity=".7"/>'
                f'<g fill="#7C5CFF" opacity=".8">'
                f'<path d="{"".join(mark_paths(cx, cy - 72, .42))}"/></g>')
    g += volume(cv, circ(cx, cy, Rd), cpoly(cx, cy, Rd), dial, extra=dial_in)
    # ---- hands: nearly time
    g += breguet(cv, cx, cy, -32, Rd * .62, 5.5, 7)
    g += breguet(cv, cx, cy, 58, Rd * .86, 4, 5.5)
    g += (f'<path d="M{cx} {cy + 34}L{cx} {cy - Rd * .9}" stroke="#C2456B" stroke-width="1.4" '
          f'transform="rotate(130 {cx} {cy})"/>')
    g += f'<circle cx="{cx}" cy="{cy}" r="7" fill="{cv.lin(cx - 7, cy - 7, cx + 7, cy + 7, BLUE)}"/>'
    g += f'<circle cx="{cx - 2}" cy="{cy - 2}" r="2" fill="#E8DEFF"/>'
    # ---- crystal
    g += (f'<path d="{crescent(cx, cy, Rd - 10, Rd - 10, 190, 268, 22)}" fill="#fff" opacity=".55" filter="{cv.blur(2)}"/>'
          f'<path d="{crescent(cx, cy, Rd - 6, Rd - 6, 200, 250, 5)}" fill="#fff" opacity=".9"/>'
          f'<path d="{crescent(cx, cy, Rd - 8, Rd - 8, 20, 70, 6)}" fill="#fff" opacity=".45"/>'
          f'<ellipse cx="{cx + 56}" cy="{cy - 66}" rx="26" ry="10" fill="#fff" opacity=".35" '
          f'transform="rotate(40 {cx + 56} {cy - 66})" filter="{cv.blur(3)}"/>')
    # ---- a little time-dust: it is working
    for (a, r, s) in ((-30, R + 30, 9), (-10, R + 44, 5), (14, R + 26, 6), (200, R + 38, 7)):
        x, y = cx + math.cos(math.radians(a)) * r, cy + math.sin(math.radians(a)) * r
        g += glow(cv, x, y, s * 2.4, "#C9B8FF", .6) + sparkle(x, y, s, "#9B85FF", .95)
    return g
