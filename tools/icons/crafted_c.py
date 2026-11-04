# SPDX-License-Identifier: GPL-2.0-or-later
"""Crafted objects, part three: the apps WolOS ships that had no icon in the language (clocks,
documents, videos, archive, disk usage). Same language as crafted_a/b.py (design/icons/LANGUAGE.md):
one lit object on the soft card, ramps and two shadows in the card's own darkest tone, one pop."""
import math
from svgk import *

BRASS = [(0, "#FFF0B3"), (.5, "#E5A93B"), (1, "#8A5A12")]
METAL = [(0, "#FFFFFF"), (.45, "#D5D9E2"), (1, "#8B93A6")]
IVORY = [(0, "#FFFFFF"), (1, "#EDE3D0")]


# ---------------------------------------------------------------- CLOCK (a brass alarm clock)
def clock(cv):
    container(cv, "#C277DE", "#4A1563", glow="#F2DAFF", edge="#1E0428", glow_op=.30)
    cx, cy, R = 512, 548, 214
    sh = "#1E0428"
    o = ""
    # feet, behind the case
    for s in (-1, 1):
        ft = f"M{cx + s * 120} {cy + 170}L{cx + s * 176} {cy + 252}"
        o += tube(cv, ft, 34, "#FFE9A0", "#A8701C", sh, hl=.6)
    # bells on the shoulders, a bridge over them and the hammer between
    for s in (-1, 1):
        bx, by = cx + s * 168, cy - 196
        bell = f"M{bx - 92} {by + 40}A92 92 0 0 1 {bx + 92} {by + 40}Z"
        o += f'<g transform="rotate({s * 30} {bx} {by + 40})">'
        o += shadow(cv, bell, 14, 10, sh, .5) + f'<path d="{bell}" fill="{cv.lin(BRASS, 0, 0, 1, 1)}"/>'
        o += rimlight(cv, bell, 5, .9) + f'<path d="{bell}" fill="none" stroke="{sh}" stroke-opacity=".35" stroke-width="3"/>'
        o += f'<ellipse cx="{bx - 30}" cy="{by - 12}" rx="26" ry="12" fill="#fff" opacity=".7" transform="rotate(-30 {bx - 30} {by - 12})"/>'
        o += f'<rect x="{bx - 92}" y="{by + 34}" width="184" height="14" rx="7" fill="#7A4C0E"/></g>'
    o += tube(cv, f"M{cx - 150} {cy - 232}Q{cx} {cy - 330} {cx + 150} {cy - 232}", 26, "#FFF0B3", "#A8701C", sh, hl=.7)
    # the case: a brass ring, then the ivory face under glass
    case = circ(cx, cy, R)
    o += shadows(cv, case, sh, (34, 24, .6), (10, 8, .45))
    o += f'<path d="{case}" fill="{cv.lin(BRASS, 0, 0, 1, 1)}"/>'
    o += rimlight(cv, case, 7, .9)
    o += f'<path d="{case}" fill="none" stroke="{sh}" stroke-opacity=".4" stroke-width="3"/>'
    face = circ(cx, cy, R - 34)
    o += f'<path d="{circ(cx, cy, R - 30)}" fill="{cv.lin([(0, "#7A4C0E"), (1, "#FFE9A0")])}"/>'
    o += f'<path d="{face}" fill="{cv.rad([(0, "#FFFFFF"), (.7, "#F7EEDD"), (1, "#E2D2B4")], .45, .35, .8)}"/>'
    # ticks: the quarters long, the rest dots
    for i in range(12):
        a = math.radians(i * 30 - 90)
        if i % 3:
            x, y = cx + 150 * math.cos(a), cy + 150 * math.sin(a)
            o += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="#5A3A6A" opacity=".7"/>'
        elif i:
            x0, y0 = cx + 130 * math.cos(a), cy + 130 * math.sin(a)
            x1, y1 = cx + 160 * math.cos(a), cy + 160 * math.sin(a)
            o += f'<path d="M{x0:.1f} {y0:.1f}L{x1:.1f} {y1:.1f}" stroke="#4A1563" stroke-width="18" stroke-linecap="round"/>'
    # twelve is a small lit door (the one motif)
    dr = f"M{cx - 20} {cy - 128}V{cy - 156}a20 20 0 0 1 40 0V{cy - 128}Z"
    o += f'<ellipse cx="{cx}" cy="{cy - 142}" rx="36" ry="40" fill="#FFC94A" opacity=".55" filter="{cv.blur(10)}"/>'
    o += f'<path d="{dr}" fill="{cv.rad([(0, "#FFF6C8"), (.5, "#FFD04A"), (1, "#F08A1C")], .5, .9, .95)}" stroke="#4A1563" stroke-width="6" stroke-linejoin="round"/>'
    # hands, with their own small shadow
    hands = f"M{cx} {cy}L{cx - 78} {cy - 70}M{cx} {cy}L{cx + 108} {cy + 46}"
    o += f'<path d="{hands}" stroke="{sh}" stroke-width="22" stroke-linecap="round" opacity=".35" filter="{cv.blur(6)}" transform="translate(0 8)"/>'
    o += f'<path d="{hands}" stroke="#2A1438" stroke-width="20" stroke-linecap="round"/>'
    o += f'<path d="M{cx} {cy}L{cx + 30} {cy - 132}" stroke="#C2416B" stroke-width="8" stroke-linecap="round"/>'
    o += knob(cv, cx, cy, 20, "#FFF3C0", "#F0B13C", "#8A5A12", sh, 4)
    # the glass: a crescent and a small specular
    o += f'<path d="M{cx - 150} {cy - 60}A168 168 0 0 1 {cx + 20} {cy - 172}Q{cx - 84} {cy - 132} {cx - 150} {cy - 60}Z" fill="#fff" opacity=".55"/>'
    o += ellipse_spec(cv, cx + 104, cy + 112, 34, 12, -40, .4, 3)
    cv.add(o)


# ---------------------------------------------------------------- DOCUMENTS (an open book with a ribbon)
def documents(cv):
    container(cv, "#F07A5A", "#8E1E22", glow="#FFE0D2", edge="#3A0608", glow_op=.30)
    sh = "#3A0608"
    cx, top, bot = 512, 300, 742
    # the leather cover under the pages, edges showing
    cover = (f"M{cx} {top + 34}Q{cx - 120} {top - 26} {cx - 290} {top + 12}V{bot + 34}Q{cx - 120} {bot - 4} {cx} {bot + 46}"
             f"Q{cx + 120} {bot - 4} {cx + 290} {bot + 34}V{top + 12}Q{cx + 120} {top - 26} {cx} {top + 34}Z")
    o = shadows(cv, cover, sh, (34, 24, .6), (10, 8, .45))
    o += f'<path d="{cover}" fill="{cv.lin([(0, "#6A3A2A"), (1, "#2E140C")])}"/>'
    o += rimlight(cv, cover, 4, .5)
    # page block edges (two lines of stacked pages under each leaf)
    for s in (-1, 1):
        for k, c in ((2, "#D8C7A8"), (1, "#EADCC2")):
            pd = (f"M{cx} {top + 14 + k * 8}Q{cx + s * 120} {top - 34 + k * 8} {cx + s * (262 + k * 6)} {top - 6 + k * 8}"
                  f"V{bot + 12 + k * 8}Q{cx + s * 120} {bot - 20 + k * 8} {cx} {bot + 28 + k * 4}Z")
            o += f'<path d="{pd}" fill="{c}"/>'
    # the two leaves, curving up from the spine
    for s in (-1, 1):
        lf = (f"M{cx} {top + 14}Q{cx + s * 120} {top - 40} {cx + s * 262} {top - 8}"
              f"V{bot + 4}Q{cx + s * 120} {bot - 30} {cx} {bot + 20}Z")
        x1, x2 = (0, 1) if s < 0 else (1, 0)
        o += f'<path d="{lf}" fill="{cv.lin([(0, "#E9DCC4"), (.25, "#FFFDF6"), (1, "#F6EBD6")], x1, 0, x2, 0)}"/>'
        o += f'<path d="{lf}" fill="none" stroke="#7A5A3A" stroke-opacity=".35" stroke-width="3"/>'
        # lines of text, following the page's curve a little
        for i in range(6):
            y = top + 70 + i * 62
            w = 170 if i % 3 != 2 else 110
            x0 = cx + 42 if s > 0 else cx - 232
            o += f'<rect x="{x0}" y="{y}" width="{w}" height="20" rx="10" fill="#6E5A72" opacity="{.62 if i else .85}"/>'
    # the spine's fold shadow
    o += f'<path d="M{cx} {top + 14}V{bot + 20}" stroke="{cv.lin([(0, "#000", .0), (.2, "#000", .30), (1, "#000", .18)])}" stroke-width="26"/>'
    o += f'<path d="M{cx} {top + 14}V{bot + 20}" stroke="#fff" stroke-opacity=".5" stroke-width="3"/>'
    # a picture on the right leaf (a document, not a novel)
    pic = rrect(cx + 52, top + 248, 186, 112, 14)
    o += f'<path d="{pic}" fill="{cv.lin([(0, "#8CC3F5"), (1, "#3B6FC0")])}"/>'
    o += f'<g clip-path="{cv.clip(pic)}"><path d="M{cx + 52} {top + 360}L{cx + 118} {top + 300}L{cx + 160} {top + 336}L{cx + 196} {top + 306}L{cx + 238} {top + 360}Z" fill="#1D3F7A"/></g>'
    o += f'<circle cx="{cx + 200}" cy="{top + 280}" r="14" fill="#FFC94A"/>'
    # the ribbon: wine silk, down over the bottom edge (the pop)
    rb = f"M{cx + 150} {top - 14}H{cx + 196}V{bot + 96}L{cx + 173} {bot + 74}L{cx + 150} {bot + 96}Z"
    o += shadow(cv, rb, 10, 6, sh, .5) + f'<path d="{rb}" fill="{cv.lin([(0, "#7C5CFF"), (1, "#3B20B8")], 0, 0, 1, 0)}"/>'
    o += f'<path d="M{cx + 160} {top}V{bot + 70}" stroke="#fff" stroke-opacity=".45" stroke-width="5"/>'
    cv.add(o)


# ---------------------------------------------------------------- VIDEOS (a clapperboard with a lit play mark)
def videos(cv):
    container(cv, "#3E8FB4", "#0B2C46", glow="#CDEBFF", edge="#020E1A", glow_op=.30)
    sh = "#020E1A"
    L, T, R, B = 262, 396, 762, 766
    slate = rrect(L, T, R - L, B - T, 40)
    o = solid(cv, slate, "#3C4258", "#141826", shade=sh, edge="#000", lip=6, amb=(34, 24, .62))
    # the stick: hinged on the left, lifted a little, black and ivory bands
    ang = -14
    stick = rrect(L, T - 104, R - L, 86, 22)
    s = shadow(cv, stick, 14, 10, sh, .55)
    s += f'<path d="{stick}" fill="{cv.lin(IVORY)}"/>'
    clip = cv.clip(stick)
    s += f'<g clip-path="{clip}">' + "".join(
        f'<path d="M{x} {T - 104}H{x + 58}L{x + 18} {T - 18}H{x - 40}Z" fill="#1B1F30"/>' for x in range(L + 30, R + 40, 116)) + "</g>"
    s += rimlight(cv, stick, 4, .9)
    o += f'<g transform="rotate({ang} {L + 20} {T - 14})">{s}</g>'
    # the lower band on the slate, the same stripes
    band = rrect(L, T, R - L, 70, 22)
    o += f'<g clip-path="{cv.clip(slate)}"><path d="{band}" fill="{cv.lin(IVORY)}"/>' + "".join(
        f'<path d="M{x} {T}H{x + 58}L{x + 18} {T + 70}H{x - 40}Z" fill="#1B1F30"/>' for x in range(L + 30, R + 40, 116)) + "</g>"
    o += f'<rect x="{L}" y="{T + 70}" width="{R - L}" height="6" fill="#000" opacity=".35"/>'
    o += knob(cv, L + 26, T - 14, 22, "#FFFFFF", "#C9CFDC", "#6D7690", sh, 6)
    # the play mark: lit from inside (bloom, gold, pale core)
    px = 462
    p = f"M{px} 522L{px + 126} 600L{px} 678Z"
    o += f'<path d="{p}" fill="#FFC94A" opacity=".55" filter="{cv.blur(26)}" stroke="#FFC94A" stroke-width="40" stroke-linejoin="round"/>'
    o += f'<path d="{p}" fill="{cv.lin([(0, "#FFF6C8"), (1, "#F0A81E")])}" stroke="{cv.lin([(0, "#FFF6C8"), (1, "#F0A81E")])}" stroke-width="26" stroke-linejoin="round"/>'
    o += f'<path d="M{px + 10} 556L{px + 70} 594" stroke="#fff" stroke-opacity=".75" stroke-width="8" stroke-linecap="round"/>'
    # chalk lines either side
    for y in (712, 738):
        o += f'<rect x="{L + 40}" y="{y - 6}" width="{120 if y == 712 else 80}" height="10" rx="5" fill="#C9D3EA" opacity=".55"/>'
    cv.add(o)


# ---------------------------------------------------------------- ARCHIVE (a banded cedar crate)
def archive(cv):
    container(cv, "#6E69AC", "#1C1842", glow="#DCD8FF", edge="#0A0824", glow_op=.30)
    sh = "#0E0B2A"
    L, T, R, B = 258, 316, 766, 762
    lid = rrect(L - 14, T, R - L + 28, 110, 26)
    box = rrect(L, T + 80, R - L, B - T - 80, 30)
    o = shadows(cv, box, sh, (34, 24, .6), (10, 8, .45))
    o += f'<path d="{box}" fill="{cv.lin([(0, "#F0B87A"), (1, "#9A5A2C")])}"/>'
    # planks: three horizontal boards with dark joints and a lit top edge each
    clip = cv.clip(box)
    o += f'<g clip-path="{clip}">'
    for i, y in enumerate((T + 196, T + 316)):
        o += f'<rect x="{L}" y="{y}" width="{R - L}" height="8" fill="#3A1C08" opacity=".55"/><rect x="{L}" y="{y + 8}" width="{R - L}" height="4" fill="#FFE2B8" opacity=".35"/>'
    for i in range(14):   # grain
        y = T + 120 + i * 24
        o += f'<path d="M{L} {y}Q{L + 160} {y + (i % 3 - 1) * 8} {L + 300} {y + 4}T{R} {y}" fill="none" stroke="#6A3410" stroke-opacity=".16" stroke-width="3"/>'
    o += f'<path d="{box}" fill="{cv.lin([(.6, "#000", 0), (1, "#000", .22)])}"/></g>'
    o += rimlight(cv, box, 5, .5)
    # two steel bands over the planks
    for x in (L + 104, R - 150):
        bd = rrect(x, T + 80, 46, B - T - 80, 6)
        o += shadow(cv, bd, 6, 4, sh, .45, dx=0) + f'<path d="{bd}" fill="{cv.lin(METAL, 0, 0, 1, 0)}"/>'
        for y in (T + 150, B - 50):
            o += f'<circle cx="{x + 23}" cy="{y}" r="9" fill="{cv.rad([(0, "#FFFFFF"), (1, "#6D7690")], .35, .3, .8)}"/>'
    # the lid, overhanging, lit along its top
    o += shadow(cv, lid, 16, 10, sh, .55)
    o += f'<path d="{lid}" fill="{cv.lin([(0, "#EDB57A"), (1, "#9A5A2A")])}"/>' + rimlight(cv, lid, 5, .85)
    o += f'<path d="{lid}" fill="none" stroke="{sh}" stroke-opacity=".35" stroke-width="3"/>'
    for x in (L + 104, R - 150):
        o += f'<rect x="{x}" y="{T}" width="46" height="110" fill="{cv.lin(METAL, 0, 0, 1, 0)}"/>'
    # a brass hasp in the middle (the pop)
    hp = rrect(512 - 44, T + 64, 88, 120, 22)
    o += shadow(cv, hp, 10, 6, sh, .55) + f'<path d="{hp}" fill="{cv.lin(BRASS, 0, 0, 1, 1)}"/>' + rimlight(cv, hp, 4, .9)
    o += f'<path d="M512 {T + 120}a16 16 0 0 1 8 30l6 24h-28l6 -24a16 16 0 0 1 8 -30z" fill="#4A2A00"/>'
    cv.add(o)


# ---------------------------------------------------------------- DISK USAGE (an enamel ring chart)
def disk_usage(cv):
    container(cv, "#F6E2B6", "#C79A52", glow="#FFFFFF", edge="#4A2E08", glow_op=.40)
    sh = "#4A2E08"
    cx, cy = 512, 520
    disc = circ(cx, cy, 262)
    o = shadows(cv, disc, sh, (34, 24, .55), (10, 8, .42))
    o += f'<path d="{disc}" fill="{cv.lin([(0, "#FFFFFF"), (1, "#D9CDB8")])}"/>' + rimlight(cv, disc, 6, .9)
    o += f'<path d="{disc}" fill="none" stroke="{sh}" stroke-opacity=".3" stroke-width="3"/>'

    def arc(r0, r1, a0, a1):
        p = lambda r, a: (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
        (x0, y0), (x1, y1), (x2, y2), (x3, y3) = p(r1, a0), p(r1, a1), p(r0, a1), p(r0, a0)
        big = 1 if a1 - a0 > 180 else 0
        return (f"M{x0:.1f} {y0:.1f}A{r1} {r1} 0 {big} 1 {x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}"
                f"A{r0} {r0} 0 {big} 0 {x3:.1f} {y3:.1f}Z")
    inner = ((-90, 60, "#8C7CFF", "#3B20B8"), (64, 170, "#4FC3E8", "#1468A8"), (174, 226, "#FF8A6A", "#C2361E"))
    outer = ((-90, -20, "#B9A8FF", "#5B3CE0"), (-16, 40, "#9B85FF", "#4A2EC8"), (64, 130, "#8CDCF5", "#2A8AC8"),
             (174, 200, "#FFB39A", "#E0582E"))
    for r0, r1, segs in ((92, 170, inner), (176, 236, outer)):
        for a0, a1, c0, c1 in segs:
            d = arc(r0, r1, a0 + 1.5, a1 - 1.5)
            o += shadow(cv, d, 8, 5, sh, .45)
            o += f'<path d="{d}" fill="{cv.lin([(0, c0), (1, c1)])}"/>'
            o += f'<path d="{d}" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="3"/>'
    # the free part: an empty groove
    o += f'<path d="{arc(92, 236, 232, 268)}" fill="#000" opacity=".06"/>'
    # the hub: brass (the pop)
    o += knob(cv, cx, cy, 62, "#FFF3C0", "#F0B13C", "#8A5A12", sh, 10)
    o += f'<circle cx="{cx}" cy="{cy}" r="18" fill="#5A3A00"/>'
    o += f'<path d="M{cx - 196} {cy - 120}A232 232 0 0 1 {cx - 40} {cy - 228}" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width="10" stroke-linecap="round"/>'
    cv.add(o)


# ---------------------------------------------------------------- ATLAS (the browser: a folded paper map, you are here)
# Direction B "Folio" of brand/atlas (directions/README.md), redrawn as an object: a map folded in
# three (a Z-fold, the near creases tall, the far one short), matte paper, the middle panel turned
# away from the light. The pop is the gold "you are here" mark, lit from inside; at full size a
# short gold route leads to it. The small drawing keeps the fold, the light/dark split and the mark.
ATLAS_X = (200, 408, 616, 824)          # the four edges of the three panels, left to right
ATLAS_TOP = (282, 210, 282, 210)        # near edges (408, 824) stand taller than the far ones
ATLAS_BOT = (746, 830, 746, 830)


def _atlas_panel(i):
    """Corners of panel i (0..2): top-left, top-right, bottom-right, bottom-left."""
    x0, x1 = ATLAS_X[i], ATLAS_X[i + 1]
    return ((x0, ATLAS_TOP[i]), (x1, ATLAS_TOP[i + 1]), (x1, ATLAS_BOT[i + 1]), (x0, ATLAS_BOT[i]))


def _atlas_at(i, u, v):
    """The point (u across, v down, both 0..1) on panel i: bilinear, so printing follows the fold."""
    (ax, ay), (bx, by), (cx_, cy_), (dx, dy) = _atlas_panel(i)
    tx, ty = ax + (bx - ax) * u, ay + (by - ay) * u
    bx_, by_ = dx + (cx_ - dx) * u, dy + (cy_ - dy) * u
    return (tx + (bx_ - tx) * v, ty + (by_ - ty) * v)


def atlas(cv):
    container(cv, "#3C8DDF", "#123F75", glow="#D6EAFF", edge="#04203F", glow_op=.30)
    sh = "#04203F"
    small = cv.small
    panels = [_atlas_panel(i) for i in range(3)]
    sheet = poly([(ATLAS_X[k], ATLAS_TOP[k]) for k in range(4)] + [(ATLAS_X[k], ATLAS_BOT[k]) for k in (3, 2, 1, 0)])
    # the whole sheet casts one shadow in the card's own darkest tone, and shows its thickness below
    o = shadows(cv, sheet, sh, (32, 24, .6), (10, 8, .46))
    o += f'<path d="{sheet}" fill="#8E7350" transform="translate(0 9)"/>'
    # paper: the two panels that face the light, the middle one turned away (the gem's 95/58 split)
    lit = cv.lin([(0, "#FFFBF2"), (.6, "#F6EBD6"), (1, "#E4CFAD")])
    shade = cv.lin([(0, "#D6C3A2"), (1, "#AE9369")])
    for i, p in enumerate(panels):
        d = poly(p)
        o += f'<path d="{d}" fill="{shade if i == 1 else lit}"/>'
    # printing: the sea in the web blue (both drawings); a river, two roads and the blocks of a town
    # (full drawing only: under 25 units they do not survive 48 px)
    for i in range(3):
        clip = cv.clip(poly(panels[i]))
        coast = [_atlas_at(i, u, .62 + .05 * math.sin(u * 5.0 + i * 2.4)) for u in (0, .2, .4, .6, .8, 1)]
        sea = smooth(coast, closed=False) + "".join(f"L{x:.1f} {y:.1f}" for x, y in (_atlas_at(i, 1, 1), _atlas_at(i, 0, 1))) + "Z"
        pr = f'<path d="{sea}" fill="#7DB4E6" opacity="{.36 if i == 1 else .46}"/>'
        if not small:
            pr += f'<path d="{smooth(coast, closed=False)}" fill="none" stroke="#5E9BD6" stroke-opacity=".55" stroke-width="5"/>'
            for k, (v0, op) in enumerate(((.12, .5), (.30, .42))):
                road = [_atlas_at(i, u, v0 + .05 * math.sin(u * 3.1 + k + i * 2.1)) for u in (0, .25, .5, .75, 1)]
                pr += f'<path d="{smooth(road, closed=False)}" fill="none" stroke="#9A7A52" stroke-opacity="{op}" stroke-width="8" stroke-linecap="round"/>'
            river = [_atlas_at(i, u, .44 + .07 * math.sin(u * 4.2 + i * 1.7)) for u in (0, .25, .5, .75, 1)]
            pr += f'<path d="{smooth(river, closed=False)}" fill="none" stroke="#5E9BD6" stroke-opacity=".7" stroke-width="11" stroke-linecap="round"/>'
            if i != 1:
                for u, v in ((.22, .2), (.42, .24), (.62, .19)):
                    a, b = _atlas_at(i, u, v), _atlas_at(i, u + .14, v + .05)
                    pr += f'<path d="{poly([a, (b[0], a[1] + (b[1] - a[1]) * .3), b, (a[0], b[1])])}" fill="#B89A72" opacity=".38"/>'
        o += f'<g clip-path="{clip}">{pr}</g>'
    # light on the folds: the near creases catch the light, the far one sits in occlusion
    for i in range(3):
        d = poly(panels[i])
        if i == 1:      # turned away: deepest at the valley (x 616), a little lighter by the ridge
            g = cv.lin([(0, "#000", .04), (.75, "#000", .10), (1, "#000", .22)], 0, 0, 1, 0)
        else:           # facing the light: occlusion at the valley side (left of panel 2), bright at the ridge
            g = cv.lin([(0, "#000", .16 if i == 2 else .05), (.3, "#000", 0), (1, "#fff", .18)], 0, 0, 1, 0)
        o += f'<path d="{d}" fill="{g}"/>'
        o += f'<path d="{d}" fill="{cv.lin([(.5, "#3A2400", 0), (1, "#3A2400", .16)])}"/>'
        o += rimlight(cv, d, 5, .85)
    for k in (1, 3):    # a lit line on each near crease and on the right edge
        x = ATLAS_X[k]
        o += f'<path d="M{x - 3} {ATLAS_TOP[k] + 4}V{ATLAS_BOT[k] - 4}" stroke="#fff" stroke-opacity=".7" stroke-width="5"/>'
    o += f'<path d="{sheet}" fill="none" stroke="{sh}" stroke-opacity=".35" stroke-width="3" stroke-linejoin="round"/>'
    # the route (full drawing only): gold dots growing towards the mark
    mx, my = _atlas_at(1, .5, .52)
    if not small:
        for k, (u, v) in enumerate(((.30, .86), (.52, .80), (.74, .75), (.94, .69))):
            x, y = _atlas_at(0, u, v)
            o += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{9 + k * 3}" fill="#F0A81E" opacity="{.70 + k * .08:.2f}"/>'
            o += f'<circle cx="{x:.1f}" cy="{y - 1.5:.1f}" r="{9 + k * 3}" fill="none" stroke="#5A3A00" stroke-opacity=".35" stroke-width="2"/>'
    # you are here: a bloom, a dark ring that holds it off the paper, the gold, a pale core
    r = 92 if small else 66
    ring = 14 if small else 9
    o += f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="{r + 30}" fill="#FFC94A" opacity=".55" filter="{cv.blur(18)}"/>'
    o += shadow(cv, circ(mx, my, r + ring), 10, 8, sh, .5)
    o += f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="{r + ring}" fill="{cv.lin([(0, "#2A4E7E"), (1, "#0B2648")])}"/>'
    o += f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="{r}" fill="{cv.rad([(0, "#FFF6C8"), (.45, "#FFC94A"), (1, "#F0A81E")], .4, .34, .8)}"/>'
    o += f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="{r * .36:.1f}" fill="#FFFBE8"/>'
    if not small:
        o += ellipse_spec(cv, mx - r * .42, my - r * .5, r * .26, r * .12, -32, .75)
    cv.add(o)
