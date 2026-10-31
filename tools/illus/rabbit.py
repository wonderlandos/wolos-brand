# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2026 Julia Klee
"""The White Rabbit: late, delighted about it, a little mad."""
import math
from kit import f, path, sample, fluffy, volume, band, fur, KEY, ellipse_pts
from parts import eye, crescent, BRASS, glow, ground, chain_links

DETAIL = 1.0   # fur-stroke density; scenes that show him small lower it to keep files light
FUR = [(0, "#FFFFFF"), (0.55, "#F7F3FC"), (1, "#D9CFF0")]
SHADE = ("#7C68C4", .42, 16, 11)     # cool violet form shadow
DEEP = ("#4B3A8C", .30, 6, 4)        # contact shadow, tighter
HI = ("#FFF7E8", .9, 10, 7)          # warm key
RIM = ("#B9A6FF", .9, 3.2, 1.6)      # violet rim


def furry(cv, pts, ranges, seed, flow, n=120, amp=6, step=8, shade=SHADE, rim=RIM, extra="", fill=None,
          hi=HI, hairs=True, sole=0, aos=()):
    d, poly = fluffy(pts, ranges, amp=amp, step=step, seed=seed)
    if sole:   # darker underside: the floor bounces less light than the sky
        extra += band(cv, d, poly, (0, 1), sole, sole * .6, "#4B3A8C", .45)
    for dr, dist, bl, col, op in aos:   # contact shadows where other parts press against this one
        extra += band(cv, d, poly, dr, dist, bl, col, op)
    x0 = min(p[0] for p in poly)
    y0 = min(p[1] for p in poly)
    x1 = max(p[0] for p in poly)
    y1 = max(p[1] for p in poly)
    fill = fill or cv.lin(x0, y0, x1 * .3 + x0 * .7 + (x1 - x0) * .4, y1, FUR)
    tex = ""
    if hairs:
        tex = fur(cv, poly, int(n * DETAIL), flow, (5, 11), .8, ("#ffffff", "#D3C8F0", "#EDE6FA"), (.15, .5), seed)
    return volume(cv, d, poly, fill, shade=shade, hi=hi, rim=rim, extra=extra + tex), d, poly


def down(cx, cy, spread=0.6):
    def flow(x, y):
        return math.atan2(y - cy, (x - cx) * spread) if (x, y) != (cx, cy) else 1.57
    return flow


def watch(cv, cx, cy, r):
    """The pocket watch held up: brass case, enamel dial, violet hands at 'late'."""
    g = ""
    case = cv.rad(cx - r * .35, cy - r * .4, r * 1.25, BRASS, cx - r * .5, cy - r * .55)
    # bow and crown
    g += (f'<ellipse cx="{f(cx)}" cy="{f(cy - r - 9)}" rx="{f(r * .26)}" ry="{f(r * .2)}" fill="none" '
          f'stroke="{cv.lin(cx - r * .3, 0, cx + r * .3, 0, BRASS)}" stroke-width="{f(r * .09)}"/>')
    g += (f'<rect x="{f(cx - r * .12)}" y="{f(cy - r - 6)}" width="{f(r * .24)}" height="{f(r * .22)}" rx="2" '
          f'fill="{cv.lin(cx - r * .12, 0, cx + r * .12, 0, BRASS)}"/>')
    # drop shadow of the watch on the chest
    g += (f'<circle cx="{f(cx + 7)}" cy="{f(cy + 9)}" r="{f(r)}" fill="#2B1B66" opacity=".35" '
          f'filter="{cv.blur(6)}"/>')
    g += f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{case}"/>'
    # knurled bezel
    ticks = ""
    for k in range(72):
        a = 2 * math.pi * k / 72
        ticks += (f"M{f(cx + math.cos(a) * r * .9)} {f(cy + math.sin(a) * r * .9)}"
                  f"L{f(cx + math.cos(a) * r * .99)} {f(cy + math.sin(a) * r * .99)}")
    g += f'<path d="{ticks}" stroke="#7A4E12" stroke-width="1" opacity=".45"/>'
    g += (f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r * .86)}" fill="none" '
          f'stroke="{cv.lin(cx, cy - r, cx, cy + r, [(0, "#8A5A16"), (1, "#FFF1BF")])}" stroke-width="{f(r * .06)}"/>')
    dial = cv.rad(cx - r * .3, cy - r * .35, r * 1.1, [(0, "#FFFFFF"), (0.6, "#FBF6EC"), (1, "#E2D6C2")])
    g += f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r * .82)}" fill="{dial}"/>'
    # inner dial shadow (the bezel overhang)
    dd = f"M{f(cx - r * .82)} {f(cy)}a{f(r * .82)} {f(r * .82)} 0 1 0 {f(r * 1.64)} 0a{f(r * .82)} {f(r * .82)} 0 1 0 {f(-r * 1.64)} 0Z"
    c = cv.clip(dd)
    g += (f'<g clip-path="{c}">'
          + band(cv, dd, [(cx - r, cy - r), (cx + r, cy + r)], (-.5, -.85), r * .12, r * .06, "#6B5330", .45)
          + "</g>")
    # minute track + numerals as bold strokes
    tr = ""
    for k in range(60):
        a = 2 * math.pi * k / 60 - math.pi / 2
        r0 = r * (.62 if k % 5 == 0 else .7)
        tr += (f"M{f(cx + math.cos(a) * r0)} {f(cy + math.sin(a) * r0)}"
               f"L{f(cx + math.cos(a) * r * .74)} {f(cy + math.sin(a) * r * .74)}")
    g += f'<path d="{tr}" stroke="#3A2A55" stroke-width="{f(r * .025)}" stroke-linecap="round"/>'
    for k in range(12):
        a = 2 * math.pi * k / 12 - math.pi / 2
        g += (f'<circle cx="{f(cx + math.cos(a) * r * .55)}" cy="{f(cy + math.sin(a) * r * .55)}" '
              f'r="{f(r * (.05 if k % 3 == 0 else .028))}" fill="#3A2A55"/>')
    # hands: five to twelve, of course
    def hand(ang, L, w, col):
        a = math.radians(ang - 90)
        tx, ty = cx + math.cos(a) * L, cy + math.sin(a) * L
        nx, ny = -math.sin(a) * w, math.cos(a) * w
        bx, by = cx - math.cos(a) * L * .18, cy - math.sin(a) * L * .18
        return (f'<path d="M{f(bx + nx)} {f(by + ny)}L{f(tx)} {f(ty)}L{f(bx - nx)} {f(by - ny)}Z" fill="{col}"/>')
    g += f'<g filter="{cv.blur(1.2)}" opacity=".35" transform="translate(2 3)">' + hand(-30, r * .62, r * .05, "#000") + hand(-5, r * .44, r * .07, "#000") + "</g>"
    g += hand(-30, r * .62, r * .05, "#5B3BE8") + hand(-5, r * .44, r * .07, "#2E1A80")
    g += f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r * .07)}" fill="{cv.lin(cx - 4, cy - 4, cx + 4, cy + 4, BRASS)}"/>'
    # crystal reflections
    g += (f'<path d="{crescent(cx, cy, r * .74, r * .74, 195, 265, r * .16)}" fill="#fff" opacity=".55" '
          f'filter="{cv.blur(1)}"/>')
    g += (f'<path d="{crescent(cx, cy, r * .74, r * .74, 20, 60, r * .06)}" fill="#fff" opacity=".5"/>')
    g += (f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r * .995)}" fill="none" stroke="#5A3A0E" '
          f'stroke-width="1.2" opacity=".6"/>')
    return g


def wrinkle(cv, d):
    return (f'<path d="{d}" stroke="#1E0E5C" stroke-width="4" fill="none" opacity=".35" stroke-linecap="round" '
            f'filter="{cv.blur(2)}"/><path d="{d}" stroke="#C9B8FF" stroke-width="1.2" fill="none" opacity=".45" '
            f'stroke-linecap="round" transform="translate(-1.5 -1.5)"/>')


def toes(cv, spots):
    """Toe creases: a soft shadow groove with a lit lip beside it."""
    g = ""
    for x, y, k in spots:
        d = f"M{x} {y}q{-4 * k} 9 {-2 * k} 20"
        g += (f'<path d="{d}" stroke="#6C58B4" stroke-width="3" fill="none" opacity=".35" filter="{cv.blur(1.2)}"/>'
              f'<path d="{d}" stroke="#8C7AC8" stroke-width="1.1" fill="none" opacity=".7" stroke-linecap="round"/>'
              f'<path d="{d}" stroke="#fff" stroke-width="1" fill="none" opacity=".9" transform="translate({-1.6 * k} 0)"/>')
    return g


def rabbit(cv, shadow=True, arms=True):
    g = ""
    if shadow:
        g += ground(cv, 262, 492, 150, 15, .32)

    # ---- far ear (bent over: a little mad)
    far_ear = [(262, 142), (264, 104), (274, 72), (292, 46), (316, 34), (342, 40), (362, 58), (374, 84),
               (376, 108), (366, 116), (352, 100), (334, 78), (314, 70), (302, 82), (298, 106), (298, 142)]
    s, d, poly = furry(cv, far_ear, [(0.12, 0.42, .5)], 11, down(320, 30, 1), 60, amp=3, step=11)
    inner = [(274, 132), (276, 104), (284, 80), (296, 62), (306, 58), (304, 72), (296, 90), (292, 112), (290, 134)]
    ip = sample(inner)
    ifill = cv.lin(280, 60, 296, 135, [(0, "#F9C9D6"), (0.6, "#F29BB5"), (1, "#E07A9C")])
    s_in = volume(cv, path(inner), ip, ifill, shade=("#B5507A", .45, 6, 4), hi=("#FFE6EE", .7, 4, 3))
    # the fold: a shadow where the ear creases over
    fold = (f'<path d="M292 50Q300 64 302 80" stroke="#6C58B4" stroke-width="5" fill="none" opacity=".35" '
            f'filter="{cv.blur(2.5)}"/><path d="M294 52Q301 64 303 78" stroke="#fff" stroke-width="1.2" fill="none" opacity=".8"/>')
    g += f'<g>{s}{s_in}{fold}</g>'

    # ---- near ear, tall, leaning out
    near_ear = [(200, 152), (186, 112), (174, 72), (168, 38), (174, 14), (192, 6), (210, 18), (224, 48),
                (236, 88), (244, 128), (240, 152)]
    s, d, poly = furry(cv, near_ear, [(0.6, 0.88, .5)], 12, down(190, 0, 1), 70, amp=3, step=11)
    inner = [(206, 136), (196, 104), (187, 70), (184, 40), (190, 22), (200, 26), (210, 52), (220, 88), (228, 128)]
    ip = sample(inner)
    ifill = cv.lin(190, 20, 222, 136, [(0, "#FAD0DB"), (0.55, "#F3A0B9"), (1, "#E07A9C")])
    veins = (f'<path d="M204 120Q198 90 194 50M212 118Q210 92 202 60" stroke="#D86C90" stroke-width="1" fill="none" '
             f'opacity=".35"/>')
    sss = f'<ellipse cx="200" cy="58" rx="9" ry="26" fill="#FFE3EA" opacity=".7" filter="{cv.blur(5)}"/>'
    s_in = volume(cv, path(inner), ip, ifill, shade=("#B5507A", .5, 7, 4), hi=("#FFE6EE", .6, 4, 3),
                  extra=sss + veins)
    g += f'<g>{s}{s_in}</g>'

    # ---- tail
    tail = ellipse_pts(346, 432, 22, 20, 10)
    s, d, poly = furry(cv, tail, [(0.1, 0.6, .7)], 21, lambda x, y: math.atan2(y - 432, x - 346), 30, amp=3, step=10)
    g += s

    # ---- far leg and foot
    thigh2 = ellipse_pts(318, 428, 40, 44, 10)
    s, d, poly = furry(cv, thigh2, [(0.12, 0.32, .6)], 22, down(318, 380), 40, amp=2.5)
    g += s
    foot2 = [(288, 476), (298, 462), (328, 456), (364, 460), (386, 470), (384, 484), (356, 492), (308, 492)]
    s, d, poly = furry(cv, foot2, [(0.05, 0.3, .5)], 23, lambda x, y: 0.1, 30, amp=2.5,
                       shade=("#6C58B4", .45, 9, 6), sole=7)
    g += f'<g transform="rotate(-9 300 486)">{s}{toes(cv, [(372, 468, 1), (360, 464, 1)])}</g>'

    # ---- torso
    torso = [(214, 262), (252, 256), (292, 262), (318, 286), (334, 330), (342, 380), (338, 420), (320, 446),
             (290, 458), (252, 462), (214, 458), (186, 444), (170, 416), (168, 376), (176, 330), (190, 288)]
    tp = sample(torso, per=12)
    tfill = cv.lin(190, 270, 320, 450, FUR)
    vest = [(150, 280, 0), (222, 266, 0), (252, 338, 0), (282, 266, 0), (370, 280, 0), (370, 410, 0),
            (310, 428), (272, 448, 0), (254, 430, 0), (236, 448, 0), (200, 430), (150, 410, 0)]
    vd = path(vest, t=0.6)
    vp = sample(vest, per=8, t=0.6)
    vfill = cv.lin(180, 270, 330, 440, [(0, "#9D85FF"), (0.45, "#7C5CFF"), (1, "#4A2FC0")])
    damask = cv.pattern(14, 14, '<path d="M7 1.5L12.5 7 7 12.5 1.5 7Z" fill="none" stroke="#fff" stroke-width=".7" opacity=".16"/>'
                        '<circle cx="7" cy="7" r="1" fill="#fff" opacity=".18"/>', "rotate(0)")
    vc = cv.clip(vd)
    vest_inner = (f'<rect x="140" y="250" width="240" height="210" fill="{damask}"/>'
                  # the belly is round: a broad soft sheen and darker flanks
                  + f'<ellipse cx="236" cy="350" rx="46" ry="62" fill="#B8A4FF" opacity=".45" filter="{cv.blur(18)}"/>'
                  + f'<ellipse cx="338" cy="380" rx="26" ry="80" fill="#1E0E5C" opacity=".35" filter="{cv.blur(14)}"/>'
                  # wrinkles pulled from the armholes and the buttons
                  + wrinkle(cv, "M200 300q16 10 20 30") + wrinkle(cv, "M312 300q-14 14 -20 34")
                  + wrinkle(cv, "M262 360q16 -2 28 -12") + wrinkle(cv, "M262 392q18 0 32 -10")
                  + wrinkle(cv, "M252 400q-16 2 -26 -8")
                  + band(cv, vd, vp, (-KEY[0], -KEY[1]), 18, 12, "#1E0E5C", .55)
                  + band(cv, vd, vp, KEY, 8, 6, "#C9B8FF", .5)
                  + band(cv, path(torso), tp, (0.85, -0.25), 4, 2.5, "#C9B8FF", .8)
                  # lapel edge highlight and the darker inside of the V
                  + '<path d="M222 266L252 338L282 266" fill="none" stroke="#2A1670" stroke-width="7" opacity=".5" '
                  + f'filter="{cv.blur(3)}"/>'
                  + '<path d="M222 268L252 336L282 268" fill="none" stroke="#C7B6FF" stroke-width="1.3" opacity=".9"/>'
                  # seam down the front
                  + '<path d="M254 338V430" stroke="#2A1670" stroke-width="1.6" opacity=".6"/>'
                  # welt pocket
                  + '<path d="M290 372l34 -4" stroke="#2A1670" stroke-width="5" stroke-linecap="round" opacity=".7"/>'
                  + '<path d="M291 375l33 -4" stroke="#B9A6FF" stroke-width="1.1" stroke-linecap="round" opacity=".8"/>'
                  + '<path d="M196 384l30 2" stroke="#2A1670" stroke-width="5" stroke-linecap="round" opacity=".6"/>'
                  + '<path d="M197 387l29 2" stroke="#B9A6FF" stroke-width="1.1" stroke-linecap="round" opacity=".7"/>'
                  # piping and topstitch along every edge
                  + f'<path d="{vd}" fill="none" stroke="#2A1670" stroke-width="5" opacity=".45"/>'
                  + f'<path d="{vd}" fill="none" stroke="#B9A6FF" stroke-width="2.4" opacity=".75"/>'
                  + f'<path d="{vd}" fill="none" stroke="#E2D8FF" stroke-width="1" stroke-dasharray="2.5 3" opacity=".5" '
                  + 'transform="scale(.985) translate(3.8 4.5)"/>')
    buttons = ""
    for by in (354, 382, 410):
        buttons += (f'<circle cx="259" cy="{by + 2}" r="6" fill="#1E0E5C" opacity=".5" filter="{cv.blur(1.5)}"/>'
                    f'<circle cx="258" cy="{by}" r="5.4" fill="{cv.rad(256, by - 2, 7, BRASS, 255, by - 3)}"/>'
                    f'<circle cx="258" cy="{by}" r="2.6" fill="none" stroke="#7A4E12" stroke-width=".8" opacity=".6"/>'
                    f'<circle cx="256.4" cy="{by - 1.8}" r="1.3" fill="#fff" opacity=".9"/>')
    belly = fur(cv, tp, int(120 * DETAIL), down(252, 250, .9), (5, 10), .8, ("#ffffff", "#D3C8F0"), (.15, .45), 31)
    torso_extra = (belly
                   + f'<path d="{vd}" fill="#1E0E5C" opacity=".35" transform="translate(4 6)" filter="{cv.blur(5)}"/>'
                   + f'<path d="{vd}" fill="{vfill}"/><g clip-path="{vc}">{vest_inner}</g>{buttons}'
                   # head's shadow on the chest
                   + f'<ellipse cx="258" cy="268" rx="72" ry="18" fill="#3B2A86" opacity=".35" filter="{cv.blur(8)}"/>')
    g += volume(cv, path(torso), tp, tfill, shade=SHADE, hi=HI, rim=RIM, extra=torso_extra)

    # ---- collar + bow tie
    collar = (f'<path d="M222 262Q236 286 250 282L246 268Z" fill="#fff"/><path d="M282 262Q268 286 254 282L258 268Z" fill="#fff"/>'
              f'<path d="M222 262Q236 286 250 282" fill="none" stroke="#B7A8E0" stroke-width="1.4"/>'
              f'<path d="M282 262Q268 286 254 282" fill="none" stroke="#B7A8E0" stroke-width="1.4"/>')
    bt = cv.lin(230, 270, 270, 300, [(0, "#C2456B"), (0.5, "#9E2650"), (1, "#5E1030")])
    bow = (f'<g filter="{cv.blur(2.5)}" opacity=".4" transform="translate(3 4)"><path d="M252 284L226 270Q220 284 226 300Z M252 284L278 270Q284 284 278 300Z" fill="#1E0E5C"/></g>'
           f'<path d="M252 284L226 270Q218 285 226 300Z" fill="{bt}"/><path d="M252 284L278 270Q286 285 278 300Z" fill="{bt}"/>'
           f'<path d="M232 276Q229 285 232 294M272 276Q275 285 272 294" stroke="#5E1030" stroke-width="1.2" fill="none" opacity=".6"/>'
           f'<path d="M227 273Q224 280 225 286" stroke="#F5A3BD" stroke-width="1.4" fill="none" opacity=".8"/>'
           f'<rect x="245" y="277" width="14" height="15" rx="4" fill="{cv.lin(245, 277, 259, 292, [(0, "#D45A80"), (1, "#7A1840")])}"/>'
           f'<path d="M248 280h6" stroke="#FFC2D4" stroke-width="1.2" stroke-linecap="round" opacity=".8"/>')
    g += collar + bow

    # ---- near leg and foot (in front)
    g += f'<ellipse cx="214" cy="440" rx="50" ry="40" fill="#2B1B66" opacity=".35" transform="translate(8 4)" filter="{cv.blur(9)}"/>'
    thigh = [(170, 400), (204, 384), (236, 396), (248, 430), (238, 462), (204, 470), (174, 456), (164, 428)]
    s, d, poly = furry(cv, thigh, [(0.5, 0.95, .7)], 41, down(205, 380), 50, amp=3.5,
                       aos=(((0.3, -1), 10, 6, "#3B2A86", .5),))
    g += s
    foot = [(138, 486), (142, 470), (162, 460), (206, 460), (238, 468), (250, 482), (236, 494), (176, 498)]
    s, d, poly = furry(cv, foot, [(0.3, 0.55, .6)], 42, lambda x, y: 3.0, 30, amp=3, shade=("#6C58B4", .45, 9, 6),
                       sole=7)
    g += s + toes(cv, [(152, 470, -1), (166, 465, -1)])

    # ---- head
    head = [(252, 112), (290, 116), (322, 134), (340, 164), (344, 198), (338, 228), (322, 252), (298, 268),
            (268, 275), (236, 275), (206, 268), (182, 252), (166, 228), (160, 198), (164, 164), (182, 134),
            (214, 116)]
    hd, hp = fluffy(head, [(0.3, 0.46, 1.0), (0.54, 0.72, 1.0), (0.97, 0.03, .8)], amp=7, step=8, seed=51)
    hfill = cv.lin(190, 120, 320, 280, FUR)
    face = ""
    # cheek blush
    face += f'<ellipse cx="196" cy="236" rx="22" ry="13" fill="#FF8FB1" opacity=".38" filter="{cv.blur(6)}"/>'
    face += f'<ellipse cx="312" cy="234" rx="20" ry="12" fill="#FF8FB1" opacity=".3" filter="{cv.blur(6)}"/>'
    hfur = fur(cv, hp, int(140 * DETAIL), down(252, 150, .8), (4, 9), .8, ("#ffffff", "#D3C8F0"), (.15, .45), 52)
    hvol = volume(cv, hd, hp, hfill, shade=SHADE, hi=HI, rim=RIM, extra=hfur + face)
    # cowlick tufts on top (mad hair)
    tufts = [(232, 124), (236, 104, 0), (244, 112), (250, 90, 0), (258, 108), (270, 92, 0), (272, 110),
             (284, 104, 0), (280, 124)]
    tvol = volume(cv, path(tufts, t=.8), sample(tufts, t=.8), cv.lin(240, 90, 270, 125, FUR),
                  shade=("#7C68C4", .25, 6, 4), hi=HI, rim=("#B9A6FF", .6, 2, 1))
    fw = ""
    # eyes: one a touch bigger than the other
    fw += eye(cv, 218, 190, 25, 30, look=(.15, .05), rot=-6, pupil_k=.4)
    fw += eye(cv, 287, 187, 28, 33, look=(-.05, .02), rot=8, lashes=3, pupil_k=.52)
    # brows, raised: fur tufts
    fw += f'<path d="{crescent(214, 160, 26, 14, 200, 320, 6, -12)}" fill="#C9BCEB"/>'
    fw += f'<path d="{crescent(292, 150, 28, 16, 210, 335, 6.5, 14)}" fill="#C9BCEB"/>'
    # muzzle
    mz = ""
    for cx, rx in ((240, 19), (265, 19)):
        mzp = ellipse_pts(cx, 236, rx, 15, 10)
        mz += volume(cv, path(mzp), sample(mzp), cv.rad(cx - 4, 228, 22, [(0, "#FFFFFF"), (1, "#F1EAFA")]),
                     shade=("#8C78CC", .35, 6, 4), hi=None)
    dots = ""
    for x, y in ((232, 234), (226, 240), (236, 242), (270, 234), (276, 240), (266, 242)):
        dots += f'<circle cx="{x}" cy="{y}" r="1.3" fill="#9C8BD0"/>'
    mouth = (f'<path d="M252 248c-10 0 -13 6 -12 14c1 9 6 14 12 14c6 0 11 -5 12 -14c1 -8 -2 -14 -12 -14Z" fill="#3A1030"/>'
             f'<ellipse cx="252" cy="270" rx="8" ry="5" fill="#E8708F"/>'
             f'<path d="M246 249h12v7q0 2 -2 2h-8q-2 0 -2 -2Z" fill="#fff"/><path d="M252 249v8" stroke="#D8CFEA" stroke-width="1"/>')
    nose = (f'<path d="M243 222Q252 217 261 222Q262 228 252 233Q242 228 243 222Z" '
            f'fill="{cv.rad(249, 222, 12, [(0, "#FFC3D3"), (0.5, "#F58FAE"), (1, "#C9557A")])}"/>'
            f'<ellipse cx="248" cy="221.5" rx="3.6" ry="1.8" fill="#fff" opacity=".85"/>'
            f'<path d="M252 233V244" stroke="#C7A6D8" stroke-width="1.6"/>')
    whisk = ""
    # whiskers: springy, one of them kinked (he is a little mad)
    for w in ("M226 238C200 228 176 222 140 226", "M226 242C196 240 170 246 132 256",
              "M228 246C206 254 186 262 158 280", "M276 238C300 226 330 214 368 214",
              "M276 242C306 238 322 252 346 244S368 240 378 250", "M274 246C298 258 318 268 346 290"):
        whisk += w
    whisk = (f'<path d="{whisk}" stroke="#6E5BB0" stroke-width="1.1" fill="none" opacity=".55" stroke-linecap="round"/>'
             f'<path d="{whisk}" stroke="#fff" stroke-width=".6" fill="none" opacity=".8" stroke-linecap="round" transform="translate(-.4 -.6)"/>')
    g += f'<g transform="rotate(-6 252 210)">{tvol}{hvol}{fw}{mz}{dots}{mouth}{nose}{whisk}</g>'

    if not arms:
        return g
    # ---- far arm: paw to cheek, "oh my ears and whiskers"
    arm2 = [(304, 296), (322, 284), (338, 264), (348, 246), (362, 240), (374, 250), (370, 270), (356, 292),
            (336, 314), (316, 322)]
    s, d, poly = furry(cv, arm2, [(0.6, 0.95, .6)], 61, down(330, 240, 1), 40, amp=3)
    g += s + '<path d="M352 246q-2 6 2 10M362 243q-1 7 3 10" stroke="#9C8BD0" stroke-width="1.2" fill="none" opacity=".7"/>'

    # ---- chain from the pocket to the watch
    g += chain_links(cv, [((306, 372), (292, 420), (220, 430), (186, 380)),
                          ((186, 380), (174, 360), (164, 340), (150, 318))], 5.2, 1.9)
    # ---- near arm and the watch
    g += watch(cv, 148, 320, 44)
    arm = [(198, 288), (222, 298), (226, 326), (214, 352), (196, 362), (182, 352), (186, 330), (190, 306)]
    s, d, poly = furry(cv, arm, [(0.12, 0.42, .6)], 62, down(205, 285, 1), 40, amp=3)
    g += f'<path d="{path(arm)}" fill="#2B1B66" opacity=".3" transform="translate(5 7)" filter="{cv.blur(6)}"/>' + s
    # paw wraps the bezel: palm behind, three fingers over the rim
    palm = [(180, 306), (196, 304), (204, 322), (198, 346), (184, 352), (178, 336)]
    s, d, poly = furry(cv, palm, [], 63, lambda x, y: 1.6, 12, shade=("#6C58B4", .45, 7, 5))
    g += s
    for (fx, fy, r) in ((182, 308, 7.5), (178, 322, 8), (179, 337, 7.5)):
        fp = ellipse_pts(fx, fy, r * 1.25, r, 8)
        g += (f'<ellipse cx="{fx + 3}" cy="{fy + 4}" rx="{r * 1.2}" ry="{r * .9}" fill="#2B1B66" opacity=".35" '
              f'filter="{cv.blur(2.5)}"/>')
        g += volume(cv, path(fp), sample(fp), cv.lin(fx - r, fy - r, fx + r, fy + r, FUR),
                    shade=("#6C58B4", .5, 5, 3), hi=HI, rim=("#B9A6FF", .8, 1.6, 1))
    return g
