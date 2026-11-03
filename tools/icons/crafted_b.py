# SPDX-License-Identifier: GPL-2.0-or-later
"""Crafted objects, part two: calculator, calendar, control centre, launcher, plugin maker, notes,
photos, system monitor, text editor, games, trash and the six Kit boxes. Same language as
crafted_a.py (LANGUAGE-v2): a lit object on the soft card, ramps and two shadows, one pop."""
import math
from svgk import *

METAL = [(0, "#FFFFFF"), (.45, "#D5D9E2"), (1, "#8B93A6")]
BRASS = [(0, "#FFF0B3"), (.5, "#E5A93B"), (1, "#8A5A12")]
PAPER = [(0, "#FFFAF0"), (.55, "#F6E7CC"), (1, "#E1C8A2")]
IVORY = [(0, "#FFFFFF"), (1, "#EAE3D6")]


def paper_lines(cv, x, y, w, n_, step, color="#8CA3A6", op=.55, h=12, first=1.0, shorten=60):
    out = ""
    for i in range(n_):
        lw = (w - (shorten if i % 2 else 0)) * (first if i == 0 else 1)
        out += f'<rect x="{n(x)}" y="{n(y + i * step)}" width="{n(lw)}" height="{h}" rx="{h / 2}" fill="{color}" opacity="{op}"/>'
    return out


# ---------------------------------------------------------------- CALCULATOR
def calculator(cv):
    container(cv, "#34C77B", "#0B5D3B", glow="#D5FFE6", edge="#02281A", glow_op=.30)
    L, T, R, B = 334, 232, 690, 794
    body = rrect(L, T, R - L, B - T, 58)
    o = solid(cv, body, "#F7F8FB", "#A3ABBD", shade="#03301F", edge="#02281A", lip=6, amb=(34, 24, .58))
    # brushed face: faint vertical grain
    o += f'<g clip-path="{cv.clip(body)}" opacity=".5">' + "".join(
        f'<rect x="{x}" y="{T}" width="2" height="{B - T}" fill="{"#fff" if i % 2 else "#6A748C"}" opacity="{.05 + .05 * ((i * 7) % 5) / 5:.3f}"/>'
        for i, x in enumerate(range(L + 6, R - 4, 7))) + '</g>'
    # display: dark glass with mint digits
    sx0, sy0, sx1, sy1 = L + 38, T + 44, R - 38, T + 176
    scr = rrect(sx0, sy0, sx1 - sx0, sy1 - sy0, 26)
    o += f'<path d="{scr}" fill="#fff" opacity=".85" transform="translate(0 4)"/>'
    o += f'<path d="{scr}" fill="{cv.lin([(0, "#0C2A27"), (1, "#14463D")])}"/>'
    o += f'<path d="{scr}" fill="none" stroke="#000" stroke-opacity=".5" stroke-width="4"/>'
    dx0 = sx0 + 104
    dg = f"M{dx0} {sy0 + 32}V{sy0 + 80}H{dx0 + 46}M{dx0 + 46} {sy0 + 32}V{sy0 + 100}"
    dg2 = f"M{dx0 + 100} {sy0 + 32}H{dx0 + 146}V{sy0 + 66}H{dx0 + 100}V{sy0 + 100}H{dx0 + 146}"
    for d_ in (dg, dg2):
        o += f'<path d="{d_}" fill="none" stroke="#2FD6A0" stroke-width="26" stroke-linecap="round" stroke-linejoin="round" opacity=".55" filter="{cv.blur(14)}"/>'
        o += f'<path d="{d_}" fill="none" stroke="{cv.lin([(0, "#C8FFEA"), (1, "#39E0A8")])}" stroke-width="15" stroke-linecap="round" stroke-linejoin="round"/>'
    o += f'<path d="M{sx0} {sy0}H{sx0 + 150}L{sx0 + 40} {sy1}H{sx0}Z" fill="#fff" opacity=".10" clip-path="{cv.clip(scr)}"/>'
    # keys 3 x 4, the right column ends in one tall key (the pop)
    kx0, ky0, kw, kh, gx, gy = L + 40, T + 220, 76, 62, 22, 22
    key = cv.lin([(0, "#FFFFFF"), (1, "#C9CFDC")])
    for r in range(4):
        for c in range(3):
            x, y = kx0 + c * (kw + gx), ky0 + r * (kh + gy)
            if c == 2 and r == 2:
                h_ = kh * 2 + gy
                d_ = rrect(x, y, kw, h_, 20)
                o += shadow(cv, d_, 10, 6, "#4A2A00", .5) + f'<path d="{d_}" fill="{cv.lin([(0, "#FFE08A"), (1, "#F0A81E")])}"/>' + rimlight(cv, d_, 4, .9)
                o += f'<path d="M{x + 22} {y + h_ / 2 - 9}H{x + kw - 22}M{x + 22} {y + h_ / 2 + 9}H{x + kw - 22}" stroke="#7A4A00" stroke-width="8" stroke-linecap="round"/>'
                continue
            if c == 2 and r == 3:
                continue
            d_ = rrect(x, y, kw, kh, 18)
            o += shadow(cv, d_, 9, 6, "#1A2236", .45) + f'<path d="{d_}" fill="{key}"/>' + rimlight(cv, d_, 4, .95)
    cv.add(o)


# ---------------------------------------------------------------- CALENDAR
def calendar(cv):
    container(cv, "#FF6B5E", "#A81F34", glow="#FFD9CF", edge="#4A0A14", glow_op=.30)
    L, T, R, B = 262, 262, 762, 774
    # the leaves underneath, edges showing
    o = ""
    for k, dy in ((2, 30), (1, 15)):
        d_ = rrect(L + 12 * k, T + dy, R - L - 24 * k, B - T, 40)
        o += shadow(cv, d_, 10, 8, "#3A0710", .35) + f'<path d="{d_}" fill="{cv.lin([(0, "#F3E4D6"), (1, "#D2B9A3")])}"/>'
    pg = rrect(L, T, R - L, B - T - 6, 44)
    o += solid(cv, pg, "#FFFFFF", "#F1E3D3", shade="#3A0710", edge="#4A0A14", lip=5, amb=(30, 22, .55))
    # header band in deep plum, with a lit lip
    hd = f"M{L} {T + 112}V{T + 44}A44 44 0 0 1 {L + 44} {T}H{R - 44}A44 44 0 0 1 {R} {T + 44}V{T + 112}Z"
    o += f'<path d="{hd}" fill="{cv.lin([(0, "#7E2A58"), (1, "#4A1236")])}"/>'
    o += rimlight(cv, hd, 5, .55) + f'<rect x="{L}" y="{T + 112}" width="{R - L}" height="6" fill="#000" opacity=".22"/>'
    # month name as a pill
    o += f'<rect x="{512 - 74}" y="{T + 40}" width="148" height="32" rx="16" fill="#fff" opacity=".75"/>'
    # binding rings, through the header
    for x in (372, 652):
        o += shadow(cv, rrect(x - 18, T - 48, 36, 120, 18), 12, 6, "#2A0610", .5)
        o += f'<rect x="{x - 18}" y="{T - 52}" width="36" height="124" rx="18" fill="{cv.lin(METAL, 0, 0, 1, 0)}"/>'
        o += f'<rect x="{x - 6}" y="{T - 40}" width="12" height="100" rx="6" fill="#fff" opacity=".8"/>'
        o += f'<rect x="{x - 12}" y="{T + 34}" width="24" height="30" rx="12" fill="#2A0610" opacity=".55"/>'
    # the grid: numerals as short pills, today ringed
    gx0, gy0, cw, ch = L + 52, T + 168, 100, 96
    for r in range(3):
        for c in range(4):
            cx_, cy_ = gx0 + c * cw + 40, gy0 + r * ch + 36
            if (r, c) == (1, 2):
                o += shadow(cv, circ(cx_, cy_, 50), 10, 6, "#6A3A00", .5)
                o += f'<circle cx="{cx_}" cy="{cy_}" r="50" fill="{cv.rad([(0, "#FFE9A6"), (1, "#F0A81E")], .4, .3, .85)}"/>'
                o += f'<rect x="{cx_ - 22}" y="{cy_ - 11}" width="44" height="22" rx="11" fill="#6A3A00"/>'
            else:
                o += f'<rect x="{cx_ - 24}" y="{cy_ - 10}" width="{48 if c % 2 else 34}" height="20" rx="10" fill="#7C6A74" opacity=".55"/>'
    cv.add(o)


# ---------------------------------------------------------------- CONTROL CENTRE
def control_center(cv):
    container(cv, "#5E8BFF", "#1B2C94", glow="#D5E2FF", edge="#060F46", glow_op=.30)
    L, T, R, B = 246, 290, 778, 738
    plate = rrect(L, T, R - L, B - T, 72)
    o = solid(cv, plate, "#FFFFFF", "#B8C6F2", shade="#050E4A", edge="#060F46", lip=6, amb=(34, 24, .6))
    o += f'<path d="{plate}" fill="{cv.lin([(.6, "#1B2C94", 0), (1, "#1B2C94", .16)])}"/>'
    rows = ((392, 470, "#4D6BFF", "#2438C8"), (514, 640, "#FFD36B", "#F0A81E"), (636, 402, "#4D6BFF", "#2438C8"))
    for y, kx, c0, c1 in rows:
        tx0, tx1 = L + 62, R - 62
        tr = rrect(tx0, y - 15, tx1 - tx0, 30, 15)
        o += f'<path d="{tr}" fill="{cv.lin([(0, "#7C8CC8"), (1, "#C4CFF0")])}"/>'
        o += f'<path d="{tr}" fill="none" stroke="#0B1A6A" stroke-opacity=".35" stroke-width="3"/>'
        fl = rrect(tx0, y - 15, kx - tx0, 30, 15)
        o += f'<path d="{fl}" fill="{cv.lin([(0, c0), (1, c1)])}"/>'
        o += f'<path d="M{tx0 + 12} {y - 8}H{kx - 12}" stroke="#fff" stroke-opacity=".5" stroke-width="5" stroke-linecap="round"/>'
        o += shadow(cv, circ(kx, y, 44), 16, 8, "#050E4A", .6)
        o += f'<circle cx="{kx}" cy="{y}" r="44" fill="{cv.lin(METAL, 0, 0, 1, 1)}"/>'
        o += f'<circle cx="{kx}" cy="{y}" r="44" fill="none" stroke="#fff" stroke-width="5" opacity=".7" clip-path="{cv.clip(circ(kx, y, 44))}"/>'
        o += f'<circle cx="{kx}" cy="{y + 3}" r="26" fill="{cv.lin([(0, "#8B93A6"), (1, "#F2F4F8")])}"/>'
    cv.add(o)


# ---------------------------------------------------------------- LAUNCHER (a magnifier)
def launcher(cv):
    container(cv, "#7A5CFF", "#1F1470", glow="#C9BEFF", edge="#0A0440", glow_op=.30)
    cx, cy, R = 466, 462, 196
    # handle first (it lies behind the ring where they meet)
    hd = "M606 604L742 740"
    o = f'<path d="{hd}" stroke="#0A0440" stroke-width="86" stroke-linecap="round" opacity=".5" filter="{cv.blur(18)}" transform="translate(0 28)"/>'
    o += f'<path d="{hd}" stroke="{cv.lin([(0, "#7A4A2A"), (1, "#3A1E10")], 0, 0, 1, 1)}" stroke-width="82" stroke-linecap="round"/>'
    o += f'<path d="{hd}" stroke="#E7B27E" stroke-opacity=".55" stroke-width="12" stroke-linecap="round" transform="translate(-14 -16)"/>'
    o += f'<path d="M588 586L628 626" stroke="{cv.lin(BRASS, 0, 0, 1, 1)}" stroke-width="92" stroke-linecap="butt"/>'
    # ring
    o += shadow(cv, circ(cx, cy, R + 26), 30, 22, "#0A0440", .6) + shadow(cv, circ(cx, cy, R + 26), 9, 7, "#0A0440", .45)
    o += f'<circle cx="{cx}" cy="{cy}" r="{R + 26}" fill="{cv.lin(BRASS, 0, 0, 1, 1)}"/>'
    o += f'<circle cx="{cx}" cy="{cy}" r="{R + 26}" fill="none" stroke="#FFF7D0" stroke-width="5" opacity=".9" clip-path="{cv.clip(circ(cx, cy, R + 26))}"/>'
    o += f'<circle cx="{cx}" cy="{cy}" r="{R + 2}" fill="{cv.lin([(0, "#8A5A12"), (1, "#FFE9A0")])}"/>'
    # glass: the lens shows a warm lit door magnified
    o += f'<circle cx="{cx}" cy="{cy}" r="{R - 8}" fill="{cv.rad([(0, "#F4EEFF"), (.5, "#BDB0FF"), (1, "#6E58E8")], .4, .35, .95)}"/>'
    door = f"M{cx - 52} {cy + 100}V{cy - 22}a52 52 0 0 1 104 0V{cy + 100}Z"
    o += f'<ellipse cx="{cx}" cy="{cy + 20}" rx="110" ry="120" fill="#FFC94A" opacity=".55" filter="{cv.blur(26)}"/>'
    o += f'<path d="{door}" fill="{cv.rad([(0, "#FFF6C8"), (.45, "#FFD04A"), (1, "#F08A1C")], .5, .9, .95)}"/>'
    o += f'<path d="{door}" fill="none" stroke="#5B3CE0" stroke-width="12" stroke-linejoin="round"/>'
    o += f'<circle cx="{cx}" cy="{cy}" r="{R - 8}" fill="none" stroke="#2A1A80" stroke-opacity=".35" stroke-width="8"/>'
    o += f'<path d="M{cx - 150} {cy - 60}A168 168 0 0 1 {cx + 30} {cy - 164}Q{cx - 80} {cy - 120} {cx - 150} {cy - 60}Z" fill="#fff" opacity=".7"/>'
    o += ellipse_spec(cv, cx + 96, cy + 128, 40, 14, -40, .45, 3)
    cv.add(o)


# ---------------------------------------------------------------- PLUGIN MAKER (a puzzle piece)
def plugin_maker(cv):
    container(cv, "#37D6E4", "#0D5F86", glow="#D5FBFF", edge="#012B42", glow_op=.30)
    x0, y0, x1, y1 = 308, 318, 716, 726
    cx, cy, k = (x0 + x1) / 2, (y0 + y1) / 2, 50
    nk = 38
    d = (f"M{x0} {y0}H{cx - nk}A{k} {k} 0 1 1 {cx + nk} {y0}H{x1}"
         f"V{cy - nk}A{k} {k} 0 1 0 {x1} {cy + nk}V{y1}H{x0}"
         f"V{cy + nk}A{k} {k} 0 1 1 {x0} {cy - nk}Z")
    # the knobs poke out: draw with a round join so the corners are soft
    o = shadows(cv, d, "#012B42", (34, 24, .6), (10, 8, .45))
    o += f'<path d="{d}" fill="{cv.lin([(0, "#B9A2FF"), (.5, "#7A55F0"), (1, "#3B1FB8")])}" stroke="{cv.lin([(0, "#B9A2FF"), (.5, "#7A55F0"), (1, "#3B1FB8")])}" stroke-width="22" stroke-linejoin="round"/>'
    o += rimlight(cv, d, 7, .85)
    o += f'<path d="{d}" fill="none" stroke="#12056A" stroke-opacity=".4" stroke-width="3"/>'
    # a brass plus inlaid
    pl = f"M{cx - 20} {cy - 96}H{cx + 20}V{cy - 20}H{cx + 96}V{cy + 20}H{cx + 20}V{cy + 96}H{cx - 20}V{cy + 20}H{cx - 96}V{cy - 20}H{cx - 20}Z"
    pl = pl.replace(str(cy), str(cy))
    o += f'<path d="{pl}" fill="#12056A" opacity=".5" transform="translate(0 -5)" stroke="#12056A" stroke-width="8" stroke-linejoin="round"/>'
    o += f'<path d="{pl}" fill="{cv.lin(BRASS)}" stroke="{cv.lin(BRASS)}" stroke-width="8" stroke-linejoin="round" transform="translate(0 2)"/>'
    o += f'<path d="{pl}" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width="3" transform="translate(0 -3)"/>'
    cv.add(o)


# ---------------------------------------------------------------- NOTES (a pad and a pencil)
def notes(cv):
    container(cv, "#FFE066", "#D4960A", glow="#FFF8CF", edge="#5A3A00", glow_op=.34)
    L, T, R, B = 268, 238, 724, 778
    pad = rrect(L, T, R - L, B - T, 40)
    o = solid(cv, pad, "#FFFFFF", "#F0E6D2", shade="#5A3A00", edge="#5A3A00", lip=5, amb=(30, 22, .55))
    # ruled lines and handwriting
    for i in range(7):
        y = 378 + i * 54
        o += f'<rect x="{L + 36}" y="{y}" width="{R - L - 72}" height="4" rx="2" fill="#7FA4C8" opacity=".55"/>'
    ink = "#3B3D8F"
    o += (f'<path d="M{L + 50} 360C{L + 80} 318 {L + 110} 400 {L + 140} 350S{L + 190} 330 {L + 210} 362" fill="none" stroke="{ink}" stroke-width="12" stroke-linecap="round" opacity=".85"/>'
          f'<path d="M{L + 50} 414C{L + 90} 380 {L + 120} 450 {L + 170} 404S{L + 250} 392 {L + 300} 410" fill="none" stroke="{ink}" stroke-width="12" stroke-linecap="round" opacity=".7"/>')
    # binding strip with wire loops
    st = f"M{L} {T + 90}V{T + 40}A40 40 0 0 1 {L + 40} {T}H{R - 40}A40 40 0 0 1 {R} {T + 40}V{T + 90}Z"
    o += f'<path d="{st}" fill="{cv.lin([(0, "#C2503A"), (1, "#7A2216")])}"/>' + rimlight(cv, st, 5, .6)
    o += f'<rect x="{L}" y="{T + 90}" width="{R - L}" height="8" fill="#3A0A04" opacity=".25"/>'
    for i in range(7):
        x = L + 56 + i * 58
        o += f'<rect x="{x - 9}" y="{T - 30}" width="18" height="96" rx="9" fill="{cv.lin(METAL, 0, 0, 1, 0)}"/>'
        o += f'<rect x="{x - 9}" y="{T + 48}" width="18" height="22" rx="9" fill="#3A0A04" opacity=".5"/>'
    # pencil
    pc = 'transform="rotate(-42 640 684)"'
    px, py, pl_, pw = 640 - 200, 684 - 40, 400, 80
    body = rrect(px + 36, py, pl_ - 120, pw, 14)
    g = shadow(cv, rrect(px, py, pl_, pw, 30), 22, 12, "#3A2000", .55)
    g += f'<rect x="{px + 36}" y="{py}" width="{pl_ - 140}" height="{pw}" rx="12" fill="{cv.lin([(0, "#58C7E6"), (.5, "#2F9AC8"), (1, "#1A5E8E")])}"/>'
    g += f'<rect x="{px + 36}" y="{py + 8}" width="{pl_ - 140}" height="10" fill="#fff" opacity=".6"/>'
    g += f'<path d="M{px + 36} {py}H{px + pl_ - 100}V{py + pw}H{px + 36}Z" fill="none"/>'
    g += f'<path d="M{px + pl_ - 104} {py}L{px + pl_ - 20} {py + 30}Q{px + pl_ - 6} {py + pw / 2} {px + pl_ - 20} {py + pw - 30}L{px + pl_ - 104} {py + pw}Z" fill="{cv.lin([(0, "#F7D9A8"), (1, "#C99A5E")])}"/>'
    g += f'<path d="M{px + pl_ - 40} {py + 20}L{px + pl_ + 22} {py + pw / 2}L{px + pl_ - 40} {py + pw - 20}Z" fill="#3A3F52"/>'
    g += f'<rect x="{px + 4}" y="{py}" width="46" height="{pw}" rx="10" fill="{cv.lin(BRASS, 0, 0, 0, 1)}"/>'
    g += f'<rect x="{px - 20}" y="{py}" width="40" height="{pw}" rx="18" fill="{cv.lin([(0, "#FFC1CE"), (1, "#E0728A")])}"/>'
    o += f'<g {pc}>{g}</g>'
    cv.add(o)


# ---------------------------------------------------------------- PHOTOS (a print, taped)
def photos(cv):
    container(cv, "#62C9FF", "#1465C0", glow="#E1F6FF", edge="#02295A", glow_op=.32)
    o = ""
    back = rrect(290, 250, 420, 500, 22)
    o += f'<g transform="rotate(-9 500 500)">{shadows(cv, back, "#02295A", (22, 16, .45), (6, 5, .35))}<path d="{back}" fill="{cv.lin([(0, "#F4F8FF"), (1, "#C9D8EC")])}"/></g>'
    fr = rrect(318, 236, 440, 536, 24)
    g = solid(cv, fr, "#FFFFFF", "#E8EDF5", shade="#02295A", edge="#02295A", lip=5, amb=(28, 20, .55))
    ph = rrect(350, 268, 376, 376, 8)
    g += f'<path d="{ph}" fill="{cv.lin([(0, "#6FC2FF"), (.62, "#FFE3A8"), (1, "#FFC38A")])}"/>'
    g += f'<g clip-path="{cv.clip(ph)}">'
    g += f'<circle cx="640" cy="404" r="74" fill="#FFE9A8" opacity=".75" filter="{cv.blur(22)}"/>'
    g += f'<circle cx="640" cy="404" r="40" fill="{cv.rad([(0, "#FFFDF0"), (1, "#FFC94A")], .4, .35, .9)}"/>'
    g += (f'<path d="M350 566C420 486 480 500 540 546C590 510 650 500 726 556V644H350Z" fill="{cv.lin([(0, "#3FA878"), (1, "#16614A")])}"/>'
          f'<path d="M350 600C440 540 520 584 590 604C640 580 690 584 726 596V644H350Z" fill="{cv.lin([(0, "#1E7F5E"), (1, "#0E3F36")])}"/>')
    g += f'<ellipse cx="470" cy="360" rx="64" ry="20" fill="#fff" opacity=".85"/><ellipse cx="510" cy="344" rx="42" ry="18" fill="#fff" opacity=".85"/>'
    g += f'<path d="M350 268H726V300H350Z" fill="#fff" opacity=".10"/></g>'
    g += f'<path d="{ph}" fill="none" stroke="#02295A" stroke-opacity=".25" stroke-width="4"/>'
    g += f'<path d="M350 644H726" stroke="#fff" stroke-opacity=".9" stroke-width="3"/>'
    g += f'<rect x="350" y="676" width="190" height="16" rx="8" fill="#8CA0BE" opacity=".6"/>'
    o += f'<g transform="rotate(5 538 504)">{g}'
    # tape
    tp = "M470 214H600L612 270H458Z"
    o += f'<path d="{tp}" fill="#FFE8A8" opacity=".85" transform="translate(0 6)"/><path d="{tp}" fill="#FFF6D6" opacity=".6"/></g>'
    cv.add(o)


# ---------------------------------------------------------------- SYSTEM MONITOR (an oscilloscope)
def system_monitor(cv):
    container(cv, "#4D6785", "#111B2C", glow="#A9C1E8", edge="#02060F", glow_op=.28)
    L, T, R, B = 236, 262, 788, 764
    bz = rrect(L, T, R - L, B - T, 60)
    o = solid(cv, bz, "#F4F6FA", "#98A2B8", shade="#02060F", edge="#02060F", lip=6, amb=(34, 24, .6))
    scr = rrect(L + 40, T + 40, R - L - 80, 290, 30)
    o += f'<path d="{scr}" fill="#fff" opacity=".8" transform="translate(0 4)"/>'
    o += f'<path d="{scr}" fill="{cv.lin([(0, "#0B2B35"), (1, "#06141F")])}"/>'
    o += f'<g clip-path="{cv.clip(scr)}">'
    for i in range(1, 5):
        o += f'<rect x="{L + 40}" y="{T + 40 + i * 58}" width="{R - L - 80}" height="3" fill="#7FE8D0" opacity=".14"/>'
    for i in range(1, 7):
        o += f'<rect x="{L + 40 + i * 69}" y="{T + 40}" width="3" height="290" fill="#7FE8D0" opacity=".10"/>'
    line = smooth([(L + 56, T + 250), (L + 130, T + 232), (L + 190, T + 262), (L + 250, T + 150), (L + 300, T + 220), (L + 350, T + 120), (L + 410, T + 210), (L + 470, T + 170), (L + 500, T + 190)], closed=False)
    area = line + f"L{L + 500} {T + 330}L{L + 56} {T + 330}Z"
    o += f'<path d="{area}" fill="{cv.lin([(0, "#2FD6A0", .45), (1, "#2FD6A0", 0)])}"/>'
    o += f'<path d="{line}" fill="none" stroke="#2FD6A0" stroke-width="30" stroke-linecap="round" stroke-linejoin="round" opacity=".6" filter="{cv.blur(14)}"/>'
    o += f'<path d="{line}" fill="none" stroke="{cv.lin([(0, "#C8FFEA"), (1, "#39E0A8")])}" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>'
    o += f'<path d="M{L + 40} {T + 40}H{L + 300}L{L + 120} {T + 330}H{L + 40}Z" fill="#fff" opacity=".08"/></g>'
    o += f'<path d="{scr}" fill="none" stroke="#000" stroke-opacity=".55" stroke-width="4"/>'
    # controls below
    for x in (L + 100, L + 214):
        o += knob(cv, x, T + 410, 40, "#FFFFFF", "#C9CFDC", "#6D7690", "#02060F", 12)
        o += f'<path d="M{x} {T + 410}L{x + 12} {T + 384}" stroke="#2A3350" stroke-width="7" stroke-linecap="round"/>'
    for i, c in enumerate(("#2FD6A0", "#2FD6A0", "#FFC94A")):
        x = R - 100 - i * 52
        o += f'<circle cx="{x}" cy="{T + 410}" r="22" fill="{c}" opacity=".45" filter="{cv.blur(8)}"/><circle cx="{x}" cy="{T + 410}" r="14" fill="{c}"/><circle cx="{x - 4}" cy="{T + 404}" r="5" fill="#fff" opacity=".8"/>'
    cv.add(o)


# ---------------------------------------------------------------- TEXT EDITOR (a page, a caret)
def text_editor(cv):
    container(cv, "#B6E36B", "#478A2A", glow="#F2FFD6", edge="#143D0A", glow_op=.32)
    L, T, R, B = 290, 236, 734, 788
    f = 96
    pg = f"M{L + 44} {T}H{R - f}L{R} {T + f}V{B - 44}A44 44 0 0 1 {R - 44} {B}H{L + 44}A44 44 0 0 1 {L} {B - 44}V{T + 44}A44 44 0 0 1 {L + 44} {T}Z"
    o = solid(cv, pg, "#FFFFFF", "#EFE9D8", shade="#143D0A", edge="#143D0A", lip=5, amb=(30, 22, .55))
    ear = f"M{R - f} {T}V{T + f - 30}A30 30 0 0 0 {R - f + 30} {T + f}H{R}Z"
    o += shadow(cv, ear, 8, 6, "#143D0A", .4) + f'<path d="{ear}" fill="{cv.lin([(0, "#E9E2CE"), (1, "#C9C0A6")], 0, 0, 1, 1)}"/>'
    # lines of text, one selected
    ink = "#4A5568"
    o += f'<rect x="{L + 50}" y="{T + 150}" width="210" height="26" rx="13" fill="{ink}" opacity=".85"/>'
    sel = rrect(L + 40, T + 220, 300, 56, 12)
    o += f'<path d="{sel}" fill="#7C5CFF" opacity=".28"/>'
    for y, w in ((T + 237, 250), (T + 320, 340), (T + 380, 300), (T + 440, 340), (T + 500, 170)):
        o += f'<rect x="{L + 52}" y="{y}" width="{w}" height="22" rx="11" fill="{ink}" opacity="{.8 if y == T + 237 else .55}"/>'
    o += f'<rect x="{L + 52 + 250 + 12}" y="{T + 214}" width="8" height="68" rx="4" fill="#5B3CE0"/>'
    cv.add(o)


# ---------------------------------------------------------------- GAMES (a pad)
def games(cv):
    container(cv, "#FF5DAA", "#9A1670", glow="#FFD3EA", edge="#470633", glow_op=.30)
    pts = [(300, 400), (420, 372), (512, 384), (604, 372), (724, 400), (792, 500), (800, 610), (762, 690),
           (700, 698), (652, 644), (604, 598), (512, 592), (420, 598), (372, 644), (324, 698), (262, 690), (224, 610), (232, 500)]
    d = smooth(pts)
    o = solid(cv, d, "#4B5078", "#161830", shade="#2A0620", edge="#000", lip=6, amb=(34, 24, .62))
    o += f'<path d="{d}" fill="none" stroke="#fff" stroke-opacity=".22" stroke-width="8" clip-path="{cv.clip(d)}" transform="translate(0 7)"/>'
    # shoulder triggers
    for x in (330, 600):
        t_ = rrect(x, 318, 96, 40, 18)
        o += f'<path d="{t_}" fill="{cv.lin([(0, "#6A70A0"), (1, "#2A2E52")])}" transform="translate(0 -4)"/>' + rimlight(cv, t_, 4, .6)
    # d-pad
    cx, cy = 372, 500
    dp = f"M{cx - 24} {cy - 74}H{cx + 24}V{cy - 24}H{cx + 74}V{cy + 24}H{cx + 24}V{cy + 74}H{cx - 24}V{cy + 24}H{cx - 74}V{cy - 24}H{cx - 24}Z"
    o += f'<path d="{dp}" fill="#000" opacity=".5" transform="translate(0 7)" stroke="#000" stroke-width="12" stroke-linejoin="round" filter="{cv.blur(5)}"/>'
    o += f'<path d="{dp}" fill="{cv.lin([(0, "#F4F6FF"), (1, "#A9B0D0")])}" stroke="{cv.lin([(0, "#F4F6FF"), (1, "#A9B0D0")])}" stroke-width="12" stroke-linejoin="round"/>'
    o += f'<path d="M{cx - 18} {cy - 56}V{cy - 18}M{cx - 56} {cy - 18}H{cx - 18}" stroke="#fff" stroke-width="5" stroke-linecap="round" fill="none" opacity=".7"/>'
    o += f'<circle cx="{cx}" cy="{cy}" r="16" fill="#6A70A0" opacity=".6"/>'
    # four buttons, one gold
    bx, by = 660, 500
    for dx, dy, c0, c1 in ((0, -56, "#E8EAFB", "#9AA2C8"), (56, 0, "#E8EAFB", "#9AA2C8"), (0, 56, "#E8EAFB", "#9AA2C8"), (-56, 0, "#FFE08A", "#F0A81E")):
        o += shadow(cv, circ(bx + dx, by + dy, 34), 9, 5, "#000", .55)
        o += f'<circle cx="{bx + dx}" cy="{by + dy}" r="34" fill="{cv.lin([(0, c0), (1, c1)])}"/>'
        o += f'<circle cx="{bx + dx}" cy="{by + dy}" r="34" fill="none" stroke="#fff" stroke-opacity=".85" stroke-width="4" clip-path="{cv.clip(circ(bx + dx, by + dy, 34))}"/>'
    # centre buttons
    for x in (480, 544):
        o += f'<rect x="{x - 18}" y="456" width="36" height="16" rx="8" fill="#0C0E22"/><rect x="{x - 18}" y="456" width="36" height="5" rx="2.5" fill="#fff" opacity=".35"/>'
    cv.add(o)


# ---------------------------------------------------------------- TRASH (a wastepaper basket)
def trash(cv):
    container(cv, "#7C8BAA", "#2B3552", glow="#D9E2FF", edge="#0A1022", glow_op=.28)
    d = "M286 360H738L694 742Q688 790 640 790H384Q336 790 330 742Z"
    o = ""
    # paper balls peek out above the rim
    for pts, fill in (([(330, 372), (346, 296), (398, 262), (456, 276), (470, 330), (446, 372)], "#FFFFFF"),
                      ([(520, 372), (530, 292), (586, 252), (650, 278), (668, 336), (650, 372)], "#FFF1D6")):
        pd = smooth(pts)
        o += shadow(cv, pd, 10, 6, "#0A1022", .45) + f'<path d="{pd}" fill="{cv.lin([(0, fill), (1, "#CFC6B4")])}"/>'
        o += f'<path d="{pd}" fill="none" stroke="#8C8470" stroke-opacity=".5" stroke-width="3" stroke-linejoin="round"/>'
    o += f'<path d="M352 300L392 340L422 296M556 286L606 340L640 280" fill="none" stroke="#8C8470" stroke-opacity=".5" stroke-width="3"/>'
    o += solid(cv, d, "#E6EAF3", "#7B87A3", shade="#0A1022", edge="#0A1022", lip=5, amb=(34, 24, .62))
    clip = cv.clip(d)
    o += f'<g clip-path="{clip}" fill="none" stroke-linecap="round">'
    for i in range(-3, 12):
        x = 250 + i * 54
        o += f'<path d="M{x} 340L{x + 220} 800M{x + 220} 340L{x} 800" stroke="#2B3552" stroke-opacity=".38" stroke-width="7"/>'
        o += f'<path d="M{x - 3} 340L{x + 217} 800M{x + 223} 340L{x + 3} 800" stroke="#fff" stroke-opacity=".34" stroke-width="3"/>'
    o += f'<path d="{d}" fill="{cv.lin([(0, "#0A1022", 0), (.6, "#0A1022", 0), (1, "#0A1022", .38)])}"/></g>'
    # the rim ring
    rim = rrect(262, 336, 500, 56, 28)
    o += shadow(cv, rim, 10, 6, "#0A1022", .5) + f'<path d="{rim}" fill="{cv.lin(METAL)}"/>' + rimlight(cv, rim, 4, .9)
    o += f'<path d="M290 378H734" stroke="#4A5578" stroke-opacity=".5" stroke-width="5" stroke-linecap="round"/>'
    cv.add(o)


# ---------------------------------------------------------------- the Kit boxes (a lid band on the card)
def kit_ai(cv):
    container(cv, "#8C7CFF", "#2B1B8A", glow="#DCD5FF", edge="#0A0440", glow_op=.30, kit=True)
    cx, cy, R = 512, 612, 196
    o = shadow(cv, circ(cx, cy, R), 30, 22, "#0A0440", .6) + shadow(cv, circ(cx, cy, R), 9, 7, "#0A0440", .45)
    o += f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{cv.rad([(0, "#B9A8FF"), (.5, "#5B3CE0"), (1, "#1A0E70")], .38, .3, .95)}"/>'
    # the rim light: clipped to the orb moved down with it (the clip sits in the shifted space)
    o += soft_ring(cv, cx, cy + 20, R - 12, 16, 10, "#9BE7FF", .9, cv.clip(circ(cx, cy + 20, R)))
    st = lambda x, y, r, w=.2: (f"M{x} {y - r}Q{x + r * w} {y - r * w} {x + r} {y}Q{x + r * w} {y + r * w} {x} {y + r}"
                                f"Q{x - r * w} {y + r * w} {x - r} {y}Q{x - r * w} {y - r * w} {x} {y - r}Z")
    big = st(cx - 8, cy + 6, 110)
    o += f'<path d="{big}" fill="#FFD36B" opacity=".6" filter="{cv.blur(22)}"/>'
    o += f'<path d="{big}" fill="{cv.lin([(0, "#FFFBE0"), (1, "#FFB93A")])}"/>'
    o += f'<path d="{st(cx + 104, cy - 82, 44, .22)}" fill="#FFF3C0"/><path d="{st(cx - 114, cy + 96, 30, .24)}" fill="#C9F4FF"/>'
    o += f'<circle cx="{cx + 90}" cy="{cy + 100}" r="9" fill="#C9F4FF"/><circle cx="{cx - 100}" cy="{cy - 78}" r="7" fill="#fff" opacity=".8"/>'
    o += f'<path d="M{cx - 150} {cy - 70}A180 180 0 0 1 {cx + 10} {cy - 176}Q{cx - 90} {cy - 130} {cx - 150} {cy - 70}Z" fill="#fff" opacity=".6"/>'
    cv.add(o)


def kit_codecs(cv):
    container(cv, "#FF8A4C", "#B72A18", glow="#FFE3CF", edge="#4A0C00", glow_op=.30, kit=True)
    cx, cy, R = 512, 614, 202
    o = shadow(cv, circ(cx, cy, R), 30, 22, "#3A0800", .6) + shadow(cv, circ(cx, cy, R), 9, 7, "#3A0800", .45)
    o += f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{cv.lin([(0, "#5A607C"), (1, "#14161F")])}"/>'
    o += f'<circle cx="{cx}" cy="{cy}" r="{R - 4}" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width="6" clip-path="{cv.clip(circ(cx, cy, R))}" transform="translate(0 3)" opacity=".7"/>'
    for i in range(6):
        a = math.radians(i * 60 - 90)
        hx, hy = cx + 118 * math.cos(a), cy + 118 * math.sin(a)
        o += f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="46" fill="#0A0B12"/>'
        o += f'<path d="M{hx - 46:.1f} {hy:.1f}a46 46 0 0 0 92 0" fill="none" stroke="#B9C0DA" stroke-opacity=".7" stroke-width="5"/>'
        o += f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="46" fill="none" stroke="#000" stroke-opacity=".6" stroke-width="4"/>'
    o += knob(cv, cx, cy, 54, "#FFF0B3", "#E5A93B", "#8A5A12", "#000", 8)
    o += f'<circle cx="{cx}" cy="{cy}" r="16" fill="#3A2400"/>'
    o += f'<path d="M{cx - 150} {cy - 110}A190 190 0 0 1 {cx - 20} {cy - 188}" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="10" stroke-linecap="round"/>'
    cv.add(o)


def kit_craft_suite(cv):
    container(cv, "#FFC857", "#D0780F", glow="#FFF3CF", edge="#5A2E00", glow_op=.34, kit=True)
    # a wooden ruler under a pencil, crossing
    rl = rrect(-250, -50, 500, 100, 14)
    g = shadow(cv, rl, 18, 10, "#3A1C00", .5) + f'<path d="{rl}" fill="{cv.lin([(0, "#FFF1CF"), (1, "#E3B873")])}"/>' + rimlight(cv, rl, 4, .9)
    for i in range(21):
        x = -230 + i * 23
        g += f'<rect x="{x}" y="-50" width="3" height="{36 if i % 5 == 0 else 22}" fill="#7A4A12" opacity=".7"/>'
    o = f'<g transform="translate(512 640) rotate(-8)">{g}</g>'
    pb = rrect(-250, -44, 380, 88, 14)
    p = shadow(cv, rrect(-260, -44, 520, 88, 30), 22, 12, "#3A1C00", .55)
    p += f'<path d="M-250 -44H130V44H-250Z" fill="{cv.lin([(0, "#6D82FF"), (.5, "#3D4FD6"), (1, "#1A2380")])}"/>'
    p += '<rect x="-250" y="-34" width="380" height="10" fill="#fff" opacity=".55"/>'
    p += f'<path d="M130 -44L238 -14Q258 0 238 14L130 44Z" fill="{cv.lin([(0, "#F7D9A8"), (1, "#C99A5E")])}"/>'
    p += '<path d="M206 -14L262 0L206 14Z" fill="#3A3F52"/>'
    p += f'<rect x="-290" y="-44" width="56" height="88" rx="10" fill="{cv.lin(BRASS)}"/>'
    p += f'<rect x="-340" y="-44" width="60" height="88" rx="26" fill="{cv.lin([(0, "#FFC1CE"), (1, "#E0728A")])}"/>'
    o += f'<g transform="translate(500 560) rotate(-36)">{p}</g>'
    cv.add(o)


def kit_creative(cv):
    container(cv, "#FF7EA6", "#B01C58", glow="#FFD8E6", edge="#4A0624", glow_op=.32, kit=True)
    pal = smooth([(262, 640), (270, 540), (350, 452), (470, 424), (590, 440), (700, 500), (770, 590), (760, 690),
                  (690, 760), (590, 742), (540, 700), (480, 706), (440, 770), (360, 782), (290, 740)])
    o = solid(cv, pal, "#FBE6C4", "#D2A96B", shade="#4A0624", edge="#4A0624", lip=5, amb=(32, 22, .6))
    o += f'<circle cx="418" cy="682" r="32" fill="#4A0624" opacity=".7" transform="translate(0 4)"/><circle cx="418" cy="682" r="32" fill="{cv.lin([(0, "#7A2A44"), (1, "#C45A78")])}"/>'
    for x, y, c0, c1 in ((330, 560, "#9BD8FF", "#2A6CD8"), (440, 502, "#FFF0A0", "#F0B018"), (560, 492, "#B8F2B8", "#2AA860"), (668, 548, "#E0C8FF", "#7B55F0"), (686, 660, "#FFB0A0", "#E23A3A")):
        b_ = smooth([(x - 54, y), (x - 38, y - 40), (x + 6, y - 50), (x + 50, y - 30), (x + 56, y + 12), (x + 20, y + 44), (x - 28, y + 40)])
        o += shadow(cv, b_, 9, 5, "#2A0412", .5) + f'<path d="{b_}" fill="{cv.lin([(0, c0), (1, c1)])}"/>'
        o += ellipse_spec(cv, x - 10, y - 26, 20, 8, -20, .85)
    # a brush lying across
    br = 'transform="translate(560 640) rotate(-34)"'
    b = shadow(cv, rrect(-60, -22, 380, 44, 20), 18, 10, "#2A0412", .55)
    b += f'<rect x="-60" y="-20" width="330" height="40" rx="18" fill="{cv.lin([(0, "#7A5C48"), (1, "#2E1E16")])}"/><rect x="-50" y="-14" width="300" height="8" rx="4" fill="#fff" opacity=".4"/>'
    b += f'<rect x="258" y="-22" width="60" height="44" rx="8" fill="{cv.lin(METAL)}"/>'
    b += f'<path d="M316 -22Q380 -26 410 0Q380 26 316 22Z" fill="{cv.lin([(0, "#FFFFFF"), (1, "#7B55F0")], 0, 0, 1, 0)}"/>'
    o += f'<g {br}>{b}</g>'
    cv.add(o)


def kit_dev(cv):
    container(cv, "#3F3A78", "#0E0B22", glow="#9B85FF", edge="#000", glow_op=.30, kit=True)
    o = ""
    for d, c0, c1, w in (("M388 560L286 650L388 740", "#C8FFEA", "#39E0A8", 62), ("M636 560L738 650L636 740", "#C8FFEA", "#39E0A8", 62),
                         ("M556 548L468 758", "#FFF3C0", "#FFB93A", 50)):
        o += f'<path d="{d}" fill="none" stroke="{c1}" stroke-width="{w + 34}" stroke-linecap="round" stroke-linejoin="round" opacity=".5" filter="{cv.blur(26)}"/>'
        o += f'<path d="{d}" fill="none" stroke="#0A0A20" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" opacity=".6" transform="translate(0 9)"/>'
        o += f'<path d="{d}" fill="none" stroke="{cv.lin([(0, c0), (1, c1)], 0, 0, 0, 1)}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'
        o += f'<path d="{d}" fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" opacity=".55" transform="translate(-6 -10)"/>'
    cv.add(o)


def kit_gaming(cv):
    container(cv, "#7DE07A", "#14783A", glow="#E6FFD9", edge="#042A0E", glow_op=.32, kit=True)
    F, Lq, Rq = (512, 790), (343, 695), (681, 695)
    Fu, Lu, Ru, T = (512, 596), (343, 501), (681, 501), (512, 406)
    left, right, top = [F, Lq, Lu, Fu], [F, Rq, Ru, Fu], [Fu, Lu, T, Ru]
    cube = poly([F, Lq, Lu, T, Ru, Rq])
    o = shadow(cv, cube, 30, 22, "#042A0E", .6) + shadow(cv, cube, 9, 7, "#042A0E", .45)
    def face(pts, a, b):
        return (f'<path d="{poly(pts)}" fill="{cv.lin(a, 0, 0, 0, 1)}" stroke="{cv.lin(a, 0, 0, 0, 1)}" stroke-width="26" stroke-linejoin="round"/>')
    o += face(left, [(0, "#F4EBDD"), (1, "#C9B79A")], 0) + face(right, [(0, "#D9C9AE"), (1, "#9C8667")], 0) + face(top, [(0, "#FFFFFF"), (1, "#EFE6D6")], 0)
    # pips
    def pips(origin, u, v, pos):
        ox, oy = origin
        mt = f'matrix({u[0] / 100:.4f} {u[1] / 100:.4f} {v[0] / 100:.4f} {v[1] / 100:.4f} {ox} {oy})'
        s = ""
        for px_, py_ in pos:
            s += f'<circle cx="{px_}" cy="{py_ + 3}" r="12" fill="#fff" opacity=".7"/><circle cx="{px_}" cy="{py_}" r="12" fill="{cv.rad([(0, "#F25A5A"), (1, "#A81428")], .4, .3, .9)}"/>'
        return f'<g transform="{mt}">{s}</g>'
    o += pips(Fu, (Lu[0] - Fu[0], Lu[1] - Fu[1]), (0, 194), [(30, 28), (70, 72)])
    o += pips(Fu, (Ru[0] - Fu[0], Ru[1] - Fu[1]), (0, 194), [(26, 24), (50, 50), (74, 76)])
    o += pips(Fu, (Lu[0] - Fu[0], Lu[1] - Fu[1]), (Ru[0] - Fu[0], Ru[1] - Fu[1]), [(50, 50)])
    o += f'<path d="{poly(top)}" fill="none" stroke="#fff" stroke-opacity=".8" stroke-width="5" stroke-linejoin="round"/>'
    cv.add(o)
